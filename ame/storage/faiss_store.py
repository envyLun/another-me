"""
Faiss 向量存储封装
职责：高性能向量相似度检索（短期记忆：0-30天）
"""
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pickle


class FaissStore:
    """
    Faiss 向量存储
    
    特性：
    - 毫秒级语义检索
    - 支持 IVF 索引（速度与精度平衡）
    - 自动 ID 映射管理
    - 持久化存储
    """
    
    def __init__(
        self, 
        dimension: int = 1536,
        index_path: Optional[str] = None,
        use_gpu: bool = False
    ):
        """
        Args:
            dimension: 向量维度（OpenAI ada-002: 1536）
            index_path: 索引文件路径
            use_gpu: 是否使用 GPU 加速
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else None
        self.use_gpu = use_gpu
        
        # ID 映射：faiss_id -> doc_id
        self.id_map: Dict[int, str] = {}
        self.reverse_id_map: Dict[str, int] = {}
        
        # 初始化索引
        self.index = self._create_index()
        
        # 如果索引文件存在，加载
        if self.index_path and self.index_path.exists():
            self.load()
    
    def _create_index(self) -> faiss.Index:
        """创建 Faiss 索引"""
        # IVF 索引：速度与精度平衡
        # nlist: 聚类中心数量，一般设为 sqrt(N)，这里先用100
        quantizer = faiss.IndexFlatL2(self.dimension)
        index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        
        if self.use_gpu and faiss.get_num_gpus() > 0:
            # GPU 加速（需要 faiss-gpu）
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)
        
        return index
    
    async def add(
        self, 
        embedding: List[float], 
        doc_id: str
    ) -> int:
        """
        添加单个向量
        
        Args:
            embedding: 向量（1536维）
            doc_id: 文档ID
        
        Returns:
            faiss_id: Faiss 内部索引ID
        """
        vector = np.array([embedding], dtype=np.float32)
        
        # 训练索引（首次添加时）
        if not self.index.is_trained:
            self.index.train(vector)
        
        # 获取当前总数作为新 ID
        faiss_id = self.index.ntotal
        
        # 添加向量
        self.index.add(vector)
        
        # 更新映射
        self.id_map[faiss_id] = doc_id
        self.reverse_id_map[doc_id] = faiss_id
        
        return faiss_id
    
    async def add_batch(
        self, 
        embeddings: List[List[float]], 
        doc_ids: List[str]
    ) -> List[int]:
        """
        批量添加向量（性能优化）
        
        Args:
            embeddings: 向量列表
            doc_ids: 文档ID列表
        
        Returns:
            faiss_ids: Faiss 内部索引ID列表
        """
        if len(embeddings) != len(doc_ids):
            raise ValueError("embeddings 和 doc_ids 长度不一致")
        
        vectors = np.array(embeddings, dtype=np.float32)
        
        # 训练索引
        if not self.index.is_trained:
            self.index.train(vectors)
        
        # 批量添加
        start_id = self.index.ntotal
        self.index.add(vectors)
        
        # 更新映射
        faiss_ids = []
        for i, doc_id in enumerate(doc_ids):
            faiss_id = start_id + i
            self.id_map[faiss_id] = doc_id
            self.reverse_id_map[doc_id] = faiss_id
            faiss_ids.append(faiss_id)
        
        return faiss_ids
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 10
    ) -> List[Dict]:
        """
        向量相似度检索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回前 K 个结果
        
        Returns:
            results: [{"doc_id": str, "score": float, "source": "faiss"}]
        """
        if self.index.ntotal == 0:
            return []
        
        query = np.array([query_embedding], dtype=np.float32)
        
        # 执行检索
        distances, indices = self.index.search(query, min(top_k, self.index.ntotal))
        
        # 转换结果
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1 and idx in self.id_map:
                # L2 距离转相似度分数（距离越小，分数越高）
                score = 1.0 / (1.0 + float(dist))
                results.append({
                    "doc_id": self.id_map[idx],
                    "score": score,
                    "distance": float(dist),
                    "source": "faiss"
                })
        
        return results
    
    async def remove(self, doc_id: str) -> bool:
        """
        删除向量
        
        注意: Faiss 不支持高效删除，只能通过 IDSelector 过滤
        这里采用标记删除策略，定期重建索引
        """
        if doc_id not in self.reverse_id_map:
            return False
        
        faiss_id = self.reverse_id_map[doc_id]
        
        # 从映射中删除
        del self.id_map[faiss_id]
        del self.reverse_id_map[doc_id]
        
        # TODO: 当删除量达到阈值时，重建索引
        return True
    
    async def remove_batch(self, doc_ids: List[str]) -> int:
        """批量删除"""
        count = 0
        for doc_id in doc_ids:
            if await self.remove(doc_id):
                count += 1
        return count
    
    def rebuild_index(self, embeddings: List[List[float]], doc_ids: List[str]):
        """
        重建索引（删除累积后使用）
        
        Args:
            embeddings: 有效向量列表
            doc_ids: 有效文档ID列表
        """
        # 清空旧索引
        self.index = self._create_index()
        self.id_map.clear()
        self.reverse_id_map.clear()
        
        # 批量添加
        vectors = np.array(embeddings, dtype=np.float32)
        if not self.index.is_trained:
            self.index.train(vectors)
        
        self.index.add(vectors)
        
        # 重建映射
        for i, doc_id in enumerate(doc_ids):
            self.id_map[i] = doc_id
            self.reverse_id_map[doc_id] = i
    
    def save(self):
        """保存索引到磁盘"""
        if not self.index_path:
            raise ValueError("未设置 index_path")
        
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存索引
        faiss.write_index(self.index, str(self.index_path))
        
        # 保存 ID 映射
        mapping_path = self.index_path.with_suffix(".mapping")
        with open(mapping_path, "wb") as f:
            pickle.dump({
                "id_map": self.id_map,
                "reverse_id_map": self.reverse_id_map
            }, f)
    
    def load(self):
        """从磁盘加载索引"""
        if not self.index_path or not self.index_path.exists():
            raise FileNotFoundError(f"索引文件不存在: {self.index_path}")
        
        # 加载索引
        self.index = faiss.read_index(str(self.index_path))
        
        # 加载 ID 映射
        mapping_path = self.index_path.with_suffix(".mapping")
        if mapping_path.exists():
            with open(mapping_path, "rb") as f:
                data = pickle.load(f)
                self.id_map = data["id_map"]
                self.reverse_id_map = data["reverse_id_map"]
    
    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "is_trained": self.index.is_trained,
            "active_docs": len(self.reverse_id_map),
            "deleted_docs": self.index.ntotal - len(self.reverse_id_map)
        }

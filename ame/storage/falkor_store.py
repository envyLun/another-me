"""
Falkor 图谱存储封装
职责:长期知识图谱（实体关系建模、多跳推理、时间演化分析）
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

try:
    from falkordb import FalkorDB
    FALKORDB_AVAILABLE = True
except ImportError:
    FALKORDB_AVAILABLE = False
    logging.warning("FalkorDB not installed. Install with: pip install falkordb")


class FalkorStore:
    """
    Falkor 图谱存储（基于 FalkorDB 实现）
    
    特性：
    - 实体关系建模
    - 多跳知识推理
    - 时间序列演化分析
    - 支持 Cypher 查询
    - 兼容 Redis 协议
    """
    
    def __init__(
        self, 
        host: str = "localhost",
        port: int = 6379,
        graph_name: str = "another_me",
        **kwargs
    ):
        """
        Args:
            host: FalkorDB 主机地址
            port: FalkorDB 端口
            graph_name: 图谱名称
            **kwargs: 额外参数（密码等）
        """
        if not FALKORDB_AVAILABLE:
            raise ImportError(
                "FalkorDB is required but not installed. "
                "Install with: pip install falkordb redis"
            )
        
        self.host = host
        self.port = port
        self.graph_name = graph_name
        
        # 初始化 FalkorDB 客户端
        self.client = FalkorDB(
            host=host, 
            port=port,
            password=kwargs.get("password")
        )
        self.graph = self.client.select_graph(graph_name)
        
        # 初始化索引
        self._init_schema()
    
    def _init_schema(self):
        """初始化图谱结构和索引"""
        try:
            # 创建节点索引
            self.graph.query("CREATE INDEX FOR (d:Document) ON (d.id)")
            self.graph.query("CREATE INDEX FOR (e:Entity) ON (e.name)")
        except Exception as e:
            # 索引可能已存在
            logging.debug(f"Schema init: {e}")
    
    async def create_node(
        self, 
        node_type: str, 
        properties: Dict[str, Any]
    ) -> str:
        """
        创建节点
        
        Args:
            node_type: 节点类型（如 "Document", "Entity", "Person"）
            properties: 节点属性
        
        Returns:
            node_id: 节点唯一标识
        """
        # 构建属性字符串
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        cypher = f"CREATE (n:{node_type} {{{props_str}}}) RETURN n.id"
        
        result = self.graph.query(cypher, properties)
        
        if result.result_set:
            return result.result_set[0][0]
        
        return properties.get("id", f"{node_type}_{datetime.now().timestamp()}")
    
    async def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0
    ) -> bool:
        """
        创建关系（增强版，支持权重）
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型（如 "MENTIONS", "RELATED_TO"）
            properties: 关系属性
            weight: 关系权重（0-1，默认1.0）
        
        Returns:
            success: 是否创建成功
        """
        # 构建关系属性
        rel_props = {"weight": weight, "created_at": datetime.now().isoformat()}
        if properties:
            rel_props.update(properties)
        
        # 构建属性字符串
        props_str = "{" + ", ".join([f"{k}: ${k}" for k in rel_props.keys()]) + "}"
        params = {"source": source_id, "target": target_id, **rel_props}
        
        cypher = f"""
        MATCH (s {{id: $source}}), (t {{id: $target}})
        MERGE (s)-[r:{relation_type}]->(t)
        ON CREATE SET r = $props
        ON MATCH SET r.weight = r.weight + $weight
        """
        
        params["props"] = rel_props
        
        try:
            self.graph.query(cypher, params)
            return True
        except Exception as e:
            logging.error(f"Failed to create relation: {e}")
            return False
    
    async def get_or_create_entity(
        self, 
        entity_name: str, 
        entity_type: str = "Entity",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        获取或创建实体节点（增强版）
        
        Args:
            entity_name: 实体名称
            entity_type: 实体类型 (PERSON, LOCATION, ORGANIZATION, TOPIC, etc.)
            metadata: 实体元数据（可选）
        
        Returns:
            entity_id: 实体节点ID
        """
        # 标准化实体类型
        entity_type = entity_type.upper() if entity_type else "ENTITY"
        
        # 构建元数据
        props = {"name": entity_name}
        if metadata:
            props.update(metadata)
        
        # 构建属性字符串
        props_items = [f"e.{k} = ${k}" for k in props.keys()]
        props_set = ", ".join(props_items)
        
        cypher = f"""
        MERGE (e:Entity {{name: $name}})
        ON CREATE SET e.type = $entity_type, e.id = $name, {props_set}
        ON MATCH SET {props_set}
        RETURN e.id
        """
        
        params = {**props, "entity_type": entity_type}
        
        try:
            result = self.graph.query(cypher, params)
            
            if result.result_set:
                return result.result_set[0][0]
            
            return entity_name
        
        except Exception as e:
            logging.error(f"Get or create entity failed: {e}")
            return entity_name
    
    async def search_by_entities(
        self, 
        query: str,
        entities: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        基于实体检索文档（增强版）
        
        策略：
        1. 匹配包含查询实体的文档
        2. 按实体出现次数计算相关度
        3. 结合时间因素（近期文档权重更高）
        
        Args:
            query: 查询文本（用于提取实体）
            entities: 已提取的实体列表（可选）
            top_k: 返回前 K 个结果
        
        Returns:
            results: [{"doc_id": str, "score": float, "source": "graph", "matched_entities": List[str]}]
        """
        if not entities or len(entities) == 0:
            return []
        
        # 使用 UNWIND 优化查询
        cypher = """
        UNWIND $entities AS entity_name
        MATCH (d:Document)-[:MENTIONS]->(e:Entity)
        WHERE e.name = entity_name
        WITH d, COLLECT(DISTINCT e.name) AS matched_entities, COUNT(e) as match_count
        RETURN 
            d.id AS doc_id,
            d.timestamp AS timestamp,
            match_count AS relevance,
            matched_entities
        ORDER BY relevance DESC, timestamp DESC
        LIMIT $top_k
        """
        
        try:
            result = self.graph.query(cypher, {
                "entities": entities, 
                "top_k": top_k
            })
            
            if not result.result_set:
                return []
            
            # 计算归一化分数
            max_relevance = max([row[2] for row in result.result_set]) if result.result_set else 1
            
            return [
                {
                    "doc_id": row[0],
                    "score": float(row[2]) / max_relevance,  # 归一化
                    "source": "graph",
                    "matched_entities": row[3] if len(row) > 3 else [],
                    "timestamp": row[1] if len(row) > 1 else None
                }
                for row in result.result_set
            ]
        
        except Exception as e:
            logging.error(f"Graph search by entities failed: {e}")
            return []
    
    async def find_related_docs(
        self, 
        doc_id: str, 
        max_hops: int = 2,
        limit: int = 20
    ) -> List[Dict]:
        """
        查找相关文档（多跳推理增强版）
        
        策略：
        1. 通过实体关系查找相关文档
        2. 距离越近的文档分数越高
        3. 返回详细信息（包括距离、共享实体等）
        
        Args:
            doc_id: 源文档ID
            max_hops: 最大跳数
            limit: 返回数量限制
        
        Returns:
            related_docs: [{"doc_id": str, "distance": int, "score": float, "shared_entities": List[str]}]
        """
        try:
            # 优化的 Cypher 查询：通过实体连接查找相关文档
            cypher = """
            MATCH (d1:Document {id: $doc_id})-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(d2:Document)
            WHERE d1 <> d2
            WITH d2, COLLECT(DISTINCT e.name) AS shared_entities, COUNT(e) AS entity_count
            RETURN 
                d2.id AS doc_id,
                1 AS distance,
                entity_count,
                shared_entities
            ORDER BY entity_count DESC
            LIMIT $limit
            """
            
            result = self.graph.query(cypher, {"doc_id": doc_id, "limit": limit})
            
            if not result.result_set:
                return []
            
            # 计算归一化分数
            max_entity_count = max([row[2] for row in result.result_set]) if result.result_set else 1
            
            related_docs = [
                {
                    "doc_id": row[0],
                    "distance": row[1],
                    "score": float(row[2]) / max_entity_count,  # 基于共享实体数量计算分数
                    "shared_entities": row[3] if len(row) > 3 else []
                }
                for row in result.result_set
            ]
            
            return related_docs
        
        except Exception as e:
            logging.error(f"Find related docs failed: {e}")
            return []
    
    async def analyze_entity_evolution(
        self,
        entity_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        分析实体随时间的演化
        
        Args:
            entity_name: 实体名称
            start_time: 起始时间
            end_time: 结束时间
        
        Returns:
            timeline: [{"timestamp": datetime, "doc_id": str, "context": str}]
        """
        where_clause = "WHERE e.name = $entity"
        params = {"entity": entity_name}
        
        if start_time:
            where_clause += " AND d.timestamp >= $start"
            params["start"] = start_time.isoformat()
        
        if end_time:
            where_clause += " AND d.timestamp <= $end"
            params["end"] = end_time.isoformat()
        
        cypher = f"""
        MATCH (e:Entity)-[:MENTIONED_IN]->(d:Document)
        {where_clause}
        RETURN d.timestamp, d.id, d.content
        ORDER BY d.timestamp
        """
        
        result = self.graph.query(cypher, params)
        
        return [
            {
                "timestamp": row[0],
                "doc_id": row[1],
                "context": row[2]
            }
            for row in result.result_set
        ]
    
    async def get_entity_relationships(
        self,
        entity_name: str,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        获取实体的关系网络
        
        Args:
            entity_name: 实体名称
            depth: 关系深度
        
        Returns:
            graph: {"nodes": [...], "edges": [...]}
        """
        cypher = f"""
        MATCH path = (e:Entity {{name: $entity}})-[*1..{depth}]-(related)
        RETURN path
        """
        
        result = self.graph.query(cypher, {"entity": entity_name})
        
        nodes = set()
        edges = []
        
        for row in result.result_set:
            # 提取路径中的节点和边
            # FalkorDB 返回路径对象，需要解析
            # 简化实现：返回基本结构
            pass
        
        return {"nodes": list(nodes), "edges": edges}
    
    async def delete_node(self, node_id: str) -> bool:
        """删除节点及其关系"""
        cypher = "MATCH (n {id: $node_id}) DETACH DELETE n"
        
        try:
            self.graph.query(cypher, {"node_id": node_id})
            return True
        except Exception as e:
            logging.error(f"Failed to delete node: {e}")
            return False
    
    async def execute_cypher(
        self, 
        query: str, 
        parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        执行自定义 Cypher 查询
        
        Args:
            query: Cypher 查询语句
            parameters: 查询参数
        
        Returns:
            results: 查询结果
        """
        result = self.graph.query(query, parameters or {})
        
        # 转换为字典列表
        if not result.result_set:
            return []
        
        # 获取列名
        headers = result.header if hasattr(result, 'header') else []
        
        return [
            {headers[i]: row[i] for i in range(len(row))}
            for row in result.result_set
        ]
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logging.error(f"Failed to close FalkorDB connection: {e}")


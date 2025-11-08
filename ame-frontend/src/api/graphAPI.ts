/**
 * 图谱 API
 * 提供知识图谱查询和分析功能
 */
import axios from 'axios';

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface EntityGraphRequest {
  entity_name: string;
  depth?: number;
}

export interface EntityGraphResponse {
  success: boolean;
  data: GraphData;
  message?: string;
}

export interface DocumentGraphRequest {
  doc_id: string;
  max_hops?: number;
}

export interface DocumentGraphResponse {
  success: boolean;
  data: GraphData;
  related_docs: Array<{
    doc_id: string;
    distance: number;
    score: number;
    shared_entities: string[];
  }>;
}

export interface GraphStatsResponse {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
  edge_types: Record<string, number>;
}

class GraphAPI {
  private axios = axios.create({
    baseURL: '/api/v1',
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
  /**
   * 获取实体关系图
   * @param entity_name 实体名称
   * @param depth 查询深度（默认 2）
   */
  async getEntityGraph(entity_name: string, depth: number = 2): Promise<EntityGraphResponse> {
    const response = await this.axios.get<EntityGraphResponse>('/graph/entity', {
      params: { entity_name, depth }
    });
    return response.data;
  }

  /**
   * 获取文档关联图
   * @param doc_id 文档 ID
   * @param max_hops 最大跳数（默认 2）
   */
  async getDocumentGraph(doc_id: string, max_hops: number = 2): Promise<DocumentGraphResponse> {
    const response = await this.axios.get<DocumentGraphResponse>('/graph/document', {
      params: { doc_id, max_hops }
    });
    return response.data;
  }

  /**
   * 获取全局知识图谱概览
   * @param limit 限制返回的节点数量（默认 100）
   */
  async getGraphOverview(limit: number = 100): Promise<EntityGraphResponse> {
    const response = await this.axios.get<EntityGraphResponse>('/graph/overview', {
      params: { limit }
    });
    return response.data;
  }

  /**
   * 获取图谱统计信息
   */
  async getGraphStats(): Promise<GraphStatsResponse> {
    const response = await this.axios.get<GraphStatsResponse>('/graph/stats');
    return response.data;
  }

  /**
   * 执行自定义 Cypher 查询
   * @param query Cypher 查询语句
   * @param parameters 查询参数
   */
  async executeCypher(query: string, parameters?: Record<string, any>): Promise<any> {
    const response = await this.axios.post('/graph/cypher', {
      query,
      parameters: parameters || {}
    });
    return response.data;
  }

  /**
   * 搜索实体
   * @param query 搜索关键词
   * @param entity_type 实体类型（可选）
   * @param limit 返回数量限制
   */
  async searchEntities(
    query: string,
    entity_type?: string,
    limit: number = 20
  ): Promise<{
    success: boolean;
    entities: GraphNode[];
  }> {
    const response = await this.axios.get('/graph/search', {
      params: { query, entity_type, limit }
    });
    return response.data;
  }
}

export const graphAPI = new GraphAPI();
export default graphAPI;

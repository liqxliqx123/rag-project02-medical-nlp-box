import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialStdService:
    """
    金融术语标准化服务
    基于向量相似度搜索提供金融术语的标准化建议
    """
    
    def __init__(self, provider="huggingface", model="BAAI/bge-m3", 
                 db_path="db/financial_bge_m3.db", collection_name="financial_concepts"):
        """
        初始化金融标准化服务
        
        Args:
            provider: 嵌入模型提供商
            model: 嵌入模型名称
            db_path: 向量数据库路径
            collection_name: 集合名称
        """
        self.provider = provider
        self.model_name = model
        self.db_path = db_path
        self.collection_name = collection_name
        self.encoder = None
        self.collection = None
        
        # 初始化服务
        self._initialize()
    
    def _initialize(self):
        """初始化嵌入模型和向量数据库"""
        try:
            # 加载嵌入模型
            logger.info(f"正在加载嵌入模型: {self.model_name}")
            self.encoder = SentenceTransformer(self.model_name)
            
            # 连接向量数据库
            logger.info(f"正在连接向量数据库: {self.db_path}")
            client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取集合
            self.collection = client.get_collection(self.collection_name)
            logger.info(f"成功连接到集合: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def search_similar_terms(self, query_term: str, n_results: int = 5, 
                           min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """
        搜索相似的金融术语
        
        Args:
            query_term: 查询术语
            n_results: 返回结果数量
            min_similarity: 最小相似度阈值
            
        Returns:
            相似术语列表
        """
        try:
            # 生成查询向量
            query_embedding = self.encoder.encode([query_term]).tolist()
            
            # 向量搜索
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 处理结果
            similar_terms = []
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # 转换为相似度
                
                if similarity >= min_similarity:
                    metadata = results['metadatas'][0][i]
                    similar_terms.append({
                        'conceptId': metadata['conceptId'],
                        'standardTerm': results['documents'][0][i],
                        'similarity': round(similarity, 4),
                        'domainId': metadata['domainId'],
                        'active': metadata['active'],
                        'effectiveTime': metadata['effectiveTime']
                    })
            
            # 按相似度排序
            similar_terms.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"为术语 '{query_term}' 找到 {len(similar_terms)} 个相似术语")
            return similar_terms
            
        except Exception as e:
            logger.error(f"术语搜索失败: {e}")
            return []
    
    def get_term_by_id(self, concept_id: str) -> Dict[str, Any]:
        """
        根据概念ID获取术语信息
        
        Args:
            concept_id: 概念ID
            
        Returns:
            术语信息字典
        """
        try:
            results = self.collection.get(
                ids=[concept_id],
                include=['documents', 'metadatas']
            )
            
            if results['documents']:
                metadata = results['metadatas'][0]
                return {
                    'conceptId': concept_id,
                    'standardTerm': results['documents'][0],
                    'domainId': metadata['domainId'],
                    'active': metadata['active'],
                    'effectiveTime': metadata['effectiveTime']
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"获取术语失败: {e}")
            return {}
    
    def batch_standardize(self, terms: List[str], n_results: int = 3,
                         min_similarity: float = 0.3) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量标准化术语
        
        Args:
            terms: 术语列表
            n_results: 每个术语返回的结果数量
            min_similarity: 最小相似度阈值
            
        Returns:
            标准化结果字典
        """
        results = {}
        for term in terms:
            results[term] = self.search_similar_terms(term, n_results, min_similarity)
        return results
    
    def get_financial_categories(self) -> List[str]:
        """
        获取金融术语类别
        
        Returns:
            类别列表
        """
        return [
            'CURRENCY',           # 货币
            'FINANCIAL_RATIO',    # 财务比率
            'FINANCIAL_INSTRUMENT', # 金融工具
            'FINANCIAL_INSTITUTION', # 金融机构
            'FINANCIAL_INDICATOR',  # 金融指标
            'ACCOUNTING_TERM',     # 会计术语
            'INVESTMENT_TERM',     # 投资术语
            'BANKING_TERM',        # 银行术语
            'INSURANCE_TERM',      # 保险术语
            'TAX_TERM'            # 税务术语
        ]
    
    def search_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        按类别搜索术语
        
        Args:
            category: 术语类别
            limit: 结果数量限制
            
        Returns:
            术语列表
        """
        try:
            # 这里可以根据实际需要实现分类搜索
            # 由于我们的数据结构相对简单，这里返回所有术语的示例
            results = self.collection.get(
                limit=limit,
                include=['documents', 'metadatas']
            )
            
            terms = []
            for i in range(len(results['documents'])):
                metadata = results['metadatas'][i]
                terms.append({
                    'conceptId': metadata['conceptId'],
                    'standardTerm': results['documents'][i],
                    'domainId': metadata['domainId'],
                    'active': metadata['active'],
                    'effectiveTime': metadata['effectiveTime']
                })
            
            return terms
            
        except Exception as e:
            logger.error(f"按类别搜索失败: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 获取集合中的项目数量
            count_result = self.collection.count()
            
            return {
                'total_terms': count_result,
                'collection_name': self.collection_name,
                'model_name': self.model_name,
                'provider': self.provider
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {} 
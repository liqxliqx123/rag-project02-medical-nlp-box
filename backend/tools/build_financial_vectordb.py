#!/usr/bin/env python3
"""
金融术语向量数据库构建工具
基于金融术语数据构建Chroma向量数据库
"""

import os
import sys
import pandas as pd
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialVectorDBBuilder:
    """金融术语向量数据库构建器"""
    
    def __init__(self, model_name="BAAI/bge-m3"):
        """
        初始化构建器
        
        Args:
            model_name: 嵌入模型名称
        """
        self.model_name = model_name
        self.model = None
        self.client = None
        
    def load_model(self):
        """加载嵌入模型"""
        try:
            logger.info(f"正在加载嵌入模型: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def initialize_db(self, db_path):
        """初始化Chroma数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 初始化Chroma客户端
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"数据库初始化成功: {db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def load_financial_data(self, data_path):
        """加载金融术语数据"""
        try:
            logger.info(f"正在加载金融术语数据: {data_path}")
            df = pd.read_csv(data_path)
            logger.info(f"成功加载 {len(df)} 条金融术语")
            return df
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise
    
    def create_collection(self, collection_name, data_df):
        """创建向量集合"""
        try:
            # 删除已存在的集合
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"删除已存在的集合: {collection_name}")
            except:
                pass
            
            # 创建新集合
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "金融术语向量集合"}
            )
            
            # 准备数据
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in data_df.iterrows():
                concept_id = str(row['conceptId'])
                fsn = row['fsn']
                domain_id = row['domainId']
                
                documents.append(fsn)
                metadatas.append({
                    'conceptId': concept_id,
                    'domainId': domain_id,
                    'active': str(row['active']),
                    'effectiveTime': str(row['effectiveTime']),
                })
                ids.append(concept_id)
            
            # 生成向量
            logger.info("正在生成向量嵌入...")
            embeddings = self.model.encode(documents, convert_to_tensor=False).tolist()
            
            # 批量添加到集合
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                
                collection.add(
                    embeddings=embeddings[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                
                logger.info(f"已处理 {end_idx}/{len(documents)} 条记录")
            
            logger.info(f"集合 {collection_name} 创建成功，共 {len(documents)} 条记录")
            return collection
            
        except Exception as e:
            logger.error(f"集合创建失败: {e}")
            raise
    
    def build_database(self, data_path, db_path, collection_name):
        """构建完整的向量数据库"""
        try:
            # 加载模型
            self.load_model()
            
            # 初始化数据库
            self.initialize_db(db_path)
            
            # 加载数据
            data_df = self.load_financial_data(data_path)
            
            # 创建集合
            collection = self.create_collection(collection_name, data_df)
            
            logger.info("金融术语向量数据库构建完成！")
            return collection
            
        except Exception as e:
            logger.error(f"数据库构建失败: {e}")
            raise

def main():
    """主函数"""
    # 配置路径
    data_path = "backend/data/financial_terms_full.csv"
    db_path = "backend/db/financial_bge_m3.db"
    collection_name = "financial_concepts"
    
    # 构建数据库
    builder = FinancialVectorDBBuilder()
    builder.build_database(data_path, db_path, collection_name)

if __name__ == "__main__":
    main() 
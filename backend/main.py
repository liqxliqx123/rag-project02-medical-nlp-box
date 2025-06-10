from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from services.ner_service import NERService
from services.financial_ner_service import FinancialNERService
from services.std_service import StdService
from services.financial_std_service import FinancialStdService
from services.abbr_service import AbbrService
from services.corr_service import CorrService
from services.gen_service import GenService
from typing import List, Dict, Optional, Literal, Union, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI()

# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化各个服务
ner_service = NERService()  # 医疗命名实体识别服务
financial_ner_service = FinancialNERService()  # 金融命名实体识别服务
standardization_service = StdService()  # 医疗术语标准化服务
abbr_service = AbbrService()  # 缩写扩展服务
gen_service = GenService()  # 文本生成服务
corr_service = CorrService()  # 拼写纠正服务

# 基础模型类
class BaseInputModel(BaseModel):
    """基础输入模型，包含所有模型共享的字段"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llmOptions: Dict[str, str] = Field(
        default_factory=lambda: {
            "provider": "ollama",
            "model": "qwen2.5:7b"
        },
        description="大语言模型配置选项"
    )

class EmbeddingOptions(BaseModel):
    """向量数据库配置选项"""
    provider: Literal["huggingface", "openai", "bedrock"] = Field(
        default="huggingface",
        description="向量数据库提供商"
    )
    model: str = Field(
        default="BAAI/bge-m3",
        description="嵌入模型名称"
    )
    dbName: str = Field(
        default="snomed_bge_m3",
        description="向量数据库名称"
    )
    collectionName: str = Field(
        default="concepts_only_name",
        description="集合名称"
    )

class TextInput(BaseInputModel):
    """文本输入模型，用于标准化和命名实体识别"""
    text: str = Field(..., description="输入文本")
    options: Dict[str, bool] = Field(
        default_factory=dict,
        description="处理选项"
    )
    termTypes: Dict[str, bool] = Field(
        default_factory=dict,
        description="术语类型"
    )
    embeddingOptions: EmbeddingOptions = Field(
        default_factory=EmbeddingOptions,
        description="向量数据库配置选项"
    )
    
class FinancialEmbeddingOptions(BaseModel):
    """金融向量数据库配置选项"""
    provider: Literal["huggingface", "openai", "bedrock"] = Field(
        default="huggingface",
        description="向量数据库提供商"
    )
    model: str = Field(
        default="BAAI/bge-m3",
        description="嵌入模型名称"
    )
    dbName: str = Field(
        default="financial_bge_m3",
        description="向量数据库名称"
    )
    collectionName: str = Field(
        default="financial_concepts",
        description="集合名称"
    )

class AbbrInput(BaseInputModel):
    """缩写扩展输入模型"""
    text: str = Field(..., description="输入文本")
    context: str = Field(
        default="",
        description="上下文信息"
    )
    method: Literal["simple_ollama", "query_db_llm_rerank", "llm_rank_query_db"] = Field(
        default="simple_ollama",
        description="处理方法"
    )
    embeddingOptions: Optional[EmbeddingOptions] = Field(
        default_factory=EmbeddingOptions,
        description="向量数据库配置选项"
    )

class ErrorOptions(BaseModel):
    """错误生成选项"""
    probability: float = Field(
        default=0.3,
        description="错误生成概率",
        ge=0.0,
        le=1.0
    )
    maxErrors: int = Field(
        default=5,
        description="最大错误数量",
        ge=1
    )
    keyboard: Literal["qwerty", "azerty"] = Field(
        default="qwerty",
        description="键盘布局"
    )

class CorrInput(BaseInputModel):
    """拼写纠正输入模型"""
    text: str = Field(..., description="输入文本")
    method: Literal["correct_spelling", "add_mistakes"] = Field(
        default="correct_spelling",
        description="处理方法"
    )
    errorOptions: ErrorOptions = Field(
        default_factory=ErrorOptions,
        description="错误生成选项"
    )

class PatientInfo(BaseModel):
    """患者信息模型"""
    name: str = Field(..., description="患者姓名")
    age: Optional[int] = Field(
        None,
        description="患者年龄",
        ge=0
    )
    gender: Optional[Literal["M", "F", "O"]] = Field(
        None,
        description="患者性别"
    )
    medicalHistory: Optional[str] = Field(
        None,
        description="既往病史"
    )

class GenInput(BaseInputModel):
    """医疗内容生成输入模型"""
    patient_info: PatientInfo = Field(..., description="患者信息")
    symptoms: List[str] = Field(..., description="症状列表")
    diagnosis: str = Field(
        default="",
        description="诊断结果"
    )
    treatment: str = Field(
        default="",
        description="治疗方案"
    )
    method: Literal["generate_medical_note", "generate_differential_diagnosis", "generate_treatment_plan"] = Field(
        default="generate_medical_note",
        description="生成方法"
    )

# API 端点：术语标准化
@app.post("/api/std")
async def standardization(input: TextInput):
    try:
        # 记录请求信息
        logger.info(f"Received request: domain={input.domain}, text={input.text}, options={input.options}")

        # 根据领域选择相应的服务
        if input.domain == "financial":
            # 金融领域处理
            all_financial_terms = input.options.pop('allFinancialTerms', False)
            term_types = {'allFinancialTerms': all_financial_terms}
            
            # 添加具体的金融术语类型
            for term_type in ['currency', 'ratio', 'instrument', 'institution', 'indicator', 'accounting']:
                if input.options.get(term_type, False):
                    term_types[term_type] = True

            # 进行金融实体识别
            ner_results = financial_ner_service.process(input.text, input.options, term_types)

            # 初始化金融标准化服务
            financial_std_service = FinancialStdService(
                provider=input.embeddingOptions.provider,
                model=input.embeddingOptions.model,
                db_path=f"db/{input.embeddingOptions.dbName}.db",
                collection_name=input.embeddingOptions.collectionName
            )

            # 获取识别到的实体
            entities = ner_results.get('entities', [])
            if not entities:
                return {"message": "No financial terms have been recognized", "standardized_terms": []}

            # 标准化每个实体
            standardized_results = []
            for entity in entities:
                std_result = financial_std_service.search_similar_terms(entity['word'])
                standardized_results.append({
                    "original_term": entity['word'],
                    "entity_group": entity['entity_group'],
                    "standardized_results": std_result
                })

        else:
            # 医疗领域处理（原有逻辑）
            all_medical_terms = input.options.pop('allMedicalTerms', False)
            term_types = {'allMedicalTerms': all_medical_terms}

            # 进行命名实体识别
            ner_results = ner_service.process(input.text, input.options, term_types)

            # 初始化标准化服务
            standardization_service = StdService(
                provider=input.embeddingOptions.provider,
                model=input.embeddingOptions.model,
                db_path=f"db/{input.embeddingOptions.dbName}.db",
                collection_name=input.embeddingOptions.collectionName
            )

            # 获取识别到的实体
            entities = ner_results.get('entities', [])
            if not entities:
                return {"message": "No medical terms have been recognized", "standardized_terms": []}

            # 标准化每个实体
            standardized_results = []
            for entity in entities:
                std_result = standardization_service.search_similar_terms(entity['word'])
                standardized_results.append({
                    "original_term": entity['word'],
                    "entity_group": entity['entity_group'],
                    "standardized_results": std_result
                })

        return {
            "message": f"{len(entities)} medical terms have been recognized and standardized",
            "standardized_terms": standardized_results
        }

    except Exception as e:
        logger.error(f"Error in standardization processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API 端点：命名实体识别
@app.post("/api/ner")
async def ner(input: TextInput):
    try:
        logger.info(f"Received NER request: domain={input.domain}, text={input.text}, options={input.options}")
        
        # 根据领域选择相应的NER服务
        if input.domain == "financial":
            # 金融领域NER
            all_financial_terms = input.options.pop('allFinancialTerms', False)
            term_types = {'allFinancialTerms': all_financial_terms}
            
            # 添加具体的金融术语类型
            for term_type in ['currency', 'ratio', 'instrument', 'institution', 'indicator', 'accounting']:
                if input.options.get(term_type, False):
                    term_types[term_type] = True
            
            results = financial_ner_service.process(input.text, input.options, term_types)
        else:
            # 医疗领域NER（原有逻辑）
            all_medical_terms = input.options.pop('allMedicalTerms', False)
            term_types = {'allMedicalTerms': all_medical_terms}
            results = ner_service.process(input.text, input.options, term_types)
        
        return results
    except Exception as e:
        logger.error(f"Error in NER processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API 端点：拼写纠正
@app.post("/api/corr")
async def correct_notes(input: CorrInput):
    try:
        if input.method == "correct_spelling":  # 拼写纠正
            return corr_service.correct_spelling(input.text, input.llmOptions)
        elif input.method == "add_mistakes":  # 添加错误（测试用）
            return corr_service.add_mistakes(input.text, input.errorOptions)
        else:
            raise HTTPException(status_code=400, detail="Invalid method")
    except Exception as e:
        logger.error(f"Error in correction processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API 端点：缩写扩展
@app.post("/api/abbr")
async def expand_abbreviations(input: AbbrInput):
    try:
        if input.method == "simple_ollama":  # 简单扩展
            output = abbr_service.simple_ollama_expansion(input.text, input.llmOptions)
            return {"input": input.text, "output": output}
        elif input.method == "query_db_llm_rerank":  # 数据库查询+重排序
            return abbr_service.query_db_llm_rerank(
                input.text, 
                input.context, 
                input.llmOptions,
                input.embeddingOptions
            )
        elif input.method == "llm_rank_query_db":  # LLM扩展+数据库标准化
            return abbr_service.llm_rank_query_db(
                input.text, 
                input.context, 
                input.llmOptions,
                input.embeddingOptions
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid method")
    except Exception as e:
        logger.error(f"Error in abbreviation expansion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API 端点：医疗文本生成
@app.post("/api/gen")
async def generate_medical_content(input: GenInput):
    try:
        if input.method == "generate_medical_note":  # 生成病历
            return gen_service.generate_medical_note(
                input.patient_info,
                input.symptoms,
                input.diagnosis,
                input.treatment,
                input.llmOptions
            )
        elif input.method == "generate_differential_diagnosis":  # 生成鉴别诊断
            return gen_service.generate_differential_diagnosis(
                input.symptoms,
                input.llmOptions
            )
        elif input.method == "generate_treatment_plan":  # 生成治疗计划
            return gen_service.generate_treatment_plan(
                input.diagnosis,
                input.patient_info,
                input.llmOptions
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid method")
    except Exception as e:
        logger.error(f"Error in medical content generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

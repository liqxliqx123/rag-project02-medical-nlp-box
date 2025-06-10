from transformers import pipeline
import torch
import logging
import re
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialNERService:
    """
    金融术语命名实体识别服务
    使用基于规则的方法和预训练模型进行金融文本的实体识别
    """
    def __init__(self):
        # 初始化通用 NER 模型
        try:
            self.pipe = pipeline("token-classification", 
                               model="dbmdz/bert-large-cased-finetuned-conll03-english", 
                               aggregation_strategy='simple',
                               device=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            logger.warning(f"无法加载预训练模型: {e}，将使用基于规则的方法")
            self.pipe = None
        
        # 金融术语模式
        self.financial_patterns = {
            'CURRENCY': [
                r'\b(?:USD|EUR|GBP|JPY|CNY|CAD|AUD|CHF|SEK|NOK|DKK)\b',
                r'\$\d+(?:\.\d{2})?',
                r'€\d+(?:\.\d{2})?',
                r'£\d+(?:\.\d{2})?',
                r'¥\d+(?:\.\d{2})?',
                r'\b\d+(?:\.\d{2})?\s*(?:美元|欧元|英镑|日元|人民币)\b'
            ],
            'FINANCIAL_RATIO': [
                r'\b(?:P/E|ROE|ROA|ROI|EBITDA|EPS|DPS|BPS)\b',
                r'\b(?:市盈率|净资产收益率|资产收益率|投资回报率|每股收益)\b',
                r'\b\d+(?:\.\d+)?%\s*(?:的|收益率|回报率|增长率)\b'
            ],
            'FINANCIAL_INSTRUMENT': [
                r'\b(?:股票|债券|期货|期权|基金|ETF|REITs|衍生品)\b',
                r'\b(?:stock|bond|futures|options|fund|derivative)\b',
                r'\b(?:A股|H股|红筹股|蓝筹股|创业板|科创板)\b'
            ],
            'FINANCIAL_INSTITUTION': [
                r'\b(?:银行|证券公司|保险公司|基金公司|信托公司|投资银行)\b',
                r'\b(?:bank|securities|insurance|fund|trust|investment)\s+(?:company|corp|corporation)\b',
                r'\b(?:央行|人民银行|证监会|银保监会|交易所)\b'
            ],
            'FINANCIAL_INDICATOR': [
                r'\b(?:GDP|CPI|PPI|PMI|失业率|通胀率|利率|汇率)\b',
                r'\b(?:gross domestic product|consumer price index|producer price index)\b',
                r'\b(?:上证指数|深证成指|恒生指数|道琼斯|纳斯达克|标普500)\b'
            ],
            'ACCOUNTING_TERM': [
                r'\b(?:资产|负债|权益|收入|费用|利润|现金流)\b',
                r'\b(?:asset|liability|equity|revenue|expense|profit|cash flow)\b',
                r'\b(?:应收账款|应付账款|存货|固定资产|无形资产)\b'
            ]
        }
        
        # 编译正则表达式
        self.compiled_patterns = {}
        for category, patterns in self.financial_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    def process(self, text: str, options: Dict[str, bool], term_types: Dict[str, bool]) -> Dict[str, Any]:
        """
        处理输入文本，识别金融术语实体
        
        Args:
            text: 输入文本
            options: 处理选项
            term_types: 需要识别的术语类型
            
        Returns:
            包含识别出的实体和原始文本的字典
        """
        entities = []
        
        # 使用基于规则的方法识别金融实体
        rule_based_entities = self._extract_financial_entities(text)
        entities.extend(rule_based_entities)
        
        # 如果有预训练模型，也使用它
        if self.pipe:
            try:
                model_entities = self._extract_model_entities(text)
                entities.extend(model_entities)
            except Exception as e:
                logger.warning(f"模型识别失败: {e}")
        
        # 移除重叠实体
        non_overlapping_result = self._remove_overlapping_entities(entities)
        
        # 根据术语类型过滤实体
        filtered_result = self._filter_entities(non_overlapping_result, term_types)
        
        return {
            "text": text,
            "entities": filtered_result
        }

    def _extract_financial_entities(self, text: str) -> List[Dict[str, Any]]:
        """使用正则表达式提取金融实体"""
        entities = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    entities.append({
                        'entity_group': category,
                        'word': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'score': 0.9  # 规则匹配的置信度
                    })
        
        return entities

    def _extract_model_entities(self, text: str) -> List[Dict[str, Any]]:
        """使用预训练模型提取实体"""
        try:
            result = self.pipe(text)
            if isinstance(result, dict):
                result = result.get('entities', [])
            
            # 转换模型输出为标准格式
            model_entities = []
            for entity in result:
                # 只保留可能与金融相关的实体
                if entity.get('entity_group') in ['ORG', 'MISC', 'PER']:
                    entity['score'] = float(entity['score'])
                    model_entities.append(entity)
            
            return model_entities
        except Exception as e:
            logger.error(f"模型实体提取失败: {e}")
            return []

    def _remove_overlapping_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """移除重叠的实体，保留得分最高的实体"""
        if not entities:
            return []
        
        # 按开始位置、结束位置（降序）和得分（降序）排序
        sorted_entities = sorted(entities, key=lambda x: (x['start'], -x['end'], -x['score']))
        non_overlapping = []
        last_end = -1

        i = 0
        while i < len(sorted_entities):
            current = sorted_entities[i]
            
            # 如果当前实体与之前的实体不重叠，直接添加
            if current['start'] >= last_end:
                non_overlapping.append(current)
                last_end = current['end']
                i += 1
            else:
                # 处理重叠实体
                same_span = [current]
                j = i + 1
                while (j < len(sorted_entities) and 
                       sorted_entities[j]['start'] == current['start'] and 
                       sorted_entities[j]['end'] == current['end']):
                    same_span.append(sorted_entities[j])
                    j += 1
                
                # 选择得分最高的实体
                best_entity = max(same_span, key=lambda x: x['score'])
                if best_entity['end'] > last_end:
                    non_overlapping.append(best_entity)
                    last_end = best_entity['end']
                
                i = j

        return non_overlapping

    def _filter_entities(self, entities: List[Dict[str, Any]], term_types: Dict[str, bool]) -> List[Dict[str, Any]]:
        """根据术语类型过滤实体"""
        if term_types.get('allFinancialTerms', False):
            return entities
        
        filtered_result = []
        for entity in entities:
            entity_group = entity['entity_group']
            
            if ((term_types.get('currency', False) and entity_group == 'CURRENCY') or
                (term_types.get('ratio', False) and entity_group == 'FINANCIAL_RATIO') or
                (term_types.get('instrument', False) and entity_group == 'FINANCIAL_INSTRUMENT') or
                (term_types.get('institution', False) and entity_group == 'FINANCIAL_INSTITUTION') or
                (term_types.get('indicator', False) and entity_group == 'FINANCIAL_INDICATOR') or
                (term_types.get('accounting', False) and entity_group == 'ACCOUNTING_TERM') or
                (term_types.get('organization', False) and entity_group in ['ORG', 'MISC', 'PER'])):
                filtered_result.append(entity)
        
        return filtered_result 
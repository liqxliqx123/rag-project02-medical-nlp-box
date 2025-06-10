#!/usr/bin/env python3
"""
金融专有名词标准化系统测试脚本
演示系统的主要功能
"""

import requests
import json
import time
from typing import Dict, Any

class FinancialSystemTester:
    """金融系统测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_cases = [
            {
                "name": "金融报告分析",
                "text": "苹果公司第三季度营收为 890 亿美元，同比增长 8%。净利润率达到 23.5%，ROE 为 15.2%。公司计划在 Q4 发行 10 亿美元的债券，用于扩张业务。分析师认为 P/E 比率 28.5 略显偏高。",
                "expected_entities": ["美元", "净利润率", "ROE", "债券", "P/E"]
            },
            {
                "name": "投资分析报告",
                "text": "该公司的 EBITDA 为 50 亿元，资产负债率为 45%。建议关注其现金流状况和市盈率变化。当前股价对应的 PB 值为 2.3 倍。",
                "expected_entities": ["EBITDA", "资产负债率", "现金流", "市盈率", "PB"]
            },
            {
                "name": "宏观经济分析",
                "text": "央行公布最新 CPI 数据为 2.1%，GDP 增长率达到 6.8%。上证指数收于 3450 点，恒生指数上涨 1.2%。",
                "expected_entities": ["央行", "CPI", "GDP", "上证指数", "恒生指数"]
            }
        ]
    
    def test_ner_api(self, text: str) -> Dict[str, Any]:
        """测试实体识别API"""
        url = f"{self.base_url}/api/ner"
        payload = {
            "text": text,
            "domain": "financial",
            "options": {},
            "termTypes": {
                "allFinancialTerms": True
            },
            "embeddingOptions": {
                "provider": "huggingface",
                "model": "BAAI/bge-m3",
                "dbName": "financial_bge_m3",
                "collectionName": "financial_concepts"
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_std_api(self, text: str) -> Dict[str, Any]:
        """测试标准化API"""
        url = f"{self.base_url}/api/std"
        payload = {
            "text": text,
            "domain": "financial",
            "options": {
                "allFinancialTerms": True
            },
            "embeddingOptions": {
                "provider": "huggingface",
                "model": "BAAI/bge-m3",
                "dbName": "financial_bge_m3",
                "collectionName": "financial_concepts"
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def run_ner_tests(self):
        """运行实体识别测试"""
        print("🔍 开始测试金融实体识别功能")
        print("=" * 60)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 测试案例 {i}: {test_case['name']}")
            print(f"输入文本: {test_case['text']}")
            
            # 调用API
            start_time = time.time()
            result = self.test_ner_api(test_case['text'])
            end_time = time.time()
            
            if "error" in result:
                print(f"❌ 错误: {result['error']}")
                continue
            
            # 显示结果
            entities = result.get('entities', [])
            print(f"⏱️  处理时间: {end_time - start_time:.2f}秒")
            print(f"🎯 识别到 {len(entities)} 个实体:")
            
            for entity in entities:
                print(f"  • {entity['word']} → {entity['entity_group']} (置信度: {entity.get('score', 'N/A')})")
            
            # 检查预期实体
            found_expected = 0
            for expected in test_case['expected_entities']:
                if any(expected.lower() in entity['word'].lower() for entity in entities):
                    found_expected += 1
            
            coverage = found_expected / len(test_case['expected_entities']) * 100
            print(f"📊 预期实体覆盖率: {coverage:.1f}% ({found_expected}/{len(test_case['expected_entities'])})")
    
    def run_std_tests(self):
        """运行标准化测试"""
        print("\n\n📚 开始测试金融术语标准化功能")
        print("=" * 60)
        
        test_terms = [
            "ROE 净资产收益率 P/E",
            "EBITDA 市盈率 资产负债率",
            "GDP CPI 上证指数"
        ]
        
        for i, terms in enumerate(test_terms, 1):
            print(f"\n📝 标准化测试 {i}")
            print(f"输入术语: {terms}")
            
            # 调用API
            start_time = time.time()
            result = self.test_std_api(terms)
            end_time = time.time()
            
            if "error" in result:
                print(f"❌ 错误: {result['error']}")
                continue
            
            # 显示结果
            standardized_terms = result.get('standardized_terms', [])
            print(f"⏱️  处理时间: {end_time - start_time:.2f}秒")
            print(f"🎯 标准化结果:")
            
            for term_result in standardized_terms:
                original = term_result.get('original_term', '')
                suggestions = term_result.get('standardized_results', [])
                print(f"\n  🔹 原术语: {original}")
                
                if suggestions:
                    for j, suggestion in enumerate(suggestions[:3], 1):
                        similarity = suggestion.get('similarity', 0)
                        standard_term = suggestion.get('standardTerm', '')
                        print(f"    {j}. {standard_term} (相似度: {similarity:.3f})")
                else:
                    print("    ❌ 未找到标准化建议")
    
    def run_performance_test(self):
        """运行性能测试"""
        print("\n\n⚡ 开始性能测试")
        print("=" * 60)
        
        test_text = "分析该公司的ROE、P/E比率、EBITDA和现金流指标，评估其投资价值。"
        iterations = 5
        
        print(f"📝 测试文本: {test_text}")
        print(f"🔄 重复次数: {iterations}")
        
        # NER性能测试
        ner_times = []
        for i in range(iterations):
            start_time = time.time()
            result = self.test_ner_api(test_text)
            end_time = time.time()
            
            if "error" not in result:
                ner_times.append(end_time - start_time)
        
        if ner_times:
            avg_ner_time = sum(ner_times) / len(ner_times)
            print(f"🔍 NER平均响应时间: {avg_ner_time:.3f}秒")
        
        # 标准化性能测试
        std_times = []
        for i in range(iterations):
            start_time = time.time()
            result = self.test_std_api(test_text)
            end_time = time.time()
            
            if "error" not in result:
                std_times.append(end_time - start_time)
        
        if std_times:
            avg_std_time = sum(std_times) / len(std_times)
            print(f"📚 标准化平均响应时间: {avg_std_time:.3f}秒")
    
    def check_system_status(self):
        """检查系统状态"""
        print("🔧 检查系统状态")
        print("=" * 60)
        
        try:
            # 检查后端服务
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务运行正常")
            else:
                print("❌ 后端服务异常")
                return False
        except Exception as e:
            print(f"❌ 无法连接后端服务: {e}")
            return False
        
        # 测试基本API
        test_result = self.test_ner_api("测试")
        if "error" not in test_result:
            print("✅ API接口工作正常")
        else:
            print(f"❌ API接口异常: {test_result['error']}")
            return False
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 金融专有名词标准化系统测试")
        print("=" * 60)
        print("基于医疗系统架构扩展的金融领域专业术语处理平台")
        print("包含15,885条金融术语，支持实体识别和标准化功能")
        print("=" * 60)
        
        # 检查系统状态
        if not self.check_system_status():
            print("\n❌ 系统状态检查失败，请确保后端服务正在运行")
            return
        
        # 运行功能测试
        self.run_ner_tests()
        self.run_std_tests()
        self.run_performance_test()
        
        print("\n\n✅ 测试完成！")
        print("💡 提示: 访问 http://localhost:3000 使用Web界面")
        print("📚 查看 '金融专有名词标准化系统.md' 了解更多详情")

def main():
    """主函数"""
    tester = FinancialSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
import React, { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { TextInput } from '../components/shared/ModelOptions';
import { getDomainFromUrl, getDomainConfig } from '../utils/domainUtils';

const color_map = {
  'DATE': "#FF9800", // 原色
  'AGE': "#E91E63", // 原色
  'SIGN_SYMPTOM': "#FF0000", // 鲜红
  'TIME': "#673AB7", // 原色
  'HEIGHT': "#3F51B5", // 原色
  'CLINICAL_EVENT': "#2196F3", // 原色
  'SHAPE': "#03A9F4", // 原色
  'FREQUENCY': "#00BCD4", // 原色
  'BIOLOGICAL_STRUCTURE': "#009688", // 原色
  'AREA': "#4CAF50", // 原色
  'WEIGHT': "#8BC34A", // 原色
  'TEXTURE': "#CDDC39", // 原色
  'COREFERENCE': "#FFEB3B", // 原色
  'MEDICATION': "#FFC107", // 原色
  'MASS': "#FF9800", // 原色
  'SEVERITY': "#FF5722", // 原色
  'BIOLOGICAL_ATTRIBUTE': "#795548", // 原色
  'DISEASE_DISORDER': "#00FF00", // 鲜绿
  'DURATION': "#607D8B", // 原色
  'VOLUME': "#D32F2F", // 调整后，深红
  'THERAPEUTIC_PROCEDURE': "#C2185B", // 原色
  'ADMINISTRATION': "#7B1FA2", // 原色
  'ACTIVITY': "#512DA8", // 原色
  'SUBJECT': "#303F9F", // 原色
  'FAMILY_HISTORY': "#1976D2", // 原色
  'HISTORY': "#0288D1", // 原色
  'QUANTITATIVE_CONCEPT': "#0097A7", // 原色
  'LAB_VALUE': "#00796B", // 原色
  'DETAILED_DESCRIPTION': "#388E3C", // 原色
  'DIAGNOSTIC_PROCEDURE': "#689F38", // 原色
  'NONBIOLOGICAL_LOCATION': "#AFB42B", // 原色
  'OUTCOME': "#FBC02D", // 原色
  'SEX': "#FFA000", // 原色
  'COLOR': "#F57C00", // 原色
  'QUALITATIVE_CONCEPT': "#E64A19", // 原色
  'DISTANCE': "#5D4037", // 原色
  'PERSONAL_BACKGROUND': "#616161", // 原色
  'OTHER_ENTITY': "#455A64", // 原色
  'OTHER_EVENT': "#C62828", // 原色
  'DOSAGE': "#AD1457", // 原色
  'OCCUPATION': "#880E4F", // 原色
  'COMBINED_BIO_SYMPTOM': "#FF4500",  // 为合并实体添加一个新颜色
};

const NERPage = () => {
  const [domain, setDomain] = useState(getDomainFromUrl());
  const [domainConfig, setDomainConfig] = useState(getDomainConfig(domain));
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [coloredResult, setColoredResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [termTypes, setTermTypes] = useState(domainConfig.termTypes);
  const [options, setOptions] = useState({
    combineBioStructure: false,
  });

  useEffect(() => {
    const currentDomain = getDomainFromUrl();
    setDomain(currentDomain);
    const config = getDomainConfig(currentDomain);
    setDomainConfig(config);
    setTermTypes(config.termTypes);
  }, []);

  const handleTermTypeChange = (e) => {
    const { name, checked } = e.target;
    const allTermsKey = domain === 'financial' ? 'allFinancialTerms' : 'allMedicalTerms';
    
    if (name === allTermsKey) {
      const newTermTypes = { ...domainConfig.termTypes };
      Object.keys(newTermTypes).forEach(key => {
        newTermTypes[key] = key === allTermsKey ? checked : false;
      });
      setTermTypes(newTermTypes);
    } else {
      setTermTypes({ ...termTypes, [name]: checked });
    }
  };

  const handleOptionChange = (e) => {
    setOptions({ ...options, [e.target.name]: e.target.checked });
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://172.20.116.213:8000/api/ner', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: input, 
          options, 
          termTypes,
          domain,
          embeddingOptions: domainConfig.embeddingOptions
        }),
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
      setColoredResult(generateColoredResult(data.text, data.entities));
    } catch (error) {
      console.error('Error:', error);
      setResult('An error occurred while processing the request.');
      setColoredResult('');
    }
    setIsLoading(false);
  };

  const generateColoredResult = (text, entities) => {
    let result = text;
    entities.sort((a, b) => b.start - a.start);
    
    for (const entity of entities) {
      const color = domainConfig.colorMap[entity.entity_group] || '#666666';
      let highlightedEntity;
      
      if (entity.entity_group === 'COMBINED_BIO_SYMPTOM' && entity.original_entities) {
        const [bioStructure, symptom] = entity.original_entities;
        highlightedEntity = `<span style="background-color: ${color}; padding: 2px; border-radius: 3px; color: white;">
          <span style="border-bottom: 2px solid ${domainConfig.colorMap[bioStructure.entity_group]};">${bioStructure.word}</span> 
          <span style="border-bottom: 2px solid ${domainConfig.colorMap[symptom.entity_group]};">${symptom.word}</span>
          <sub>${bioStructure.entity_group}+${symptom.entity_group}</sub>
        </span>`;
      } else {
        highlightedEntity = `<span style="background-color: ${color}; padding: 2px; border-radius: 3px; color: white;">
          ${entity.word}<sub>${entity.entity_group}</sub>
        </span>`;
      }
      
      result = result.slice(0, entity.start) + highlightedEntity + result.slice(entity.end);
    }
    
    return result;
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{domainConfig.title} {domainConfig.icon}</h1>
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">输入文本</h2>
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          rows={4}
          placeholder={domainConfig.placeholder}
        />
        
        <h3 className="text-lg font-semibold mb-2">术语类型</h3>
        <div className="mb-4">
          {Object.entries(domainConfig.termTypeLabels).map(([key, label]) => (
            <label key={key} className="mr-4 mb-2 inline-block">
              <input
                type="checkbox"
                name={key}
                checked={termTypes[key] || false}
                onChange={handleTermTypeChange}
                className="mr-1"
              />
              {label}
            </label>
          ))}
        </div>

        {domain === 'medical' && (
          <>
            <h3 className="text-lg font-semibold mb-2">选项</h3>
            <div className="mb-4">
              <label>
                <input
                  type="checkbox"
                  name="combineBioStructure"
                  checked={options.combineBioStructure}
                  onChange={handleOptionChange}
                  className="mr-1"
                />
                合并生物结构和症状
              </label>
            </div>
          </>
        )}
        
        {/* 示例文本 */}
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <h4 className="font-medium mb-2">示例文本：</h4>
          <div className="text-sm text-gray-600">
            {domain === 'financial' ? (
              <p>
                "苹果公司第三季度营收为 890 亿美元，同比增长 8%。净利润率达到 23.5%，ROE 为 15.2%。
                公司计划在 Q4 发行 10 亿美元的债券，用于扩张业务。分析师认为 P/E 比率 28.5 略显偏高。"
              </p>
            ) : (
              <p>
                "患者主诉头痛伴恶心呕吐3天，既往有高血压病史。体格检查：血压150/90mmHg，心率88次/分。
                建议进行头颅CT检查，排除颅内病变。"
              </p>
            )}
          </div>
          <button
            onClick={() => setInput(domain === 'financial' 
              ? "苹果公司第三季度营收为 890 亿美元，同比增长 8%。净利润率达到 23.5%，ROE 为 15.2%。公司计划在 Q4 发行 10 亿美元的债券，用于扩张业务。分析师认为 P/E 比率 28.5 略显偏高。"
              : "患者主诉头痛伴恶心呕吐3天，既往有高血压病史。体格检查：血压150/90mmHg，心率88次/分。建议进行头颅CT检查，排除颅内病变。"
            )}
            className="mt-2 text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
          >
            使用示例
          </button>
        </div>

        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className={`bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isLoading ? '处理中...' : '识别实体'}
        </button>
      </div>
      {coloredResult && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">识别结果</h2>
          <div 
            dangerouslySetInnerHTML={{ __html: coloredResult }} 
            style={{
              lineHeight: '2',
              wordBreak: 'break-word'
            }}
          />
        </div>
      )}
      {result && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
          <p className="font-bold">JSON 结果：</p>
          <pre>{result}</pre>
        </div>
      )}
      <div className="flex items-center text-yellow-700 bg-yellow-100 p-4 rounded-md">
        <AlertCircle className="mr-2" />
        <span>这是演示版本, 并非所有功能都可以正常工作。更多功能需要您来增强并实现。</span>
      </div>
    </div>
  );
};

export default NERPage;
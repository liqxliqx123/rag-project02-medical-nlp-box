import React, { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { EmbeddingOptions, TextInput } from '../components/shared/ModelOptions';
import { getDomainFromUrl, getDomainConfig } from '../utils/domainUtils';

const StdPage = () => {
  const [domain, setDomain] = useState(getDomainFromUrl());
  const [domainConfig, setDomainConfig] = useState(getDomainConfig(domain));
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 根据领域设置初始选项
  const getInitialOptions = (currentDomain) => {
    if (currentDomain === 'financial') {
      return {
        currency: true,
        ratio: true,
        instrument: true,
        institution: true,
        indicator: true,
        accounting: true,
        allFinancialTerms: true,
      };
    } else {
      return {
        disease: true,
        combineBioStructure: true,
        medicine: true,
        laboratory: true,
        physicalExamination: true,
        surgeryProcedure: true,
        radiology: true,
        commonMedicalObservations: true,
        lifestyleObservations: true,
        cognitiveBehaviorItems: true,
        allMedicalTerms: true,
      };
    }
  };

  const [options, setOptions] = useState(getInitialOptions(domain));
  const [embeddingOptions, setEmbeddingOptions] = useState(domainConfig.embeddingOptions);

  useEffect(() => {
    const currentDomain = getDomainFromUrl();
    setDomain(currentDomain);
    const config = getDomainConfig(currentDomain);
    setDomainConfig(config);
    setOptions(getInitialOptions(currentDomain));
    setEmbeddingOptions(config.embeddingOptions);
  }, []);

  const handleOptionChange = (e) => {
    const { name, checked } = e.target;
    const allTermsKey = domain === 'financial' ? 'allFinancialTerms' : 'allMedicalTerms';
    
    if (name === allTermsKey) {
      // 如果选择全部术语，则设置所有选项为相同状态
      setOptions(prevOptions => {
        const newOptions = {};
        Object.keys(prevOptions).forEach(key => {
          newOptions[key] = checked;
        });
        return newOptions;
      });
    } else {
      // 更新单个选项
      setOptions(prevOptions => ({
        ...prevOptions,
        [name]: checked,
        // 如果取消选择任何一个选项，全部术语也取消选择
        [allTermsKey]: checked && 
          Object.entries(prevOptions)
            .filter(([key]) => key !== allTermsKey && key !== name)
            .every(([, value]) => value)
      }));
    }
  };

  const handleEmbeddingOptionChange = (e) => {
    const { name, value } = e.target;
    setEmbeddingOptions(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError('');
    setResult('');
    try {
      const response = await fetch('http://172.20.116.213:8000/api/std', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: input, 
          options,
          embeddingOptions,
          domain
        }),
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error:', error);
      setError(`An error occurred: ${error.message}`);
    }
    setIsLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{domain === 'financial' ? '金融术语标准化 💰' : '医疗术语标准化 📚'}</h1>
      <div className="grid grid-cols-3 gap-6">
        {/* 左侧面板：文本输入和嵌入选项 */}
        <div className="col-span-2 bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">输入{domain === 'financial' ? '金融' : '医疗'}术语</h2>
          <TextInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={4}
            placeholder={domain === 'financial' ? '请输入需要标准化的金融术语...' : '请输入需要标准化的医疗术语...'}
          />
          
          {/* 示例文本 */}
          <div className="mb-4 p-3 bg-gray-50 rounded">
            <h4 className="font-medium mb-2">示例文本：</h4>
            <div className="text-sm text-gray-600">
              {domain === 'financial' ? (
                <p>"请分析该公司的 ROE、P/E 比率和 EBITDA 指标。该股票的市盈率为 28.5，净资产收益率达 15.2%。"</p>
              ) : (
                <p>"患者诊断为高血压、糖尿病，需要进行血常规、肝功能检查。"</p>
              )}
            </div>
            <button
              onClick={() => setInput(domain === 'financial' 
                ? "请分析该公司的 ROE、P/E 比率和 EBITDA 指标。该股票的市盈率为 28.5，净资产收益率达 15.2%。"
                : "患者诊断为高血压、糖尿病，需要进行血常规、肝功能检查。"
              )}
              className="mt-2 text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
            >
              使用示例
            </button>
          </div>
          
          <EmbeddingOptions options={embeddingOptions} onChange={handleEmbeddingOptionChange} />

          <button
            onClick={handleSubmit}
            className="bg-purple-500 text-white px-4 py-2 rounded-md hover:bg-purple-600 w-full"
            disabled={isLoading}
          >
            {isLoading ? '处理中...' : '标准化术语'}
          </button>
        </div>

        {/* 右侧面板：选项列表 */}
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">术语类型</h2>
          <div className="space-y-3">
            {domain === 'financial' ? (
              <>
                {[
                  ['currency', '货币'],
                  ['ratio', '财务比率'],
                  ['instrument', '金融工具'],
                  ['institution', '金融机构'],
                  ['indicator', '金融指标'],
                  ['accounting', '会计术语'],
                ].map(([key, label]) => (
                  <div key={key} className="flex items-center">
                    <input
                      type="checkbox"
                      id={key}
                      name={key}
                      checked={options[key]}
                      onChange={handleOptionChange}
                      className="mr-2"
                    />
                    <label htmlFor={key}>{label}</label>
                  </div>
                ))}
                
                <div className="flex items-center pt-4 border-t">
                  <input
                    type="checkbox"
                    id="allFinancialTerms"
                    name="allFinancialTerms"
                    checked={options.allFinancialTerms}
                    onChange={handleOptionChange}
                    className="mr-2"
                  />
                  <label htmlFor="allFinancialTerms" className="font-semibold">所有金融术语</label>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="disease"
                    name="disease"
                    checked={options.disease}
                    onChange={handleOptionChange}
                    className="mr-2"
                  />
                  <label htmlFor="disease">疾病</label>
                  {options.disease && (
                    <div className="ml-6">
                      <input
                        type="checkbox"
                        id="combineBioStructure"
                        name="combineBioStructure"
                        checked={options.combineBioStructure}
                        onChange={handleOptionChange}
                        className="mr-2"
                      />
                      <label htmlFor="combineBioStructure">合并生物结构</label>
                    </div>
                  )}
                </div>
                
                {[
                  ['medicine', '药物'],
                  ['laboratory', '实验室检查'],
                  ['physicalExamination', '体格检查'],
                  ['surgeryProcedure', '手术/操作'],
                  ['radiology', '放射检查'],
                  ['commonMedicalObservations', '常见医学观察'],
                  ['lifestyleObservations', '生活方式观察'],
                  ['cognitiveBehaviorItems', '认知行为项目'],
                ].map(([key, label]) => (
                  <div key={key} className="flex items-center">
                    <input
                      type="checkbox"
                      id={key}
                      name={key}
                      checked={options[key]}
                      onChange={handleOptionChange}
                      className="mr-2"
                    />
                    <label htmlFor={key}>{label}</label>
                  </div>
                ))}
                
                <div className="flex items-center pt-4 border-t">
                  <input
                    type="checkbox"
                    id="allMedicalTerms"
                    name="allMedicalTerms"
                    checked={options.allMedicalTerms}
                    onChange={handleOptionChange}
                    className="mr-2"
                  />
                  <label htmlFor="allMedicalTerms" className="font-semibold">所有医疗术语</label>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* 结果显示区域 */}
      {(error || result) && (
        <div className="mt-6">
          {error && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
              <p className="font-bold">错误：</p>
              <p>{error}</p>
            </div>
          )}
          {result && (
            <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6" role="alert">
              <p className="font-bold">结果：</p>
              <pre>{result}</pre>
            </div>
          )}
        </div>
      )}

      <div className="flex items-center text-yellow-700 bg-yellow-100 p-4 rounded-md mt-6">
        <AlertCircle className="mr-2" />
        <span>这是演示版本, 并非所有功能都可以正常工作。更多功能需要您来增强并实现。</span>
      </div>
    </div>
  );
};

export default StdPage;
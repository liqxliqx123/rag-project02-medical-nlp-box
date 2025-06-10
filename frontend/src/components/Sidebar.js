import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Stethoscope, 
  FileCheck, 
  BookOpen, 
  FileEdit, 
  FileText,
  TrendingUp,
  DollarSign,
  BarChart3,
  Building2
} from 'lucide-react';

const Sidebar = ({ width }) => {
  const [selectedDomain, setSelectedDomain] = useState('medical');

  return (
    <div className="bg-white shadow-lg" style={{ width: `${width}px` }}>
      <div className="p-5">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
          <span className="text-white text-2xl font-bold">AI</span>
        </div>
        <h1 className="text-xl font-bold mb-2">专有名词标准化系统</h1>
        <p className="text-sm text-gray-600 mb-4">智能术语处理工具集</p>
        
        {/* 领域切换 */}
        <div className="mb-4">
          <div className="flex rounded-lg bg-gray-100 p-1">
            <button
              className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-colors ${
                selectedDomain === 'medical' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              onClick={() => setSelectedDomain('medical')}
            >
              医疗
            </button>
            <button
              className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-colors ${
                selectedDomain === 'financial' 
                  ? 'bg-green-500 text-white' 
                  : 'text-gray-600 hover:text-gray-800'
              }`}
              onClick={() => setSelectedDomain('financial')}
            >
              金融
            </button>
          </div>
        </div>
      </div>
      
      <nav className="mt-2">
        {selectedDomain === 'medical' ? (
          <>
            <Link to="/ner?domain=medical" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600">
              <Stethoscope className="mr-3" /> 医疗实体识别
            </Link>
            <Link to="/stand?domain=medical" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600">
              <FileCheck className="mr-3" /> 医疗术语标准化
            </Link>
            <Link to="/abbr?domain=medical" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600">
              <BookOpen className="mr-3" /> 医疗缩写展开
            </Link>
            <Link to="/corr?domain=medical" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600">
              <FileEdit className="mr-3" /> 医疗记录纠错
            </Link>        
            <Link to="/gen?domain=medical" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600">
              <FileText className="mr-3" /> 医疗内容生成
            </Link>
          </>
        ) : (
          <>
            <Link to="/ner?domain=financial" className="flex items-center p-3 text-gray-700 hover:bg-green-50 hover:text-green-600">
              <TrendingUp className="mr-3" /> 金融实体识别
            </Link>
            <Link to="/stand?domain=financial" className="flex items-center p-3 text-gray-700 hover:bg-green-50 hover:text-green-600">
              <DollarSign className="mr-3" /> 金融术语标准化
            </Link>
            <Link to="/abbr?domain=financial" className="flex items-center p-3 text-gray-700 hover:bg-green-50 hover:text-green-600">
              <BarChart3 className="mr-3" /> 金融缩写展开
            </Link>
            <Link to="/corr?domain=financial" className="flex items-center p-3 text-gray-700 hover:bg-green-50 hover:text-green-600">
              <Building2 className="mr-3" /> 金融文本纠错
            </Link>
          </>
        )}
      </nav>
      
      {/* 统计信息 */}
      <div className="mt-auto p-4 border-t">
        <div className="text-xs text-gray-500">
          {selectedDomain === 'medical' ? (
            <div>
              <div className="font-medium mb-1">医疗术语库</div>
              <div>• SNOMED CT标准</div>
              <div>• 多语言支持</div>
            </div>
          ) : (
            <div>
              <div className="font-medium mb-1">金融术语库</div>
              <div>• 15,885条术语</div>
              <div>• 智能向量匹配</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
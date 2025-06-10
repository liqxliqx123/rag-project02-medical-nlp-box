import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import NERPage from './pages/NERPage';
import StdPage from './pages/StdPage';
import CorrPage from './pages/CorrPage';
import AbbrPage from './pages/AbbrPage';
import GenPage from './pages/GenPage';

const WelcomePage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        {/* 医疗领域 */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <img src="/images/medical-img.png" alt="医疗记录处理" className="w-32 h-auto mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-blue-600 mb-2">医疗领域</h2>
          <p className="text-gray-600 mb-4">专业的医疗术语处理和标准化工具</p>
          <div className="text-sm text-gray-500">
            • 医疗实体识别<br/>
            • 术语标准化<br/>
            • 缩写扩展<br/>
            • 记录纠错
          </div>
        </div>
        
        {/* 金融领域 */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="w-32 h-32 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
            <span className="text-4xl">💰</span>
          </div>
          <h2 className="text-2xl font-bold text-green-600 mb-2">金融领域</h2>
          <p className="text-gray-600 mb-4">全面的金融术语识别和标准化系统</p>
          <div className="text-sm text-gray-500">
            • 金融实体识别<br/>
            • 术语标准化<br/>
            • 15885条金融术语<br/>
            • 智能匹配推荐
          </div>
        </div>
      </div>
      <h1 className="text-3xl font-bold text-gray-800 mb-4 mt-8">专有名词标准化系统</h1>
      <p className="text-xl text-gray-600">请从左侧菜单选择要使用的功能</p>
    </div>
  );
};

const App = () => {
  const [sidebarWidth, setSidebarWidth] = useState(250);

  const handleResize = (e) => {
    setSidebarWidth(e.clientX);
  };

  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar width={sidebarWidth} />
        <div
          className="w-1 cursor-col-resize bg-gray-300 hover:bg-blue-500"
          onMouseDown={() => {
            document.addEventListener('mousemove', handleResize);
            document.addEventListener('mouseup', () => {
              document.removeEventListener('mousemove', handleResize);
            });
          }}
        />
        <main className="flex-1 overflow-y-auto p-5">
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/ner" element={<NERPage />} />
            <Route path="/stand" element={<StdPage />} />
            <Route path="/corr" element={<CorrPage />} />
            <Route path="/abbr" element={<AbbrPage />} />
            <Route path="/gen" element={<GenPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
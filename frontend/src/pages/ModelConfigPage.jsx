import React, { useState } from "react";

export default function ModelConfigPage() {
  const [config, setConfig] = useState({
    baseUrl: "http://localhost:8000",
    provider: "FastAPI",
    modelName: "gpt-4",
  });

  const handleSave = () => {
    alert("模型配置已保存！\n" + JSON.stringify(config, null, 2));
    // 可以保存到 localStorage 或 Electron 配置
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded shadow mt-6">
      <h2 className="text-xl font-bold mb-4">模型配置</h2>

      <div className="mb-4">
        <label className="block mb-1 font-semibold">Base URL</label>
        <input
          type="text"
          className="w-full border p-2 rounded"
          value={config.baseUrl}
          onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
        />
      </div>

      <div className="mb-4">
        <label className="block mb-1 font-semibold">模型供应商</label>
        <select
          className="w-full border p-2 rounded"
          value={config.provider}
          onChange={(e) => setConfig({ ...config, provider: e.target.value })}
        >
          <option>FastAPI</option>
          <option>OpenAI</option>
          <option>本地模型</option>
        </select>
      </div>

      <div className="mb-4">
        <label className="block mb-1 font-semibold">模型名称</label>
        <input
          type="text"
          className="w-full border p-2 rounded"
          value={config.modelName}
          onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
        />
      </div>

      <button
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-400"
        onClick={handleSave}
      >
        保存配置
      </button>
    </div>
  );
}

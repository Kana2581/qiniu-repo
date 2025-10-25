import React, { useState } from "react";

export default function ChatConfigPage() {
  const [config, setConfig] = useState({
    width: 800,
    height: 600,
    systemPrompt: "你是一个有帮助的智能助手。",
  });

  const handleSave = () => {
    localStorage.setItem("chatConfig", JSON.stringify(config));
    alert("聊天配置已保存！");
  };

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded shadow mt-6">
      <h2 className="text-xl font-bold mb-4">聊天配置</h2>

      {/* 聊天窗口大小 */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block mb-1 font-semibold">窗口宽度 (px)</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            value={config.width}
            onChange={(e) =>
              setConfig({ ...config, width: parseInt(e.target.value) })
            }
          />
        </div>
        <div>
          <label className="block mb-1 font-semibold">窗口高度 (px)</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            value={config.height}
            onChange={(e) =>
              setConfig({ ...config, height: parseInt(e.target.value) })
            }
          />
        </div>
      </div>

      {/* 系统提示词 */}
      <div className="mb-6">
        <label className="block mb-1 font-semibold">系统提示词</label>
        <textarea
          rows={4}
          className="w-full border p-2 rounded resize-none"
          value={config.systemPrompt}
          onChange={(e) =>
            setConfig({ ...config, systemPrompt: e.target.value })
          }
        />
        <p className="text-sm text-gray-500 mt-1">
          这个提示词会在每次对话开始时作为系统角色信息发送给模型。
        </p>
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

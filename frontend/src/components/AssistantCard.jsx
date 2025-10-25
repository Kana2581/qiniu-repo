// src/components/AssistantCard.jsx
import React from "react";

export default function AssistantCard({ assistant, onEdit, onDelete }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-5 flex flex-col hover:shadow-lg transition">
      {/* 头像与名称 */}
      <div className="flex items-center mb-4">
        <div className="text-4xl bg-gray-100 rounded-full w-14 h-14 flex items-center justify-center mr-3">
          {assistant.avatar || "🤖"}
        </div>
        <div>
          <h3 className="text-lg font-semibold">{assistant.name}</h3>
          <p className="text-sm text-gray-500">{assistant.provider}</p>
        </div>
      </div>

      {/* 基本信息 */}
      <div className="flex-1 space-y-1 text-sm text-gray-700">
        <p>
          <span className="font-medium">模型：</span>
          {assistant.model_name || "-"}
        </p>
        <p>
          <span className="font-medium">语音：</span>
          {assistant.voice_name || "未设置"}
        </p>
        <p>
          <span className="font-medium">系统：</span>
          {assistant.system_type || "未设置"}
        </p>
        <p>
          <span className="font-medium">路径：</span>
          {assistant.base_file_path || "未设置"}
        </p>
      </div>

      {/* 操作按钮 */}
      <div className="flex justify-end space-x-3 mt-4">
        <button
          onClick={() => onEdit(assistant.id)}
          className="px-3 py-1 text-sm text-blue-600 border border-blue-500 rounded hover:bg-blue-50"
        >
          编辑
        </button>
        <button
          onClick={() => onDelete(assistant.id)}
          className="px-3 py-1 text-sm text-red-600 border border-red-500 rounded hover:bg-red-50"
        >
          删除
        </button>
      </div>
    </div>
  );
}

import React from "react";

export default function SettingsPanel({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded-lg w-96">
        <h2 className="text-xl font-bold mb-4">设置</h2>

        {/* 示例设置 */}
        <div className="mb-4">
          <label className="block mb-1">主题</label>
          <select className="w-full border p-2 rounded">
            <option>浅色</option>
            <option>深色</option>
          </select>
        </div>

        <div className="mb-4">
          <button
            className="px-4 py-2 bg-red-400 text-white rounded"
            onClick={onClose}
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}

import React from "react";

export default function SettingsPage() {
  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded shadow mt-6">
      <h2 className="text-xl font-bold mb-4">设置</h2>
      <div className="mb-4">
        <label className="block mb-1">主题</label>
        <select className="w-full border p-2 rounded">
          <option>浅色</option>
          <option>深色</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block mb-1">快捷键配置</label>
        <input
          type="text"
          placeholder="Ctrl + Enter 发送"
          className="w-full border p-2 rounded"
        />
      </div>
    </div>
  );
}

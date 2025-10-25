// src/components/SessionSidebar.jsx
import React, { useEffect, useState } from "react";
import { apiFetch } from "../utils/api.js";
import { v4 as uuidv4 } from "uuid";
export default function SessionSidebar({ selectedId, onSelect }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [assistants, setAssistants] = useState([]);
  const [selectedAssistant, setSelectedAssistant] = useState(null);

  // 获取所有 session
  const fetchSessions = async () => {
    try {
      const res = await apiFetch("/session/");
      if (!res.ok) throw new Error("Failed to fetch sessions");
      const data = await res.json();
      setSessions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  // 获取所有 assistants
  const fetchAssistants = async () => {
    try {
      const res = await apiFetch("/assistants/");
      if (!res.ok) throw new Error("Failed to fetch assistants");
      const data = await res.json();
      setAssistants(data);
    } catch (err) {
      console.error(err);
    }
  };

  // 弹窗打开
  const openModal = () => {
    fetchAssistants();
    setShowModal(true);
  };

  // 创建 session
  const createSession = async () => {
    console.log("Selected Assistant:", selectedAssistant);
    if (!selectedAssistant) return;
    const newId = uuidv4(); // ✅ 前端生成 UUID
    try {
      const res = await apiFetch(`/session/${newId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assistant_id: selectedAssistant.id }),
      });
      if (!res.ok) throw new Error("Failed to create session");
      setShowModal(false);
      setSelectedAssistant(null);
      await fetchSessions();
      onSelect(newId);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
      {/* 顶部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <span className="font-semibold text-lg">Sessions</span>
        <button
          onClick={openModal}
          className="text-sm text-white bg-blue-500 hover:bg-blue-600 px-2 py-1 rounded"
        >
          新建
        </button>
      </div>

      {/* session 列表 */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-gray-500">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-gray-400">No sessions</div>
        ) : (
          sessions.map((s) => (
            <div
              key={s.session_id}
              onClick={() => onSelect(s.session_id)}
              className={`p-3 cursor-pointer ${
                s.session_id === selectedId
                  ? "bg-blue-100 text-blue-700"
                  : "hover:bg-gray-100"
              }`}
            >
              {s.session_id}
            </div>
          ))
        )}
      </div>

      {/* 新建 session 弹窗 */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg p-6 w-80">
            <h2 className="text-lg font-semibold mb-4">选择 Assistant</h2>
            <select
              className="w-full p-2 border rounded"
              value={selectedAssistant?.id || ""}
                onChange={(e) => {
                const assistant = assistants.find((a) => String(a.id) === e.target.value);
                setSelectedAssistant(assistant || null);
                }}
            >
              <option value="">请选择</option>
              {assistants.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>

            <div className="flex justify-end mt-4 space-x-2">
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedAssistant(null);
                }}
                className="px-3 py-1 border rounded"
              >
                取消
              </button>
              <button
                onClick={createSession}
                className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
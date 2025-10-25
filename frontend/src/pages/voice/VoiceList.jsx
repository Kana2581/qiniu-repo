import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../utils/api.js";

export default function AssistantList() {
  const [assistants, setAssistants] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAssistants();
  }, []);

  const fetchAssistants = async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/assistants");
      const data = await res.json();
      setAssistants(data);
    } catch (err) {
      console.error("加载助手列表失败：", err);
      alert("加载失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("确定要删除这个助手吗？")) return;
    try {
      await apiFetch(`/assistants/${id}`, { method: "DELETE" });
      setAssistants((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error("删除失败：", err);
      alert("删除失败，请重试");
    }
  };

  if (loading) return <div className="p-6 text-center">正在加载...</div>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* 顶部标题与按钮 */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">助手列表</h2>
        <button
          onClick={() => navigate("/system/assistants/new")}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          ＋ 新增助手
        </button>
      </div>

      {/* 卡片网格布局 */}
      {assistants.length === 0 ? (
        <div className="text-gray-500 text-center py-10">暂无助手配置</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {assistants.map((a) => (
            <div
              key={a.id}
              className="bg-white shadow-md rounded-xl p-5 flex flex-col hover:shadow-lg transition"
            >
              {/* 头像与名称 */}
              <div className="flex items-center mb-4">
                <div className="text-4xl bg-gray-100 rounded-full w-14 h-14 flex items-center justify-center mr-3">
                  {a.avatar || "🤖"}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{a.name}</h3>
                  <p className="text-sm text-gray-500">{a.provider}</p>
                </div>
              </div>

              {/* 基本信息 */}
              <div className="flex-1 space-y-1 text-sm text-gray-700">
                <p>
                  <span className="font-medium">模型：</span>
                  {a.model_name || "-"}
                </p>
                <p>
                  <span className="font-medium">语音：</span>
                  {a.voice_type || "未设置"}
                </p>
                <p>
                  <span className="font-medium">窗口：</span>
                  {a.window_size}
                </p>
              </div>

              {/* 操作按钮 */}
              <div className="flex justify-end space-x-3 mt-4">
                <button
                  onClick={() => navigate(`/system/assistants/${a.id}/edit`)}
                  className="px-3 py-1 text-sm text-blue-600 border border-blue-500 rounded hover:bg-blue-50"
                >
                  编辑
                </button>
                <button
                  onClick={() => handleDelete(a.id)}
                  className="px-3 py-1 text-sm text-red-600 border border-red-500 rounded hover:bg-red-50"
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

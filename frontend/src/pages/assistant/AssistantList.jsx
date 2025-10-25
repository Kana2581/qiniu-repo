import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../utils/api.js";
import AssistantCard from "../../components/AssistantCard.jsx";

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
            <AssistantCard
              key={a.id}
              assistant={a}
              onEdit={(id) => navigate(`/system/assistants/${id}/edit`)}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiFetch } from "../../utils/api.js";
export default function VoiceDetail() {
  const { id } = useParams();
  const [config, setConfig] = useState(null);

  useEffect(() => {
    apiFetch(`/config/voice/${id}`)
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch((err) => console.error("加载语音配置失败:", err));
  }, [id]);

  if (!config) return <div className="p-6">加载中...</div>;

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">语音配置详情</h2>
      <div className="bg-white shadow rounded-lg p-4 space-y-2">
        <p><strong>ID：</strong>{config.id}</p>
        <p><strong>模型ID：</strong>{config.model_id}</p>
        <p><strong>语音类型：</strong>{config.voice_type}</p>
        <p><strong>语速：</strong>{config.speech_speed}</p>
      </div>
      <div className="mt-4">
        <Link to={`/system/voice/edit/${config.id}`} className="text-blue-500 hover:underline">
          编辑
        </Link>
      </div>
    </div>
  );
}

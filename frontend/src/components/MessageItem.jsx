// ...existing code...
import React, { useEffect, useState, useRef } from "react";
import { apiFetch } from "../utils/api.js";
import { Play, Pause } from 'lucide-react'; // 添加这一行
async function fetchAudioUrl(ttsKey) {
  const res = await apiFetch(`/oss?key=${encodeURIComponent(ttsKey)}`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`请求音频失败: ${res.status}`);
  const data = await res.json();
  return data.url; // 假设返回 { url: "https://oss.xxx.com/file.mp3" }
}

export default function MessageItem({ message }) {
  const isUser = message.type === "human";
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    // 清理：组件卸载时停止并释放音频
    return () => {
      if (audioRef.current) {
        try {
          audioRef.current.pause();
        } catch (e) {}
        audioRef.current = null;
      }
    };
  }, []);

  const handleTogglePlay = async () => {
    if (playing && audioRef.current) {
      // 暂停
      audioRef.current.pause();
      setPlaying(false);
      return;
    }

    // 如果已有实例但未播放，直接播放
    if (audioRef.current && audioUrl) {
      try {
        await audioRef.current.play();
        setPlaying(true);
      } catch (err) {
        console.error("播放失败:", err);
        setError("播放失败");
      }
      return;
    }

    // 尚未获取真实 URL，点击时才请求并播放
    if (!message.tts_key) return;
    setLoading(true);
    setError(null);
    try {
      const url = await fetchAudioUrl(message.tts_key);
      setAudioUrl(url);
      // 使用 Audio 对象即时播放，避免依赖 DOM 更新
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => setPlaying(false);
      audio.onpause = () => setPlaying(false);
      await audio.play();
      setPlaying(true);
    } catch (err) {
      console.error("获取/播放音频失败:", err);
      setError("获取或播放音频失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`my-2 flex ${isUser ? "justify-end" : "justify-start"}`}>
    <div
      className={`p-3 rounded-lg break-words ${
        isUser
          ? "bg-blue-500 text-white w-1/2"
          : "bg-gray-200 text-black w-[70%]"
      }`}
    >
        <p>{message.content}</p>

        {!isUser && message.tts_key && (
        <div className="mt-2 flex items-center">
          <button
            onClick={handleTogglePlay}
            className={`px-4 py-2 rounded transition duration-300 ease-in-out ${
              loading ? "bg-gray-400" : playing ? "bg-red-500 hover:bg-red-600" : "bg-green-500 hover:bg-green-600"
            } text-white font-semibold shadow-md flex items-center`}
            disabled={loading}
          >
            {loading ? (
              "加载中..."
            ) : playing ? (
              <>
                <Pause className="mr-2" /> 暂停
              </>
            ) : (
              <>
                <Play className="mr-2" /> 播放
              </>
            )}
          </button>
          {error && <div className="text-red-500 text-sm mt-1 ml-2">{error}</div>}
        </div>
        )}
      </div>
    </div>
  );
}
// ...existing code...
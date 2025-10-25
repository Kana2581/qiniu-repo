import React, { useEffect, useState, useRef } from "react";
import { apiFetch } from "../utils/api.js";
import { Play, Pause, Volume2 } from "lucide-react";

async function fetchAudioUrl(ttsKey) {
  const res = await apiFetch(`/oss?key=${encodeURIComponent(ttsKey)}`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`请求音频失败: ${res.status}`);
  const data = await res.json();
  return data.url;
}

export default function MessageItem({ message }) {
  const isUser = message.type === "human";
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        try {
          audioRef.current.pause();
        } catch {}
        audioRef.current = null;
      }
    };
  }, []);

  const handleTogglePlay = async () => {
    if (playing && audioRef.current) {
      audioRef.current.pause();
      setPlaying(false);
      return;
    }

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

    if (!message.tts_key) return;
    setLoading(true);
    setError(null);
    try {
      const url = await fetchAudioUrl(message.tts_key);
      setAudioUrl(url);
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
    <div
      className={`my-5 flex ${isUser ? "justify-end" : "justify-start"} transition-all`}
    >
      <div
        className={`my-3 relative max-w-[70%] p-4 rounded-2xl shadow-sm text-sm leading-relaxed ${
          isUser
            ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-br-none"
            : "bg-white border border-gray-200 text-gray-800 rounded-bl-none"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>

        {!isUser && message.tts_key && (
          <div className="absolute -bottom-4 right-3">
            <button
              onClick={handleTogglePlay}
              disabled={loading}
              className={`w-10 h-10 flex items-center justify-center rounded-full shadow-md border transition-all duration-300 ${
                loading
                  ? "bg-gray-300 border-gray-300 cursor-not-allowed"
                  : playing
                  ? "bg-red-500 hover:bg-red-600 border-red-600 text-white"
                  : "bg-green-500 hover:bg-green-600 border-green-600 text-white"
              }`}
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : playing ? (
                <Pause size={20} />
              ) : (
                <Play size={20} />
              )}
            </button>
          </div>
        )}
        {error && (
          <div className="text-red-500 text-xs mt-2">{error}</div>
        )}
      </div>
    </div>
  );
}

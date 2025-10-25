import React, { useState, useRef, useEffect } from "react";
import { Mic, Send, Square, ChevronDown, Headphones } from "lucide-react";
import { streamChat } from "../utils/sseClient";
import { useParams } from "react-router-dom";

export default function ChatInput({ addMessage, updateMessageById }) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isSending, setIsSending] = useState(false); // ✅ 新增状态
  const [devices, setDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const { sessionId } = useParams();

  useEffect(() => {
    async function loadDevices() {
      try {
        const allDevices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = allDevices.filter(d => d.kind === "audioinput");
        setDevices(audioInputs);
        if (audioInputs.length > 0) setSelectedDeviceId(audioInputs[0].deviceId);
      } catch (err) {
        console.error("无法获取麦克风设备列表:", err);
      }
    }

    loadDevices();
    navigator.mediaDevices.addEventListener("devicechange", loadDevices);
    return () => navigator.mediaDevices.removeEventListener("devicechange", loadDevices);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isSending) return; // ✅ 防止重复发送
    setIsSending(true);
    addMessage({ type: "human", content: input });
    const messageToSend = input;
    setInput("");

    try {
      await streamChat(messageToSend, (chunk) => {
        if (chunk.id) {
          addMessage({
            id: chunk.id,
            type: chunk.type || "ai",
            content: chunk.content || "",
            tts_key: chunk.tts_key || null,
          });
        } else {
          updateMessageById(chunk.id, msg => ({
            ...msg,
            content: msg.content + chunk.content
          }));
        }
      }, sessionId);
    } catch (err) {
      console.error("消息发送失败:", err);
    } finally {
      setIsSending(false); // ✅ 发送完成恢复按钮
    }
  };

  const blobToBase64 = (blob) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = reject;
      reader.onloadend = () => {
        const parts = String(reader.result).split(",");
        resolve(parts[1] || "");
      };
      reader.readAsDataURL(blob);
    });

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined,
          echoCancellation: false,
          noiseSuppression: false,
          channelCount: 1,
        },
      });

      const mr = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
      chunksRef.current = [];

      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm;codecs=opus" });
        const base64 = await blobToBase64(blob);
        addMessage({ type: "human", content: "[语音消息]" });

        setIsSending(true);
        try {
          await streamChat(base64, (chunk) => {
            if (chunk.id) {
              addMessage({
                id: chunk.id,
                type: chunk.type || "ai",
                content: chunk.content || "",
                tts_key: chunk.tts_key || null,
              });
            } else {
              updateMessageById(chunk.id, msg => ({
                ...msg,
                content: msg.content + chunk.content
              }));
            }
          }, sessionId, { type: "audio" });
        } finally {
          setIsSending(false);
        }
      };

      mediaRecorderRef.current = mr;
      mr.start();
      setIsRecording(true);
    } catch (e) {
      console.error("无法启动录音:", e);
    }
  };

  const stopRecording = () => {
    try {
      const mr = mediaRecorderRef.current;
      if (mr && mr.state !== "inactive") {
        mr.stop();
        mr.stream?.getTracks?.().forEach((t) => t.stop());
      }
    } catch (e) {
      console.error("停止录音失败:", e);
    } finally {
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) stopRecording();
    else startRecording();
  };

  return (
    <div className="flex items-center bg-white rounded-full px-3 py-2 shadow-md border border-gray-200 space-x-2">
      {/* 麦克风设备选择 */}
      <div className="relative group">
        <button className="flex items-center gap-1 bg-gray-50 hover:bg-gray-100 border border-gray-300 text-gray-700 text-sm rounded-full px-3 py-1.5 transition-all">
          <Headphones size={16} className="text-gray-500" />
          <span>{devices.find(d => d.deviceId === selectedDeviceId)?.label?.slice(0, 12) || "选择设备"}</span>
          <ChevronDown size={14} className="text-gray-400" />
        </button>
        <div className="absolute left-0 bottom-full mb-1 hidden group-hover:block bg-white shadow-lg rounded-md border border-gray-200 z-10 w-48">
          {devices.length === 0 ? (
            <div className="px-3 py-2 text-sm text-gray-500">未检测到麦克风</div>
          ) : (
            devices.map(d => (
              <div
                key={d.deviceId}
                onClick={() => setSelectedDeviceId(d.deviceId)}
                className={`px-3 py-2 text-sm cursor-pointer hover:bg-blue-50 ${
                  d.deviceId === selectedDeviceId ? "bg-blue-100 text-blue-700" : "text-gray-700"
                }`}
              >
                {d.label || `麦克风 ${d.deviceId.slice(0, 5)}...`}
              </div>
            ))
          )}
        </div>
      </div>

      <input
        type="text"
        placeholder="你可以说话或输入文字..."
        className="flex-1 bg-transparent text-sm outline-none px-2 text-gray-800"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={isSending} // ✅ 发送中禁用输入
      />

      <button
        onClick={toggleRecording}
        className={`relative flex items-center justify-center w-10 h-10 rounded-full shadow-md transition-all ${
          isRecording ? "bg-red-500 animate-pulse shadow-red-300" : "bg-blue-500 hover:bg-blue-600"
        }`}
        disabled={isSending} // ✅ 发送中禁用录音
      >
        {isRecording ? <Square size={18} color="white" /> : <Mic size={20} color="white" />}
      </button>

      <button
        onClick={handleSend}
        className={`ml-1 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 transition shadow-md ${
          isSending ? "opacity-50 cursor-not-allowed" : ""
        }`}
        disabled={isSending} // ✅ 发送中禁用发送按钮
      >
        <Send size={18} />
      </button>
    </div>
  );
}

import React, { useState, useRef } from "react";
import { Mic, Send, Square } from "lucide-react";
import { streamChat } from "../utils/sseClient";
import { useParams } from "react-router-dom";

export default function ChatInput({ addMessage, updateMessageById }) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const { sessionId } = useParams();

const handleSend = async () => {
  if (!input.trim()) return;

  // Only add user message
  addMessage({ type: "human", content: input });
  setInput("");
  // Let the backend handle AI message creation and streaming
  await streamChat(input, (chunk) => {
    // If chunk contains message ID and initial content
    if (chunk.id) {
      addMessage({
        id: chunk.id,
        type: chunk.type || "ai",
        content: chunk.content || "",
        tts_key: chunk.tts_key || null,
      });
    } else {
      // For subsequent chunks, update existing message
      updateMessageById(chunk.id, msg => ({
        ...msg,
        content: msg.content + chunk.content
      }));
    }
  }, sessionId);

  setInput("");
};

// Similarly update handleAudioResponse
const handleAudioResponse = async (base64Audio) => {
  // Add user voice message
  addMessage({ type: "human", content: "[语音消息]" });

  // Let backend handle AI message creation and streaming
  await streamChat(base64Audio, (chunk) => {
    if (chunk.id) {
      addMessage({
        id: chunk.id,
        type: "ai",
        content: chunk.content || ""
      });
    } else {
      updateMessageById(chunk.id, msg => ({
        ...msg,
        content: msg.content + chunk.content
      }));
    }
  }, sessionId, { type: "audio" });
};

  const blobToBase64 = (blob) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = reject;
      reader.onloadend = () => {
        // reader.result 是 data:audio/webm;base64,AAAA...
        const parts = String(reader.result).split(",");
        resolve(parts[1] || "");
      };
      reader.readAsDataURL(blob);
    });

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      chunksRef.current = [];
      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };
      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const base64 = await blobToBase64(blob);

        // 可选：在聊天中添加一条用户语音占位消息
        addMessage({ type: "human", content: "[语音消息]" });

        // 添加空的 AI 消息（会被 stream 更新）
        let aiMessage = { type: "ai", content: "" };
        addMessage(aiMessage);

        // 发送 base64 音频给后端，type 为 "audio"，并通过 SSE 实时接收回复
      await streamChat(base64, (chunk) => {
        aiMessage.content += chunk;
        addMessage((prev) => [...prev]);
      }, sessionId, { type: "audio" });
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
        // 停止所有音轨（释放麦克风）
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
    <div className="flex items-center bg-gray-100 rounded-full px-3 py-2 shadow-inner">
      <input
        type="text"
        placeholder="你可以说话或输入文字..."
        className="flex-1 bg-transparent text-sm outline-none px-2"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        onClick={toggleRecording}
        className={`relative flex items-center justify-center w-10 h-10 rounded-full transition-all ${
          isRecording ? "bg-red-500 animate-pulse" : "bg-blue-500"
        }`}
      >
        {isRecording ? <Square size={18} color="white" /> : <Mic size={20} color="white" />}
      </button>
      <button
        onClick={handleSend}
        className="ml-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 transition"
      >
        <Send size={18} />
      </button>
    </div>
  );
}

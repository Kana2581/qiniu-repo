import { v4 as uuidv4 } from "uuid";
import { apiFetch } from "../utils/api.js";

const audioQueue = []; // 音频播放队列
let isPlaying = false; // 播放状态标识

export async function streamChat(content, onMessage, sessionId, opts = {}) {
  const { type = "text", id = uuidv4() } = opts;

  const response = await apiFetch(`/chats/${sessionId}/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ content, id, type }),
  });

  if (!response.body) throw new Error("没有返回流");

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      if (!part.startsWith("event:")) continue;

      const [eventLine, dataLine] = part.split("\n");
      const eventType = eventLine.replace("event: ", "").trim();
      const dataRaw = dataLine.replace("data: ", "").trim();

      try {
        const data = JSON.parse(dataRaw);
        console.log("SSE 原始数据:", eventType, data);

        if (eventType === "message") {
          const chunk = data?.chunk?.data?.content;
          const ttsKey = data?.chunk?.data?.tts_key;
          
          // 文本更新
          if (chunk) onMessage(data?.chunk?.data);

          // 旧版 TTS 播放逻辑
          //if (ttsKey) handleTtsAudio(ttsKey).catch(console.error);
        }

        // ✅ 新增：直接播放 base64 音频的逻辑
        else if (eventType === "audio") {
          const base64 = data?.base64;
          if (base64) {
            enqueueAudio(base64);
          }
        }
      } catch (e) {
        console.error("SSE 数据解析失败:", e, part);
      }
    }
  }
}

/**
 * 将音频加入播放队列
 */
function enqueueAudio(base64) {
  audioQueue.push(base64);
  if (!isPlaying) playNextAudio();
}

/**
 * 顺序播放队列中的音频
 */
async function playNextAudio() {
  if (audioQueue.length === 0) {
    isPlaying = false;
    return;
  }

  isPlaying = true;
  const base64 = audioQueue.shift();
  const audioUrl = `data:audio/mp3;base64,${base64}`;
  const audio = new Audio(audioUrl);

  audio.onended = () => {
    isPlaying = false;
    playNextAudio(); // 播放下一个
  };

  audio.onerror = (e) => {
    console.error("音频播放失败:", e);
    isPlaying = false;
    playNextAudio();
  };

  try {
    await audio.play();
  } catch (err) {
    console.error("播放被阻止（可能用户未交互）:", err);
  }
}

/**
 * 旧逻辑：根据 tts_key 获取 OSS 音频 URL
 */
async function handleTtsAudio(ttsKey) {
  try {
    const audioUrl = await fetchAudioUrl(ttsKey);
    console.log("获取到音频 URL:", audioUrl);
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      await audio.play();
    }
  } catch (e) {
    console.error("音频处理失败:", e);
  }
}

async function fetchAudioUrl(ttsKey) {
  const res = await apiFetch(`/oss?key=${encodeURIComponent(ttsKey)}`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`请求音频失败: ${res.status}`);
  const data = await res.json();
  return data.url;
}

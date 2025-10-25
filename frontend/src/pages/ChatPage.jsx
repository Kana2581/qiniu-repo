// ...existing code...
import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import SessionSidebar from "../components/SessionSidebar";
import { apiFetch } from "../utils/api";
import { v4 as uuidv4 } from "uuid";

export default function ChatPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [selectedSession, setSelectedSession] = useState(sessionId || null);
  const [loading, setLoading] = useState(false);
  const [fetchedSessions, setFetchedSessions] = useState({});
  const [assistantConfig, setAssistantConfig] = useState(null);
  const [fetchedAssistants, setFetchedAssistants] = useState({});

  /** 更新指定消息的内容 */
  const updateMessageById = useCallback((messageId, updater) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const index = newMessages.findIndex(msg => msg.id === messageId);
      if (index !== -1) {
        newMessages[index] = {
          ...newMessages[index],
          ...(typeof updater === 'function' ? updater(newMessages[index]) : updater)
        };
      }
      return newMessages;
    });

    // 同时更新缓存
    setFetchedSessions(prev => ({
      ...prev,
      [selectedSession]: prev[selectedSession]?.map(msg => 
        msg.id === messageId 
          ? { ...msg, ...(typeof updater === 'function' ? updater(msg) : updater) }
          : msg
      )
    }));
  }, [selectedSession]);

  /** 拉取 assistant 配置并缓存 */
  const fetchAssistant = useCallback(async (id) => {
    if (!id) return;
    if (fetchedAssistants[id]) {
      setAssistantConfig(fetchedAssistants[id]);
      return;
    }
    try {
      const res = await apiFetch(`/assistants/${id}`, {
        headers: { accept: "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch assistant config");
      const data = await res.json();
      setAssistantConfig(data);
      setFetchedAssistants(prev => ({ ...prev, [id]: data }));
    } catch (err) {
      console.error("Error fetching assistant config:", err);
      setAssistantConfig(null);
    }
  }, [fetchedAssistants]);

  /** 新增：先拉取 session 信息以获取 assistant_id，然后拉取 assistant 配置 */
  const fetchSession = useCallback(async (id) => {
    if (!id) return;
    try {
      const res = await apiFetch(`/session/${id}`, {
        headers: { accept: "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch session");
      const data = await res.json();
      // 兼容不同字段命名：assistant_id | assistantId | assistant.id
      const assistantId = data.assistant_id || data.assistantId || (data.assistant && data.assistant.id);
      if (assistantId) {
        await fetchAssistant(assistantId);
      } else {
        setAssistantConfig(null);
      }
    } catch (err) {
      console.error("Error fetching session:", err);
      setAssistantConfig(null);
    }
  }, [fetchAssistant]);

  /** 添加新消息 */
  const addMessage = useCallback((message) => {
    const messageWithId = { ...message, id: uuidv4() };
    setMessages(prev => [...prev, messageWithId]);
    
    // 更新缓存
    setFetchedSessions(prev => ({
      ...prev,
      [selectedSession]: [...(prev[selectedSession] || []), messageWithId],
    }));

    return messageWithId;
  }, [selectedSession]);


  /** ✅ 拉取指定会话的历史消息 */
  const fetchMessages = useCallback(async (id) => {
    if (!id) return;

    // 如果之前加载过该会话，直接从缓存中恢复
    if (fetchedSessions[id]) {
      setMessages(fetchedSessions[id]);
      return;
    }

    setLoading(true);
    try {
      const res = await apiFetch(`/chats/${id}/messages/`, {
        headers: { accept: "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch messages");

      const data = await res.json();

      // ✅ 过滤 human 消息 或 含 tts 的消息
      const filtered = data.messages.filter((msg) => msg.type === "human" || msg.tts_key);

      setMessages(filtered);
      setFetchedSessions((prev) => ({ ...prev, [id]: filtered }));
    } catch (err) {
      console.error("Error fetching messages:", err);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [fetchedSessions]);

  /** ✅ 监听 URL 改变：先拉取 messages，再根据 session 获取 assistant */
  useEffect(() => {
    setSelectedSession(sessionId || null);
    if (sessionId) {
      fetchMessages(sessionId);
      fetchSession(sessionId);
    } else {
      setMessages([]);
      setAssistantConfig(null);
    }
  }, [sessionId, fetchMessages, fetchSession]);

  // helper: 判断 avatar 是否是 URL（否则按 emoji/text 直接渲染）
  const renderAvatar = (avatar) => {
    if (!avatar) {
      return (
        <div className="w-8 h-8 rounded-full mr-2 flex items-center justify-center text-xl bg-gray-100">
          🤖
        </div>
      );
    }
    const isUrl = typeof avatar === "string" && (avatar.startsWith("http://") || avatar.startsWith("https://") || avatar.startsWith("/"));
    if (isUrl) {
      return (
        <img
          src={avatar}
          alt={assistantConfig?.name || "Voice Assistant"}
          className="w-8 h-8 rounded-full mr-2 object-cover"
        />
      );
    }
    // 非 URL，直接当作 emoji / 文本渲染
    return (
      <div className="w-8 h-8 rounded-full mr-2 flex items-center justify-center text-xl bg-gray-100">
        {avatar}
      </div>
    );
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* 左侧：会话侧边栏 */}
      <SessionSidebar
        selectedId={selectedSession}
        onSelect={(id) => {
          setSelectedSession(id);
          navigate(`/chat/${id}`);
        }}
      />

      {/* 右侧：聊天主区域 */}
      <div className="flex flex-col flex-1">
        {/* 顶部栏 */}
        <div className="flex items-center justify-center p-3 bg-white shadow-sm">
          {renderAvatar(assistantConfig?.avatar)}
          <div className="text-center">
            <h1 className="text-lg font-semibold text-gray-800">
              {assistantConfig?.name || "语音助手"}
            </h1>
            {assistantConfig?.description && (
              <div className="text-xs text-gray-500">{assistantConfig.description}</div>
            )}
          </div>
        </div>

        {/* 聊天消息区 */}
        <div className="flex-1 overflow-y-auto">
          {selectedSession ? (
            loading ? (
              <div className="flex items-center justify-center h-full text-gray-400">
                加载中...
              </div>
            ) : (
              <ChatWindow messages={messages} />
            )
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              请选择一个会话开始聊天
            </div>
          )}
        </div>

        {/* 输入栏 */}
        {selectedSession && (
          <div className="p-3 bg-white border-t">
            <ChatInput addMessage={addMessage} updateMessageById={updateMessageById} />
          </div>
        )}
      </div>
    </div>
  );
}
// ...existing code...
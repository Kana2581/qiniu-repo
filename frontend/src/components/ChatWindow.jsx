import React, { useRef, useEffect } from "react";
import MessageItem from "./MessageItem";

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  console.log("ChatWindow 消息列表:", messages);
  return (
    <div
      className="flex flex-col space-y-2 p-3 overflow-y-auto"
      style={{  maxHeight: '80vh' }}
    >
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

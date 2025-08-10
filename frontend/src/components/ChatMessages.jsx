import MessageBubble from "./MessageBubble";
import { useEffect, useRef } from "react";

export default function ChatMessages({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="messages">
      {messages.map((m, i) => (
        <MessageBubble key={i} role={m.role} content={m.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

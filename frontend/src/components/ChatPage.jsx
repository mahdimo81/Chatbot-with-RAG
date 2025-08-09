import { useState, useRef, useEffect } from "react";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";
import { sendMessage } from "../services/api";
import { connectWS } from "../services/websocket";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef(null);

  const handleSend = async (text) => {
    const newMessages = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    setIsTyping(true);

    // WebSocket mode
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ message: text }));
      return;
    }

    // HTTP mode
    const aiResponse = await sendMessage(text, newMessages);
    setMessages([...newMessages, { role: "assistant", content: aiResponse.content }]);
    setIsTyping(false);
  };

  // WebSocket setup
  useEffect(() => {
    // Comment this out if you don't want streaming
    wsRef.current = connectWS((chunk) => {
      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg?.role === "assistant") {
          return [...prev.slice(0, -1), { ...lastMsg, content: lastMsg.content + chunk }];
        } else {
          return [...prev, { role: "assistant", content: chunk }];
        }
      });
    }, () => setIsTyping(false));

    return () => wsRef.current?.close();
  }, []);

  return (
    <>
      <ChatMessages messages={messages} />
      {isTyping && <TypingIndicator />}
      <ChatInput onSend={handleSend} />
    </>
  );
}

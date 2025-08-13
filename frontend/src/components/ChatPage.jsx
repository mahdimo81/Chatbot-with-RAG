import { useState, useRef, useEffect } from "react";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";
import { sendMessage } from "../services/api";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef(null);

  const handleSend = async (text) => {
    const newMessages = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    setIsTyping(true);

    

    // HTTP mode
    const aiResponse = await sendMessage(text, newMessages);
    setMessages([...newMessages, { role: "assistant", content: aiResponse.content }]);
    setIsTyping(false);
  };


  return (
    <>
    <div className="chat-container">
      <ChatMessages messages={messages} />
      {isTyping && <TypingIndicator />}
    </div>
      <ChatInput onSend={handleSend} />
    </>
  );
}

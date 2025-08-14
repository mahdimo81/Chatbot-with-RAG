import { useState } from "react";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";
import { sendMessage } from "../services/api";

function formatMessage(){
  let rawMessages =sessionStorage.getItem("currentConv");
  rawMessages = rawMessages ? JSON.parse(rawMessages).pairs : [];
  const formatted = rawMessages.flatMap(m => [
    { role: "user", content: m[0] },
    { role: "assistant", content: m[1] }
    ]);
  return formatted;
}



export default function ChatPage() {
  const [messages, setMessages] = useState(formatMessage());
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (text) => {
    const newMessages = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    


    const aiResponse = await sendMessage(text, newMessages);
    setMessages([...newMessages, { role: "assistant", content: aiResponse.response }]);
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

import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <form className="input-area" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button type="submit">Send</button>
    </form>
  );
}

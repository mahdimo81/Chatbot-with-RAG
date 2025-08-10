import React, { useState } from "react";
import Sidebar from "../src/components/Sidear";
import ChatPage from "../src/components/ChatPage";
import "./App.css";

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [conversations] = useState([
    { id: 1, title: "Project Q&A" },
    { id: 2, title: "Brainstorm Ideas" }
  ]);

  return (
    <div>
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        conversations={conversations}
        onSelect={(id) => console.log("Selected conversation:", id)}
      />
      <div style={{ flex: 1 }}>
        <ChatPage />
      </div>
    </div>
  );
}

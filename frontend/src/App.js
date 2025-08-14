import React, { useState } from "react";
import Sidebar from "../src/components/Sidebar";
import ChatPage from "../src/components/ChatPage";
import Auth from "../src/components/Auth";
import "./styles/App.css";

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [conversations] = useState([
    { id: 1, title: "Project Q&A" },
    { id: 2, title: "Brainstorm Ideas" }
  ]);

  return (
  <>
    {!sessionStorage.getItem("access_token") ? (
      <Auth />
    ) : (
      <div style={{ display: "flex", height: "100vh" }}>
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
    )}
  </>
);

}

import React, { useState, useEffect } from "react";
import Sidebar from "../src/components/Sidebar";
import ChatPage from "../src/components/ChatPage";
import Auth from "../src/components/Auth";
import "./styles/App.css";

export default function App() {
  const [conversations, setConversations] = useState(
    sessionStorage.getItem("conversations")
  );
  const trimmedConv = conversations? JSON.parse(conversations).conversations: [];
  const token = sessionStorage.getItem("access_token");

  const loadConversation = async (id) => {
    try {
      const res = await fetch(
        `http://localhost:8000/chat/get-messages/${id}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      const data = await res.json();
      sessionStorage.setItem("currentConv", JSON.stringify(data));
      sessionStorage.setItem("conversationId", id);
      window.location.reload();
    } catch (error) {
      console.log(error);
    }
  };

  const handleDelete = async (id) => {
    try {
      const response = await fetch(
        `http://localhost:8000/chat/del-conv/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const updated = trimmedConv.filter((c) => c.id !== id);
      setConversations(JSON.stringify({ conversations: updated }));
    } catch (err) {
      console.error("Failed to delete conversation", err);
    }
  };

  useEffect(() => {
    console.log("Conversations changed:", trimmedConv);
    if(trimmedConv.length === 0){
      console.log("ijnkm;l'")
      sessionStorage.removeItem("conversationId");
      sessionStorage.removeItem("currentConv");
    }
    sessionStorage.setItem("conversations", JSON.stringify({ conversations: trimmedConv }));
  }, [conversations]);

  return (
    <>
      {!token ? (
        <Auth />
      ) : (
        <div style={{ display: "flex", height: "100vh" }}>
          <Sidebar
            conversations={trimmedConv}
            onSelect={loadConversation}
            onDelete={handleDelete}
          />
          <div style={{ flex: 1 }}>
            <ChatPage />
          </div>
        </div>
      )}
    </>
  );
}

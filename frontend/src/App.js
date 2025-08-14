import React, { useState } from "react";
import Sidebar from "../src/components/Sidebar";
import ChatPage from "../src/components/ChatPage";
import Auth from "../src/components/Auth";
import "./styles/App.css";

async function loadConversation(id){
  const token = sessionStorage.getItem("access_token");
  try{
    const res = await fetch(`http://localhost:8000/chat/get-messages/${id}`,{
      method:"POST",
      headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }})
      const data = await res.json();
      sessionStorage.setItem("currentConv",JSON.stringify(data));
      sessionStorage.setItem("conversationId",id);
      window.location.reload();
  }catch(error){
    console.log(error)
  }
}

export default function App() {
  const [conversations] = useState(sessionStorage.getItem("conversations"));
  const trimmedConv = conversations? JSON.parse(conversations).conversations:[];
  return (
  <>
    {!sessionStorage.getItem("access_token") ? (
      <Auth />
    ) : (
      <div style={{ display: "flex", height: "100vh" }}>
        <Sidebar
          conversations={trimmedConv}
          onSelect={loadConversation}
        />
        <div style={{ flex: 1 }}>
          <ChatPage />
        </div>
      </div>
    )}
  </>
);

}

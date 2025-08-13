import React from "react";
import "../styles/App.css";

export default function Sidebar({ isOpen, onToggle, conversations, onSelect }) {
  return (
    <div className={"sidebar"}>
      <div className="sidebar-content">
        {conversations.map((conv, i) => (
          <div
            key={i}
            className="conversation-item"
            onClick={() => onSelect(conv.id)}
          >
            {conv.title || `Conversation ${i + 1}`}
          </div>
        ))}
      </div>

    
    </div>
  );
}

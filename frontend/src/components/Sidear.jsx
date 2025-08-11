import React from "react";
import "../sidebar.css";

export default function Sidebar({ isOpen, onToggle, conversations, onSelect }) {
  return (
    <div className={`sidebar ${isOpen ? "open" : "closed"}`}>
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

      <button className="toggle-button" onClick={onToggle}>
        {isOpen ? "Close Sidebar" : "Open Sidebar"}
      </button>
    </div>
  );
}

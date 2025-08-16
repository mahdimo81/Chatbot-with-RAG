import React from "react";
import "../styles/App.css";

export default function Sidebar({ conversations, onSelect, onDelete }) {
  return (
    <div className="sidebar">
      <div className="sidebar-content">
        {conversations.map((conv, i) => (
          <div
            key={i}
            className="conversation-item"
            onClick={() => onSelect(conv.id, conversations)}
          >
            {conv.title || `Conversation ${i + 1}`}

            {/* Trash icon */}
            <img
              className="recycle"
              src="/icons8-trash-50.png"
              alt="delete"
              onClick={(e) => {
                e.stopPropagation(); 
                onDelete(conv.id);   
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

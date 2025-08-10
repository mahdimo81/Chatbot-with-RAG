export default function MessageBubble({ role, content }) {
  return (
    <div className={`message-bubble ${role === "user" ? "user-bubble" : "ai-bubble"}`}>
      {content}
    </div>
  );
}

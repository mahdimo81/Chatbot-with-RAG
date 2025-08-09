export const connectWS = (onChunk, onComplete) => {
  const ws = new WebSocket("ws://localhost:8000/ws/chat/");

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "chunk") onChunk(data.content);
    if (data.type === "end") onComplete();
  };

  ws.onclose = () => console.log("WebSocket closed");

  return ws;
};

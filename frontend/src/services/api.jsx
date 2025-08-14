import axios from "axios";

const CHAT = axios.create({ baseURL: "http://localhost:8000/chat" });


export const sendMessage = async (message) => {
  const token = sessionStorage.getItem("access_token");
  const formData = new FormData();
  formData.append("message", message);
  formData.append("conversation_id", sessionStorage.getItem("conversationId"));
  try{
  const res = await CHAT.post("/chat/", formData, {
    headers: {
      "Authorization": `Bearer ${token}`, 
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;}
  catch(error){
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    window.location.reload();
  }
  
};

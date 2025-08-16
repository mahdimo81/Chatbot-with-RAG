import axios, { AxiosHeaders } from "axios";
import ChatInput from "../components/ChatInput";

const CHAT = axios.create({ baseURL: "http://localhost:8000/chat" });



export const sendMessage = async (message) => {
  const token = sessionStorage.getItem("access_token");
  const formData = new FormData();
  const convId = sessionStorage.getItem("conversationId");
  const convList = sessionStorage.getItem("conversations");
  formData.append("message", message);
  if(convId)
  formData.append("conversation_id",convId );
  try{
  const res = await CHAT.post("/chat/",
     formData, {
    headers: {
      "Authorization": `Bearer ${token}`, 
      "Content-Type": "multipart/form-data",
    },
  });
  sessionStorage.setItem("conversationId",res.data.conversation.id)
  if(!isConvExists(res.data.conversation.id,convList)){
    let data = await getConvs()
    if(data)
      sessionStorage.setItem("conversations",JSON.stringify(data));
  }
  return res.data;}
  catch(error){
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    window.location.reload();
  }  
};

const getConvs = async () => {
  const token = sessionStorage.getItem("access_token");
  try {
    const res = await CHAT.get("conversations/", {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    
    return res.data;
  } catch (error) {
    console.error("Failed to get conversations:", error);
    return null; 
  }
};


function isConvExists(id,convlist){
  for(let c in convlist)
    if(c.id === id) return true;
  return false;
}
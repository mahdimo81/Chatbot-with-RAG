import axios from "axios";

const API = axios.create({ baseURL: "http://localhost:8000/chat" });

export const sendMessage = async (message, history) => {
  const token = sessionStorage.getItem("access_token");
  
  const formData = new FormData();
  formData.append("message", message);
  const res = await API.post("/chat/", formData, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "multipart/form-data",
    },
  });

  return res.data; 
};

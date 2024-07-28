// import NLP from "./NLP";
import Live2D from './Live2D';
import { postData,fetchData } from "./utils";

const { model, motions } = Live2D;
const form = <HTMLFormElement>document.getElementById('form');
const input = <HTMLInputElement>document.getElementById('message');
const messages = <HTMLElement>document.getElementById('messages');
const audioPlayer = <HTMLAudioElement>document.getElementById('audioPlayer');

type MsgType = "AI" | "System" | "User" | "Tool";

interface ChatMessage {
  user: string;
  message: string;
  msgType: MsgType;
}

interface ChatHistory {
  history: ChatMessage[];
  status: string;
  code: number;
}

const createMessage = (sender: 'user' | 'reply', message: string) => {
  const div = document.createElement('div');
  div.className = sender;
  div.innerText = message;
  messages.append(div);
  div.scrollIntoView();
}

// const restoreChatHistory = async () => {
//   let chatHistory: ChatHistory = await fetchData("http://localhost:8000/chatHistory");
//   console.log(chatHistory)
//   chatHistory.history.forEach((msg) => {
//     if (msg.msgType === "AI") {
//       createMessage("reply", msg.message);
//     } 
//     if (msg.msgType === "User") 
//     {
//       createMessage("user", msg.message);
//     }  
//   });
// }
const restoreChatHistory = async (): Promise<void> => {
  const apiUrl = "http://localhost:8000/chatHistory";
  const authToken = localStorage.getItem("authToken");
  const apiKey = localStorage.getItem("apiKey");

  try {
    const headers: Record<string, string> = {};
    if (authToken) {
      headers["Authorization"] = `Bearer ${authToken}`;
    } else if (apiKey) {
      headers["X-API-Key"] = apiKey;
    } else {
      console.error("No authentication method found");
      return;
    }

    const response = await fetch(apiUrl, {
      method: "GET",
      headers: headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const chatHistory: ChatHistory = await response.json();
    console.log(chatHistory);

    chatHistory.history.forEach((msg: ChatMessage) => {
      if (msg.msgType === "AI") {
        createMessage("reply", msg.message);
      }
      if (msg.msgType === "User") {
        createMessage("user", msg.message);
      }
    });
  } catch (error) {
    console.error("Error fetching chat history:", error);
  }
};

const processMessage = async (message: string) => {
  const chatMessage: ChatMessage = {
    user: 'User',
    message: message,
    msgType: "User"
  };
}

const getTextToSpeech = async (text: string): Promise<string> => {
  const url = 'http://localhost:8000/en2jp_speach';
  const data = { data: text };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const message = input.value.trim();

  if (!message.length) return;

  createMessage('user', message);
  processMessage(message);

  input.value = '';
});



export { createMessage, processMessage, restoreChatHistory };

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Union
from main.bot.bot_main import main

router = APIRouter()

# Define the chat message model for the base 
class ChatMessage(BaseModel):
    user: str
    message: str
    msgType: str
    start: Optional[int]
    end: Optional[int]


# Define ChatHistory return model
class ChatHistory(BaseModel):
    history: List[ChatMessage]
    status: str
    code: int

# Define reciving message model
class RecieveMessage(BaseModel):
    message: str
    user: str


@router.post("/chat", tags=["chat"], response_model=ChatMessage)
async def chat(message: RecieveMessage):
    output = main(message.message)
    if output == "":
        return ChatMessage(user="bot", message="I am sorry, I could not answer this question. i blame microsoft -pooh", msgType="text", start="", end="")
    return ChatMessage(user="bot", message=output, msgType="text", start="", end="")

@router.get("/chatHistory", tags=["chat"], response_model=ChatHistory)
async def chatHistory():
    return ChatHistory(history=[], status="success", code=200)
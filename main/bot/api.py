from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Union, Any
from main.bot.bot_main import main, history
from main.bot.lib.models import ChatMessage, ChatHistory

router = APIRouter()

# Define ChatHistory return model
class ReplyChatHistory(BaseModel):
    history: List[ChatMessage] = None
    status: str
    code: int

# Define reciving message model
class RecieveMessage(BaseModel):
    message: str
    user: str


@router.post("/chat", tags=["chat"], response_model=ChatMessage)
async def chat(message: RecieveMessage):
    output = await main(message.message)
    print(type(output))
    if output == "":
        return ChatMessage(user="bot", message="I am sorry, I could not answer this question. i blame microsoft -pooh", msgType="AI")
    return ChatMessage(user="bot", message=output, msgType="AI")

@router.get("/chatHistory", tags=["chat"], response_model=ReplyChatHistory)
async def chatHistory():
    if history.getHistoryLen == 0:
        print("No history")
        return ReplyChatHistory(history=[], status="failed", code=200)
    print("History found")
    return ReplyChatHistory(history=history.exportHistory(), status="success", code=200)

@router.post("/chatvoice", tags=["chat"], response_model=ChatMessage)
async def chatVoice(message: RecieveMessage):
    output = await main(message.message)
    print(type(output))
    if output == "":
        return ChatMessage(user="bot", message="I am sorry, I could not answer this question. i blame microsoft -pooh", msgType="text")
    return ChatMessage(user="bot", message=output, msgType="text")


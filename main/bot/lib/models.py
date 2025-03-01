from typing import Annotated, Dict, List, Literal, Optional, Union
from pydantic import BaseModel

# Tools base object model
class ToolsObj(BaseModel):
    name: str
    description: str
    usage: str


class ChatMessage(BaseModel):
    user: str
    start: Optional[str] = None
    end: Optional[str] = None
    msgType: Literal["AI", "System", "User", "Tool", "Context"]
    message: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage]

    def add_message(self, user: str, message: str, type: str, end: Optional[str] = None, start: Optional[str] = None) -> None:
        self.messages.append(ChatMessage(user=user, message=message, msgType=type, start=start, end=end))

    def getHistory(self) -> List[ChatMessage]:
        return self.messages

    def getHistoryLen(self) -> int:
        return len(self.messages)

    def exportHistory(self) -> List[ChatMessage]:
        export = []
        for msg in self.messages:
            if msg.msgType == "User" or "AI":
                export.append(msg)
        return export
    
    def getContextList(self) -> List[ChatMessage]:
        export = []
        for msg in self.messages:
            if msg.msgType == "Context":
                export.append(msg)
        return msg
        
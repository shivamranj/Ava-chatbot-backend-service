from pydantic import BaseModel,EmailStr,RootModel
from typing import List


class MessageChatbot(BaseModel):
    message: str
    user_id: str

class userCreate(BaseModel):
    email: EmailStr

class MessageCreate(BaseModel):
    message: str
    email: EmailStr 

class MessageResponse(BaseModel):
    reply: str

class userResponse(BaseModel):
    status_code: int
    data: dict[str, str] 

class MessageItem(BaseModel):
    id: int
    user: str
    text: str

class MessageHistoryResponse(RootModel[List[MessageItem]]):
    pass
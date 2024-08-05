from fastapi import APIRouter
from app.models import Message  
from app.services import generate_response

router = APIRouter()

@router.post("/chat")
async def chat(message: Message):
    user_message = message.message
    bot_reply = generate_response(user_message)
    return {"reply": bot_reply}
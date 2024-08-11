from .models import User, Message
from fastapi import APIRouter, HTTPException, Depends
from .database import LocalDbSession
from .services import generate_response
from sqlalchemy.orm import Session
from .schemas import *
from .constant import *
import random
import json
from .redis_client import redis_client
from uuid import uuid4
from app.logging_config import logger

router = APIRouter()


def get_db():
    db = LocalDbSession()
    try:
        yield db
    finally:
        db.close()


@router.post(CREATE_USER, response_model=userResponse)
async def create_user(user: userCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return userResponse(
            status_code=200,
            data={"user_id": db_user.unique_id}
        )

    unique_id = str(random.randint(1000000, 9999999))

    new_user = User(email=user.email, unique_id=unique_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return userResponse(
        status_code=200,
        data={"user_id": new_user.unique_id}
    )


@router.post(CHAT)
async def chat(message: MessageChatbot, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.unique_id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    userMessage = message.message
    bot_reply = generate_response(userMessage)

    user_message_entry = Message(
        user_id=user.unique_id, user_message=userMessage, bot_reply=bot_reply)
    db.add(user_message_entry)
    db.commit()
    db.refresh(user_message_entry)

    cache_key = f"message_history:{user.unique_id}"
    messages = db.query(Message).filter(
        Message.user_id == user.unique_id).all()
    formatted_messages = []
    message_id_counter = 1
    for msg in messages:
        formatted_messages.append(
            MessageItem(id=message_id_counter,
                        user='User', text=msg.user_message)
        )
        message_id_counter += 1

        formatted_messages.append(
            MessageItem(id=message_id_counter, user='Bot', text=msg.bot_reply)
        )
        message_id_counter += 1

    redis_client.set(cache_key, json.dumps(
        [msg.dict() for msg in formatted_messages]), ex=3600)

    return {"reply": bot_reply}


@router.get(f"{GET_HISTORY}/{{user_id}}", response_model=MessageHistoryResponse)
async def get_message_history(user_id: str, db: Session = Depends(get_db)):

    cache_key = f"message_history:{user_id}"

    cached_data = redis_client.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for user_id: {user_id}")
        formatted_messages = json.loads(cached_data)
        return MessageHistoryResponse([MessageItem(**msg) for msg in formatted_messages])

    logger.info(f"Cache not hit for user_id: {user_id}")
    messages = db.query(Message).filter(Message.user_id == user_id).all()

    if not messages:
        raise HTTPException(status_code=400, detail=PREVIOUS_MSG_ERROR)

    message_id_counter = 1
    formatted_messages = []
    for message in messages:
        formatted_messages.append(
            MessageItem(id=message_id_counter, user='User',
                        text=message.user_message)
        )
        message_id_counter += 1

        formatted_messages.append(
            MessageItem(id=message_id_counter, user='Bot',
                        text=message.bot_reply)
        )
        message_id_counter += 1
    redis_client.set(cache_key, json.dumps(
        [msg.dict() for msg in formatted_messages]), ex=3600)
    return MessageHistoryResponse(formatted_messages)

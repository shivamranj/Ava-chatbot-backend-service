from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "new_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    unique_id = Column(String, unique=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('new_users.unique_id'), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_reply = Column(Text)
    timestamp = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    user = relationship("User", back_populates="messages")

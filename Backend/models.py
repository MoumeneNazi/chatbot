from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy import ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # can be 'user' or 'therapist'


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # "user" or "bot"
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="messages")

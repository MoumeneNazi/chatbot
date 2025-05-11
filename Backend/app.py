from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import MentalHealthChatbot
from fastapi.middleware.cors import CORSMiddleware
from journal import save_entry, get_entries
from journal import get_sentiment_summary
from auth import router as auth_router
from database import Base, engine
from auth import get_current_user
from sqlalchemy.orm import Session
from fastapi import Depends
from models import ChatMessage
from database import SessionLocal
import models
from database import Base
from therapist import router as therapist_router


app = FastAPI()


Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(therapist_router)

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "mimo2021"

# Instantiate chatbot with required credentials
chatbot = MentalHealthChatbot(uri=URI, user=USERNAME, password=PASSWORD)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Mental Health Chatbot API is running."}


@app.post("/journal")
def submit_journal(message: Message):
    entry = save_entry(message.message)
    return {"status": "saved", "entry": entry}

@app.get("/journal")
def read_journal():
    return {"entries": get_entries()}


@app.get("/session")
def session_history():
    return chatbot.session


@app.get("/progress")
def mood_summary():
    return get_sentiment_summary()



@app.post("/chat")
def get_chat_response(message: Message, current_user=Depends(get_current_user)):
    db = SessionLocal()

    # Store user message
    user_msg = ChatMessage(user_id=current_user.id, role="user", message=message.message)
    db.add(user_msg)

    # Generate bot reply
    response = chatbot.chat(message.message)

    # Store bot reply
    bot_msg = ChatMessage(user_id=current_user.id, role="bot", message=response)
    db.add(bot_msg)

    db.commit()
    return {"response": response}





@app.get("/chat/history")
def get_chat_history(current_user=Depends(get_current_user)):
    db = SessionLocal()
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).order_by(ChatMessage.timestamp).all()
    return [
        {
            "role": msg.role,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]




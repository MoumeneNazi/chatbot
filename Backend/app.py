from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import MentalHealthChatbot
from fastapi.middleware.cors import CORSMiddleware
from journal import save_entry, get_entries
from journal import get_sentiment_summary


app = FastAPI()

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
def get_chat_response(message: Message):
    response = chatbot.chat(message.message)
    return {"response": response}

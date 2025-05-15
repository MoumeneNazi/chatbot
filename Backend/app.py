from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
from jose import jwt
from config import SECRET_KEY, ALGORITHM
from chatbot import MentalHealthChatbot
from journal import save_entry, get_entries, get_sentiment_summary
from auth import router as auth_router, get_current_user, create_access_token
from database import Base, engine, SessionLocal
from models import User, ChatMessage
from schemas import UserCreate
from security import hash_password, verify_password
from therapist import router as therapist_router, get_current_therapist
import json
from datetime import datetime, timedelta

# App setup
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(therapist_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j chatbot setup
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "mimo2021"
chatbot = MentalHealthChatbot(uri=URI, user=USERNAME, password=PASSWORD)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role-based access
def require_user(current_user=Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Access denied: Users only.")
    return current_user

def require_therapist(current_user=Depends(get_current_user)):
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied: Therapists only.")
    return current_user

# Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    message: str

# Routes
@app.get("/")
def root():
    return {"message": "Mental Health Chatbot API is running."}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "Account created. Please login."}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username}, role=user.role)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/token")
async def token(
    request: Request,
    username: str = Form(None),
    password: str = Form(None),
    db: Session = Depends(get_db)
):
    if request.headers.get("content-type") == "application/json":
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")
    login_request = LoginRequest(username=username, password=password)
    return login(login_request, db)

@app.post("/chat")
def get_chat_response(message: Message, db: Session = Depends(get_db), current_user=Depends(require_user)):
    db.add(ChatMessage(user_id=current_user.id, role="user", message=message.message))
    reply = chatbot.chat(message.message)
    if isinstance(reply, dict):
        reply = next(iter(reply.values()), json.dumps(reply))
    db.add(ChatMessage(user_id=current_user.id, role="bot", message=reply))
    db.commit()
    return {"response": reply}

@app.get("/chat/history")
def get_chat_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).order_by(ChatMessage.timestamp).all()
    return [
        {
            "role": msg.role,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

@app.post("/journal")
def submit_journal(message: Message, current_user=Depends(require_user)):
    entry = save_entry(message.message, current_user.username)
    return {"status": "saved", "entry": entry}

@app.get("/journal")
def read_journal(current_user=Depends(require_user)):
    return {"entries": get_entries(current_user.username)}

@app.get("/session")
def session_history():
    return chatbot.session_context.get("session_history", [])

@app.get("/progress")
def mood_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "therapist":
        return get_sentiment_summary(db)
    else:
        return get_sentiment_summary(db, user_id=current_user.id)

@app.post("/therapist/add")
def add_therapist(user: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_therapist)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
        role="therapist"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "Therapist account created successfully."}

@app.get("/therapist/chat/history")
def get_all_chat_history(db: Session = Depends(get_db), current_user=Depends(require_therapist)):
    messages = db.query(ChatMessage).order_by(ChatMessage.timestamp).all()
    return [
        {
            "user_id": msg.user_id,
            "role": msg.role,
            "message": msg.message,
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

@app.get("/therapist/dashboard")
def get_therapist_dashboard(db: Session = Depends(get_db), current_user=Depends(require_therapist)):
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    patients = (
        db.query(User)
        .join(ChatMessage, User.id == ChatMessage.user_id)
        .filter(ChatMessage.timestamp >= one_day_ago)
        .distinct()
        .all()
    )
    return [
        {
            "username": patient.username,
            "last_interaction": max(
                msg.timestamp for msg in patient.messages if msg.timestamp >= one_day_ago
            ).isoformat(),
        }
        for patient in patients
    ]

@app.get("/debug/user")
def debug_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return {"username": user.username, "hashed_password": user.hashed_password, "role": user.role}
    return {"error": "User not found"}

@app.get("/debug/token")
def debug_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"decoded_token": decoded_token}
    except Exception as e:
        return {"error": str(e)}

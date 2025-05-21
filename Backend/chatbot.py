from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import GraphDatabase
import json, os, logging, requests
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from dependencies import get_current_user
from database import get_db
from sqlalchemy.orm import Session
from models import ChatMessageModel, User, UserModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot")

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Initialize API router
router = APIRouter(prefix="/api", tags=["chat"])

# Load Gemini API key and Neo4j config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

class ChatMessage(BaseModel):
    message: str

class MentalHealthChatbot:
    def __init__(self, uri, user, password, memory_file="session_memory.json"):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            with self.driver.session() as s: 
                s.run("RETURN 1")
            logger.info("Neo4j connected successfully")
            self.neo4j_available = True
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            self.driver = None
            self.neo4j_available = False

        self.memory_file = memory_file
        self.session_context = self.load_session()
        self.symptom_list = self.load_symptom_list() if self.neo4j_available else []
        self.disorder_list = self.load_disorder_list() if self.neo4j_available else []

    def load_symptom_list(self):
        try:
            with self.driver.session() as s:
                return [r["name"] for r in s.run("MATCH (s:Symptom) RETURN s.name AS name")]
        except Exception as e:
            logger.error(f"Error loading symptoms: {e}")
            return []

    def load_disorder_list(self):
        try:
            with self.driver.session() as s:
                return [r["name"] for r in s.run("MATCH (d:Disorder) RETURN d.name AS name")]
        except Exception as e:
            logger.error(f"Error loading disorders: {e}")
            return []

    def load_session(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"reported_symptoms": [], "session_history": [], "last_interaction": None}

    def save_session(self):
        try:
            self.session_context["last_interaction"] = datetime.now().isoformat()
            with open(self.memory_file, "w") as f:
                json.dump(self.session_context, f, indent=2)
        except Exception as e:
            logger.error(f"Failed saving session: {e}")

    def extract_symptoms(self, text):
        return [s for s in self.symptom_list if s.lower() in text.lower()]

    def find_disorders(self, text):
        return [d for d in self.disorder_list if d.lower() in text.lower()]

    def _generate_response_gemini(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": GEMINI_API_KEY}
            payload = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }

            response = requests.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            data = response.json()

            text = (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
            )

            return text if text else None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    def _generate_fallback_response(self, message):
        msg_lower = message.lower()
        if any(g in msg_lower for g in ["hi", "hello", "hey"]):
            return "Hello! I'm here to support you. How are you feeling today?"
        if "depress" in msg_lower:
            return "I'm sorry you're feeling this way. You're not alone—talking helps. Would you like to share more?"
        if any(x in msg_lower for x in ["anxious", "anxiety", "stress"]):
            return "Anxiety can be tough. Try deep breathing, and know that help is available. Want to talk more?"
        return "I'm here for you. Could you tell me more about how you're feeling?"

    def chat(self, message: str) -> str:
        self.session_context["session_history"].append({
            "user": message,
            "timestamp": datetime.now().isoformat()
        })

        response = None
        try:
            disorders = self.find_disorders(message)
            if disorders:
                prompt = f"A user mentioned {disorders[0]}. Provide brief, supportive, empathetic advice."
                response = self._generate_response_gemini(prompt)

            if not response:
                symptoms = self.extract_symptoms(message)
                if symptoms:
                    prompt = f"A user mentioned symptoms: {', '.join(symptoms)}. Offer emotional support and suggestions."
                    response = self._generate_response_gemini(prompt)
                    self.session_context["reported_symptoms"].extend(symptoms)

            if not response:
                response = self._generate_response_gemini(message)

        except Exception as e:
            logger.error(f"Chat processing error: {e}")

        if not response:
            response = self._generate_fallback_response(message)

        self.session_context["session_history"].append({
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
        self.save_session()
        return response


chatbot_instance = MentalHealthChatbot(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


@router.post("/chat")
async def send_message(
    message_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user_message = ChatMessageModel(
            user_id=current_user.id,
            role="user",
            content=message_data.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)

        reply = chatbot_instance.chat(message_data.message)

        bot_message = ChatMessageModel(
            user_id=current_user.id,
            role="assistant",
            content=reply,
            timestamp=datetime.utcnow()
        )
        db.add(bot_message)
        db.commit()

        return {"message": reply}
    except Exception as e:
        db.rollback()
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.get("/chat/history")
async def get_my_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id
        ).order_by(ChatMessageModel.timestamp).all()
        return [{
            "role": m.role,
            "content": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages]
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve history")

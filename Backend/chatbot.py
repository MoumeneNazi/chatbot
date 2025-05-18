from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import GraphDatabase
import json
import os
import random
from datetime import datetime
from textblob import TextBlob
import groq
from dotenv import load_dotenv
from pydantic import BaseModel
from dependencies import get_current_user, check_user_role
from database import get_db
from sqlalchemy.orm import Session
from models import ChatMessageModel, User
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables for Groq API
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)
logger.info(f"Loading .env from: {env_path}")

router = APIRouter(
    prefix="/api",
    tags=["chat"]
)

# Get environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file. Please add it to Backend/.env")

groq_client = groq.Groq(api_key=GROQ_API_KEY)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")  # Default password if not in env

logger.info("Attempting to connect to Neo4j...")
try:
    # Test Neo4j connection
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        session.run("RETURN 1")
    driver.close()
    logger.info("Successfully connected to Neo4j")
except Exception as e:
    logger.error(f"Failed to connect to Neo4j: {str(e)}")

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def send_message(
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create user message
        user_message = ChatMessageModel(
            user_id=current_user.id,
            role="user",
            content=message,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        
        # TODO: Add chatbot response logic here
        bot_response = "I am here to help you. How are you feeling today?"
        
        # Create bot message
        bot_message = ChatMessageModel(
            user_id=current_user.id,
            role="assistant",
            content=bot_response,
            timestamp=datetime.utcnow()
        )
        db.add(bot_message)
        
        db.commit()
        return {"message": bot_response}
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.get("/chat/history")
async def get_chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Get all messages for the current user
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id
        ).order_by(ChatMessageModel.timestamp).all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@router.get("/chat/history/{user_id}")
async def get_user_chat_history(
    user_id: int,
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
    db: Session = Depends(get_db)
):
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == user_id
        ).order_by(ChatMessageModel.timestamp).all()
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

def ask_groq(message: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a mental health support system. Respond with specific, actionable guidance. Reference the user's exact words. Never use think blocks or meta-commentary."
                },
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        content = re.sub(r'<[^>]+>.*?</[^>]+>|\[.*?\]|\(.*?\)|thinking:|let me|I should|as an AI|as a chatbot', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content if content else "Could you tell me more about what's troubling you?"
    except Exception as e:
        logger.error(f"[Groq API Error]: {str(e)}")
        return "I'm here to listen. What's on your mind?"

class MentalHealthChatbot:
    def __init__(self, uri, user, password, memory_file="session_memory.json"):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            self.driver = None
            
        self.memory_file = memory_file
        self.session_context = self.load_session()
        self.symptom_list = self.load_symptom_list() if self.driver else []
        self.disorder_list = self.load_disorder_list() if self.driver else []

    def load_symptom_list(self):
        if not self.driver:
            return []
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (s:Symptom) RETURN s.name AS name")
                return [r["name"] for r in result]
        except Exception as e:
            logger.error(f"Error loading symptoms: {str(e)}")
            return []

    def load_disorder_list(self):
        if not self.driver:
            return []
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (d:Disorder) RETURN d.name AS name")
                return [r["name"] for r in result]
        except Exception as e:
            logger.error(f"Error loading disorders: {str(e)}")
            return []

    def load_session(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all required fields exist
                    return {
                        "reported_symptoms": data.get("reported_symptoms", []),
                        "session_history": data.get("session_history", []),
                        "last_interaction": data.get("last_interaction", None)
                    }
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
        
        # Return default structure if file doesn't exist or there's an error
        return {
            "reported_symptoms": [],
            "session_history": [],
            "last_interaction": None
        }

    def save_session(self):
        try:
            # Add timestamp to track last interaction
            self.session_context["last_interaction"] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.session_context, f, indent=4)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")

    def close(self):
        self.save_session()
        if self.driver:
            self.driver.close()

    def extract_symptoms(self, user_input):
        low = user_input.lower()
        return [name for name in self.symptom_list if name.lower() in low]

    def diagnose_disorders(self, symptoms):
        query = """
        MATCH (s:Symptom)-[:INDICATES]->(d:Disorder)
        WHERE s.name IN $symptoms
        RETURN d.name AS disorder, count(*) AS score
        ORDER BY score DESC
        """
        with self.driver.session() as session:
            result = session.run(query, symptoms=symptoms)
            preds, total = [], max(len(symptoms), 1)
            for r in result:
                preds.append((r["disorder"], min(100, (r["score"] / total) * 100)))
            return preds

    def add_journal_entry(self, entry, mood_rating):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session_context["journals"].append({
            "date": now,
            "entry": entry,
            "mood_rating": mood_rating
        })
        self.save_session()

    def get_journal_entries(self):
        return self.session_context["journals"]

    def detect_sentiment(self, text):
        return TextBlob(text).sentiment.polarity

    def chat(self, user_input):
        try:
            normalized_input = user_input.lower()
            logger.info(f"Processing chat input: {user_input}")
            
            # Add to session history
            self.session_context["session_history"].append({
                "user": user_input,
                "timestamp": datetime.now().isoformat()
            })

            # Process symptoms if Neo4j is available
            response = None
            if self.driver:
                # Check for disorders
                for disorder in self.disorder_list:
                    if disorder.lower() in normalized_input:
                        response = ask_groq(f"Provide specific information and support about {disorder}, focusing on symptoms, coping strategies, and when to seek professional help.")
                        break
                
                # Check for symptoms
                if not response:
                    found_symptoms = self.extract_symptoms(user_input)
                    if found_symptoms:
                        symptom_string = ", ".join(found_symptoms)
                        response = ask_groq(f"Address these specific symptoms: {symptom_string}. Provide practical coping strategies and explain when professional help might be needed.")
                        
                        # Track reported symptoms
                        self.session_context["reported_symptoms"].extend(found_symptoms)
            
            # If no specific response generated, use default handling
            if not response:
                response = ask_groq(user_input)
            
            # Add response to history
            self.session_context["session_history"].append({
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save session after each interaction
            self.save_session()
            
            return response

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return "I'm having trouble processing that. Could you rephrase?"

# Optional CLI
if __name__ == "__main__":
    # Ensure you have a .env file with your GROQ_API_KEY
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in .env file.")
    else:
        bot = MentalHealthChatbot(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        print("🤖 Hello! I'm here to support you. Type 'exit' to quit.\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Chatbot: Take care! 💙")
                break
            response = bot.chat(user_input)
            if response:
                print("Chatbot:", response)
            else:
                print("Chatbot: I'm having trouble connecting right now. Please try again later.")
        bot.close()




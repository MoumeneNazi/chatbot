from fastapi import APIRouter, Depends, HTTPException, status, Body
from neo4j import GraphDatabase
import json, os, logging, requests
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from dependencies import get_current_user
from database import get_db
from sqlalchemy.orm import Session
from models import ChatMessageModel, User, UserModel
from typing import List, Dict, Optional

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
            
            # Modify prompt to explicitly request short responses
            short_prompt = f"{prompt} Please provide a very brief response in 2-3 short sentences maximum."
            
            payload = {
                "contents": [
                    {"parts": [{"text": short_prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 150,  # Limit output length
                    "topP": 0.95
                }
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
            return "Hello! How are you feeling today?"
        if "depress" in msg_lower:
            return "I'm sorry you're feeling down. Would you like to share more about what's going on?"
        if any(x in msg_lower for x in ["anxious", "anxiety", "stress"]):
            return "Anxiety can be tough. Try deep breathing and remember that help is available."
        return "I'm here to listen. How can I support you today?"

    def chat(self, message: str) -> str:
        self.session_context["session_history"].append({
            "user": message,
            "timestamp": datetime.now().isoformat()
        })

        # Check if user is asking if the bot is a mental health assistant
        msg_lower = message.lower()
        if any(phrase in msg_lower for phrase in [
            "are you a mental health", "mental health assistant", 
            "mental health bot", "what are you", "who are you",
            "what do you do", "what is your purpose"
        ]):
            response = "I am a mental health assistant designed to provide support, information, and resources about mental well-being. I can discuss various mental health topics, symptoms, and disorders, but I'm not a replacement for professional mental health care. How can I help you today?"
            self.session_context["session_history"].append({
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            self.save_session()
            return response
            
        # Check if user is asking who created the bot
        if any(phrase in msg_lower for phrase in [
            "who made you", "who created you", "who developed you", 
            "who built you", "who programmed you", "who designed you",
            "who is your creator", "who are your creators", "your developer"
        ]):
            response = "I was created by a team of developers using various technologies including Python, FastAPI, Neo4j, React, and Google Gemini AI. My purpose is to provide mental health support and information."
            self.session_context["session_history"].append({
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            self.save_session()
            return response

        # Check if this is a mental health related question
        mental_health_terms = [
            "anxiety", "depression", "stress", "mental health", "therapy", 
            "counseling", "psychiatrist", "psychologist", "medication", 
            "panic attack", "trauma", "ptsd", "bipolar", "schizophrenia",
            "ocd", "adhd", "eating disorder", "phobia", "insomnia", "mood",
            "emotional", "suicide", "self-harm", "wellbeing", "coping", 
            "meditation", "mindfulness", "cognitive", "behavioral"
        ]
        
        if any(term in msg_lower for term in mental_health_terms):
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
                    prompt = f"The user is asking about mental health: {message}. Provide a supportive, informative response as a mental health assistant."
                    response = self._generate_response_gemini(prompt)

            except Exception as e:
                logger.error(f"Mental health response error: {e}")

            if not response:
                response = "I'm here to talk about mental health topics. While I can provide general information, remember I'm not a replacement for professional care. Would you like to discuss specific aspects of mental well-being?"

            self.session_context["session_history"].append({
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            self.save_session()
            return response

        # For messages not specifically about mental health or the bot's identity
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
            "message": m.content,
            "timestamp": m.timestamp.isoformat()
        } for m in messages]
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve history")

# Function to handle messages using external AI services
async def process_with_external_ai(message: str, conversation_history: List[Dict]) -> str:
    """Process a message using an external AI service like Gemini."""
    try:
        # Import necessary modules only when needed
        import google.generativeai as genai
        from groq import Groq
        
        # Try Gemini API first
        try:
            # Configure Gemini
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            
            # Create model instance
            model = genai.GenerativeModel('gemini-pro')
            
            # Get response from Gemini
            response = model.generate_content(
                [
                    {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
                    for msg in conversation_history
                ]
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error with Gemini API: {str(e)}")
            
            # Fallback to Groq API
            try:
                # Configure Groq
                groq_api_key = os.getenv("GROQ_API_KEY")
                client = Groq(api_key=groq_api_key)
                
                # Get response from Groq
                response = client.chat.completions.create(
                    messages=[
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in conversation_history
                    ],
                    model="llama3-70b-8192",
                    temperature=0.7,
                    max_tokens=800,
                )
                
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error with Groq API: {str(e)}")
                raise Exception("External AI services unavailable")
                
    except Exception as e:
        logger.error(f"Error with external AI services: {str(e)}")
        raise Exception("External AI services unavailable")

# Function to fall back to Neo4j knowledge base
async def process_with_knowledge_base(message: str) -> str:
    """Process a message using the local knowledge base when external AI services are unavailable."""
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Extract potential disorder mentions from the message
        disorder_query = """
        MATCH (d:Disorder)
        WHERE toLower($message) CONTAINS toLower(d.name)
        RETURN d.name AS disorder
        """
        
        disorders = []
        with driver.session() as session:
            result = session.run(disorder_query, message=message)
            disorders = [record["disorder"] for record in result]
        
        # If disorders found, get their symptoms
        if disorders:
            response_parts = ["Based on our knowledge base, I can provide some information:"]
            
            for disorder in disorders:
                symptom_query = """
                MATCH (d:Disorder {name: $disorder})-[:HAS_SYMPTOM]->(s:Symptom)
                RETURN s.name AS symptom
                """
                
                with driver.session() as session:
                    result = session.run(symptom_query, disorder=disorder)
                    symptoms = [record["symptom"] for record in result]
                
                if symptoms:
                    response_parts.append(f"\n\n{disorder} is typically associated with these symptoms:")
                    for symptom in symptoms:
                        response_parts.append(f"- {symptom}")
                else:
                    response_parts.append(f"\n\n{disorder} is in our database but we don't have detailed symptom information yet.")
            
            response_parts.append("\n\nPlease note that this information is not a substitute for professional medical advice.")
            return "\n".join(response_parts)
        
        # Check for symptom mentions if no disorders found
        symptom_query = """
        MATCH (s:Symptom)
        WHERE toLower($message) CONTAINS toLower(s.name)
        RETURN s.name AS symptom
        """
        
        symptoms = []
        with driver.session() as session:
            result = session.run(symptom_query, message=message)
            symptoms = [record["symptom"] for record in result]
        
        if symptoms:
            response_parts = ["I notice you mentioned some symptoms that could be associated with certain conditions:"]
            
            for symptom in symptoms:
                disorder_query = """
                MATCH (s:Symptom {name: $symptom})<-[:HAS_SYMPTOM]-(d:Disorder)
                RETURN d.name AS disorder
                """
                
                with driver.session() as session:
                    result = session.run(disorder_query, symptom=symptom)
                    related_disorders = [record["disorder"] for record in result]
                
                if related_disorders:
                    response_parts.append(f"\n\nThe symptom '{symptom}' is associated with:")
                    for disorder in related_disorders:
                        response_parts.append(f"- {disorder}")
                else:
                    response_parts.append(f"\n\nThe symptom '{symptom}' is in our database, but it's not linked to specific disorders yet.")
            
            response_parts.append("\n\nPlease remember this is based on our current knowledge base and not a substitute for professional advice.")
            return "\n".join(response_parts)
        
        # Generic response if no specific knowledge found
        return "I'm working with limited connectivity right now and couldn't find specific information about your query in our knowledge base. Could you try asking about a different mental health topic, or perhaps try again later when external services might be available?"
        
    except Exception as e:
        logger.error(f"Error with knowledge base fallback: {str(e)}")
        return "I'm currently operating with limited capabilities due to connection issues. I'll try to assist with what I know, but my responses will be more basic than usual."
    finally:
        if 'driver' in locals():
            driver.close()

@router.post("/")
async def chat(
    message_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a chat message using AI and store in database."""
    try:
        # Extract user message
        user_message = message_data.get("message", "").strip()
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Store user message in database
        user_chat_message = ChatMessageModel(
            user_id=current_user.id,
            content=user_message,
            role="user",
            timestamp=datetime.utcnow()
        )
        db.add(user_chat_message)
        db.commit()
        
        # Get conversation history (last 10 messages)
        history = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id
        ).order_by(ChatMessageModel.timestamp.desc()).limit(10).all()
        
        # Format history for AI model (reversed to be in chronological order)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(history)
        ]
        
        # Try to process with external AI first
        try:
            response_text = await process_with_external_ai(user_message, conversation_history)
        except Exception:
            # Fall back to knowledge base if external AI fails
            logger.info("External AI unavailable, falling back to knowledge base")
            response_text = await process_with_knowledge_base(user_message)
        
        # Store assistant response in database
        assistant_chat_message = ChatMessageModel(
            user_id=current_user.id,
            content=response_text,
            role="assistant",
            timestamp=datetime.utcnow()
        )
        db.add(assistant_chat_message)
        db.commit()
        
        return {"message": response_text}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user."""
    try:
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id
        ).order_by(ChatMessageModel.timestamp).all()
        
        return [
            {
                "id": msg.id,
                "content": msg.content,
                "role": msg.role,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chat history: {str(e)}"
        )

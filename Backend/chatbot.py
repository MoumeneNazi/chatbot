from fastapi import APIRouter, Depends, HTTPException, status
from neo4j import GraphDatabase
import json, os, logging
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from dependencies import get_current_user
from database import get_db
from sqlalchemy.orm import Session
from models import ChatMessageModel, User, UserModel
import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Initialize API router
router = APIRouter(prefix="/api", tags=["chat"])

# Load API keys and configurations
GEMINI_API_KEY = "AIzaSyAGcXvCDt5hlATBXeu5LAjSVkeqvCZ-MuA"
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Initialize Vertex AI
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Model Schema
class ChatMessage(BaseModel):
    message: str


class MentalHealthChatbot:
    """
    Mental Health Chatbot with Google Gemini integration and Neo4j knowledge base
    """
    def __init__(self, uri, user, password, memory_file="session_memory.json"):
        """Initialize the chatbot with Neo4j connection and load resources"""
        # Connect to Neo4j
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

        # Initialize Gemini model
        try:
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized successfully")
            self.gemini_available = True
        except Exception as e:
            logger.error(f"Gemini model initialization failed: {e}")
            self.gemini_available = False

        # Initialize session and knowledge
        self.memory_file = memory_file
        self.session_context = self.load_session()
        self.symptom_list = self.load_symptom_list() if self.neo4j_available else []
        self.disorder_list = self.load_disorder_list() if self.neo4j_available else []

    def load_symptom_list(self):
        """Load all symptoms from Neo4j database"""
        if not self.driver: 
            return []
        try:
            with self.driver.session() as s:
                return [r["name"] for r in s.run("MATCH (s:Symptom) RETURN s.name AS name")]
        except Exception as e:
            logger.error(f"Error loading symptoms: {e}")
            return []

    def load_disorder_list(self):
        """Load all mental health disorders from Neo4j database"""
        if not self.driver: 
            return []
        try:
            with self.driver.session() as s:
                return [r["name"] for r in s.run("MATCH (d:Disorder) RETURN d.name AS name")]
        except Exception as e:
            logger.error(f"Error loading disorders: {e}")
            return []

    def load_session(self):
        """Load previous session memory if available"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    return {
                        "reported_symptoms": data.get("reported_symptoms", []),
                        "session_history": data.get("session_history", []),
                        "last_interaction": data.get("last_interaction", None)
                    }
            except Exception as e:
                logger.warning(f"Session load error: {e}")
                return self._create_empty_session()
        return self._create_empty_session()

    def _create_empty_session(self):
        """Create a new empty session"""
        return {
            "reported_symptoms": [],
            "session_history": [],
            "last_interaction": None
        }

    def save_session(self):
        """Save the current session to disk"""
        try:
            self.session_context["last_interaction"] = datetime.now().isoformat()
            with open(self.memory_file, "w") as f:
                json.dump(self.session_context, f, indent=2)
        except Exception as e:
            logger.error(f"Failed saving session: {e}")

    def extract_symptoms(self, text):
        """Extract symptoms from user message based on the Neo4j knowledge base"""
        return [s for s in self.symptom_list if s.lower() in text.lower()]

    def find_disorders(self, text):
        """Find disorders mentioned in user message based on the Neo4j knowledge base"""
        return [d for d in self.disorder_list if d.lower() in text.lower()]

    def _generate_response_gemini(self, prompt):
        """Generate a response using Google Gemini API"""
        try:
            if not self.gemini_available:
                return None
                
            logger.info(f"Calling Gemini API with prompt: {prompt[:50]}...")
            
            # Add system prompt to guide the model's behavior
            system_prompt = "You are a supportive mental health chatbot. Respond directly with helpful and brief answers. Be empathetic and compassionate without unnecessary preambles."
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            # Generate response with Gemini
            response = self.model.generate_content(full_prompt)
            
            content = response.text.strip()
            logger.info(f"Gemini response received ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None

    def _generate_fallback_response(self, message):
        """Generate a fallback response when API is unavailable"""
        msg_lower = message.lower().strip()
        
        # Basic greeting detection
        if any(greeting in msg_lower for greeting in ["hey", "hi", "hello", "howdy", "greetings"]):
            return "Hello! I'm here to support you. How are you feeling today?"
        
        # Handle depression
        if "depress" in msg_lower:
            return "Depression can be challenging to deal with. Regular exercise, maintaining a routine, and speaking with a professional can help. Would you like to share more about how you're feeling?"
        
        # Handle anxiety
        if any(word in msg_lower for word in ["anxious", "anxiety", "worried", "stress", "panic"]):
            return "Anxiety can feel overwhelming. Deep breathing exercises, mindfulness, and speaking with a professional can be helpful. Remember that you're not alone in this experience."
        
        # Handle sleep issues
        if any(word in msg_lower for word in ["sleep", "insomnia", "tired", "exhausted", "fatigue"]):
            return "Sleep issues can affect our mental health. Try maintaining a regular sleep schedule, avoiding screens before bed, and creating a relaxing bedtime routine. If problems persist, consider speaking with a healthcare provider."
        
        # Handle crisis situations - prioritize these
        if any(word in msg_lower for word in ["help", "suicide", "kill myself", "die", "end it"]):
            return "I'm concerned about what you're sharing. Please reach out to a crisis support line immediately: National Suicide Prevention Lifeline at 988 or 1-800-273-8255, or text HOME to 741741 to reach the Crisis Text Line. Your life matters."
        
        # Handle therapy questions
        if any(word in msg_lower for word in ["therapy", "therapist", "counseling", "psychologist", "psychiatrist"]):
            return "Seeking therapy can be a positive step toward better mental health. Types include cognitive-behavioral therapy, psychodynamic therapy, and others. Would you like more information about finding a therapist?"
        
        # Default response
        return "I'm here to listen and support you. Would you like to tell me more about what you're experiencing?"

    def chat(self, message: str) -> str:
        """Process a user message and generate a response"""
        logger.info(f"Processing message: {message[:50]}...")
        
        # Record message in session history
        self.session_context["session_history"].append({
            "user": message, 
            "timestamp": datetime.now().isoformat()
        })
        
        # Initialize response
        response = None
        
        # Process with Neo4j knowledge if available
        if self.neo4j_available:
            try:
                # Check for mentioned disorders
                mentioned_disorders = self.find_disorders(message)
                if mentioned_disorders:
                    disorder = mentioned_disorders[0]  # Focus on the first mentioned disorder
                    prompt = f"A user mentioned {disorder}. Provide supportive information and brief tips for managing this condition. Be empathetic and direct."
                    response = self._generate_response_gemini(prompt)
                    
                    # Fallback for disorders if API fails
                    if not response:
                        response = f"It sounds like you're mentioning {disorder}. This can be challenging to deal with. Would you like to share more about your experience with {disorder}? Remember that professional help is often important for managing this condition effectively."
                
                # If no disorders found, check for symptoms
                if not response:
                    symptoms = self.extract_symptoms(message)
                    if symptoms:
                        prompt = f"A user mentioned these symptoms: {', '.join(symptoms)}. Provide supportive information and suggestions, while encouraging professional help if needed. Be empathetic and direct."
                        response = self._generate_response_gemini(prompt)
                        
                        # Fallback for symptoms if API fails
                        if not response:
                            response = f"I notice you mentioned symptoms like {', '.join(symptoms)}. These symptoms can be associated with various conditions. It's important to discuss these with a healthcare provider for proper evaluation. Would you like to share more about when these symptoms occur?"
                        
                        # Track reported symptoms
                        self.session_context["reported_symptoms"].extend(symptoms)
            except Exception as e:
                logger.error(f"Error in Neo4j knowledge processing: {e}")
        
        # If no response generated yet, use general API response
        if not response:
            response = self._generate_response_gemini(message)
        
        # If API call failed, use fallback
        if not response:
            response = self._generate_fallback_response(message)
        
        # Save response in session history
        self.session_context["session_history"].append({
            "assistant": response, 
            "timestamp": datetime.now().isoformat()
        })
        
        # Persist session
        self.save_session()
        
        return response


# Create chatbot instance
chatbot_instance = MentalHealthChatbot(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


@router.post("/chat")
async def send_message(
    message_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a message from the user and return a chatbot response"""
    try:
        # Record user message in database
        user_message = ChatMessageModel(
            user_id=current_user.id, 
            role="user", 
            content=message_data.message, 
            timestamp=datetime.utcnow()
        )
        db.add(user_message)

        # Get response from chatbot
        bot_reply = chatbot_instance.chat(message_data.message)

        # Record bot response in database
        bot_message = ChatMessageModel(
            user_id=current_user.id, 
            role="assistant", 
            content=bot_reply, 
            timestamp=datetime.utcnow()
        )
        db.add(bot_message)
        db.commit()

        return {"message": bot_reply}
    except Exception as e:
        db.rollback()
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.get("/chat/history")
async def get_my_history(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get the chat history for the current user"""
    try:
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == current_user.id
        ).order_by(ChatMessageModel.timestamp).all()
        
        return [
            {
                "role": m.role, 
                "content": m.content, 
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve chat history")


@router.get("/chat/history/{user_id}")
async def get_user_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the chat history for a specific user (for therapists only)"""
    # Check therapist access
    if current_user.role != "therapist":
        raise HTTPException(
            status_code=403, 
            detail="Only therapists can access other users' chat history"
        )
    
    # Verify user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        messages = db.query(ChatMessageModel).filter(
            ChatMessageModel.user_id == user_id
        ).order_by(ChatMessageModel.timestamp).all()
        
        return [
            {
                "role": m.role, 
                "content": m.content, 
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    except Exception as e:
        logger.error(f"User history fetch error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user chat history")
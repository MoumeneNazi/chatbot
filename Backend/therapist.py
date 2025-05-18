from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, ChatMessage, UserModel
from journal_models import JournalEntry
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",  # Logs will be saved to 'app.log' in the current directory
    filemode="a",  # Append to the file instead of overwriting
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter(
    prefix="/api/therapist",
    tags=["therapist"]
)

async def get_current_therapist(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is a therapist."""
    if current_user.role != "therapist":
        logging.debug(f"Access denied for user: {current_user.username}, Role: {current_user.role}")
        raise HTTPException(status_code=403, detail="Access forbidden: Therapists only.")
    return current_user

@router.get("/chat/{username}")
async def get_user_chat(
    username: str,
    current_user: User = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific user (therapist only)."""
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        messages = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).order_by(ChatMessage.timestamp).all()
        return [
            {
                "role": msg.role,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    except Exception as e:
        logging.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@router.get("/journal/{username}")
async def get_user_journal(
    username: str,
    current_user: User = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Get journal entries for a specific user (therapist only)."""
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).order_by(JournalEntry.timestamp).all()
        return [
            {
                "entry": e.entry,
                "sentiment": e.sentiment,
                "timestamp": e.timestamp.isoformat()
            }
            for e in entries
        ]
    except Exception as e:
        logging.error(f"Error fetching journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch journal entries")

@router.get("/users")
async def list_users(current_user: User = Depends(get_current_therapist), db: Session = Depends(get_db)):
    """Get all users (therapist only)."""
    try:
        users = db.query(UserModel).all()
        logging.debug(f"Retrieved users: {[u.username for u in users]}")
        return [{"username": u.username, "role": u.role} for u in users]
    except Exception as e:
        logging.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.put("/promote/{username}")
async def promote_user(
    username: str, 
    current_user: User = Depends(get_current_therapist), 
    db: Session = Depends(get_db)
):
    """Promote a user to therapist role (therapist only)."""
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logging.debug(f"Promoting user: {username}, Current Role: {user.role}")
        user.role = "therapist"
        db.commit()
        db.refresh(user)
        logging.debug(f"User {username} promoted successfully. New Role: {user.role}")
        return {"msg": f"{username} has been promoted to therapist"}
    except Exception as e:
        logging.error(f"Error promoting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to promote user")

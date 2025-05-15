from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, ChatMessage, JournalEntry
from auth import get_current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",  # Logs will be saved to 'app.log' in the current directory
    filemode="a",  # Append to the file instead of overwriting
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_therapist(token: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Ensure the current user is a therapist."""
    user = get_current_user(token, db)
    if user.role != "therapist":
        logging.debug(f"Access denied for user: {user.username}, Role: {user.role}")
        raise HTTPException(status_code=403, detail="Access forbidden: Therapists only.")
    return user

@router.get("/admin/chat/{username}")
def get_user_chat(username: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.username == username).first()
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

@router.get("/admin/journal/{username}")
def get_user_journal(username: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.username == username).first()
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

@router.put("/admin/promote/{username}")
def promote_user(username: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    logging.debug(f"Current user: {current_user.username}, Role: {current_user.role}")
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logging.debug(f"Promoting user: {username}, Current Role: {user.role}")
    user.role = "therapist"
    db.commit()
    db.refresh(user)  # Ensure the user object is updated
    logging.debug(f"User {username} promoted successfully. New Role: {user.role}")
    return {"msg": f"{username} has been promoted to therapist"}

@router.get("/admin/users")
def list_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    logging.debug(f"Listing users for: {current_user.username}, Role: {current_user.role}")
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")

    users = db.query(User).all()
    logging.debug(f"Retrieved users: {[u.username for u in users]}")
    return [{"username": u.username, "role": u.role} for u in users]

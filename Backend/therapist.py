from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, ChatMessage
from auth import get_current_user
from models import JournalEntry


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def promote_to_therapist(username: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Only therapists can promote others.")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = "therapist"
    db.commit()
    return {"message": f"{username} has been promoted to therapist."}

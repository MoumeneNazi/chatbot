from fastapi import APIRouter, Depends, HTTPException
from models import User, JournalModel, TreatmentProgressModel
from dependencies import require_role
from database import get_journal_by_username, get_db
from sqlalchemy.orm import Session
from datetime import datetime
from textblob import TextBlob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",  # Add prefix to match frontend expectations
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)

@router.get("/journal/{username}")
def get_journal(username: str, current_user: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    """Get a user's journal entries. Only accessible by therapists (admins)."""
    logger.info(f"Admin {current_user.username} requesting journal for user {username}")
    journal = get_journal_by_username(username, db)
    if not journal:
        raise HTTPException(status_code=404, detail="No journal found")
    return journal

@router.post("/journal/entry")
def create_journal_entry(entry: str, mood_rating: int, current_user: User = Depends(require_role("user")), db: Session = Depends(get_db)):
    """Create a new journal entry for the current user."""
    try:
        # Calculate sentiment score
        sentiment = TextBlob(entry).sentiment.polarity
        
        journal_entry = JournalModel(
            user_id=current_user.id,
            entry=entry,
            mood_rating=mood_rating,
            sentiment_score=sentiment
        )
        db.add(journal_entry)
        db.commit()
        return {"message": "Journal entry created successfully"}
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create journal entry")

@router.get("/journal/entries")
def get_journal_entries(current_user: User = Depends(require_role("user")), db: Session = Depends(get_db)):
    """Get all journal entries for the current user."""
    try:
        entries = db.query(JournalModel).filter(
            JournalModel.user_id == current_user.id
        ).order_by(JournalModel.timestamp.desc()).all()
        
        return [
            {
                "id": entry.id,
                "entry": entry.entry,
                "mood_rating": entry.mood_rating,
                "sentiment_score": entry.sentiment_score,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in entries
        ]
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch journal entries")

@router.post("/treatment/progress")
def add_treatment_progress(
    user_id: int,
    notes: str,
    treatment_plan: str,
    progress_status: str,
    current_user: User = Depends(require_role("therapist")),
    db: Session = Depends(get_db)
):
    """Add treatment progress for a user (therapist only)."""
    try:
        progress = TreatmentProgressModel(
            user_id=user_id,
            therapist_id=current_user.id,
            notes=notes,
            treatment_plan=treatment_plan,
            progress_status=progress_status
        )
        db.add(progress)
        db.commit()
        return {"message": "Treatment progress added successfully"}
    except Exception as e:
        logger.error(f"Error adding treatment progress: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add treatment progress")

@router.get("/treatment/progress/{user_id}")
def get_treatment_progress(
    user_id: int,
    current_user: User = Depends(require_role("therapist")),
    db: Session = Depends(get_db)
):
    """Get treatment progress for a user (therapist only)."""
    try:
        progress = db.query(TreatmentProgressModel).filter(
            TreatmentProgressModel.user_id == user_id
        ).order_by(TreatmentProgressModel.timestamp.desc()).all()
        
        return [
            {
                "id": p.id,
                "notes": p.notes,
                "treatment_plan": p.treatment_plan,
                "progress_status": p.progress_status,
                "timestamp": p.timestamp.isoformat()
            }
            for p in progress
        ]
    except Exception as e:
        logger.error(f"Error fetching treatment progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch treatment progress")

@router.get("/my/treatment/progress")
def get_my_treatment_progress(current_user: User = Depends(require_role("user")), db: Session = Depends(get_db)):
    """Get treatment progress for the current user."""
    try:
        progress = db.query(TreatmentProgressModel).filter(
            TreatmentProgressModel.user_id == current_user.id
        ).order_by(TreatmentProgressModel.timestamp.desc()).all()
        
        return [
            {
                "id": p.id,
                "notes": p.notes,
                "treatment_plan": p.treatment_plan,
                "progress_status": p.progress_status,
                "timestamp": p.timestamp.isoformat()
            }
            for p in progress
        ]
    except Exception as e:
        logger.error(f"Error fetching treatment progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch treatment progress")
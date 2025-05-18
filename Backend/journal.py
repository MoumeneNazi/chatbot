from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from dependencies import check_user_role
from sqlalchemy.orm import Session
from datetime import datetime
from textblob import TextBlob
import logging
from journal_models import (
    JournalEntryModel, 
    JournalEntryCreate, 
    JournalEntry,
    TreatmentProgressModel,
    TreatmentProgressCreate,
    TreatmentProgress
)
from journal_database import get_journal_db
from database import get_db
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["journal"],
    responses={404: {"description": "Not found"}}
)

@contextmanager
def managed_db_session(db: Session):
    """Context manager for database sessions to ensure proper cleanup."""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@router.get("/journal")
async def get_journal_entries(
    current_user: User = Depends(lambda user: check_user_role(user, "user")),
    journal_db: Session = Depends(get_journal_db)
):
    """Get journal entries for the current user."""
    try:
        with managed_db_session(journal_db):
            entries = journal_db.query(JournalEntryModel).filter(
                JournalEntryModel.user_id == current_user.id
            ).order_by(JournalEntryModel.timestamp.desc()).all()
            
            return [
                {
                    "id": entry.id,
                    "entry": entry.entry,
                    "mood_rating": entry.mood_rating,
                    "sentiment": entry.sentiment,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in entries
            ]
    except Exception as e:
        logger.error(f"Error fetching journal entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch journal entries: {str(e)}"
        )

@router.post("/journal")
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    current_user: User = Depends(lambda user: check_user_role(user, "user")),
    journal_db: Session = Depends(get_journal_db)
):
    """Create a new journal entry."""
    try:
        with managed_db_session(journal_db):
            # Calculate sentiment using TextBlob
            sentiment = TextBlob(entry_data.entry).sentiment.polarity
            
            entry = JournalEntryModel(
                user_id=current_user.id,
                entry=entry_data.entry,
                mood_rating=entry_data.mood_rating,
                sentiment=sentiment,
                timestamp=datetime.utcnow()
            )
            journal_db.add(entry)
            journal_db.flush()
            
            return {
                "id": entry.id,
                "entry": entry.entry,
                "mood_rating": entry.mood_rating,
                "sentiment": entry.sentiment,
                "timestamp": entry.timestamp.isoformat()
            }
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create journal entry: {str(e)}"
        )

@router.get("/journal/{user_id}")
async def get_user_journal_entries(
    user_id: int,
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
    journal_db: Session = Depends(get_journal_db),
    main_db: Session = Depends(get_db)
):
    """Get journal entries for a specific user (therapist only)."""
    try:
        with managed_db_session(journal_db):
            # Verify user exists
            user = main_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )
            
            entries = journal_db.query(JournalEntryModel).filter(
                JournalEntryModel.user_id == user_id
            ).order_by(JournalEntryModel.timestamp.desc()).all()
            
            return [
                {
                    "id": entry.id,
                    "entry": entry.entry,
                    "mood_rating": entry.mood_rating,
                    "sentiment": entry.sentiment,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in entries
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user journal entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch journal entries: {str(e)}"
        )

@router.post("/treatment/progress", response_model=TreatmentProgress)
async def add_treatment_progress(
    progress_data: TreatmentProgressCreate,
    user_id: int,
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
    journal_db: Session = Depends(get_journal_db),
    main_db: Session = Depends(get_db)
):
    """Add treatment progress for a user (therapist only)."""
    try:
        with managed_db_session(journal_db):
            # Verify user exists
            user = main_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )
            
            progress = TreatmentProgressModel(
                user_id=user_id,
                therapist_id=current_user.id,
                notes=progress_data.notes,
                treatment_plan=progress_data.treatment_plan,
                progress_status=progress_data.progress_status
            )
            journal_db.add(progress)
            journal_db.flush()
            
            return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding treatment progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add treatment progress: {str(e)}"
        )

@router.get("/treatment/progress/{user_id}", response_model=list[TreatmentProgress])
async def get_treatment_progress(
    user_id: int,
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
    journal_db: Session = Depends(get_journal_db),
    main_db: Session = Depends(get_db)
):
    """Get treatment progress for a user (therapist only)."""
    try:
        with managed_db_session(journal_db):
            # Verify user exists
            user = main_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )
            
            progress = journal_db.query(TreatmentProgressModel).filter(
                TreatmentProgressModel.user_id == user_id
            ).order_by(TreatmentProgressModel.timestamp.desc()).all()
            
            return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching treatment progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch treatment progress: {str(e)}"
        )

@router.get("/my/treatment/progress", response_model=list[TreatmentProgress])
async def get_my_treatment_progress(
    current_user: User = Depends(lambda user: check_user_role(user, "user")), 
    journal_db: Session = Depends(get_journal_db)
):
    """Get treatment progress for the current user."""
    try:
        with managed_db_session(journal_db):
            progress = journal_db.query(TreatmentProgressModel).filter(
                TreatmentProgressModel.user_id == current_user.id
            ).order_by(TreatmentProgressModel.timestamp.desc()).all()
            
            return progress
    except Exception as e:
        logger.error(f"Error fetching treatment progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch treatment progress: {str(e)}"
        )
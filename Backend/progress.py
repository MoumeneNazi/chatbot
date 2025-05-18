from fastapi import APIRouter, Depends, HTTPException, status
from models import User
from dependencies import check_user_role
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from journal_models import (
    JournalEntryModel,
    TreatmentProgressModel
)
from journal_database import get_journal_db
from database import get_db
from textblob import TextBlob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["progress"],
    responses={404: {"description": "Not found"}}
)

@router.get("/progress")
async def get_progress(
    current_user: User = Depends(lambda user: check_user_role(user, "user")),
    journal_db: Session = Depends(get_journal_db)
):
    """Get progress data for the current user."""
    try:
        # Get journal entries from the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        entries = journal_db.query(JournalEntryModel).filter(
            JournalEntryModel.user_id == current_user.id,
            JournalEntryModel.timestamp >= thirty_days_ago
        ).order_by(JournalEntryModel.timestamp).all()

        # Get treatment progress
        treatment_progress = journal_db.query(TreatmentProgressModel).filter(
            TreatmentProgressModel.user_id == current_user.id,
            TreatmentProgressModel.timestamp >= thirty_days_ago
        ).order_by(TreatmentProgressModel.timestamp).all()

        # Calculate mood trends
        mood_data = []
        sentiment_data = []
        for entry in entries:
            mood_data.append({
                "date": entry.timestamp.isoformat(),
                "value": entry.mood_rating
            })
            sentiment_data.append({
                "date": entry.timestamp.isoformat(),
                "value": entry.sentiment
            })

        # Format treatment progress
        progress_data = []
        for progress in treatment_progress:
            progress_data.append({
                "date": progress.timestamp.isoformat(),
                "notes": progress.notes,
                "treatment_plan": progress.treatment_plan,
                "progress_status": progress.progress_status
            })

        return {
            "mood_trends": mood_data,
            "sentiment_trends": sentiment_data,
            "treatment_progress": progress_data,
            "total_entries": len(entries),
            "average_mood": sum(entry.mood_rating for entry in entries) / len(entries) if entries else 0,
            "average_sentiment": sum(entry.sentiment for entry in entries) / len(entries) if entries else 0
        }
    except Exception as e:
        logger.error(f"Error fetching progress data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch progress data: {str(e)}"
        )

@router.get("/progress/{user_id}")
async def get_user_progress(
    user_id: int,
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
    journal_db: Session = Depends(get_journal_db),
    main_db: Session = Depends(get_db)
):
    """Get progress data for a specific user (therapist only)."""
    try:
        # Verify user exists
        user = main_db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )

        # Get journal entries from the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        entries = journal_db.query(JournalEntryModel).filter(
            JournalEntryModel.user_id == user_id,
            JournalEntryModel.timestamp >= thirty_days_ago
        ).order_by(JournalEntryModel.timestamp).all()

        # Get treatment progress
        treatment_progress = journal_db.query(TreatmentProgressModel).filter(
            TreatmentProgressModel.user_id == user_id,
            TreatmentProgressModel.timestamp >= thirty_days_ago
        ).order_by(TreatmentProgressModel.timestamp).all()

        # Calculate mood trends
        mood_data = []
        sentiment_data = []
        for entry in entries:
            mood_data.append({
                "date": entry.timestamp.isoformat(),
                "value": entry.mood_rating
            })
            sentiment_data.append({
                "date": entry.timestamp.isoformat(),
                "value": entry.sentiment
            })

        # Format treatment progress
        progress_data = []
        for progress in treatment_progress:
            progress_data.append({
                "date": progress.timestamp.isoformat(),
                "notes": progress.notes,
                "treatment_plan": progress.treatment_plan,
                "progress_status": progress.progress_status
            })

        return {
            "mood_trends": mood_data,
            "sentiment_trends": sentiment_data,
            "treatment_progress": progress_data,
            "total_entries": len(entries),
            "average_mood": sum(entry.mood_rating for entry in entries) / len(entries) if entries else 0,
            "average_sentiment": sum(entry.sentiment for entry in entries) / len(entries) if entries else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user progress data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch progress data: {str(e)}"
        ) 
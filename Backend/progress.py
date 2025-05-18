from fastapi import APIRouter, Depends, HTTPException, status
from models import User, UserModel
from dependencies import check_user_role, get_current_user
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from journal_models import (
    JournalEntryModel,
    TreatmentProgressModel,
    DisorderTreatmentModel
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
    current_user: User = Depends(get_current_user),
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

        # Get active disorder treatments
        disorder_treatments = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.user_id == current_user.id,
            DisorderTreatmentModel.status == "Active"
        ).all()

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
                "value": entry.sentiment_score if hasattr(entry, 'sentiment_score') else 0
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

        # Format disorder treatments
        treatment_data = []
        for treatment in disorder_treatments:
            treatment_data.append({
                "id": treatment.id,
                "disorder": treatment.disorder,
                "treatment_plan": treatment.treatment_plan,
                "duration_weeks": treatment.duration_weeks,
                "status": treatment.status,
                "start_date": treatment.created_at.isoformat(),
                "last_updated": treatment.updated_at.isoformat()
            })

        return {
            "mood_trends": mood_data,
            "sentiment_trends": sentiment_data,
            "treatment_progress": progress_data,
            "disorder_treatments": treatment_data,
            "total_entries": len(entries),
            "average_mood": sum(entry.mood_rating for entry in entries) / len(entries) if entries else 0,
            "average_sentiment": sum(entry.sentiment_score if hasattr(entry, 'sentiment_score') else 0 for entry in entries) / len(entries) if entries else 0
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
    current_user: User = Depends(get_current_user),
    journal_db: Session = Depends(get_journal_db),
    main_db: Session = Depends(get_db)
):
    """Get progress data for a specific user (therapist only)."""
    try:
        # Verify user is a therapist
        if current_user.role != "therapist":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only therapists can access this endpoint"
            )
        
        # Verify user exists
        user = main_db.query(UserModel).filter(UserModel.id == user_id).first()
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

        # Get all disorder treatments (active and completed)
        disorder_treatments = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.user_id == user_id
        ).order_by(DisorderTreatmentModel.created_at.desc()).all()

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
                "value": entry.sentiment_score if hasattr(entry, 'sentiment_score') else 0
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

        # Format disorder treatments
        treatment_data = []
        for treatment in disorder_treatments:
            treatment_data.append({
                "id": treatment.id,
                "disorder": treatment.disorder,
                "treatment_plan": treatment.treatment_plan,
                "duration_weeks": treatment.duration_weeks,
                "status": treatment.status,
                "start_date": treatment.created_at.isoformat(),
                "last_updated": treatment.updated_at.isoformat()
            })

        return {
            "mood_trends": mood_data,
            "sentiment_trends": sentiment_data,
            "treatment_progress": progress_data,
            "disorder_treatments": treatment_data,
            "total_entries": len(entries),
            "average_mood": sum(entry.mood_rating for entry in entries) / len(entries) if entries else 0,
            "average_sentiment": sum(entry.sentiment_score if hasattr(entry, 'sentiment_score') else 0 for entry in entries) / len(entries) if entries else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user progress data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch progress data: {str(e)}"
        )

@router.get("/treatments")
async def get_user_treatments(
    current_user: User = Depends(get_current_user),
    journal_db: Session = Depends(get_journal_db)
):
    """Get all treatments for the current user."""
    try:
        # Get all disorder treatments
        treatments = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.user_id == current_user.id
        ).order_by(DisorderTreatmentModel.created_at.desc()).all()
        
        return [
            {
                "id": t.id,
                "disorder": t.disorder,
                "treatment_plan": t.treatment_plan,
                "duration_weeks": t.duration_weeks,
                "status": t.status,
                "start_date": t.created_at.isoformat(),
                "end_date": (t.created_at + timedelta(weeks=t.duration_weeks)).isoformat(),
                "progress_percentage": calculate_progress_percentage(t)
            }
            for t in treatments
        ]
    except Exception as e:
        logger.error(f"Error fetching user treatments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch treatments: {str(e)}"
        )

def calculate_progress_percentage(treatment):
    """Calculate the progress percentage of a treatment based on time elapsed."""
    if treatment.status == "Completed":
        return 100
    
    if treatment.status == "Canceled":
        return 0
    
    # Calculate based on time elapsed vs total duration
    start_date = treatment.created_at
    end_date = start_date + timedelta(weeks=treatment.duration_weeks)
    now = datetime.utcnow()
    
    # If treatment has ended but status is still active
    if now > end_date:
        return 100
    
    total_duration = (end_date - start_date).total_seconds()
    elapsed_duration = (now - start_date).total_seconds()
    
    return min(round((elapsed_duration / total_duration) * 100), 100) 
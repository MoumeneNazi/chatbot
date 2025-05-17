from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, ReviewModel, Review
from database import get_db
from dependencies import require_role
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",  # Add prefix to match frontend expectations
    tags=["reviews"],
    responses={404: {"description": "Not found"}}
)

@router.get("/reviews", response_model=List[Review])
def get_reviews(
    disorder: str = None,
    user_id: int = None,
    current_user: User = Depends(require_role(["user", "therapist"])),
    db: Session = Depends(get_db)
):
    """Get reviews with optional filters."""
    try:
        query = db.query(ReviewModel)
        
        # Apply filters
        if disorder and disorder != 'all':
            query = query.filter(ReviewModel.disorder == disorder)
        if user_id:
            query = query.filter(ReviewModel.user_id == user_id)
        elif current_user.role == "user":
            # Users can only see their own reviews
            query = query.filter(ReviewModel.user_id == current_user.id)
            
        reviews = query.order_by(ReviewModel.timestamp.desc()).all()
        
        # Add therapist names to reviews
        result = []
        for review in reviews:
            therapist = db.query(User).filter(User.id == review.therapist_id).first()
            review_dict = Review.model_validate(review).model_dump()
            review_dict["therapist_name"] = therapist.username if therapist else None
            result.append(review_dict)
            
        return result
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@router.post("/reviews")
def create_review(
    title: str,
    content: str,
    disorder: str,
    specialty: str,
    user_id: int,
    current_user: User = Depends(require_role("therapist")),
    db: Session = Depends(get_db)
):
    """Create a new review. Only accessible by therapists."""
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        review = ReviewModel(
            title=title,
            content=content,
            disorder=disorder,
            specialty=specialty,
            user_id=user_id,
            therapist_id=current_user.id
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return {"message": "Review created successfully", "id": review.id}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create review")

@router.get("/users")
def get_users(current_user: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    """Get all users. Only accessible by therapists."""
    try:
        users = db.query(User).filter(User.role == "user").all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users") 
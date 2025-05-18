from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, ReviewModel, Review
from database import get_db
from dependencies import check_user_role
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
    current_user: User = Depends(lambda user: check_user_role(user, ["user", "therapist"])),
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
    current_user: User = Depends(lambda user: check_user_role(user, "therapist")),
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
def get_users(current_user: User = Depends(lambda user: check_user_role(user, "therapist")), db: Session = Depends(get_db)):
    """Get all users. Only accessible by therapists."""
    try:
        users = db.query(User).filter(User.role == "user").all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.get("/symptoms")
def get_symptoms(
    disorder: str = None,
    current_user: User = Depends(lambda user: check_user_role(user, ["user", "therapist"])),
    db: Session = Depends(get_db)
):
    """Get symptoms with optional disorder filter."""
    try:
        # Define common symptoms for each disorder
        symptoms_map = {
            "Anxiety": [
                {"name": "Excessive worry"},
                {"name": "Restlessness"},
                {"name": "Difficulty concentrating"},
                {"name": "Sleep problems"},
                {"name": "Muscle tension"}
            ],
            "Depression": [
                {"name": "Persistent sadness"},
                {"name": "Loss of interest"},
                {"name": "Changes in appetite"},
                {"name": "Sleep disturbances"},
                {"name": "Fatigue"}
            ],
            "Generalized Anxiety Disorder": [
                {"name": "Chronic worry"},
                {"name": "Difficulty controlling worry"},
                {"name": "Physical tension"},
                {"name": "Sleep disturbances"},
                {"name": "Irritability"}
            ],
            "Major Depressive Disorder": [
                {"name": "Severe depression"},
                {"name": "Hopelessness"},
                {"name": "Loss of pleasure"},
                {"name": "Weight changes"},
                {"name": "Suicidal thoughts"}
            ],
            "Panic Disorder": [
                {"name": "Panic attacks"},
                {"name": "Fear of panic attacks"},
                {"name": "Avoidance behavior"},
                {"name": "Heart palpitations"},
                {"name": "Sweating"}
            ],
            "Bipolar Disorder": [
                {"name": "Mood swings"},
                {"name": "Manic episodes"},
                {"name": "Depressive episodes"},
                {"name": "Changes in energy"},
                {"name": "Impulsivity"}
            ],
            "Post-Traumatic Stress Disorder": [
                {"name": "Flashbacks"},
                {"name": "Nightmares"},
                {"name": "Avoidance"},
                {"name": "Hypervigilance"},
                {"name": "Emotional numbness"}
            ],
            "Obsessive-Compulsive Disorder": [
                {"name": "Intrusive thoughts"},
                {"name": "Compulsive behaviors"},
                {"name": "Anxiety about rituals"},
                {"name": "Time-consuming rituals"},
                {"name": "Distress when rituals interrupted"}
            ]
        }
        
        if disorder and disorder != 'all':
            return symptoms_map.get(disorder, [])
        
        # If no disorder specified or 'all' selected, return all symptoms
        all_symptoms = []
        for symptoms in symptoms_map.values():
            all_symptoms.extend(symptoms)
        return list({s['name']: s for s in all_symptoms}.values())  # Remove duplicates
        
    except Exception as e:
        logger.error(f"Error fetching symptoms: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch symptoms") 
from fastapi import APIRouter, Depends, HTTPException, Form, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import User, ReviewModel, Review, UserModel
from database import get_db
from dependencies import check_user_role, get_current_user
from typing import List, Optional
import logging
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Pydantic model for review creation
class ReviewCreate(BaseModel):
    title: str
    content: str
    disorder: str
    specialty: str
    user_id: int = Field(..., alias="user_id")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Assessment of Major Depressive Disorder",
                "content": "Patient exhibits symptoms consistent with Major Depressive Disorder...",
                "disorder": "Major Depressive Disorder",
                "specialty": "Clinical Psychology",
                "user_id": 1
            }
        }

router = APIRouter(
    prefix="/api",  # Add prefix to match frontend expectations
    tags=["reviews"],
    responses={404: {"description": "Not found"}}
)

@router.get("/reviews", response_model=List[Review])
def get_reviews(
    disorder: str = None,
    user_id: int = None,
    current_user: User = Depends(get_current_user),
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
            therapist = db.query(UserModel).filter(UserModel.id == review.therapist_id).first()
            review_dict = Review.model_validate(review).model_dump()
            review_dict["therapist_name"] = therapist.username if therapist else None
            result.append(review_dict)
            
        return result
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@router.post("/reviews")
async def create_review(
    review_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new review. Only accessible by therapists."""
    try:
        # Check if user is a therapist
        if current_user.role != "therapist":
            raise HTTPException(
                status_code=403,
                detail="Access forbidden. Only therapists can create reviews."
            )
        
        # Print the received data for debugging
        logger.info(f"Received review data: {review_data}")
        
        # Extract fields directly from the request body
        if not all(k in review_data for k in ["title", "content", "disorder", "specialty", "user_id"]):
            raise HTTPException(
                status_code=422,
                detail="Missing required fields. Please provide title, content, disorder, specialty, and user_id"
            )
            
        # Extract data
        title = review_data["title"]
        content = review_data["content"]
        disorder = review_data["disorder"]
        specialty = review_data["specialty"]
        user_id = review_data["user_id"]
            
        # Verify user exists
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        logger.info(f"Creating review for user {user_id} with title: {title}, disorder: {disorder}")
        
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
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")

@router.get("/users")
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users. Only accessible by therapists."""
    try:
        # Check if user is a therapist
        if current_user.role != "therapist":
            raise HTTPException(status_code=403, detail="Access forbidden. Only therapists can view all users.")
        
        # Query the UserModel instead of User (which is a Pydantic model)
        users = db.query(UserModel).filter(UserModel.role == "user").all()
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

def get_neo4j_connection():
    """Create and return a Neo4j driver instance."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test connection
        with driver.session() as session:
            session.run("RETURN 1")
        return driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {str(e)}")
        return None

@router.get("/symptoms")
def get_symptoms(
    disorder: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get symptoms with optional disorder filter."""
    try:
        driver = get_neo4j_connection()
        if not driver:
            raise HTTPException(status_code=500, detail="Database connection error")
            
        with driver.session() as session:
            if disorder and disorder != 'all':
                # Get symptoms for a specific disorder
                result = session.run(
                    """
                    MATCH (d:Disorder {name: $disorder})-[:HAS_SYMPTOM]->(s:Symptom)
                    RETURN s.name as name
                    """,
                    disorder=disorder
                )
                symptoms = [{"name": record["name"]} for record in result]
            else:
                # Get all symptoms
                result = session.run("MATCH (s:Symptom) RETURN DISTINCT s.name as name")
                symptoms = [{"name": record["name"]} for record in result]
                
        driver.close()
        return symptoms
    except Exception as e:
        logger.error(f"Error fetching symptoms: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch symptoms")

@router.get("/disorders")
def get_disorders(
    current_user: User = Depends(get_current_user)
):
    """Get all mental health disorders."""
    try:
        driver = get_neo4j_connection()
        if not driver:
            raise HTTPException(status_code=500, detail="Database connection error")
            
        with driver.session() as session:
            result = session.run("MATCH (d:Disorder) RETURN d.name as name")
            disorders = [{"name": record["name"]} for record in result]
                
        driver.close()
        return disorders
    except Exception as e:
        logger.error(f"Error fetching disorders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch disorders") 
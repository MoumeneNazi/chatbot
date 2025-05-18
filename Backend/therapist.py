from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, ChatMessage, UserModel
from journal_models import JournalEntry, DisorderTreatmentModel, DisorderTreatmentCreate
from journal_database import get_journal_db
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

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
        
        entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).order_by(JournalEntry.timestamp.desc()).all()
        return [
            {
                "id": e.id,
                "title": e.title if hasattr(e, 'title') else "Journal Entry",
                "content": e.entry,
                "mood": e.mood if hasattr(e, 'mood') else e.sentiment,
                "activities": e.activities if hasattr(e, 'activities') else [],
                "timestamp": e.timestamp.isoformat(),
                "user_id": e.user_id
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
        return [{"id": u.id, "username": u.username, "role": u.role} for u in users]
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

@router.get("/disorders")
async def get_disorders(
    current_user: User = Depends(get_current_therapist)
):
    """Get all mental health disorders from Neo4j."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("MATCH (d:Disorder) RETURN d.name AS name ORDER BY d.name")
            disorders = [record["name"] for record in result]
        driver.close()
        
        return disorders
    except Exception as e:
        logging.error(f"Error fetching disorders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch disorders")

@router.post("/treatment/{user_id}")
async def create_treatment(
    user_id: int,
    treatment: DisorderTreatmentCreate,
    current_user: User = Depends(get_current_therapist),
    main_db: Session = Depends(get_db),
    journal_db: Session = Depends(get_journal_db)
):
    """Create a treatment plan for a user's disorder."""
    try:
        # Verify user exists
        user = main_db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify disorder exists
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(
                "MATCH (d:Disorder {name: $name}) RETURN d.name", 
                name=treatment.disorder
            )
            if not result.single():
                driver.close()
                raise HTTPException(status_code=404, detail="Disorder not found")
        driver.close()
        
        # Create treatment
        new_treatment = DisorderTreatmentModel(
            user_id=user_id,
            therapist_id=current_user.id,
            disorder=treatment.disorder,
            treatment_plan=treatment.treatment_plan,
            duration_weeks=treatment.duration_weeks,
            status="Active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        journal_db.add(new_treatment)
        journal_db.commit()
        journal_db.refresh(new_treatment)
        
        return {
            "id": new_treatment.id,
            "user_id": new_treatment.user_id,
            "therapist_id": new_treatment.therapist_id,
            "disorder": new_treatment.disorder,
            "treatment_plan": new_treatment.treatment_plan,
            "duration_weeks": new_treatment.duration_weeks,
            "status": new_treatment.status,
            "created_at": new_treatment.created_at.isoformat(),
            "updated_at": new_treatment.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        journal_db.rollback()
        logging.error(f"Error creating treatment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create treatment: {str(e)}")

@router.get("/treatment/{user_id}")
async def get_treatments(
    user_id: int,
    current_user: User = Depends(get_current_therapist),
    main_db: Session = Depends(get_db),
    journal_db: Session = Depends(get_journal_db)
):
    """Get all treatments for a user."""
    try:
        # Verify user exists
        user = main_db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        treatments = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.user_id == user_id
        ).order_by(DisorderTreatmentModel.created_at.desc()).all()
        
        return [
            {
                "id": t.id,
                "user_id": t.user_id,
                "therapist_id": t.therapist_id,
                "disorder": t.disorder,
                "treatment_plan": t.treatment_plan,
                "duration_weeks": t.duration_weeks,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in treatments
        ]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching treatments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch treatments: {str(e)}")

@router.put("/treatment/{treatment_id}/status")
async def update_treatment_status(
    treatment_id: int,
    status: str = Body(..., embed=True),
    current_user: User = Depends(get_current_therapist),
    journal_db: Session = Depends(get_journal_db)
):
    """Update the status of a treatment (Active, Completed, Canceled)."""
    try:
        if status not in ["Active", "Completed", "Canceled"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'Active', 'Completed', or 'Canceled'.")
        
        treatment = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.id == treatment_id
        ).first()
        
        if not treatment:
            raise HTTPException(status_code=404, detail="Treatment not found")
        
        # Verify the therapist is authorized to update this treatment
        if treatment.therapist_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this treatment")
        
        treatment.status = status
        treatment.updated_at = datetime.utcnow()
        
        journal_db.commit()
        journal_db.refresh(treatment)
        
        return {
            "id": treatment.id,
            "user_id": treatment.user_id,
            "disorder": treatment.disorder,
            "status": treatment.status,
            "updated_at": treatment.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        journal_db.rollback()
        logging.error(f"Error updating treatment status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update treatment status: {str(e)}")

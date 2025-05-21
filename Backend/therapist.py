from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, ChatMessage, UserModel, TherapistApplicationModel, TherapistApplicationCreate, TherapistApplication
from journal_models import JournalEntry, DisorderTreatmentModel, DisorderTreatmentCreate
from journal_database import get_journal_db
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import shutil
from typing import Optional
import uuid

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

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_current_therapist(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is a therapist."""
    if current_user.role != "therapist":
        logging.debug(f"Access denied for user: {current_user.username}, Role: {current_user.role}")
        raise HTTPException(status_code=403, detail="Access forbidden: Therapists only.")
    return current_user

async def get_therapist_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is either a therapist or an admin."""
    if current_user.role not in ["therapist", "admin"]:
        logging.debug(f"Access denied for user: {current_user.username}, Role: {current_user.role}")
        raise HTTPException(status_code=403, detail="Access forbidden: Therapists and Admins only.")
    return current_user

@router.post("/apply", response_model=TherapistApplication)
async def apply_for_therapist(
    full_name: str = Form(...),
    email: str = Form(...),
    specialty: str = Form(...),
    license_number: str = Form(...),
    certification: str = Form(...),
    experience_years: int = Form(...),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an application to become a therapist."""
    try:
        # Check if user already has a pending application
        existing_application = db.query(TherapistApplicationModel).filter(
            TherapistApplicationModel.user_id == current_user.id,
            TherapistApplicationModel.status == "pending"
        ).first()
        
        if existing_application:
            raise HTTPException(
                status_code=400,
                detail="You already have a pending application"
            )
        
        # Handle document upload if provided
        document_path = None
        if document:
            # Create a unique filename
            file_extension = os.path.splitext(document.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            document_path = unique_filename
            
            # Save the file
            file_location = os.path.join(UPLOAD_DIR, unique_filename)
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(document.file, file_object)
        
        # Create application
        application = TherapistApplicationModel(
            user_id=current_user.id,
            full_name=full_name,
            email=email,
            specialty=specialty,
            license_number=license_number,
            certification=certification,
            experience_years=experience_years,
            document_path=document_path,
            status="pending"
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        return application
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating therapist application: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit application: {str(e)}"
        )

@router.get("/application/status")
async def get_application_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of the current user's therapist application."""
    try:
        application = db.query(TherapistApplicationModel).filter(
            TherapistApplicationModel.user_id == current_user.id
        ).order_by(TherapistApplicationModel.created_at.desc()).first()
        
        if not application:
            return {"status": "not_applied"}
        
        return {
            "status": application.status,
            "applied_at": application.created_at.isoformat(),
            "updated_at": application.updated_at.isoformat()
        }
    except Exception as e:
        logging.error(f"Error fetching application status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch application status: {str(e)}"
        )

@router.get("/applications", response_model=list[TherapistApplication])
async def list_applications(
    status: Optional[str] = None,
    current_user: User = Depends(get_therapist_or_admin),
    db: Session = Depends(get_db)
):
    """List all therapist applications (therapist and admin)."""
    try:
        query = db.query(TherapistApplicationModel)
        
        if status:
            query = query.filter(TherapistApplicationModel.status == status)
            
        applications = query.order_by(TherapistApplicationModel.created_at.desc()).all()
        return applications
    except Exception as e:
        logging.error(f"Error listing applications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list applications: {str(e)}"
        )

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str = Body(..., embed=True),
    current_user: User = Depends(get_therapist_or_admin),
    db: Session = Depends(get_db)
):
    """Update the status of a therapist application (therapist and admin)."""
    try:
        if status not in ["pending", "approved", "rejected"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be 'pending', 'approved', or 'rejected'"
            )
            
        application = db.query(TherapistApplicationModel).filter(
            TherapistApplicationModel.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        application.status = status
        application.updated_at = datetime.utcnow()
        
        # If approved, update user role
        if status == "approved":
            user = db.query(UserModel).filter(UserModel.id == application.user_id).first()
            if user:
                user.role = "therapist"
        
        db.commit()
        
        return {"message": f"Application status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating application status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update application status: {str(e)}"
        )

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

@router.post("/chat/{username}")
async def send_message_to_user(
    username: str,
    message_data: dict = Body(...),
    current_user: User = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Send a message to a user (therapist only)."""
    try:
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Record therapist message in database
        therapist_message = ChatMessageModel(
            user_id=user.id,
            role="therapist",
            content=message_data.get("message"),
            timestamp=datetime.utcnow()
        )
        db.add(therapist_message)
        db.commit()
        
        return {"message": message_data.get("message")}
    except Exception as e:
        db.rollback()
        logging.error(f"Error sending message to user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

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

@router.get("/disorders")
async def get_disorders(
    current_user: User = Depends(get_therapist_or_admin)
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
    """Update the status of a treatment plan (therapist only)."""
    try:
        if status not in ["Active", "Completed", "Canceled"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be 'Active', 'Completed', or 'Canceled'"
            )
            
        treatment = journal_db.query(DisorderTreatmentModel).filter(
            DisorderTreatmentModel.id == treatment_id
        ).first()
        
        if not treatment:
            raise HTTPException(status_code=404, detail="Treatment plan not found")
        
        treatment.status = status
        treatment.updated_at = datetime.utcnow()
        
        journal_db.commit()
        
        return {"message": f"Treatment status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        journal_db.rollback()
        logging.error(f"Error updating treatment status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update treatment status: {str(e)}"
        )

@router.post("/fix-document-paths")
async def fix_document_paths(
    current_user: User = Depends(get_current_therapist),
    db: Session = Depends(get_db)
):
    """Fix existing document paths by removing the 'uploads/' prefix."""
    try:
        # Find all applications with document paths that start with 'uploads/'
        applications = db.query(TherapistApplicationModel).filter(
            TherapistApplicationModel.document_path.like("uploads/%")
        ).all()
        
        fixed_count = 0
        for app in applications:
            # Extract just the filename
            filename = os.path.basename(app.document_path)
            app.document_path = filename
            fixed_count += 1
        
        db.commit()
        
        return {"message": f"Fixed {fixed_count} document paths"}
    except Exception as e:
        db.rollback()
        logging.error(f"Error fixing document paths: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fix document paths: {str(e)}"
        )

@router.get("/symptoms")
async def get_symptoms(
    disorder: Optional[str] = None,
    current_user: User = Depends(get_therapist_or_admin)
):
    """Get all symptoms or symptoms for a specific disorder."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            if disorder:
                # Get symptoms for a specific disorder
                result = session.run(
                    """
                    MATCH (d:Disorder {name: $disorder})-[:HAS_SYMPTOM]->(s:Symptom)
                    RETURN s.name AS name ORDER BY s.name
                    """,
                    disorder=disorder
                )
            else:
                # Get all symptoms
                result = session.run("MATCH (s:Symptom) RETURN s.name AS name ORDER BY s.name")
            
            symptoms = [record["name"] for record in result]
        driver.close()
        return symptoms
    except Exception as e:
        logging.error(f"Error fetching symptoms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch symptoms: {str(e)}")

@router.post("/disorders")
async def add_disorder(
    disorder_data: dict = Body(...),
    current_user: User = Depends(get_therapist_or_admin)
):
    """Add a new disorder to the knowledge base."""
    try:
        name = disorder_data.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="Disorder name is required")
        
        # Check if disorder already exists
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(
                "MATCH (d:Disorder {name: $name}) RETURN d.name",
                name=name
            )
            if result.single():
                driver.close()
                raise HTTPException(status_code=400, detail=f"Disorder '{name}' already exists")
            
            # Create disorder
            session.run(
                "CREATE (d:Disorder {name: $name})",
                name=name
            )
        driver.close()
        
        return {"message": f"Disorder '{name}' added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error adding disorder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add disorder: {str(e)}")

@router.post("/symptoms")
async def add_symptom(
    symptom_data: dict = Body(...),
    current_user: User = Depends(get_therapist_or_admin)
):
    """Add a new symptom and optionally associate it with disorder(s)."""
    try:
        name = symptom_data.get("name")
        disorders = symptom_data.get("disorders", [])
        
        if not name:
            raise HTTPException(status_code=400, detail="Symptom name is required")
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Create symptom
            session.run(
                "MERGE (s:Symptom {name: $name})",
                name=name
            )
            
            # Create relationships with disorders if provided
            for disorder in disorders:
                # Check if disorder exists
                result = session.run(
                    "MATCH (d:Disorder {name: $name}) RETURN d.name",
                    name=disorder
                )
                if not result.single():
                    continue  # Skip if disorder doesn't exist
                
                # Create relationship
                session.run(
                    """
                    MATCH (d:Disorder {name: $disorder})
                    MATCH (s:Symptom {name: $symptom})
                    MERGE (d)-[:HAS_SYMPTOM]->(s)
                    """,
                    disorder=disorder,
                    symptom=name
                )
        driver.close()
        
        if disorders:
            return {"message": f"Symptom '{name}' added and linked to {len(disorders)} disorders"}
        else:
            return {"message": f"Symptom '{name}' added successfully"}
    except Exception as e:
        logging.error(f"Error adding symptom: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add symptom: {str(e)}")

@router.post("/disorders/{disorder_name}/symptoms")
async def link_symptom_to_disorder(
    disorder_name: str,
    symptom_data: dict = Body(...),
    current_user: User = Depends(get_therapist_or_admin)
):
    """Link an existing symptom to a disorder or create a new symptom."""
    try:
        symptom_name = symptom_data.get("name")
        if not symptom_name:
            raise HTTPException(status_code=400, detail="Symptom name is required")
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Check if disorder exists
            disorder_result = session.run(
                "MATCH (d:Disorder {name: $name}) RETURN d.name",
                name=disorder_name
            )
            if not disorder_result.single():
                driver.close()
                raise HTTPException(status_code=404, detail=f"Disorder '{disorder_name}' not found")
            
            # Create symptom if it doesn't exist
            session.run(
                "MERGE (s:Symptom {name: $name})",
                name=symptom_name
            )
            
            # Create relationship
            session.run(
                """
                MATCH (d:Disorder {name: $disorder})
                MATCH (s:Symptom {name: $symptom})
                MERGE (d)-[:HAS_SYMPTOM]->(s)
                """,
                disorder=disorder_name,
                symptom=symptom_name
            )
        driver.close()
        
        return {"message": f"Symptom '{symptom_name}' linked to disorder '{disorder_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error linking symptom to disorder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to link symptom to disorder: {str(e)}")

@router.delete("/disorders/{disorder_name}")
async def delete_disorder(
    disorder_name: str,
    current_user: User = Depends(get_therapist_or_admin)
):
    """Delete a disorder from the knowledge base."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Check if disorder exists
            disorder_result = session.run(
                "MATCH (d:Disorder {name: $name}) RETURN d.name",
                name=disorder_name
            )
            if not disorder_result.single():
                driver.close()
                raise HTTPException(status_code=404, detail=f"Disorder '{disorder_name}' not found")
            
            # Delete disorder and its relationships
            session.run(
                """
                MATCH (d:Disorder {name: $name})
                DETACH DELETE d
                """,
                name=disorder_name
            )
        driver.close()
        
        return {"message": f"Disorder '{disorder_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting disorder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete disorder: {str(e)}")

@router.delete("/symptoms/{symptom_name}")
async def delete_symptom(
    symptom_name: str,
    current_user: User = Depends(get_therapist_or_admin)
):
    """Delete a symptom from the knowledge base."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Check if symptom exists
            symptom_result = session.run(
                "MATCH (s:Symptom {name: $name}) RETURN s.name",
                name=symptom_name
            )
            if not symptom_result.single():
                driver.close()
                raise HTTPException(status_code=404, detail=f"Symptom '{symptom_name}' not found")
            
            # Delete symptom and its relationships
            session.run(
                """
                MATCH (s:Symptom {name: $name})
                DETACH DELETE s
                """,
                name=symptom_name
            )
        driver.close()
        
        return {"message": f"Symptom '{symptom_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting symptom: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete symptom: {str(e)}")

@router.delete("/disorders/{disorder_name}/symptoms/{symptom_name}")
async def unlink_symptom_from_disorder(
    disorder_name: str,
    symptom_name: str,
    current_user: User = Depends(get_therapist_or_admin)
):
    """Remove the link between a symptom and a disorder."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Check if relationship exists
            relationship_result = session.run(
                """
                MATCH (d:Disorder {name: $disorder})-[r:HAS_SYMPTOM]->(s:Symptom {name: $symptom})
                RETURN r
                """,
                disorder=disorder_name,
                symptom=symptom_name
            )
            if not relationship_result.single():
                driver.close()
                raise HTTPException(
                    status_code=404, 
                    detail=f"Relationship between disorder '{disorder_name}' and symptom '{symptom_name}' not found"
                )
            
            # Delete relationship
            session.run(
                """
                MATCH (d:Disorder {name: $disorder})-[r:HAS_SYMPTOM]->(s:Symptom {name: $symptom})
                DELETE r
                """,
                disorder=disorder_name,
                symptom=symptom_name
            )
        driver.close()
        
        return {"message": f"Symptom '{symptom_name}' unlinked from disorder '{disorder_name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error unlinking symptom from disorder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to unlink symptom from disorder: {str(e)}")

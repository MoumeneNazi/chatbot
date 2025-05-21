from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from journal_database import get_journal_db
from dependencies import get_current_admin
from models import User, UserModel, TherapistApplicationModel
from typing import List, Optional
import logging
from datetime import datetime
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import subprocess
import sys

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "mimo2021")

# Password hashing - match what's used in auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

@router.get("/users")
async def list_users(
    search: Optional[str] = None, 
    role: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering by search term or role.
    Admin only endpoint.
    """
    try:
        query = db.query(UserModel)
        
        # Apply filters if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                UserModel.username.ilike(search_term)
            )
        
        if role:
            query = query.filter(UserModel.role == role)
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Count total matching users
        total_count = query.count()
        
        return {
            "total": total_count,
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
        }
    except Exception as e:
        logging.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    Admin only endpoint.
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int = Path(..., gt=0),
    role: str = Body(..., embed=True),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    Admin only endpoint.
    """
    try:
        if role not in ["user", "therapist", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'user', 'therapist', or 'admin'"
            )
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.role = role
        db.commit()
        
        return {"message": f"User role updated to {role}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating user role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    journal_db: Session = Depends(get_journal_db)
):
    """
    Delete a user account and all associated data.
    Admin only endpoint.
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting the only admin
        admin_count = db.query(func.count(UserModel.id)).filter(UserModel.role == "admin").scalar()
        if user.role == "admin" and admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the only admin account"
            )
        
        # Delete user's journal entries and other related data
        journal_db.execute(f"DELETE FROM journal_entries WHERE user_id = {user_id}")
        journal_db.execute(f"DELETE FROM treatment_plans WHERE user_id = {user_id}")
        journal_db.commit()
        
        # Delete chat messages and therapist applications
        db.execute(f"DELETE FROM chat_messages WHERE user_id = {user_id}")
        db.execute(f"DELETE FROM therapist_applications WHERE user_id = {user_id}")
        
        # Finally delete the user
        db.delete(user)
        db.commit()
        
        return {"message": f"User {user.username} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        journal_db.rollback()
        logging.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/applications")
async def list_all_applications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all therapist applications with optional filtering.
    Admin only endpoint.
    """
    try:
        query = db.query(TherapistApplicationModel)
        
        if status:
            query = query.filter(TherapistApplicationModel.status == status)
        
        applications = query.order_by(
            TherapistApplicationModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        total_count = query.count()
        
        return {
            "total": total_count,
            "applications": [
                {
                    "id": app.id,
                    "user_id": app.user_id,
                    "full_name": app.full_name,
                    "email": app.email,
                    "specialty": app.specialty,
                    "license_number": app.license_number,
                    "certification": app.certification,
                    "experience_years": app.experience_years,
                    "document_path": app.document_path,
                    "status": app.status,
                    "created_at": app.created_at.isoformat(),
                    "updated_at": app.updated_at.isoformat() if app.updated_at else None
                }
                for app in applications
            ]
        }
    except Exception as e:
        logging.error(f"Error listing applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list applications: {str(e)}"
        )

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int = Path(..., gt=0),
    status: str = Body(..., embed=True),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update the status of a therapist application.
    Admin only endpoint.
    """
    try:
        if status not in ["pending", "approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'pending', 'approved', or 'rejected'"
            )
        
        application = db.query(TherapistApplicationModel).filter(
            TherapistApplicationModel.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update application status
        application.status = status
        application.updated_at = datetime.utcnow()
        
        # If approved, update user role to therapist
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application status: {str(e)}"
        )

@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    journal_db: Session = Depends(get_journal_db)
):
    """
    Get system statistics including user counts, activity metrics, etc.
    Admin only endpoint.
    """
    try:
        # User statistics
        total_users = db.query(func.count(UserModel.id)).scalar()
        user_count = db.query(func.count(UserModel.id)).filter(UserModel.role == "user").scalar()
        therapist_count = db.query(func.count(UserModel.id)).filter(UserModel.role == "therapist").scalar()
        admin_count = db.query(func.count(UserModel.id)).filter(UserModel.role == "admin").scalar()
        
        # Application statistics
        pending_applications = db.query(func.count(TherapistApplicationModel.id)).filter(
            TherapistApplicationModel.status == "pending"
        ).scalar()
        
        # Chat statistics
        total_messages = db.query(func.count("id")).select_from("chat_messages").scalar()
        
        # Journal statistics
        total_journal_entries = journal_db.query(func.count("id")).select_from("journal_entries").scalar()
        
        # Get Neo4j statistics
        neo4j_stats = {}
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            with driver.session() as session:
                # Count disorders
                disorder_result = session.run("MATCH (d:Disorder) RETURN count(d) as count")
                neo4j_stats["disorders"] = disorder_result.single()["count"] if disorder_result.peek() else 0
                
                # Count symptoms
                symptom_result = session.run("MATCH (s:Symptom) RETURN count(s) as count")
                neo4j_stats["symptoms"] = symptom_result.single()["count"] if symptom_result.peek() else 0
                
                # Count relationships
                rel_result = session.run("MATCH ()-[r:HAS_SYMPTOM]->() RETURN count(r) as count")
                neo4j_stats["relationships"] = rel_result.single()["count"] if rel_result.peek() else 0
            driver.close()
        except Exception as e:
            logging.error(f"Error getting Neo4j stats: {str(e)}")
            neo4j_stats = {"error": str(e)}
        
        return {
            "users": {
                "total": total_users,
                "users": user_count,
                "therapists": therapist_count,
                "admins": admin_count
            },
            "applications": {
                "pending": pending_applications
            },
            "activity": {
                "total_messages": total_messages,
                "total_journal_entries": total_journal_entries
            },
            "knowledge_base": neo4j_stats
        }
    except Exception as e:
        logging.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system statistics: {str(e)}"
        )

@router.post("/create-admin")
async def create_admin_account(
    username: str = Body(...),
    password: str = Body(...),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new admin account.
    Admin only endpoint.
    """
    try:
        # Check if username already exists
        existing_user = db.query(UserModel).filter(
            UserModel.username == username
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Create password hash
        hashed_password = get_password_hash(password)
        
        # Create new admin user
        new_admin = UserModel(
            username=username,
            password=hashed_password,
            role="admin",
            created_at=datetime.utcnow()
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return {
            "message": "Admin account created successfully",
            "user_id": new_admin.id,
            "username": new_admin.username,
            "role": new_admin.role
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating admin account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin account: {str(e)}"
        )

@router.post("/run-chat-learning-system")
async def run_chat_learning_system(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Run the chat learning system.
    Admin only endpoint.
    """
    try:
        # Run the chat learning system
        script_path = os.path.join(os.path.dirname(__file__), "chat_learning.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to run chat learning system: {result.stderr}"
            )
        
        return {"message": "Chat learning system run successfully"}
    except Exception as e:
        logging.error(f"Error running chat learning system: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run chat learning system: {str(e)}"
        )

@router.put("/users/{user_id}/status")
async def update_account_status(
    user_id: int = Path(..., gt=0),
    is_active: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate a user account.
    Admin only endpoint.
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deactivating the only admin
        if user.role == "admin" and not is_active:
            admin_count = db.query(func.count(UserModel.id)).filter(
                UserModel.role == "admin", 
                UserModel.is_active == True,
                UserModel.id != user_id
            ).scalar()
            
            if admin_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the only active admin account"
                )
        
        # Update account status
        user.is_active = is_active
        db.commit()
        
        action = "activated" if is_active else "deactivated"
        return {"message": f"Account {action} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating account status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account status: {str(e)}"
        )
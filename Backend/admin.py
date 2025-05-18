from fastapi import APIRouter, Depends, HTTPException
from models import User
from database import get_all_users, promote_user, get_db
from dependencies import get_current_user, check_user_role
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin",  # Updated prefix to match frontend expectations
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)

@router.get("/users")
async def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users. Only accessible by therapists (admins)."""
    # Check if user is a therapist
    await check_user_role(current_user, "therapist")
    
    try:
        logger.info(f"Admin {current_user.username} requesting user list")
        users = get_all_users(db)
        if not users:
            logger.warning("No users found")
            return []
        return [{"username": u.username, "role": u.role} for u in users]
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/promote/{username}")
async def promote(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Promote a user to therapist role. Only accessible by existing therapists (admins)."""
    # Check if user is a therapist
    await check_user_role(current_user, "therapist")
    
    try:
        logger.info(f"Admin {current_user.username} attempting to promote user {username}")
        result = promote_user(username, db)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {"msg": f"{username} promoted to therapist"}
    except Exception as e:
        logger.error(f"Error promoting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException
from models import User
from database import get_all_users, promote_user, get_db
from dependencies import require_role
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",  # Add prefix to match frontend expectations
    tags=["admin"],
    responses={404: {"description": "Not found"}}
)

@router.get("/users")
def get_users(current_user: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    """Get all users. Only accessible by therapists (admins)."""
    logger.info(f"Admin {current_user.username} requesting user list")
    users = get_all_users(db)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@router.put("/promote/{username}")
def promote(username: str, current_user: User = Depends(require_role("therapist")), db: Session = Depends(get_db)):
    """Promote a user to therapist role. Only accessible by existing therapists (admins)."""
    logger.info(f"Admin {current_user.username} attempting to promote user {username}")
    result = promote_user(username, db)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": f"{username} promoted to therapist"}
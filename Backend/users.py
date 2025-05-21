from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db, get_all_users, get_user_by_username, promote_user
from models import User, UserModel
from dependencies import check_user_role, get_current_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's information."""
    try:
        logger.info(f"Fetching current user info for {current_user.username}")
        # Refresh user data from database
        user = get_user_by_username(current_user.username, db)
        if not user:
            logger.error(f"Current user not found in database: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current user not found in database"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user info: {str(e)}"
        )

@router.get("/", response_model=list[User])
async def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users. Accessible by both users and therapists."""
    try:
        logger.info(f"User {current_user.username} requesting users list")
        users = get_all_users(db)
        if not users:
            logger.warning("No users found in database")
            return []
            
        # If user is not a therapist, only return their own info
        if current_user.role != "therapist":
            users = [u for u in users if u.id == current_user.id]
            
        logger.info(f"Successfully fetched {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/{username}", response_model=User)
async def get_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by username. Only accessible by therapists."""
    try:
        # Check if user is a therapist
        if current_user.role != "therapist":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. Required role: therapist"
            )
            
        # Prevent confusion with /me endpoint
        if username.lower() == "me":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Use /api/users/me endpoint to get current user info'
            )
            
        logger.info(f"Fetching user details for username: {username}")
        user = get_user_by_username(username, db)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {username} not found"
            )
        logger.info(f"Successfully fetched user details for {username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user details: {str(e)}"
        )
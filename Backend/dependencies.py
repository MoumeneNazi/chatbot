from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from database import get_user_by_username, get_db
from models import User
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
import os
from typing import Union, List
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auth configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)  # Generate a secure random key
    logger.warning("Using default JWT_SECRET_KEY. This is not recommended for production. Please set JWT_SECRET_KEY environment variable.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Role hierarchy definition
ROLE_HIERARCHY = {
    "admin": ["admin", "therapist", "user"],  # Admin has access to all endpoints
    "therapist": ["therapist", "user"],  # Therapist can access both therapist and user endpoints
    "user": ["user"]  # User can only access user endpoints
}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info("Attempting to decode token")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token payload missing username")
            raise credentials_exception
        
        # Validate role
        role = payload.get("role")
        if role not in ROLE_HIERARCHY:
            logger.warning(f"Invalid role in token: {role}")
            raise credentials_exception
            
        logger.info(f"Token decoded successfully for user: {username}")
    except JWTError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception
        
    user = get_user_by_username(username, db)
    if user is None:
        logger.warning(f"User not found for token: {username}")
        raise credentials_exception
        
    # Verify role matches
    if user.role != role:
        logger.warning(f"Token role mismatch. Token: {role}, User: {user.role}")
        raise credentials_exception
    
    # Check if account is active
    if not user.is_active:
        logger.warning(f"Deactivated account attempted access: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated, please contact an administrator"
        )
        
    logger.info(f"User {username} authenticated successfully")
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def check_user_role(current_user: User = Depends(get_current_user), required_roles: Union[str, List[str]] = None) -> User:
    """
    Check if the current user has the required role(s).
    Args:
        current_user: The current authenticated user
        required_roles: Either a single role string or a list of role strings
    """
    if required_roles is None:
        return current_user

    # Convert single role to list for consistent handling
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    # Get allowed roles for the user's role
    allowed_roles = ROLE_HIERARCHY.get(current_user.role, [])
    
    # Check if any of the required roles are in the allowed roles
    if not any(role in allowed_roles for role in required_roles):
        logger.warning(
            f"Unauthorized access attempt: User {current_user.username} with role {current_user.role} "
            f"tried to access endpoint requiring one of {required_roles}. Allowed roles: {allowed_roles}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted. Required roles: {required_roles}"
        )
    return current_user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get the current active user regardless of role."""
    return current_user

def get_current_therapist(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get the current user only if they are a therapist."""
    if current_user.role != "therapist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires therapist role"
        )
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admins only"
        )
    return current_user

async def get_therapist_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is either a therapist or an admin."""
    if current_user.role not in ["therapist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Therapists and Admins only"
        )
    return current_user
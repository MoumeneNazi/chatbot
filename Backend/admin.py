from fastapi import APIRouter, Depends, HTTPException
from models import User
from database import get_all_users, promote_user
from dependencies import require_role

router = APIRouter()

@router.get("/admin/users")
def get_users(current_user: User = Depends(require_role("therapist"))):
    return get_all_users()

@router.put("/admin/promote/{username}")
def promote(username: str, current_user: User = Depends(require_role("therapist"))):
    promote_user(username)
    return {"msg": f"{username} promoted to therapist"}
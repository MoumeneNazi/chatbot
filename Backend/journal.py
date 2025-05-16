from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import require_role
from database import get_journal_by_username

router = APIRouter()

@router.get("/admin/journal/{username}")
def get_journal(username: str, current_user: User = Depends(require_role("therapist"))):
    journal = get_journal_by_username(username)
    if not journal:
        raise HTTPException(status_code=404, detail="No journal found")
    return journal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, ChatMessage
from auth import get_current_user
from typing import List
import logging

router = APIRouter(
    prefix="/api",
    tags=["chat"]
)

@router.get("/chat/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.timestamp).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

@router.get("/chat/history/{user_id}")
async def get_user_chat_history(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific user (therapist only)"""
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(ChatMessage.timestamp).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

@router.post("/chat")
async def send_message(
    message: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message as the current user"""
    try:
        # Save user message
        user_message = ChatMessage(
            user_id=current_user.id,
            content=message["message"],
            role="user"
        )
        db.add(user_message)
        db.commit()
        
        # Get AI response
        response = "This is a test response"  # Replace with actual AI logic
        
        # Save AI response
        ai_message = ChatMessage(
            user_id=current_user.id,
            content=response,
            role="assistant"
        )
        db.add(ai_message)
        db.commit()
        
        return {"response": response}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/{user_id}")
async def send_message_as_therapist(
    user_id: int,
    message: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a specific user's chat (therapist only)"""
    if current_user.role != "therapist":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Save therapist message
        therapist_message = ChatMessage(
            user_id=user_id,
            content=message["message"],
            role="user"  # Using "user" role for consistency
        )
        db.add(therapist_message)
        db.commit()
        
        # Get AI response
        response = "This is a test response"  # Replace with actual AI logic
        
        # Save AI response
        ai_message = ChatMessage(
            user_id=user_id,
            content=response,
            role="assistant"
        )
        db.add(ai_message)
        db.commit()
        
        return {"response": response}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 
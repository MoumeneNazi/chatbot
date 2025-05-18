from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User, UserModel, ChatMessage, ChatMessageModel
from typing import List
import logging
from chatbot import ask_groq  # Import the AI function
from datetime import datetime

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
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.user_id == current_user.id
    ).order_by(ChatMessageModel.timestamp).all()
    
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
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.user_id == user_id
    ).order_by(ChatMessageModel.timestamp).all()
    
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
        if "message" not in message:
            raise HTTPException(status_code=422, detail="Message field is required")
            
        user_input = message["message"]
        if not user_input or not isinstance(user_input, str):
            raise HTTPException(status_code=422, detail="Message must be a non-empty string")
            
        # Save user message
        user_message = ChatMessageModel(
            user_id=current_user.id,
            content=user_input,
            role="user",
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # Get AI response using the chatbot's AI function
        response = ask_groq(user_input)
        
        # Save AI response
        ai_message = ChatMessageModel(
            user_id=current_user.id,
            content=response,
            role="assistant",
            timestamp=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        
        return {"response": response}
    except HTTPException:
        db.rollback()
        raise
    except KeyError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Message field is required")
    except Exception as e:
        db.rollback()
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

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
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        if "message" not in message:
            raise HTTPException(status_code=422, detail="Message field is required")
            
        user_input = message["message"]
        if not user_input or not isinstance(user_input, str):
            raise HTTPException(status_code=422, detail="Message must be a non-empty string")
            
        # Save therapist message
        therapist_message = ChatMessageModel(
            user_id=user_id,
            content=user_input,
            role="user",  # Using "user" role for consistency
            timestamp=datetime.utcnow()
        )
        db.add(therapist_message)
        db.commit()
        
        # Get AI response using the chatbot's AI function
        response = ask_groq(user_input)
        
        # Save AI response
        ai_message = ChatMessageModel(
            user_id=user_id,
            content=response,
            role="assistant",
            timestamp=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        
        return {"response": response}
    except HTTPException:
        db.rollback()
        raise
    except KeyError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Message field is required")
    except Exception as e:
        db.rollback()
        logging.error(f"Error in therapist chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}") 
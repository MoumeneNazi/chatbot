from pydantic import BaseModel, Field, validator
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List

Base = declarative_base()

# SQLAlchemy Models
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")  # "user" or "therapist"
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    timestamp = Column(DateTime, default=datetime.utcnow)

class JournalModel(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entry = Column(Text)
    mood_rating = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, nullable=True)

class TreatmentProgressModel(Base):
    __tablename__ = "treatment_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    therapist_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    treatment_plan = Column(Text)
    progress_status = Column(String)  # "Initial", "In Progress", "Completed"
    timestamp = Column(DateTime, default=datetime.utcnow)

class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    therapist_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    disorder = Column(String, nullable=False)
    specialty = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class UserBase(BaseModel):
    username: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    password: str

class ChatMessage(BaseModel):
    id: int
    content: str
    role: str
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

class Journal(BaseModel):
    id: int
    entry: str
    mood_rating: int = Field(..., ge=1, le=10)
    timestamp: datetime
    sentiment_score: Optional[float] = None
    user_id: int

    class Config:
        from_attributes = True

class JournalCreate(BaseModel):
    entry: str
    mood_rating: int = Field(..., ge=1, le=10)

class TreatmentProgress(BaseModel):
    id: int
    notes: str
    treatment_plan: str
    progress_status: str = Field(..., pattern="^(Initial|In Progress|Completed)$")
    timestamp: datetime
    user_id: int
    therapist_id: int

    class Config:
        from_attributes = True

class TreatmentProgressCreate(BaseModel):
    notes: str
    treatment_plan: str
    progress_status: str = Field(..., pattern="^(Initial|In Progress|Completed)$")

class Review(BaseModel):
    id: int
    title: str
    content: str
    disorder: str
    specialty: Optional[str] = None
    timestamp: datetime
    user_id: int
    therapist_id: int

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    title: str
    content: str
    disorder: str
    specialty: Optional[str] = None 
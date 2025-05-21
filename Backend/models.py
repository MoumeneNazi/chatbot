from pydantic import BaseModel, Field, validator
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List
from sqlalchemy.orm import relationship

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
    is_active = Column(Boolean, default=True)  # Track if account is active
    messages = relationship("ChatMessageModel", back_populates="user")
    problem_reports = relationship("ProblemReportModel", back_populates="user")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="messages")

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

class TherapistApplicationModel(Base):
    __tablename__ = "therapist_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    license_number = Column(String, nullable=False)
    certification = Column(String, nullable=False)
    experience_years = Column(Integer, nullable=False)
    document_path = Column(String, nullable=True)  # Path to uploaded document
    status = Column(String, default="pending")  # "pending", "approved", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProblemReportModel(Base):
    __tablename__ = "problem_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # 'technical', 'content', 'suggestion', etc.
    status = Column(String, default="pending")  # 'pending', 'in_progress', 'resolved', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("UserModel", back_populates="problem_reports")

# Pydantic Models for API
class UserBase(BaseModel):
    username: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    """User model for API operations."""
    id: int
    username: str
    role: str  # "user", "therapist", or "admin"
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    email: Optional[str] = None  # Make email optional since it's not in the database

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

class TherapistApplicationCreate(BaseModel):
    full_name: str
    email: str
    specialty: str
    license_number: str
    certification: str
    experience_years: int = Field(..., ge=0)
    
class TherapistApplication(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    specialty: str
    license_number: str
    certification: str
    experience_years: int
    document_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProblemReportCreate(BaseModel):
    title: str
    description: str
    category: str

class ProblemReportUpdate(BaseModel):
    status: str

class ProblemReport(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    category: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True 
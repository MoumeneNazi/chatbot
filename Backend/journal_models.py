from sqlalchemy import Column, Integer, Text, DateTime, Float, ForeignKey, String
from datetime import datetime
from journal_database import JournalBase
from pydantic import BaseModel, Field
from typing import Optional, List

class JournalEntryModel(JournalBase):
    __tablename__ = "journals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    entry = Column(Text)
    mood_rating = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, nullable=True)

class TreatmentProgressModel(JournalBase):
    __tablename__ = "treatment_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    therapist_id = Column(Integer, index=True)
    notes = Column(Text)
    treatment_plan = Column(Text)
    progress_status = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

class DisorderTreatmentModel(JournalBase):
    __tablename__ = "disorder_treatments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    therapist_id = Column(Integer, index=True)
    disorder = Column(String(100))
    treatment_plan = Column(Text)
    duration_weeks = Column(Integer)
    status = Column(String(50), default="Active")  # Active, Completed, Canceled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API
class JournalEntryCreate(BaseModel):
    entry: str
    mood_rating: int = Field(..., ge=1, le=10, description="Mood rating from 1-10")

class JournalEntry(BaseModel):
    id: int
    entry: str
    mood_rating: int = Field(..., ge=1, le=10)
    timestamp: datetime
    sentiment_score: Optional[float] = None

    class Config:
        from_attributes = True

class TreatmentProgressCreate(BaseModel):
    notes: str
    treatment_plan: str
    progress_status: str = Field(..., pattern="^(Initial|In Progress|Completed)$")

class TreatmentProgress(BaseModel):
    id: int
    user_id: int
    therapist_id: int
    notes: str
    treatment_plan: str
    progress_status: str
    timestamp: datetime

    class Config:
        from_attributes = True

class DisorderTreatmentCreate(BaseModel):
    disorder: str
    treatment_plan: str
    duration_weeks: int = Field(..., ge=1, le=52)

class DisorderTreatment(BaseModel):
    id: int
    user_id: int
    therapist_id: int
    disorder: str
    treatment_plan: str
    duration_weeks: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
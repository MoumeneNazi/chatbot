from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class ErrorResponse(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None
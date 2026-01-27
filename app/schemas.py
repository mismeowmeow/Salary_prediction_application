from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Prediction Schemas
class PredictionInput(BaseModel):
    test_score: float = Field(..., ge=0, le=100, description="Test score (0-100)")
    interview_score: float = Field(..., ge=0, le=100, description="Interview score (0-100)")
    years_experience: float = Field(..., ge=0, le=50, description="Years of experience")

class PredictionResponse(BaseModel):
    id: int
    test_score: float
    interview_score: float
    years_experience: float
    predicted_salary: float
    created_at: datetime
    
    class Config:
        from_attributes = True
"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="agent", pattern="^(agent|bank|admin)$")

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Farmer Schemas
class FarmerCreate(BaseModel):
    farmer_id: str = Field(..., min_length=6, max_length=20)
    name: str = Field(..., min_length=2, max_length=100)
    mobile: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    aadhar: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    land_area: Optional[float] = Field(None, gt=0)
    crop_type: Optional[str] = None
    consent_given: bool = True

class FarmerResponse(BaseModel):
    id: int
    farmer_id: str
    name: str
    mobile: str
    state: Optional[str]
    district: Optional[str]
    village: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    land_area: Optional[float]
    crop_type: Optional[str]
    consent_given: bool
    created_at: datetime
    latest_score: Optional[float] = None
    
    class Config:
        from_attributes = True

# Score Schemas
class ScoreRequest(BaseModel):
    farmer_id: str

class Driver(BaseModel):
    feature: str
    impact: float
    explanation: str

class ScoreResponse(BaseModel):
    farmer_id: str
    score: float = Field(..., ge=0, le=100)
    score_band: str
    drivers: List[Driver]
    model_type: str
    computed_at: datetime

class ScoreHistoryResponse(BaseModel):
    farmer_id: str
    scores: List[ScoreResponse]

# Batch Score Schemas
class BatchScoreRequest(BaseModel):
    farmer_ids: List[str] = Field(..., min_items=1, max_items=1000)

class BatchScoreResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Job Schemas
class JobStatus(BaseModel):
    job_id: str
    job_type: str
    status: str
    progress: int = Field(..., ge=0, le=100)
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# Loan Schemas
class LoanQuoteRequest(BaseModel):
    farmer_id: str
    requested_amount: Optional[float] = Field(None, gt=0)

class EMIPlan(BaseModel):
    emi_amount: float
    duration_months: int
    interest_rate: float
    total_repayment: float

class LoanQuoteResponse(BaseModel):
    farmer_id: str
    credit_score: float
    eligible: bool
    max_loan_amount: float
    recommended_amount: float
    emi_plans: List[EMIPlan]
    crop_cycle_months: int
    remarks: str

# Health Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str
    redis: str

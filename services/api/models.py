"""
Database models for Farmer Credit Score Engine
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="agent")  # agent, bank, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Farmer(Base):
    """Farmer profile model"""
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    aadhar = Column(String(20))
    
    # Location
    state = Column(String(50))
    district = Column(String(50))
    village = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Farm details
    land_area = Column(Float)  # hectares
    crop_type = Column(String(50))
    
    # Consent
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scores = relationship("Score", back_populates="farmer", cascade="all, delete-orphan")
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")

class Farm(Base):
    """Farm/land parcel model"""
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    land_id = Column(String(20), unique=True, index=True, nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    
    # Land details
    area = Column(Float)  # hectares
    crop_type = Column(String(50))
    sowing_date = Column(DateTime(timezone=True))
    
    # Satellite data
    ndvi_mean = Column(Float)
    ndvi_trend = Column(Float)
    last_satellite_update = Column(DateTime(timezone=True))
    
    # Weather data
    rainfall_anomaly_3mo = Column(Float)
    last_weather_update = Column(DateTime(timezone=True))
    
    # Yield
    last_year_yield_est = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farmer = relationship("Farmer", back_populates="farms")

class Score(Base):
    """Credit score model"""
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    
    # Score
    score = Column(Float, nullable=False)  # 0-100
    score_band = Column(String(20))  # low, medium, high
    
    # Features used
    features = Column(JSON)
    
    # Explainability
    drivers = Column(JSON)  # Top 3 drivers
    
    # Model info
    model_version = Column(String(20), default="1.0")
    model_type = Column(String(20))  # ml, deterministic
    
    # Metadata
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    computed_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    farmer = relationship("Farmer", back_populates="scores")

class Job(Base):
    """Background job model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)
    job_type = Column(String(50), nullable=False)  # batch_score, ingest_data
    
    # Status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # Input/Output
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

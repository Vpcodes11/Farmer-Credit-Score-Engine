"""
Farmer management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import User, Farmer, Score
from schemas import FarmerCreate, FarmerResponse
from auth import get_current_active_user

router = APIRouter(prefix="/farmers", tags=["Farmers"])

@router.post("", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def onboard_farmer(
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Onboard a new farmer
    
    Args:
        farmer_data: Farmer registration data
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Created farmer profile
    """
    # Check if farmer_id already exists
    existing = db.query(Farmer).filter(Farmer.farmer_id == farmer_data.farmer_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Farmer with ID {farmer_data.farmer_id} already exists"
        )
    
    # Create farmer
    new_farmer = Farmer(
        **farmer_data.model_dump(),
        created_by=current_user.id,
        consent_date=datetime.utcnow() if farmer_data.consent_given else None
    )
    
    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)
    
    return new_farmer

@router.get("/{farmer_id}", response_model=FarmerResponse)
def get_farmer(
    farmer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get farmer profile with latest score
    
    Args:
        farmer_id: Farmer ID
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Farmer profile with latest score
    """
    farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer {farmer_id} not found"
        )
    
    # Get latest score
    latest_score = db.query(Score).filter(
        Score.farmer_id == farmer.id
    ).order_by(Score.computed_at.desc()).first()
    
    farmer_response = FarmerResponse.model_validate(farmer)
    if latest_score:
        farmer_response.latest_score = latest_score.score
    
    return farmer_response

@router.get("", response_model=List[FarmerResponse])
def list_farmers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all farmers
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user
    
    Returns:
        List of farmer profiles
    """
    farmers = db.query(Farmer).offset(skip).limit(limit).all()
    
    # Add latest scores
    farmer_responses = []
    for farmer in farmers:
        latest_score = db.query(Score).filter(
            Score.farmer_id == farmer.id
        ).order_by(Score.computed_at.desc()).first()
        
        farmer_response = FarmerResponse.model_validate(farmer)
        if latest_score:
            farmer_response.latest_score = latest_score.score
        
        farmer_responses.append(farmer_response)
    
    return farmer_responses

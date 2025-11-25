"""
Scoring routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import sys
import os
import uuid

# Add ML module to path
ml_path = os.path.join(os.path.dirname(__file__), '../../ml')
sys.path.insert(0, ml_path)

from database import get_db
from models import User, Farmer, Score, Job
from schemas import (
    ScoreRequest,
    ScoreResponse,
    Driver,
    ScoreHistoryResponse,
    BatchScoreRequest,
    BatchScoreResponse
)
from auth import get_current_active_user
from config import settings

# Import ML module
try:
    from model import get_model
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML module not available")

router = APIRouter(prefix="/score", tags=["Scoring"])

def get_score_band(score: float) -> str:
    """Determine score band from score value"""
    if score < 40:
        return "low"
    elif score < 70:
        return "medium"
    else:
        return "high"

@router.post("", response_model=ScoreResponse)
def compute_score(
    request: ScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compute credit score for a farmer (synchronous)
    
    Args:
        request: Score request with farmer_id
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Computed score with drivers
    """
    # Get farmer
    farmer = db.query(Farmer).filter(Farmer.farmer_id == request.farmer_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer {request.farmer_id} not found"
        )
    
    if not farmer.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmer consent required for scoring"
        )
    
    # Prepare farmer data
    farmer_data = {
        'farmer_id': farmer.farmer_id,
        'land_area': farmer.land_area or 2.0,
        'crop_type': farmer.crop_type or 'rice',
        'last_year_yield_est': 3.0,  # Default, should come from Farm model
        'ndvi_mean': 0.6,  # Default, should come from satellite data
        'ndvi_trend': 0.05,
        'rainfall_anomaly_3mo': 0.0,
        'past_kcc_defaults': 0,
        'upi_txn_freq': 15,
        'market_price_volatility': 15.0,
        'fpo_membership_flag': 0,
        'distance_to_mandi_km': 20.0
    }
    
    # Compute score using ML model or deterministic fallback
    try:
        if ML_AVAILABLE and settings.USE_ML_MODEL:
            model = get_model(settings.MODEL_PATH if os.path.exists(settings.MODEL_PATH) else None)
            score_value, drivers_data = model.predict(farmer_data)
            model_type = "ml" if model.model is not None else "deterministic"
        else:
            from scoring import compute_deterministic_score
            score_value, drivers_data = compute_deterministic_score(farmer_data)
            model_type = "deterministic"
    except Exception as e:
        print(f"Scoring error: {e}")
        # Fallback to deterministic
        from scoring import compute_deterministic_score
        score_value, drivers_data = compute_deterministic_score(farmer_data)
        model_type = "deterministic"
    
    # Save score to database
    new_score = Score(
        farmer_id=farmer.id,
        score=score_value,
        score_band=get_score_band(score_value),
        features=farmer_data,
        drivers=drivers_data,
        model_version="1.0",
        model_type=model_type,
        computed_by=current_user.id
    )
    
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    
    # Prepare response
    drivers = [Driver(**d) for d in drivers_data]
    
    return ScoreResponse(
        farmer_id=farmer.farmer_id,
        score=score_value,
        score_band=get_score_band(score_value),
        drivers=drivers,
        model_type=model_type,
        computed_at=new_score.computed_at
    )

@router.get("/{farmer_id}/history", response_model=ScoreHistoryResponse)
def get_score_history(
    farmer_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get score history for a farmer
    
    Args:
        farmer_id: Farmer ID
        limit: Maximum number of scores to return
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Score history
    """
    farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer {farmer_id} not found"
        )
    
    # Get score history
    scores = db.query(Score).filter(
        Score.farmer_id == farmer.id
    ).order_by(Score.computed_at.desc()).limit(limit).all()
    
    score_responses = []
    for score in scores:
        drivers = [Driver(**d) for d in score.drivers]
        score_responses.append(ScoreResponse(
            farmer_id=farmer_id,
            score=score.score,
            score_band=score.score_band,
            drivers=drivers,
            model_type=score.model_type,
            computed_at=score.computed_at
        ))
    
    return ScoreHistoryResponse(
        farmer_id=farmer_id,
        scores=score_responses
    )

@router.post("/batch", response_model=BatchScoreResponse)
def batch_score(
    request: BatchScoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit batch scoring job
    
    Args:
        request: Batch score request with farmer IDs
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Job ID and status
    """
    # Create job
    job_id = str(uuid.uuid4())
    
    new_job = Job(
        job_id=job_id,
        job_type="batch_score",
        status="pending",
        input_data={"farmer_ids": request.farmer_ids},
        created_by=current_user.id
    )
    
    db.add(new_job)
    db.commit()
    
    # In a real implementation, this would trigger a Celery task
    # For now, we'll just mark it as pending
    
    return BatchScoreResponse(
        job_id=job_id,
        status="pending",
        message=f"Batch scoring job created for {len(request.farmer_ids)} farmers"
    )

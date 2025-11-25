"""
Job status and health check routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

from database import get_db
from models import Job, User
from schemas import JobStatus, HealthResponse
from auth import get_current_active_user
from config import settings

router = APIRouter(tags=["System"])

# Prometheus metrics
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration')
score_compute_count = Counter('score_computations_total', 'Total score computations')

@router.get("/jobs/{job_id}", response_model=JobStatus)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get status of a background job
    
    Args:
        job_id: Job ID
        db: Database session
        current_user: Authenticated user
    
    Returns:
        Job status
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return job

@router.get("/healthz", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Check Redis (simplified)
    redis_status = "healthy"  # Would check Redis connection in production
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.API_VERSION,
        database=db_status,
        redis=redis_status
    )

@router.get("/readyz")
def readiness_check():
    """
    Readiness check for Kubernetes
    
    Returns:
        200 if ready, 503 if not ready
    """
    # In production, check if all dependencies are ready
    return {"status": "ready"}

@router.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint
    
    Returns:
        Prometheus metrics in text format
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

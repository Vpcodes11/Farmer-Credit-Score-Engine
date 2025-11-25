"""
Worker Service for background tasks
"""
from celery import Celery
import os
import sys

# Add ML module to path
ml_path = os.path.join(os.path.dirname(__file__), '../ml')
sys.path.insert(0, ml_path)

# Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
app = Celery('fcs_worker', broker=REDIS_URL, backend=REDIS_URL)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(name='compute_score_task')
def compute_score_task(farmer_data: dict) -> dict:
    """
    Background task to compute farmer credit score
    
    Args:
        farmer_data: Farmer information dictionary
    
    Returns:
        Score and drivers
    """
    try:
        from model import get_model
        model = get_model()
        score, drivers = model.predict(farmer_data)
        
        return {
            'success': True,
            'score': score,
            'drivers': drivers
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.task(name='batch_score_task')
def batch_score_task(farmer_ids: list) -> dict:
    """
    Background task for batch scoring
    
    Args:
        farmer_ids: List of farmer IDs to score
    
    Returns:
        Batch results
    """
    results = []
    
    for farmer_id in farmer_ids:
        # In production, fetch farmer data from database
        # For now, return placeholder
        results.append({
            'farmer_id': farmer_id,
            'status': 'completed'
        })
    
    return {
        'success': True,
        'total': len(farmer_ids),
        'completed': len(results),
        'results': results
    }

@app.task(name='ingest_satellite_data')
def ingest_satellite_data() -> dict:
    """
    Background task to ingest satellite data
    
    Returns:
        Ingestion status
    """
    # Placeholder for satellite data ingestion
    return {
        'success': True,
        'message': 'Satellite data ingestion completed'
    }

@app.task(name='ingest_weather_data')
def ingest_weather_data() -> dict:
    """
    Background task to ingest weather data
    
    Returns:
        Ingestion status
    """
    # Placeholder for weather data ingestion
    return {
        'success': True,
        'message': 'Weather data ingestion completed'
    }

if __name__ == '__main__':
    app.start()

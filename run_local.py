"""
Simplified local test script for Farmer Credit Score Engine
Runs API service with in-memory SQLite database
"""
import sys
import os

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

# Set environment variables for local testing
os.environ['DB_HOST'] = 'localhost'
os.environ['JWT_SECRET'] = 'test-secret-key-for-local-development'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['MOCK_AGRI_URL'] = 'http://localhost:5001'
os.environ['USE_ML_MODEL'] = 'false'  # Use deterministic scoring
os.environ['ENVIRONMENT'] = 'development'

print("="*60)
print("Farmer Credit Score Engine - Local Test Mode")
print("="*60)
print()
print("Starting API service with SQLite database...")
print("No Docker required!")
print()
print("Once started, visit:")
print("  • API Docs: http://localhost:8000/docs")
print("  • Health: http://localhost:8000/healthz")
print()
print("="*60)
print()

# Import and run API
try:
    from api.main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
except ImportError as e:
    print(f"Error: {e}")
    print()
    print("Please install dependencies first:")
    print("  cd services/api")
    print("  pip install -r requirements.txt")
    sys.exit(1)

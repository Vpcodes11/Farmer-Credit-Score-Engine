# Running the Farmer Credit Score Engine (Without Docker)

Since Docker is not installed, here are alternative ways to run and test the project:

## Option 1: Run API Service Locally (Recommended for Testing)

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, can use SQLite for testing)

### Quick Start

1. **Install API Dependencies**:
```bash
cd services/api
pip install -r requirements.txt
```

2. **Set Environment Variables** (create `.env` in project root):
```bash
# Use SQLite for local testing (no PostgreSQL needed)
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=sqlite:///./fcs.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=test-secret-key-change-in-production
MOCK_AGRI_URL=http://localhost:5001
```

3. **Run API Server**:
```bash
cd services/api
python main.py
```

4. **Access API**:
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/healthz

### Test the API

```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"agent1\",\"email\":\"agent@test.com\",\"password\":\"pass123\",\"role\":\"agent\"}"

# The response will include a JWT token
# Use that token for subsequent requests
```

---

## Option 2: Run Mock Agri Stack (Standalone)

```bash
cd services/mock-agri-stack
pip install -r requirements.txt
python main.py
```

Access at: http://localhost:5001

---

## Option 3: Test ML Module (Standalone)

### Train the Model:
```bash
cd services/ml
pip install -r requirements.txt
python train.py
```

### Test Scoring:
```python
from model import get_model

# Load model
model = get_model('model.joblib')

# Test farmer data
farmer_data = {
    'land_area': 5.5,
    'crop_type': 'wheat',
    'last_year_yield_est': 3.5,
    'ndvi_mean': 0.7,
    'ndvi_trend': 0.05,
    'rainfall_anomaly_3mo': -10,
    'past_kcc_defaults': 0,
    'upi_txn_freq': 20,
    'market_price_volatility': 12,
    'fpo_membership_flag': 1,
    'distance_to_mandi_km': 15
}

# Compute score
score, drivers = model.predict(farmer_data)
print(f"Score: {score}")
print(f"Drivers: {drivers}")
```

---

## Option 4: Install Docker (Recommended for Full System)

### Windows:
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and restart
3. Run: `docker-compose up -d`

### Alternative (WSL2):
1. Install WSL2: `wsl --install`
2. Install Docker in WSL2
3. Run project from WSL2 terminal

---

## What You Can Test Without Docker

✅ **API Service** (with SQLite instead of PostgreSQL)
✅ **Mock Agri Stack** (standalone)
✅ **ML Module** (train model, test scoring)
✅ **Synthetic Data Generation**
❌ **Full Microservices** (requires Docker)
❌ **Worker Service** (requires Redis)
❌ **Frontend** (requires build step)

---

## Simplified Local Test

I can create a simplified test script that runs the API with SQLite:

```bash
# Run this from project root
python -m services.api.main
```

Would you like me to:
1. Create a simplified local test script?
2. Guide you through installing Docker?
3. Set up just the API service for testing?

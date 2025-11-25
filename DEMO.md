# Farmer Credit Score Engine - Demo Guide

## 3-Minute Demo Script

This guide provides a quick walkthrough to demonstrate the Farmer Credit Score Engine to judges or stakeholders.

### Prerequisites

```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Start the system
cd farmer-credit-score-engine
docker-compose up -d

# Wait for services to be healthy (~30 seconds)
docker-compose ps
```

### Demo Flow

#### 1. API Documentation (30 seconds)

**Navigate to**: http://localhost:8000/docs

**Show**:
- Interactive Swagger UI
- All API endpoints organized by category
- Authentication, Farmers, Scoring, Loan, System endpoints

**Say**: "The API provides RESTful endpoints for all operations, with automatic OpenAPI documentation."

---

#### 2. Register Agent (30 seconds)

**Using Swagger UI** or **curl**:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent001",
    "email": "agent@example.com",
    "password": "password123",
    "role": "agent"
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Save the token** for subsequent requests.

---

#### 3. Onboard Farmer (30 seconds)

```bash
curl -X POST http://localhost:8000/farmers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FRM000001",
    "name": "Rajesh Kumar",
    "mobile": "+919876543210",
    "state": "Punjab",
    "district": "Ludhiana",
    "village": "Khanna",
    "latitude": 30.7046,
    "longitude": 76.2179,
    "land_area": 5.5,
    "crop_type": "wheat",
    "consent_given": true
  }'
```

**Expected Response**:
```json
{
  "id": 1,
  "farmer_id": "FRM000001",
  "name": "Rajesh Kumar",
  "mobile": "+919876543210",
  "state": "Punjab",
  ...
}
```

---

#### 4. Compute Credit Score (45 seconds)

```bash
curl -X POST http://localhost:8000/score \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FRM000001"
  }'
```

**Expected Response**:
```json
{
  "farmer_id": "FRM000001",
  "score": 74.3,
  "score_band": "high",
  "drivers": [
    {
      "feature": "Crop health (satellite)",
      "impact": -8.5,
      "explanation": "Lower crop vigor detected from satellite"
    },
    {
      "feature": "Credit history",
      "impact": 12.3,
      "explanation": "Clean credit history"
    },
    {
      "feature": "Previous yield",
      "impact": 6.7,
      "explanation": "Strong previous yield"
    }
  ],
  "model_type": "deterministic",
  "computed_at": "2024-11-25T12:00:00Z"
}
```

**Highlight**:
- Score: 74.3 (High band)
- Top 3 drivers with human-readable explanations
- Transparent scoring logic

---

#### 5. Get Loan Quote (30 seconds)

```bash
curl -X POST http://localhost:8000/loan/quote \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "FRM000001",
    "requested_amount": 200000
  }'
```

**Expected Response**:
```json
{
  "farmer_id": "FRM000001",
  "credit_score": 74.3,
  "eligible": true,
  "max_loan_amount": 275000,
  "recommended_amount": 220000,
  "emi_plans": [
    {
      "emi_amount": 224800,
      "duration_months": 5,
      "interest_rate": 9.03,
      "total_repayment": 224800
    },
    {
      "emi_amount": 18567,
      "duration_months": 12,
      "interest_rate": 9.03,
      "total_repayment": 222804
    }
  ],
  "crop_cycle_months": 5,
  "remarks": "Excellent credit profile. Eligible for premium rates."
}
```

**Highlight**:
- Crop-cycle aligned EMI (5 months for wheat)
- Multiple repayment options
- Interest rate based on credit score

---

#### 6. View Score History (15 seconds)

```bash
curl -X GET http://localhost:8000/score/FRM000001/history \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Show**: Historical scores with timestamps and drivers.

---

## 6 Quick Manual Tests

### Test 1: System Health

```bash
curl http://localhost:8000/healthz
```

**Expected**: `{"status": "healthy", ...}`

---

### Test 2: Mock Agri Stack Integration

```bash
curl http://localhost:5001/mock/farmer/FRM000001
```

**Expected**: Farmer data with land parcels from mock Agri Stack.

---

### Test 3: Batch Scoring

```bash
curl -X POST http://localhost:8000/score/batch \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_ids": ["FRM000001", "FRM000002", "FRM000003"]
  }'
```

**Expected**: Job ID and status `"pending"`.

---

### Test 4: Job Status

```bash
curl -X GET http://localhost:8000/jobs/JOB_ID_HERE \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected**: Job status with progress.

---

### Test 5: Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

**Expected**: Prometheus-formatted metrics.

---

### Test 6: Frontend Access

**Navigate to**: http://localhost:3000

**Expected**: React frontend loads (login page).

---

## Acceptance Criteria Checklist

- [ ] `docker-compose up` brings up all services without errors
- [ ] Frontend accessible at http://localhost:3000
- [ ] API Swagger UI accessible at http://localhost:8000/docs
- [ ] Dashboard accessible at http://localhost:3001
- [ ] Onboarding a farmer via API returns 201 Created
- [ ] Score computation returns score (0-100) with 3 drivers
- [ ] Drivers have human-readable explanations
- [ ] Loan quote returns EMI plans aligned with crop cycle
- [ ] Health check returns `"healthy"`
- [ ] Metrics endpoint returns Prometheus format
- [ ] Mock Agri Stack returns farmer data
- [ ] Batch scoring creates job with ID

---

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs api
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Database connection errors

```bash
# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready

# Check database
docker-compose exec postgres psql -U postgres -d fcs -c "\dt"
```

### Port conflicts

```bash
# Stop conflicting services
docker-compose down

# Change ports in docker-compose.yml if needed
```

---

## Demo Tips

1. **Preparation**: Start services 5 minutes before demo
2. **Backup**: Have curl commands ready in a script
3. **Visuals**: Show Swagger UI for interactive exploration
4. **Highlight**: Emphasize transparency (SHAP drivers)
5. **Questions**: Be ready to explain scoring formula

---

## Next Steps After Demo

1. **Explore API**: Try all endpoints in Swagger UI
2. **View Data**: Check `sample_data/farmers.csv`
3. **Read Docs**: See `MODEL.md` for scoring details
4. **Deploy**: Follow `README.md` for Kubernetes deployment
5. **Customize**: Modify features in `services/ml/features.py`

---

**Demo Duration**: 3-5 minutes  
**Difficulty**: Easy  
**Prerequisites**: Docker, curl  
**Contact**: demo@example.com

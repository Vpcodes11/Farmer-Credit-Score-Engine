# Farmer Credit Score Engine

**Transparent credit scoring for farmers using Agri Stack data + satellite/weather/alternative data**

[![CI](https://github.com/youruser/farmer-credit-score-engine/workflows/CI/badge.svg)](https://github.com/youruser/farmer-credit-score-engine/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Overview

The Farmer Credit Score Engine is a production-ready microservices platform that computes transparent credit scores (0-100) for farmers. It combines:

- **Agri Stack data**: Land records, crop registry, farmer profiles
- **Satellite imagery**: NDVI vegetation indices for crop health
- **Weather data**: Rainfall patterns and anomalies
- **Alternative data**: UPI transactions, FPO membership, market access

**Key Features:**
- ✅ Transparent scoring with SHAP explainability (top 3 drivers)
- ✅ REST APIs for banks and field agents
- ✅ Offline-first PWA for rural connectivity
- ✅ Crop-cycle aligned EMI plans
- ✅ Full Docker + Kubernetes deployment
- ✅ CI/CD with GitHub Actions

## 🚀 Quick Start

### Local Development (Docker Compose)

```bash
# Clone repository
git clone https://github.com/youruser/farmer-credit-score-engine.git
cd farmer-credit-score-engine

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Access Points:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:3001
- Mock Agri Stack: http://localhost:5001

### Production Deployment (Kubernetes)

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n fcs-engine
kubectl get services -n fcs-engine

# Access via Ingress
# Configure DNS: fcs.example.com -> Ingress IP
```

## 📁 Project Structure

```
farmer-credit-score-engine/
├── services/
│   ├── api/              # FastAPI REST API
│   ├── worker/           # Celery background workers
│   ├── ml/               # ML scoring module (RandomForest + SHAP)
│   ├── frontend/         # React PWA for field agents
│   ├── dashboard/        # React admin dashboard for banks
│   └── mock-agri-stack/  # Simulated Agri Stack API
├── sample_data/          # Synthetic farmer data (200 records)
├── scripts/              # Deployment and data generation scripts
├── k8s/                  # Kubernetes manifests
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Local development setup
└── README.md
```

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   API (8000) │─────▶│  PostgreSQL │
│  (React PWA)│      │   (FastAPI)  │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ Redis (Job Queue)
                            │
                            ├─────▶ Worker (Celery)
                            │
                            └─────▶ Mock Agri Stack
```

## 📊 Scoring Model

### Features (11 total)

| Feature | Weight | Description |
|---------|--------|-------------|
| `ndvi_mean` | 15% | Crop health from satellite |
| `past_kcc_defaults` | 15% | Credit history |
| `last_year_yield_est` | 12% | Previous yield |
| `ndvi_trend` | 10% | Crop vigor trend |
| `upi_txn_freq` | 10% | Digital transaction activity |
| `land_area` | 8% | Farm size |
| `rainfall_anomaly_3mo` | 8% | Rainfall pattern |
| `crop_type` | 6% | Crop category |
| `market_price_volatility` | 6% | Price stability |
| `fpo_membership_flag` | 5% | FPO membership |
| `distance_to_mandi_km` | 5% | Market access |

### Scoring Logic

1. **Deterministic Fallback**: Weighted sum of normalized features (always available)
2. **RandomForest Model**: Trained on synthetic data with SHAP explainability
3. **Output**: Score (0-100) + Top 3 drivers with human-readable explanations

**Example Output:**
```json
{
  "score": 74,
  "score_band": "high",
  "drivers": [
    {
      "feature": "Crop health (satellite)",
      "impact": -12,
      "explanation": "Lower crop vigor detected from satellite"
    },
    {
      "feature": "Rainfall pattern",
      "impact": -8,
      "explanation": "Delayed rainfall observed"
    },
    {
      "feature": "Credit history",
      "impact": -6,
      "explanation": "1 default in KCC history"
    }
  ]
}
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register agent/bank user
- `POST /auth/login` - Login and get JWT token

### Farmers
- `POST /farmers` - Onboard new farmer
- `GET /farmers/{id}` - Get farmer profile + latest score
- `GET /farmers` - List all farmers

### Scoring
- `POST /score` - Compute score (synchronous)
- `GET /score/{farmer_id}/history` - Score history
- `POST /score/batch` - Batch scoring (async)

### Loan
- `POST /loan/quote` - Get loan eligibility + EMI plans

### System
- `GET /healthz` - Health check
- `GET /readyz` - Readiness check
- `GET /metrics` - Prometheus metrics
- `GET /jobs/{job_id}` - Job status

**Full API documentation**: http://localhost:8000/docs

## 🧪 Testing

```bash
# Unit tests
cd services/api
pytest --cov=. --cov-report=html

# Integration tests
docker-compose up -d postgres redis mock-agri-stack
pytest tests/test_integration.py

# E2E tests
npm run test:e2e

# Load test
python scripts/load_test.py --concurrent=100
```

## 📦 Deployment

### Docker Compose (Single Server)

```bash
# Production build
docker-compose -f docker-compose.yml up -d

# Scale API
docker-compose up -d --scale api=3

# View logs
docker-compose logs -f api
```

### Kubernetes (Cloud)

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy secrets (edit first!)
kubectl apply -f k8s/configmap.yaml

# Deploy all services
kubectl apply -f k8s/

# Monitor deployment
kubectl get pods -n fcs-engine -w

# Access logs
kubectl logs -f deployment/api -n fcs-engine
```

**Cloud Providers:**
- **AWS EKS**: See `infra/README.md#aws`
- **Azure AKS**: See `infra/README.md#azure`
- **Google GKE**: See `infra/README.md#gke`

## 🔧 Configuration

### Environment Variables

```bash
# API
API_HOST=0.0.0.0
API_PORT=8000
JWT_SECRET=your-secret-key-change-in-production

# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=fcs

# Redis
REDIS_URL=redis://redis:6379/0

# ML Model
MODEL_PATH=../ml/model.joblib
USE_ML_MODEL=true
```

See `.env.example` for full list.

## 📈 Observability

### Metrics (Prometheus)

```bash
# Scrape endpoint
curl http://localhost:8000/metrics

# Key metrics:
# - api_requests_total
# - api_request_duration_seconds
# - score_computations_total
```

### Logs (JSON structured)

```bash
# View API logs
docker-compose logs -f api

# Example log:
{"time": "2024-11-25T12:00:00", "level": "INFO", "message": "Score computed for FRM000001"}
```

### Health Checks

```bash
# Liveness
curl http://localhost:8000/healthz

# Readiness
curl http://localhost:8000/readyz
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Email**: support@example.com

## 🙏 Acknowledgments

- Synthetic data generated using realistic agricultural patterns
- SHAP library for model explainability
- FastAPI framework for high-performance APIs

---

**Built with ❤️ for transparent rural lending**

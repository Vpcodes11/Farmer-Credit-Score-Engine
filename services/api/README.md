# API Service

FastAPI-based REST API for the Farmer Credit Score Engine.

## Features

- JWT authentication
- Farmer onboarding and management
- Credit score computation (sync + async)
- Loan eligibility calculation
- SHAP-based explainability
- Health checks and metrics

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASS=postgres
export DB_NAME=fcs
export REDIS_URL=redis://localhost:6379/0
export JWT_SECRET=your-secret-key

# Run database migrations
python -c "from database import init_db; init_db()"

# Start server
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## Docker

```bash
# Build image
docker build -t fcs-api .

# Run container
docker run -p 8000:8000 \
  -e DB_HOST=postgres \
  -e REDIS_URL=redis://redis:6379/0 \
  fcs-api
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | Host to bind | `0.0.0.0` |
| `API_PORT` | Port to bind | `8000` |
| `JWT_SECRET` | JWT secret key | Required |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASS` | Database password | Required |
| `DB_NAME` | Database name | `fcs` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `MOCK_AGRI_URL` | Mock Agri Stack URL | `http://localhost:5001` |
| `MODEL_PATH` | Path to ML model | `../ml/model.joblib` |

## Project Structure

```
api/
├── main.py              # FastAPI application
├── config.py            # Configuration
├── database.py          # Database connection
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── auth.py              # Authentication utilities
├── routes/              # API route handlers
│   ├── auth.py
│   ├── farmers.py
│   ├── scoring.py
│   ├── loan.py
│   └── system.py
└── tests/               # Unit and integration tests
```

## License

MIT

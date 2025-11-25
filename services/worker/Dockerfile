FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Run Celery worker
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]

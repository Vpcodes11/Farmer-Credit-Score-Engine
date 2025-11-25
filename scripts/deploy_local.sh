#!/bin/bash

# Local Deployment Script for Farmer Credit Score Engine
# This script sets up the entire system locally using Docker Compose

set -e

echo "=========================================="
echo "Farmer Credit Score Engine - Local Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker found: $(docker --version)"
echo "✓ Docker Compose found: $(docker-compose --version)"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please edit .env file to set your secrets before production use"
    echo ""
fi

# Create Docker network
echo "Creating Docker network..."
docker network create fcs-network 2>/dev/null || echo "✓ Network already exists"
echo ""

# Pull images
echo "Pulling base images..."
docker-compose pull
echo ""

# Build services
echo "Building services..."
docker-compose build
echo ""

# Start services
echo "Starting services..."
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

services=("postgres" "redis" "mock-agri-stack" "api" "frontend" "dashboard")

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✓ $service is running"
    else
        echo "❌ $service failed to start"
    fi
done

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access Points:"
echo "  • Frontend:        http://localhost:3000"
echo "  • API Docs:        http://localhost:8000/docs"
echo "  • Dashboard:       http://localhost:3001"
echo "  • Mock Agri Stack: http://localhost:5001"
echo ""
echo "Quick Test:"
echo "  curl http://localhost:8000/healthz"
echo ""
echo "View Logs:"
echo "  docker-compose logs -f api"
echo ""
echo "Stop Services:"
echo "  docker-compose down"
echo ""
echo "For demo guide, see: DEMO.md"
echo "=========================================="

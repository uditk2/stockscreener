#!/bin/bash

# Stock Screener - Quick Start Script

echo "========================================"
echo "  Stock Screener - Starting Application"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your LLM_API_KEY if you want AI-powered analysis"
    echo ""
fi

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check health
echo ""
echo "Checking application health..."
curl -s http://localhost:8000/health | python -m json.tool

echo ""
echo "========================================"
echo "  Application Started Successfully!"
echo "========================================"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f api"
echo ""
echo "To stop:"
echo "  docker-compose down"
echo ""

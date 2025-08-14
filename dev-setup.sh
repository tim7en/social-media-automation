#!/bin/bash

# Development setup script

echo "🔧 Setting up development environment..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file - please configure your API keys"
fi

# Start Docker services for development
docker-compose up -d db redis

echo "⏳ Waiting for services..."
sleep 5

# Run migrations
alembic upgrade head

echo "✅ Development environment ready!"
echo ""
echo "🚀 To start the development server:"
echo "   source venv/bin/activate"
echo "   uvicorn src.main:app --reload"
echo ""
echo "🔧 To start Celery worker:"
echo "   celery -A src.core.celery_app worker --loglevel=info"

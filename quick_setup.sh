#!/usr/bin/env bash
# Quick dependency installation script

echo "=== Social Media Automation Platform - Quick Setup ==="
echo ""

# Ensure virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install core dependencies first
echo "Installing core dependencies..."
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv email-validator

# Install database dependencies
echo "Installing database dependencies..."
pip install sqlalchemy asyncpg alembic

# Install remaining dependencies individually (to handle conflicts)
echo "Installing remaining dependencies..."
pip install structlog
pip install openai anthropic requests
pip install celery flower redis
pip install python-jose[cryptography] python-multipart passlib[bcrypt]
pip install cryptography psutil
pip install starlette
pip install elevenlabs Pillow moviepy opencv-python numpy
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install facebook-sdk pytube instagrapi TikTokApi
pip install ffmpeg-python pydub whisper
pip install beautifulsoup4 scrapy feedparser
pip install APScheduler dramatiq
pip install psycopg2-binary boto3 minio
pip install sentry-sdk prometheus-client
pip install pytest pytest-asyncio black flake8 mypy pre-commit
pip install aiofiles httpx jinja2 python-slugify python-crontab

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "🚀 To launch the application:"
echo "   source .venv/bin/activate"
echo "   python -m src.main"
echo ""
echo "🌐 The application will be available at:"
echo "   - API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Celery Monitor: http://localhost:5555"
echo ""
echo "⚠️  Make sure Docker services are running:"
echo "   docker-compose up -d"

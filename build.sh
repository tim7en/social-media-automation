#!/bin/bash

# Social Media Automation Platform - Build Script

set -e

echo "🚀 Building Social Media Automation Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running the platform"
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p /tmp/generated_content
mkdir -p static/generated
mkdir -p logs

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Start services
echo "🔄 Starting services..."
docker-compose up -d db redis minio

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm app alembic upgrade head

echo "✅ Build completed successfully!"
echo ""
echo "🌐 Platform URLs:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Celery Monitor: http://localhost:5555"
echo "   - MinIO Console: http://localhost:9001"
echo ""
echo "🚀 To start the platform:"
echo "   docker-compose up -d"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "⚠️  Don't forget to configure your API keys in the .env file!"

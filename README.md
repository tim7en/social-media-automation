# Social Media Automation Platform

A comprehensive AI-powered content creation and social media automation platform that supports multiple platforms including YouTube, TikTok, Instagram, and Facebook. The platform can create faceless content using AI voiceovers or content with AI avatars.

## 🚀 Features

### AI Content Generation
- **Script Generation**: AI-powered script creation optimized for different platforms
- **Voice Synthesis**: ElevenLabs integration for high-quality voiceovers
- **Video Creation**: Automated video generation with customizable templates
- **Title & Description Generation**: Platform-optimized metadata creation
- **Hashtag Generation**: Trending and relevant hashtag suggestions

### Multi-Platform Publishing
- **YouTube**: Direct upload to YouTube with metadata
- **Instagram**: Automated posting to Instagram (Reels)
- **Facebook**: Video publishing to Facebook pages/profiles  
- **TikTok**: Content preparation for TikTok (manual upload required)
- **Batch Publishing**: Publish to multiple platforms simultaneously

### Analytics & Insights
- **Performance Tracking**: Monitor views, engagement, and growth
- **Platform Analytics**: Detailed metrics for each social platform
- **Trend Analysis**: Identify optimal posting times and content types
- **ROI Calculation**: Track return on investment for campaigns

### Automation & Scheduling
- **Content Campaigns**: Automated content generation workflows
- **Scheduled Publishing**: Plan and schedule content in advance
- **Background Processing**: Asynchronous content generation
- **Webhook Integration**: Real-time updates from social platforms

## 🛠 Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis
- **AI Services**: OpenAI GPT-4, ElevenLabs
- **Video Processing**: MoviePy, OpenCV
- **Social APIs**: YouTube Data API, Facebook Graph API, Instagram Basic Display API
- **Storage**: AWS S3 or MinIO (self-hosted)
- **Monitoring**: Flower (Celery), Structlog
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

1. **API Keys Required**:
   - OpenAI API key
   - ElevenLabs API key
   - Google/YouTube API credentials
   - Facebook/Instagram API tokens
   - (Optional) TikTok API access

2. **System Requirements**:
   - Docker & Docker Compose
   - 4GB+ RAM
   - 10GB+ storage space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd social-media-automation
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### 4. Alternative: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn src.main:app --reload --port 8000

# Start Celery worker (new terminal)
celery -A src.core.celery_app worker --loglevel=info

# Start Celery beat scheduler (new terminal)
celery -A src.core.celery_app beat --loglevel=info
```

## 📚 API Documentation

Once running, access:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Celery Monitor**: http://localhost:5555 (Flower)

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# AI Services
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_default_voice

# Social Media APIs  
YOUTUBE_API_KEY=your_youtube_key
FACEBOOK_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# Database & Redis
DATABASE_URL=postgresql://user:pass@localhost:5432/social_automation
REDIS_URL=redis://localhost:6379/0

# Storage (AWS S3 or MinIO)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket
```

### Content Generation Settings

```bash
# Video Configuration
DEFAULT_VIDEO_DURATION=60
MAX_VIDEO_SIZE_MB=50
CONTENT_OUTPUT_DIR=/tmp/generated_content

# AI Settings
OPENAI_MODEL=gpt-4-turbo-preview
```

## 💡 Usage Examples

### 1. Generate Complete Content

```python
import requests

# Request content generation
response = requests.post("http://localhost:8000/api/v1/content/generate", json={
    "title": "AI Content Creation Tips",
    "topic": "How to create engaging content with AI",
    "content_type": "video",
    "duration": 60,
    "style": "educational",
    "target_platforms": ["youtube", "instagram"],
    "project_id": 1
})

task_id = response.json()["task_id"]

# Check task status
status = requests.get(f"http://localhost:8000/api/v1/content/task/{task_id}")
print(status.json())
```

### 2. Publish to Multiple Platforms

```python
# Publish generated content
response = requests.post("http://localhost:8000/api/v1/platforms/publish", json={
    "video_path": "/tmp/generated_content/video_123.mp4",
    "platforms": ["youtube", "instagram"],
    "content_data": {
        "title": "AI Content Creation Tips",
        "description": "Learn how to create amazing content with AI...",
        "tags": ["AI", "content", "creation"],
        "hashtags": ["AI", "ContentCreation", "SocialMedia"]
    }
})
```

### 3. Get Analytics

```python
# Get analytics overview
response = requests.post("http://localhost:8000/api/v1/analytics/overview", json={
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-31T23:59:59",
    "platforms": ["youtube", "instagram"]
})

analytics = response.json()
print(f"Total views: {analytics['total_views']}")
print(f"Engagement rate: {analytics['engagement_rate']}%")
```

## 🔐 Authentication Setup

### YouTube/Google APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Set redirect URI to your application
6. Generate refresh token

### Facebook/Instagram APIs

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login and Instagram products
4. Generate access tokens
5. Set up webhooks for real-time updates

### ElevenLabs

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Get API key from dashboard
3. Note your preferred voice IDs

## 📊 Monitoring & Logging

### Celery Monitoring
- Access Flower at `http://localhost:5555`
- Monitor task queues, workers, and execution

### Application Logs
```bash
# View application logs
docker-compose logs -f app

# View worker logs  
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

### Database Management
```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d social_automation

# Run migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

## 🔧 Development

### Adding New Platforms

1. Create new publisher in `src/services/social_publisher.py`
2. Add platform to schemas in `src/schemas/schemas.py`
3. Update API routes in `src/api/routers/platforms.py`
4. Add platform-specific tasks in `src/tasks/`

### Custom Content Templates

1. Create templates in `src/services/video_processor.py`
2. Add template configurations
3. Update content generation logic

### Extending AI Capabilities

1. Add new AI services in `src/services/`
2. Update content generation workflows
3. Add new task types in `src/tasks/`

## 🚨 Important Notes

### Platform API Limitations

- **TikTok**: Requires special API approval for automated posting
- **Instagram**: Limited by Instagram Basic Display API capabilities  
- **Facebook**: Requires page management permissions
- **YouTube**: Subject to quota limits and policies

### Content Guidelines

- Ensure all generated content complies with platform policies
- Review AI-generated content before publishing
- Respect copyright and intellectual property rights
- Follow community guidelines for each platform

### Security Considerations

- Store API keys securely (use environment variables)
- Implement rate limiting for API endpoints
- Use HTTPS in production
- Regularly rotate access tokens
- Monitor for unusual activity

## 📈 Scaling

### Production Deployment

1. Use proper secrets management (AWS Secrets Manager, etc.)
2. Set up load balancing for multiple app instances
3. Use managed database services (AWS RDS, etc.)
4. Implement proper monitoring (Prometheus, Grafana)
5. Set up CI/CD pipelines

### Performance Optimization

1. Scale Celery workers based on load
2. Use Redis Cluster for high availability
3. Implement caching strategies
4. Optimize database queries
5. Use CDN for static content

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review logs for error details
3. Check platform API status pages
4. Verify API key validity and permissions

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Note**: This platform is designed for educational and legitimate content creation purposes. Users are responsible for ensuring compliance with all applicable laws, platform terms of service, and content policies.

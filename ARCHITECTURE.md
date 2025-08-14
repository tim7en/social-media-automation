# Project Structure

```
social-media-automation/
├── src/                           # Main application source code
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/                       # API layer
│   │   └── routers/               # API route handlers
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── content.py         # Content generation endpoints
│   │       ├── platforms.py       # Social media platform endpoints
│   │       ├── analytics.py       # Analytics endpoints
│   │       └── webhooks.py        # Webhook handlers
│   ├── core/                      # Core application components
│   │   ├── __init__.py
│   │   ├── config.py              # Application configuration
│   │   ├── database.py            # Database connection and setup
│   │   ├── logger.py              # Logging configuration
│   │   ├── redis.py               # Redis connection manager
│   │   └── celery_app.py          # Celery configuration
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   └── models.py              # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py             # Request/response schemas
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── ai_content_generator.py    # AI content generation
│   │   ├── voice_generator.py         # ElevenLabs voice synthesis
│   │   ├── video_processor.py         # Video creation and editing
│   │   └── social_publisher.py        # Social media publishing
│   └── tasks/                     # Celery background tasks
│       ├── __init__.py
│       ├── content_generation.py  # Content generation tasks
│       ├── social_publishing.py   # Publishing tasks
│       └── analytics.py           # Analytics collection tasks
├── alembic/                       # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── static/                        # Static files
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Docker services configuration
├── Dockerfile                     # Application Docker image
├── alembic.ini                    # Alembic configuration
├── build.sh                       # Build script
├── dev-setup.sh                   # Development setup script
└── README.md                      # Project documentation
```

## Key Components

### 1. API Layer (`src/api/`)
- RESTful API built with FastAPI
- Modular router structure for different functionalities
- Authentication and authorization
- Request/response validation with Pydantic

### 2. Core Services (`src/services/`)
- **AIContentGenerator**: OpenAI integration for script generation
- **VoiceGenerator**: ElevenLabs integration for voice synthesis
- **VideoProcessor**: MoviePy-based video creation and editing
- **SocialMediaPublisher**: Multi-platform publishing capabilities

### 3. Background Tasks (`src/tasks/`)
- Celery-based asynchronous task processing
- Content generation pipeline
- Social media publishing workflows
- Analytics data collection

### 4. Database Layer (`src/models/`)
- SQLAlchemy ORM models
- PostgreSQL database support
- Alembic migrations for schema management

### 5. Configuration (`src/core/`)
- Centralized configuration management
- Database and Redis connections
- Logging setup
- Celery configuration

## Database Models

### User Management
- **User**: User accounts and authentication
- **Project**: Content projects organization

### Content Management
- **ContentItem**: Generated content (scripts, videos, etc.)
- **Template**: Reusable content templates
- **Campaign**: Automated content campaigns

### Social Media Integration
- **SocialAccount**: Connected social media accounts
- **Publication**: Published content tracking
- **APIUsage**: API usage and cost tracking

### Analytics
- Built-in analytics tracking for all publications
- Performance metrics collection
- ROI calculation capabilities

## API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /me` - Current user info
- `POST /refresh` - Token refresh

### Content Generation (`/api/v1/content/`)
- `POST /generate` - Generate complete content
- `POST /script` - Generate script only
- `POST /voice` - Generate voice audio
- `POST /video` - Create video
- `GET /task/{id}` - Check task status

### Social Platforms (`/api/v1/platforms/`)
- `POST /accounts` - Add social account
- `GET /accounts` - List social accounts
- `POST /publish` - Publish to multiple platforms
- `GET /analytics/{platform}/{post_id}` - Get post analytics

### Analytics (`/api/v1/analytics/`)
- `POST /overview` - Analytics overview
- `GET /platforms/{platform}` - Platform-specific analytics
- `GET /trends` - Trending topics and insights

## Background Processing

### Content Generation Pipeline
1. **Script Generation**: AI-powered script creation
2. **Voice Synthesis**: ElevenLabs audio generation
3. **Video Creation**: Automated video compilation
4. **Metadata Generation**: Titles, descriptions, hashtags

### Publishing Workflow
1. **Platform Preparation**: Format content for each platform
2. **Authentication**: Verify social media credentials
3. **Upload**: Publish content to selected platforms
4. **Tracking**: Monitor publication status

### Analytics Collection
1. **Data Fetching**: Collect metrics from platform APIs
2. **Processing**: Calculate engagement rates and trends
3. **Storage**: Update database with latest metrics
4. **Reporting**: Generate insights and recommendations

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management

### AI and Media Processing
- **OpenAI**: GPT-4 for content generation
- **ElevenLabs**: High-quality voice synthesis
- **MoviePy**: Video editing and composition
- **OpenCV**: Computer vision for video processing

### Task Processing
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **Flower**: Celery monitoring interface

### Social Media APIs
- **YouTube Data API v3**: YouTube integration
- **Facebook Graph API**: Facebook/Instagram publishing
- **Instagram Basic Display API**: Instagram content management
- **TikTok API**: TikTok content preparation

### Infrastructure
- **PostgreSQL**: Primary database
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **MinIO**: S3-compatible object storage

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Secure password hashing with bcrypt
- Token refresh mechanism

### API Security
- CORS protection
- Rate limiting capabilities
- Input validation and sanitization
- Secure credential storage

### Platform Integration
- OAuth 2.0 for social media APIs
- Encrypted credential storage
- Token management and refresh
- Webhook signature verification

## Monitoring & Observability

### Logging
- Structured logging with structlog
- JSON format for production
- Multiple log levels and filtering
- Centralized log aggregation ready

### Monitoring
- Celery task monitoring with Flower
- Database connection monitoring
- API endpoint health checks
- External service status tracking

### Error Handling
- Comprehensive exception handling
- Graceful degradation for service failures
- Retry mechanisms for external APIs
- User-friendly error messages

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Load balancer ready
- Database connection pooling
- Distributed task processing

### Performance Optimization
- Async/await for I/O operations
- Database query optimization
- Redis caching for frequent data
- Background processing for heavy tasks

### Resource Management
- Configurable worker processes
- Memory-efficient video processing
- Temporary file cleanup
- Resource usage monitoring

This architecture provides a solid foundation for a production-ready social media automation platform with room for future enhancements and scaling.

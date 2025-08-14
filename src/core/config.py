from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import secrets
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with enhanced validation and security"""
    
    # Application
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/social_automation"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = ""
    
    # Google/YouTube
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""
    YOUTUBE_API_KEY: str = ""
    
    # Facebook/Instagram
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_ACCESS_TOKEN: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    
    # TikTok
    TIKTOK_ACCESS_TOKEN: str = ""
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    
    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"
    
    # MinIO (alternative storage)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "social-media-content"
    
    # Content Settings
    DEFAULT_VIDEO_DURATION: int = 60
    MAX_VIDEO_SIZE_MB: int = 50
    CONTENT_OUTPUT_DIR: str = "./output"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # AI Avatar
    HEYGEN_API_KEY: str = ""
    D_ID_API_KEY: str = ""
    
    # Webhooks
    WEBHOOK_BASE_URL: str = "https://your-domain.com/webhooks"
    
    # Security Settings
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 900  # 15 minutes
    MAX_REQUEST_SIZE_MB: int = 10
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Performance Settings
    CACHE_TTL_SECONDS: int = 3600
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    WORKER_TIMEOUT: int = 300
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields from environment
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_settings()
        self._setup_directories()
    
    def _validate_settings(self):
        """Validate critical settings and provide warnings"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Security validations
        if self.SECRET_KEY == "your-super-secret-key-change-in-production":
            if not self.DEBUG:
                raise ValueError("SECRET_KEY must be changed in production!")
            logger.warning("Using default SECRET_KEY in development mode")
        
        if len(self.SECRET_KEY) < 32:
            logger.warning("SECRET_KEY should be at least 32 characters long")
        
        # Environment-specific validations
        if not self.DEBUG:  # Production mode
            if not self.SENTRY_DSN:
                logger.warning("SENTRY_DSN not configured for production monitoring")
            
            if "localhost" in self.DATABASE_URL:
                logger.warning("Using localhost database URL in production")
            
            if self.ALLOWED_ORIGINS == ["*"]:
                logger.warning("CORS allows all origins in production - security risk")
        
        # API key validations (warn if missing but don't fail)
        required_for_full_functionality = {
            "OPENAI_API_KEY": "AI content generation",
            "ELEVENLABS_API_KEY": "Voice synthesis",
        }
        
        for key, feature in required_for_full_functionality.items():
            if not getattr(self, key):
                logger.warning(f"{key} not configured - {feature} will be disabled")
    
    def _setup_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.CONTENT_OUTPUT_DIR,
            os.path.join(self.CONTENT_OUTPUT_DIR, "temp"),
            os.path.join(self.CONTENT_OUTPUT_DIR, "cache"),
            "logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return not self.DEBUG and self.ENVIRONMENT.lower() == "production"
    
    @property
    def database_config(self) -> dict:
        """Get database configuration for SQLAlchemy"""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        }
    
    def get_api_keys_status(self) -> dict:
        """Get status of all API keys (without exposing the keys)"""
        keys = {
            "openai": bool(self.OPENAI_API_KEY),
            "anthropic": bool(self.ANTHROPIC_API_KEY),
            "elevenlabs": bool(self.ELEVENLABS_API_KEY),
            "google": bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET),
            "youtube": bool(self.YOUTUBE_API_KEY),
            "facebook": bool(self.FACEBOOK_APP_ID and self.FACEBOOK_APP_SECRET),
            "instagram": bool(self.INSTAGRAM_ACCESS_TOKEN),
            "tiktok": bool(self.TIKTOK_ACCESS_TOKEN),
            "aws": bool(self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY),
            "heygen": bool(self.HEYGEN_API_KEY),
            "d_id": bool(self.D_ID_API_KEY),
        }
        return keys
    
    def generate_secure_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)


settings = Settings()


def get_settings() -> Settings:
    """Dependency to get settings instance"""
    return settings


def validate_environment():
    """Validate environment setup and provide detailed report"""
    import sys
    import psutil
    
    report = {
        "python_version": sys.version,
        "platform": sys.platform,
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_free_gb": round(psutil.disk_usage("/").free / (1024**3), 2),
        "settings_valid": True,
        "errors": [],
        "warnings": [],
        "api_keys_configured": settings.get_api_keys_status()
    }
    
    try:
        # Test settings validation
        settings._validate_settings()
    except Exception as e:
        report["settings_valid"] = False
        report["errors"].append(f"Settings validation failed: {str(e)}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        report["errors"].append("Python 3.8+ is required")
    
    # Check available memory
    if report["memory_gb"] < 2:
        report["warnings"].append("Less than 2GB RAM available - may cause issues")
    
    # Check disk space
    if report["disk_free_gb"] < 1:
        report["warnings"].append("Less than 1GB disk space available")
    
    return report

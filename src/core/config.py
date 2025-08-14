from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
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
    CONTENT_OUTPUT_DIR: str = "/tmp/generated_content"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # AI Avatar
    HEYGEN_API_KEY: str = ""
    D_ID_API_KEY: str = ""
    
    # Webhooks
    WEBHOOK_BASE_URL: str = "https://your-domain.com/webhooks"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

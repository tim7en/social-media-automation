from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"


class Platform(str, Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ServiceType(str, Enum):
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"
    FLIKI = "fliki"
    HEYGEN = "heygen"
    CAPCUT = "capcut"
    CANVA = "canva"
    RUNWAY = "runway"
    PIKA = "pika"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class Project(ProjectBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Content Generation Schemas
class ContentGenerationRequest(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    project_id: int
    
    # AI Settings
    topic: str
    style: Optional[str] = "engaging"
    duration: Optional[int] = 60  # seconds for video
    voice_id: Optional[str] = None  # ElevenLabs voice ID
    use_avatar: Optional[bool] = False
    
    # Platform-specific settings
    target_platforms: List[Platform] = []
    
    # Advanced settings
    ai_model: Optional[str] = "gpt-4-turbo-preview"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000


class ContentItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content_type: ContentType
    status: ContentStatus
    script: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    file_paths: Optional[Dict[str, str]] = None
    ai_settings: Optional[Dict[str, Any]] = None
    project_id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    project_id: int


class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ContentStatus] = None
    script: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Social Account Schemas
class SocialAccountBase(BaseModel):
    platform: Platform
    account_name: str
    account_id: Optional[str] = None


class SocialAccountCreate(SocialAccountBase):
    credentials: Dict[str, Any]


class SocialAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SocialAccount(SocialAccountBase):
    id: int
    user_id: int
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Campaign Schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None
    target_platforms: List[Platform] = []
    content_templates: Optional[Dict[str, Any]] = None
    ai_settings: Optional[Dict[str, Any]] = None


class CampaignCreate(CampaignBase):
    project_id: int


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None
    target_platforms: Optional[List[Platform]] = None
    is_active: Optional[bool] = None


class Campaign(CampaignBase):
    id: int
    project_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Publication Schemas
class PublicationBase(BaseModel):
    platform: Platform
    scheduled_at: Optional[datetime] = None


class PublicationCreate(PublicationBase):
    content_item_id: int
    campaign_id: Optional[int] = None


class Publication(PublicationBase):
    id: int
    content_item_id: int
    campaign_id: Optional[int] = None
    platform_post_id: Optional[str] = None
    status: str
    published_at: Optional[datetime] = None
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    platforms: Optional[List[Platform]] = None
    content_types: Optional[List[ContentType]] = None


class AnalyticsResponse(BaseModel):
    total_publications: int
    total_views: int
    total_engagement: int
    engagement_rate: float
    platform_breakdown: Dict[str, Dict[str, Any]]
    top_performing_content: List[Dict[str, Any]]
    trends: Dict[str, Any]


# Template Schemas
class TemplateBase(BaseModel):
    name: str
    category: str
    template_data: Dict[str, Any]
    is_public: bool = False


class TemplateCreate(TemplateBase):
    pass


class Template(TemplateBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# API Key Schemas
class ApiKeyBase(BaseModel):
    service_name: ServiceType
    api_key: str


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyUpdate(BaseModel):
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class ApiKey(BaseModel):
    id: int
    user_id: int
    service_name: ServiceType
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApiKeyList(BaseModel):
    service_name: ServiceType
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Response Schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class TaskResponse(BaseModel):
    task_id: str
    message: str
    status: str = "processing"

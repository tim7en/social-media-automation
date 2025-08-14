from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import uuid


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    content_items = relationship("ContentItem", back_populates="creator")
    api_keys = relationship("ApiKey", back_populates="user")


class Project(Base):
    """Content project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    settings = Column(JSON)  # Project-specific settings
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    content_items = relationship("ContentItem", back_populates="project")
    campaigns = relationship("Campaign", back_populates="project")


class ContentItem(Base):
    """Generated content item"""
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)  # video, image, text, audio
    status = Column(String, default="draft")  # draft, processing, ready, published, failed
    
    # Content data
    script = Column(Text)  # Generated script/text
    content_metadata = Column(JSON)  # Additional metadata
    file_paths = Column(JSON)  # Paths to generated files
    
    # AI settings used
    ai_settings = Column(JSON)
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    project = relationship("Project", back_populates="content_items")
    creator = relationship("User", back_populates="content_items")
    publications = relationship("Publication", back_populates="content_item")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ApiKey(Base):
    """User API keys for external services"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_name = Column(String, nullable=False)  # openai, elevenlabs, fliki, heygen, etc.
    api_key = Column(String, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class SocialAccount(Base):
    """Social media account credentials"""
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(String, nullable=False)  # youtube, tiktok, instagram, facebook
    account_name = Column(String, nullable=False)
    account_id = Column(String)  # Platform-specific account ID
    credentials = Column(JSON)  # Encrypted credentials
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Campaign(Base):
    """Content campaign for scheduled publishing"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Scheduling
    schedule_config = Column(JSON)  # Cron-like scheduling configuration
    is_active = Column(Boolean, default=True)
    
    # Target platforms
    target_platforms = Column(JSON)  # List of platforms to publish to
    
    # Content generation settings
    content_templates = Column(JSON)
    ai_settings = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="campaigns")
    publications = relationship("Publication", back_populates="campaign")


class Publication(Base):
    """Publication record for tracking published content"""
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    platform = Column(String, nullable=False)
    platform_post_id = Column(String)  # Platform-specific post ID
    
    status = Column(String, default="pending")  # pending, published, failed
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    
    # Analytics data
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Additional platform-specific metrics
    metrics = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="publications")
    campaign = relationship("Campaign", back_populates="publications")


class Template(Base):
    """Content templates"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # script, visual, audio
    template_data = Column(JSON)  # Template structure and settings
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class APIUsage(Base):
    """Track API usage and costs"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service = Column(String, nullable=False)  # openai, elevenlabs, etc.
    endpoint = Column(String)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    request_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

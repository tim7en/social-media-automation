"""
Comprehensive input validation for the social media automation platform.
"""
import re
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class ContentGenerationRequest(BaseModel):
    """Validation for content generation requests"""
    title: str = Field(..., min_length=1, max_length=200, description="Content title")
    topic: str = Field(..., min_length=5, max_length=500, description="Content topic/description")
    content_type: str = Field(..., regex="^(video|image|text|audio)$", description="Type of content to generate")
    duration: Optional[int] = Field(30, ge=15, le=600, description="Duration in seconds for video/audio content")
    style: Optional[str] = Field("casual", regex="^(casual|professional|educational|entertaining|promotional)$")
    target_platforms: List[str] = Field(..., min_items=1, description="Target social media platforms")
    project_id: Optional[int] = Field(None, ge=1, description="Associated project ID")
    
    @validator("target_platforms")
    def validate_platforms(cls, v):
        valid_platforms = {"youtube", "instagram", "facebook", "tiktok", "twitter", "linkedin"}
        invalid_platforms = set(v) - valid_platforms
        if invalid_platforms:
            raise ValueError(f"Invalid platforms: {invalid_platforms}. Valid platforms: {valid_platforms}")
        return v
    
    @validator("title", "topic")
    def validate_text_content(cls, v, field):
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'<iframe.*?>',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Invalid content detected in {field.name}")
        
        return v.strip()


class PublishRequest(BaseModel):
    """Validation for content publishing requests"""
    content_id: int = Field(..., ge=1, description="Content ID to publish")
    platforms: List[str] = Field(..., min_items=1, description="Platforms to publish to")
    schedule_time: Optional[str] = Field(None, description="ISO format schedule time")
    custom_metadata: Optional[Dict[str, Any]] = Field({}, description="Platform-specific metadata")
    
    @validator("platforms")
    def validate_platforms(cls, v):
        valid_platforms = {"youtube", "instagram", "facebook", "tiktok", "twitter", "linkedin"}
        invalid_platforms = set(v) - valid_platforms
        if invalid_platforms:
            raise ValueError(f"Invalid platforms: {invalid_platforms}")
        return v
    
    @validator("schedule_time")
    def validate_schedule_time(cls, v):
        if v:
            from datetime import datetime
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
        return v


class AnalyticsRequest(BaseModel):
    """Validation for analytics requests"""
    start_date: str = Field(..., description="Start date in ISO format")
    end_date: str = Field(..., description="End date in ISO format")
    platforms: Optional[List[str]] = Field(None, description="Platforms to analyze")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")
    
    @validator("start_date", "end_date")
    def validate_dates(cls, v):
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
        return v
    
    @validator("platforms")
    def validate_platforms(cls, v):
        if v:
            valid_platforms = {"youtube", "instagram", "facebook", "tiktok", "twitter", "linkedin"}
            invalid_platforms = set(v) - valid_platforms
            if invalid_platforms:
                raise ValueError(f"Invalid platforms: {invalid_platforms}")
        return v


class UserRegistrationRequest(BaseModel):
    """Validation for user registration"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    terms_accepted: bool = Field(..., description="User must accept terms")
    
    @validator("password")
    def validate_password(cls, v):
        # Check password strength
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @validator("full_name")
    def validate_name(cls, v):
        # Remove extra whitespace and validate
        name = re.sub(r'\s+', ' ', v.strip())
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
            raise ValueError("Name can only contain letters, spaces, hyphens, apostrophes, and periods")
        return name
    
    @validator("terms_accepted")
    def validate_terms(cls, v):
        if not v:
            raise ValueError("Terms and conditions must be accepted")
        return v


class ProjectRequest(BaseModel):
    """Validation for project creation/update"""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    target_audience: Optional[str] = Field(None, max_length=200, description="Target audience description")
    content_themes: Optional[List[str]] = Field([], description="Content themes/topics")
    brand_guidelines: Optional[Dict[str, Any]] = Field({}, description="Brand guidelines and preferences")
    
    @validator("name")
    def validate_name(cls, v):
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', v.strip())
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
            raise ValueError("Project name can only contain letters, numbers, spaces, hyphens, underscores, and periods")
        return name
    
    @validator("content_themes")
    def validate_themes(cls, v):
        if len(v) > 20:
            raise ValueError("Maximum 20 content themes allowed")
        return [theme.strip() for theme in v if theme.strip()]


def validate_file_upload(file_data: bytes, filename: str, allowed_types: List[str], max_size_mb: int = 50) -> bool:
    """Validate uploaded files"""
    
    # Check file size
    if len(file_data) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )
    
    # Check file extension
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )
    
    # Basic file header validation for common types
    file_signatures = {
        'jpg': [b'\xff\xd8\xff'],
        'jpeg': [b'\xff\xd8\xff'],
        'png': [b'\x89\x50\x4e\x47'],
        'gif': [b'\x47\x49\x46\x38'],
        'mp4': [b'\x00\x00\x00\x18\x66\x74\x79\x70\x6d\x70\x34'],
        'pdf': [b'\x25\x50\x44\x46'],
        'txt': [],  # Text files don't have a specific signature
        'json': []  # JSON files don't have a specific signature
    }
    
    if file_extension in file_signatures and file_signatures[file_extension]:
        valid_signature = False
        for signature in file_signatures[file_extension]:
            if file_data.startswith(signature):
                valid_signature = True
                break
        
        if not valid_signature:
            raise HTTPException(
                status_code=400,
                detail="File content doesn't match file extension"
            )
    
    return True


def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """Sanitize text input to prevent XSS and injection attacks"""
    if not text:
        return ""
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove or escape dangerous characters
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#x27;')
    text = text.replace('&', '&amp;')
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_api_key(api_key: str, key_type: str) -> bool:
    """Validate API key format based on provider"""
    
    key_patterns = {
        'openai': r'^sk-[a-zA-Z0-9]{48}$',
        'elevenlabs': r'^[a-f0-9]{32}$',
        'google': r'^[a-zA-Z0-9_-]{39}$',
        'facebook': r'^[a-zA-Z0-9]{32,}$',
        'generic': r'^[a-zA-Z0-9_-]{8,}$'
    }
    
    pattern = key_patterns.get(key_type, key_patterns['generic'])
    
    if not re.match(pattern, api_key):
        logger.warning(f"Invalid {key_type} API key format provided")
        return False
    
    return True


def validate_webhook_payload(payload: Dict[str, Any], expected_fields: List[str]) -> bool:
    """Validate webhook payload structure"""
    
    # Check required fields
    missing_fields = set(expected_fields) - set(payload.keys())
    if missing_fields:
        logger.warning(f"Webhook payload missing required fields: {missing_fields}")
        return False
    
    # Check for suspicious content in string fields
    for key, value in payload.items():
        if isinstance(value, str):
            if len(value) > 10000:  # Arbitrary large size limit
                logger.warning(f"Webhook payload field '{key}' exceeds size limit")
                return False
            
            # Check for suspicious patterns
            if re.search(r'<script|javascript:|eval\(|<iframe', value, re.IGNORECASE):
                logger.warning(f"Suspicious content detected in webhook field '{key}'")
                return False
    
    return True
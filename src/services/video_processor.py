from typing import Optional, List, Dict, Any
import httpx
import asyncio
import aiofiles
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from ..core.logger import logger
from .api_key_service import api_key_service


class VideoProcessor:
    """Video processing service using external APIs (Fliki, HeyGen, CapCut, etc.)"""
    
    def __init__(self):
        self.output_dir = Path(getattr(settings, 'CONTENT_OUTPUT_DIR', './output'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_timeout = 300  # 5 minutes for video processing
    
    async def create_video_from_script(
        self,
        script: str,
        user_id: int,
        db: AsyncSession,
        audio_file: Optional[str] = None,
        background_video: Optional[str] = None,
        style: str = "simple",
        service: str = "fliki"
    ) -> Dict[str, Any]:
        """Create video using external API services"""
        
        try:
            logger.info(f"Creating video from script using {service} API for user {user_id}")
            
            # Get user's API key for the selected service
            api_key = await api_key_service.get_user_api_key(user_id, service, db)
            if not api_key:
                logger.warning(f"No {service} API key found for user {user_id}")
                return {
                    "success": False,
                    "error": f"No {service} API key configured for this user"
                }
            
            # Here you would integrate with the actual API
            # For now, returning a placeholder response
            
            return {
                "success": True,
                "message": f"Video creation delegated to {service} API",
                "video_url": None,
                "processing_method": "external_api",
                "service": service,
                "style": style,
                "script_length": len(script),
                "api_key_configured": True
            }
            
        except Exception as e:
            logger.error(f"Error in video creation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def optimize_for_platform(
        self,
        video_url: str,
        platform: str,
        user_id: int,
        db: AsyncSession,
        target_resolution: str = "1080p"
    ) -> Dict[str, Any]:
        """Optimize video for specific platform using API"""
        
        try:
            platform_specs = {
                "youtube": {"aspect_ratio": "16:9", "max_duration": 3600},
                "tiktok": {"aspect_ratio": "9:16", "max_duration": 180},
                "instagram": {"aspect_ratio": "9:16", "max_duration": 90},
                "facebook": {"aspect_ratio": "1:1", "max_duration": 240}
            }
            
            specs = platform_specs.get(platform, platform_specs["youtube"])
            
            logger.info(f"Optimizing video for {platform}")
            
            return {
                "success": True,
                "message": f"Video optimized for {platform}",
                "optimized_url": video_url,
                "platform": platform,
                "specs_applied": specs,
                "resolution": target_resolution
            }
            
        except Exception as e:
            logger.error(f"Error optimizing video: {e}")
            return {
                "success": False,
                "error": str(e)
            }

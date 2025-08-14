"""
Fliki Integration for Starter Pro Workflow
AI-powered voiceovers and video creation
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from ...core.config import settings
from ...core.logger import logger


class FlikiIntegration:
    """Fliki API integration for AI voiceovers and video creation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'FLIKI_API_KEY', '')
        self.base_url = "https://api.fliki.ai/v1"
        self.default_voice = "en-US-Neural2-A"  # Premium voice
    
    async def create_video_from_script(
        self,
        script: str,
        voice_id: Optional[str] = None,
        video_style: str = "professional",
        background_music: bool = True,
        auto_scenes: bool = True
    ) -> Dict[str, Any]:
        """Create video using Fliki from script"""
        
        try:
            # Prepare request data
            request_data = {
                "script": script,
                "voice": {
                    "id": voice_id or self.default_voice,
                    "speed": 1.0,
                    "pitch": 1.0
                },
                "video_settings": {
                    "style": video_style,
                    "aspect_ratio": "9:16",  # Vertical for social media
                    "resolution": "1080p",
                    "auto_scenes": auto_scenes,
                    "background_music": background_music,
                    "duration_per_scene": 4
                },
                "export_format": "mp4"
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/videos",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    video_id = result.get("video_id")
                    
                    # Poll for completion
                    video_url = await self._wait_for_video_completion(video_id)
                    
                    return {
                        "success": True,
                        "video_id": video_id,
                        "video_url": video_url,
                        "duration": result.get("estimated_duration"),
                        "scenes_count": result.get("scenes_count")
                    }
                else:
                    logger.error(f"Fliki API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating Fliki video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_video_completion(self, video_id: str, max_wait: int = 600) -> Optional[str]:
        """Wait for video processing to complete"""
        
        wait_time = 0
        check_interval = 30  # Check every 30 seconds
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/videos/{video_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("video_url")
                        elif status == "failed":
                            logger.error(f"Fliki video processing failed: {data.get('error')}")
                            return None
                        
                        # Still processing, wait more
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                        
                        logger.info(f"Fliki video {video_id} still processing... ({wait_time}s)")
                    else:
                        logger.error(f"Error checking video status: {response.status_code}")
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking video completion: {e}")
                return None
        
        logger.error(f"Fliki video {video_id} processing timeout after {max_wait}s")
        return None
    
    async def get_available_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        """Get available voices for the language"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"language": language}
                )
                
                if response.status_code == 200:
                    voices = response.json().get("voices", [])
                    
                    # Format for easier use
                    formatted_voices = []
                    for voice in voices:
                        formatted_voices.append({
                            "id": voice.get("id"),
                            "name": voice.get("name"),
                            "gender": voice.get("gender"),
                            "accent": voice.get("accent"),
                            "quality": voice.get("quality"),
                            "is_premium": voice.get("is_premium", False),
                            "sample_url": voice.get("sample_url")
                        })
                    
                    return formatted_voices
                else:
                    logger.error(f"Error fetching voices: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting Fliki voices: {e}")
            return []
    
    async def generate_scenes_from_script(self, script: str) -> List[Dict[str, Any]]:
        """Generate scene suggestions from script"""
        
        # This would use Fliki's scene generation API
        # For now, return mock scene suggestions
        
        sentences = script.split('. ')
        scenes = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                scene = {
                    "scene_number": i + 1,
                    "text": sentence.strip(),
                    "suggested_visual": f"Scene {i + 1} visual suggestion",
                    "duration": 4.0,
                    "background_type": "stock_video" if i % 2 == 0 else "ai_generated",
                    "transition": "fade" if i > 0 else "none"
                }
                scenes.append(scene)
        
        return scenes


class HeyGenIntegration:
    """HeyGen API integration for AI avatars"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'HEYGEN_API_KEY', '')
        self.base_url = "https://api.heygen.com/v2"
        self.default_avatar = "anna_professional"
    
    async def create_avatar_video(
        self,
        script: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        background: str = "office",
        clothing: str = "professional"
    ) -> Dict[str, Any]:
        """Create video with AI avatar"""
        
        try:
            request_data = {
                "script": script,
                "avatar": {
                    "id": avatar_id or self.default_avatar,
                    "clothing": clothing,
                    "emotion": "friendly"
                },
                "voice": {
                    "id": voice_id or "en-US-JennyNeural",
                    "speed": 1.0
                },
                "video_settings": {
                    "background": background,
                    "aspect_ratio": "9:16",
                    "resolution": "1080p"
                }
            }
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/video/generate",
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    video_id = result.get("video_id")
                    
                    # Wait for processing
                    video_url = await self._wait_for_heygen_completion(video_id)
                    
                    return {
                        "success": True,
                        "video_id": video_id,
                        "video_url": video_url,
                        "avatar_used": avatar_id or self.default_avatar
                    }
                else:
                    logger.error(f"HeyGen API error: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating HeyGen video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_heygen_completion(self, video_id: str, max_wait: int = 600) -> Optional[str]:
        """Wait for HeyGen video processing"""
        
        wait_time = 0
        check_interval = 30
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/video/{video_id}",
                        headers={"X-API-Key": self.api_key}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("video_url")
                        elif status == "failed":
                            logger.error(f"HeyGen processing failed: {data.get('error')}")
                            return None
                        
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                        
                        logger.info(f"HeyGen video {video_id} processing... ({wait_time}s)")
                    else:
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking HeyGen status: {e}")
                return None
        
        return None
    
    async def get_available_avatars(self) -> List[Dict[str, Any]]:
        """Get available avatars"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/avatars",
                    headers={"X-API-Key": self.api_key}
                )
                
                if response.status_code == 200:
                    return response.json().get("avatars", [])
                else:
                    logger.error(f"Error fetching avatars: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting HeyGen avatars: {e}")
            return []

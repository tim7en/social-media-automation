"""
CapCut API Integration for Video Editing Automation
Professional video editing workflows for social media content
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
import json
from ...core.config import settings
from ...core.logger import logger


class CapCutIntegration:
    """CapCut API integration for automated video editing"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CAPCUT_API_KEY', '')
        self.base_url = "https://openapi.capcut.com/v1"
        
    async def create_auto_edited_video(
        self,
        video_clips: List[str],
        audio_track: Optional[str] = None,
        template_id: Optional[str] = None,
        style: str = "dynamic"
    ) -> Dict[str, Any]:
        """Create auto-edited video from clips using CapCut templates"""
        
        try:
            # Prepare editing parameters
            editing_params = {
                "video_clips": video_clips,
                "editing_style": style,
                "auto_sync": True,
                "auto_transitions": True,
                "auto_effects": True,
                "output_format": {
                    "resolution": "1080p",
                    "aspect_ratio": "9:16",
                    "fps": 30,
                    "bitrate": "high"
                }
            }
            
            if audio_track:
                editing_params["audio_track"] = audio_track
                editing_params["auto_audio_sync"] = True
                
            if template_id:
                editing_params["template_id"] = template_id
            
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/edit/auto",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=editing_params
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("task_id")
                    
                    # Wait for editing completion
                    edited_video_url = await self._wait_for_editing_completion(task_id)
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "video_url": edited_video_url,
                        "style": style,
                        "clips_count": len(video_clips)
                    }
                else:
                    logger.error(f"CapCut API error: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error with CapCut auto editing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def apply_template_editing(
        self,
        video_clips: List[str],
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Apply specific CapCut template to video clips"""
        
        try:
            request_data = {
                "template_id": template_id,
                "video_clips": video_clips,
                "auto_fit": True,
                "maintain_aspect_ratio": True,
                "output_settings": {
                    "format": "mp4",
                    "quality": "high",
                    "resolution": "1080p"
                }
            }
            
            if customizations:
                request_data["customizations"] = customizations
            
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/template/apply",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("task_id")
                    
                    video_url = await self._wait_for_editing_completion(task_id)
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "video_url": video_url,
                        "template_id": template_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Template application failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error applying CapCut template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_captions_and_effects(
        self,
        video_url: str,
        transcript: str,
        effect_style: str = "modern",
        font_style: str = "bold"
    ) -> Dict[str, Any]:
        """Add auto-generated captions and effects to video"""
        
        try:
            request_data = {
                "video_url": video_url,
                "transcript": transcript,
                "auto_captions": True,
                "caption_style": {
                    "font": font_style,
                    "size": "large",
                    "color": "#FFFFFF",
                    "background": "transparent",
                    "position": "center",
                    "animation": "typewriter"
                },
                "effects": {
                    "style": effect_style,
                    "transitions": True,
                    "music_sync": True,
                    "visual_effects": True
                }
            }
            
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{self.base_url}/enhance/captions-effects",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("task_id")
                    
                    enhanced_video_url = await self._wait_for_editing_completion(task_id)
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "enhanced_video_url": enhanced_video_url,
                        "captions_added": True,
                        "effects_applied": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Enhancement failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error enhancing video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_social_media_variations(
        self,
        video_url: str,
        platforms: List[str] = ["youtube", "tiktok", "instagram", "facebook"]
    ) -> Dict[str, Any]:
        """Create platform-optimized variations of the video"""
        
        platform_specs = {
            "youtube": {
                "aspect_ratio": "16:9",
                "resolution": "1920x1080",
                "max_duration": 3600,  # 60 minutes
                "format": "mp4"
            },
            "tiktok": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 180,  # 3 minutes
                "format": "mp4"
            },
            "instagram": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 90,  # 1.5 minutes for reels
                "format": "mp4"
            },
            "facebook": {
                "aspect_ratio": "1:1",
                "resolution": "1080x1080",
                "max_duration": 240,  # 4 minutes
                "format": "mp4"
            }
        }
        
        variations = {}
        
        for platform in platforms:
            if platform not in platform_specs:
                continue
                
            specs = platform_specs[platform]
            
            try:
                request_data = {
                    "source_video": video_url,
                    "output_specs": specs,
                    "auto_crop": True,
                    "maintain_quality": True,
                    "platform_optimization": platform
                }
                
                async with httpx.AsyncClient(timeout=600) as client:
                    response = await client.post(
                        f"{self.base_url}/convert/platform",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json=request_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        task_id = result.get("task_id")
                        
                        variation_url = await self._wait_for_editing_completion(task_id)
                        
                        variations[platform] = {
                            "success": True,
                            "video_url": variation_url,
                            "specs": specs,
                            "task_id": task_id
                        }
                    else:
                        variations[platform] = {
                            "success": False,
                            "error": f"Conversion failed: {response.status_code}"
                        }
                        
            except Exception as e:
                logger.error(f"Error creating {platform} variation: {e}")
                variations[platform] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": len([v for v in variations.values() if v.get("success")]) > 0,
            "variations": variations,
            "platforms_processed": len(variations)
        }
    
    async def _wait_for_editing_completion(self, task_id: str, max_wait: int = 900) -> Optional[str]:
        """Wait for CapCut editing task to complete"""
        
        wait_time = 0
        check_interval = 20  # Check every 20 seconds
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/task/{task_id}/status",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        progress = data.get("progress", 0)
                        
                        if status == "completed":
                            return data.get("output_url")
                        elif status == "failed":
                            logger.error(f"CapCut editing failed: {data.get('error_message')}")
                            return None
                        
                        logger.info(f"CapCut task {task_id} progress: {progress}% ({wait_time}s)")
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                    else:
                        logger.error(f"Error checking CapCut status: {response.status_code}")
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking CapCut completion: {e}")
                return None
        
        logger.error(f"CapCut editing timeout after {max_wait}s")
        return None


class CapCutWorkflows:
    """Pre-built workflows for common video editing tasks"""
    
    def __init__(self):
        self.capcut = CapCutIntegration()
    
    async def create_tiktok_ready_video(
        self,
        raw_clips: List[str],
        voiceover_audio: str,
        hook_text: str,
        cta_text: str
    ) -> Dict[str, Any]:
        """Create TikTok-optimized video with hooks, captions, and CTA"""
        
        try:
            # Step 1: Auto-edit the clips
            editing_result = await self.capcut.create_auto_edited_video(
                video_clips=raw_clips,
                audio_track=voiceover_audio,
                style="energetic"
            )
            
            if not editing_result.get("success"):
                return editing_result
            
            base_video_url = editing_result.get("video_url")
            
            # Step 2: Add captions and effects
            transcript = f"{hook_text} ... {cta_text}"  # Simplified for example
            
            enhanced_result = await self.capcut.add_captions_and_effects(
                video_url=base_video_url,
                transcript=transcript,
                effect_style="trendy",
                font_style="bold"
            )
            
            if not enhanced_result.get("success"):
                return enhanced_result
            
            # Step 3: Create TikTok variation
            final_video_url = enhanced_result.get("enhanced_video_url")
            
            platform_result = await self.capcut.create_social_media_variations(
                video_url=final_video_url,
                platforms=["tiktok"]
            )
            
            tiktok_variation = platform_result.get("variations", {}).get("tiktok", {})
            
            return {
                "success": True,
                "tiktok_video_url": tiktok_variation.get("video_url"),
                "editing_steps": {
                    "auto_edit": editing_result.get("task_id"),
                    "captions_effects": enhanced_result.get("task_id"),
                    "platform_optimization": tiktok_variation.get("task_id")
                },
                "features_applied": [
                    "auto_editing",
                    "captions",
                    "effects",
                    "tiktok_optimization"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating TikTok video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_youtube_shorts_series(
        self,
        source_video: str,
        segment_duration: int = 60,
        max_segments: int = 5
    ) -> Dict[str, Any]:
        """Split long-form content into YouTube Shorts series"""
        
        try:
            # Create multiple short segments
            segments_data = {
                "source_video": source_video,
                "segment_duration": segment_duration,
                "max_segments": max_segments,
                "auto_hooks": True,
                "series_branding": True,
                "cross_promotion": True
            }
            
            async with httpx.AsyncClient(timeout=600) as self.capcut.client:
                response = await self.capcut.client.post(
                    f"{self.capcut.base_url}/segment/shorts-series",
                    headers={
                        "Authorization": f"Bearer {self.capcut.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=segments_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("task_id")
                    
                    # Wait for segmentation completion
                    series_data = await self._wait_for_series_completion(task_id)
                    
                    return {
                        "success": True,
                        "series_data": series_data,
                        "segments_created": len(series_data.get("segments", [])),
                        "task_id": task_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Series creation failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating YouTube Shorts series: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_series_completion(self, task_id: str) -> Dict[str, Any]:
        """Wait for series segmentation to complete"""
        
        wait_time = 0
        max_wait = 600
        check_interval = 15
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.capcut.base_url}/task/{task_id}/series-status",
                        headers={"Authorization": f"Bearer {self.capcut.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "completed":
                            return data.get("series_data", {})
                        
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                    else:
                        return {}
                        
            except Exception as e:
                logger.error(f"Error checking series status: {e}")
                return {}
        
        return {}

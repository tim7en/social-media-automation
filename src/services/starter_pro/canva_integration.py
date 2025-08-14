"""
Canva Integration for Brand Design and Social Media Graphics
Automated brand asset creation and template management
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from ...core.config import settings
from ...core.logger import logger


class CanvaIntegration:
    """Canva API integration for automated design creation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CANVA_API_KEY', '')
        self.base_url = "https://api.canva.com/rest/v1"
        
    async def create_brand_kit(
        self,
        brand_name: str,
        primary_color: str,
        secondary_color: str,
        logo_url: Optional[str] = None,
        fonts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a brand kit with colors, fonts, and logo"""
        
        try:
            brand_data = {
                "name": brand_name,
                "colors": {
                    "primary": primary_color,
                    "secondary": secondary_color,
                    "accent": "#FFFFFF",
                    "text": "#000000"
                }
            }
            
            if logo_url:
                brand_data["logo"] = {"url": logo_url}
                
            if fonts:
                brand_data["fonts"] = fonts
            else:
                brand_data["fonts"] = ["Montserrat", "Open Sans", "Roboto"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/brand-kits",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=brand_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    brand_kit_id = result.get("id")
                    
                    return {
                        "success": True,
                        "brand_kit_id": brand_kit_id,
                        "brand_data": result,
                        "colors": brand_data["colors"],
                        "fonts": brand_data["fonts"]
                    }
                else:
                    logger.error(f"Canva brand kit creation error: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating Canva brand kit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_social_media_designs(
        self,
        brand_kit_id: str,
        content_theme: str,
        platforms: List[str],
        text_content: str,
        design_style: str = "modern"
    ) -> Dict[str, Any]:
        """Create social media graphics for multiple platforms"""
        
        platform_templates = {
            "instagram": {
                "post": "instagram-post-1080x1080",
                "story": "instagram-story-1080x1920", 
                "reel": "instagram-reel-1080x1920"
            },
            "facebook": {
                "post": "facebook-post-1200x630",
                "cover": "facebook-cover-1640x859",
                "story": "facebook-story-1080x1920"
            },
            "youtube": {
                "thumbnail": "youtube-thumbnail-1280x720",
                "banner": "youtube-banner-2560x1440",
                "short": "youtube-short-1080x1920"
            },
            "tiktok": {
                "video": "tiktok-video-1080x1920",
                "profile": "tiktok-profile-200x200"
            },
            "twitter": {
                "post": "twitter-post-1200x675",
                "header": "twitter-header-1500x500"
            }
        }
        
        created_designs = {}
        
        for platform in platforms:
            if platform not in platform_templates:
                continue
                
            platform_designs = {}
            templates = platform_templates[platform]
            
            for design_type, template_id in templates.items():
                try:
                    design_result = await self._create_design_from_template(
                        template_id=template_id,
                        brand_kit_id=brand_kit_id,
                        content_theme=content_theme,
                        text_content=text_content,
                        design_style=design_style
                    )
                    
                    if design_result.get("success"):
                        platform_designs[design_type] = design_result
                    
                except Exception as e:
                    logger.error(f"Error creating {platform} {design_type}: {e}")
                    platform_designs[design_type] = {
                        "success": False,
                        "error": str(e)
                    }
            
            created_designs[platform] = platform_designs
        
        return {
            "success": True,
            "designs": created_designs,
            "platforms_processed": len(created_designs),
            "brand_kit_id": brand_kit_id
        }
    
    async def _create_design_from_template(
        self,
        template_id: str,
        brand_kit_id: str,
        content_theme: str,
        text_content: str,
        design_style: str
    ) -> Dict[str, Any]:
        """Create a design from a specific template"""
        
        try:
            design_data = {
                "template_id": template_id,
                "brand_kit_id": brand_kit_id,
                "content": {
                    "text": text_content,
                    "theme": content_theme,
                    "style": design_style
                },
                "auto_layout": True,
                "high_quality": True
            }
            
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.base_url}/designs",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=design_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    design_id = result.get("id")
                    
                    # Wait for design generation
                    design_url = await self._wait_for_design_completion(design_id)
                    
                    return {
                        "success": True,
                        "design_id": design_id,
                        "design_url": design_url,
                        "template_id": template_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Design creation failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating design from template: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_thumbnail_variations(
        self,
        video_title: str,
        brand_kit_id: str,
        thumbnail_style: str = "attention-grabbing",
        variations_count: int = 3
    ) -> Dict[str, Any]:
        """Create multiple YouTube thumbnail variations"""
        
        thumbnail_styles = {
            "attention-grabbing": {
                "colors": ["#FF0000", "#FFD700", "#00FF00"],
                "fonts": ["Impact", "Arial Black"],
                "effects": ["drop_shadow", "glow"]
            },
            "professional": {
                "colors": ["#2C3E50", "#3498DB", "#FFFFFF"],
                "fonts": ["Helvetica", "Open Sans"],
                "effects": ["subtle_shadow"]
            },
            "playful": {
                "colors": ["#E74C3C", "#F39C12", "#9B59B6"],
                "fonts": ["Comic Sans MS", "Fredoka One"],
                "effects": ["bounce", "colorful_border"]
            }
        }
        
        style_config = thumbnail_styles.get(thumbnail_style, thumbnail_styles["professional"])
        thumbnails = []
        
        for i in range(variations_count):
            try:
                variation_data = {
                    "template_id": "youtube-thumbnail-dynamic",
                    "brand_kit_id": brand_kit_id,
                    "content": {
                        "title": video_title,
                        "style": thumbnail_style,
                        "variation": i + 1
                    },
                    "style_overrides": {
                        "primary_color": style_config["colors"][i % len(style_config["colors"])],
                        "font": style_config["fonts"][i % len(style_config["fonts"])],
                        "effects": style_config["effects"]
                    }
                }
                
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(
                        f"{self.base_url}/designs/thumbnail",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json=variation_data
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        design_id = result.get("id")
                        
                        thumbnail_url = await self._wait_for_design_completion(design_id)
                        
                        thumbnails.append({
                            "variation": i + 1,
                            "design_id": design_id,
                            "thumbnail_url": thumbnail_url,
                            "style": thumbnail_style,
                            "primary_color": variation_data["style_overrides"]["primary_color"]
                        })
                    
            except Exception as e:
                logger.error(f"Error creating thumbnail variation {i+1}: {e}")
                thumbnails.append({
                    "variation": i + 1,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": len([t for t in thumbnails if "thumbnail_url" in t]) > 0,
            "thumbnails": thumbnails,
            "video_title": video_title,
            "style": thumbnail_style,
            "variations_created": len([t for t in thumbnails if "thumbnail_url" in t])
        }
    
    async def create_content_series_templates(
        self,
        series_name: str,
        brand_kit_id: str,
        episode_count: int = 10,
        platforms: List[str] = ["youtube", "instagram", "tiktok"]
    ) -> Dict[str, Any]:
        """Create consistent template series for content"""
        
        try:
            series_data = {
                "series_name": series_name,
                "brand_kit_id": brand_kit_id,
                "episode_count": episode_count,
                "platforms": platforms,
                "consistency_rules": {
                    "maintain_branding": True,
                    "consistent_layout": True,
                    "episode_numbering": True,
                    "series_identifier": True
                }
            }
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/series/templates",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=series_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    series_id = result.get("series_id")
                    
                    # Wait for template generation
                    templates = await self._wait_for_series_templates(series_id)
                    
                    return {
                        "success": True,
                        "series_id": series_id,
                        "templates": templates,
                        "episode_count": episode_count,
                        "platforms": platforms
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Series creation failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating content series: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_design_completion(self, design_id: str, max_wait: int = 120) -> Optional[str]:
        """Wait for design creation to complete"""
        
        wait_time = 0
        check_interval = 5
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/designs/{design_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("download_url")
                        elif status == "failed":
                            logger.error(f"Canva design failed: {data.get('error')}")
                            return None
                        
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                    else:
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking design completion: {e}")
                return None
        
        return None
    
    async def _wait_for_series_templates(self, series_id: str) -> Dict[str, Any]:
        """Wait for series template generation"""
        
        wait_time = 0
        max_wait = 300
        check_interval = 10
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/series/{series_id}/templates",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "ready":
                            return data.get("templates", {})
                        
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                    else:
                        return {}
                        
            except Exception as e:
                logger.error(f"Error checking series templates: {e}")
                return {}
        
        return {}


class CanvaBrandManager:
    """Manager for brand consistency across all designs"""
    
    def __init__(self):
        self.canva = CanvaIntegration()
    
    async def setup_complete_brand(
        self,
        brand_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up complete brand kit and generate all necessary assets"""
        
        # Create brand kit
        brand_kit_result = await self.canva.create_brand_kit(
            brand_name=brand_info.get("name", "My Brand"),
            primary_color=brand_info.get("primary_color", "#3498DB"),
            secondary_color=brand_info.get("secondary_color", "#2C3E50"),
            logo_url=brand_info.get("logo_url"),
            fonts=brand_info.get("fonts")
        )
        
        if not brand_kit_result.get("success"):
            return brand_kit_result
        
        brand_kit_id = brand_kit_result.get("brand_kit_id")
        
        # Create social media designs
        social_designs = await self.canva.create_social_media_designs(
            brand_kit_id=brand_kit_id,
            content_theme=brand_info.get("theme", "professional"),
            platforms=brand_info.get("platforms", ["youtube", "instagram", "tiktok"]),
            text_content=brand_info.get("sample_text", "Coming Soon!"),
            design_style=brand_info.get("style", "modern")
        )
        
        # Create thumbnail variations
        thumbnail_variations = await self.canva.create_thumbnail_variations(
            video_title=brand_info.get("sample_video_title", "Amazing Content Coming Soon"),
            brand_kit_id=brand_kit_id,
            thumbnail_style=brand_info.get("thumbnail_style", "professional")
        )
        
        return {
            "success": True,
            "brand_kit": brand_kit_result,
            "social_designs": social_designs,
            "thumbnail_variations": thumbnail_variations,
            "brand_kit_id": brand_kit_id,
            "setup_complete": True
        }

from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

class PresetManager:
    """Manage content generation presets and configurations"""
    
    def __init__(self):
        self.presets = self._load_default_presets()
        
    def _load_default_presets(self) -> Dict[str, Any]:
        """Load default presets"""
        return {
            "viral_reel": {
                "id": "viral_reel",
                "name": "Viral Reel Generator",
                "type": "content_generation",
                "platform": "instagram",
                "config": {
                    "content_type": "reel",
                    "tone": "energetic",
                    "hooks": ["Did you know", "This will blow your mind", "You won't believe"],
                    "cta_styles": ["Follow for more", "Save this post", "Share with friends"],
                    "hashtag_count": 15,
                    "trending_hashtags": True,
                    "max_length": 60
                },
                "ai_settings": {
                    "creativity": 0.8,
                    "model": "gpt-4",
                    "temperature": 0.7
                }
            },
            "educational_youtube": {
                "id": "educational_youtube",
                "name": "Educational YouTube Content",
                "type": "content_generation",
                "platform": "youtube",
                "config": {
                    "content_type": "educational",
                    "tone": "informative",
                    "structure": "intro-main-conclusion",
                    "include_timestamps": True,
                    "target_duration": 600,
                    "engagement_hooks": True
                },
                "ai_settings": {
                    "creativity": 0.6,
                    "model": "gpt-4",
                    "temperature": 0.5
                }
            },
            "tiktok_trending": {
                "id": "tiktok_trending",
                "name": "TikTok Trending Content",
                "type": "content_generation",
                "platform": "tiktok",
                "config": {
                    "content_type": "trending",
                    "tone": "casual",
                    "follow_trends": True,
                    "use_sounds": True,
                    "max_duration": 30,
                    "hashtag_count": 5
                },
                "ai_settings": {
                    "creativity": 0.9,
                    "model": "gpt-4",
                    "temperature": 0.8
                }
            },
            "professional_linkedin": {
                "id": "professional_linkedin",
                "name": "Professional LinkedIn Post",
                "type": "content_generation",
                "platform": "linkedin",
                "config": {
                    "content_type": "professional",
                    "tone": "professional",
                    "include_insights": True,
                    "call_to_action": "thought-provoking",
                    "hashtag_count": 3
                },
                "ai_settings": {
                    "creativity": 0.5,
                    "model": "gpt-4",
                    "temperature": 0.4
                }
            },
            "multi_platform_campaign": {
                "id": "multi_platform_campaign",
                "name": "Multi-Platform Campaign",
                "type": "campaign",
                "platform": "multi",
                "config": {
                    "platforms": ["instagram", "tiktok", "youtube"],
                    "content_variations": True,
                    "consistent_branding": True,
                    "cross_promotion": True,
                    "schedule_optimization": True
                },
                "ai_settings": {
                    "creativity": 0.7,
                    "model": "gpt-4",
                    "temperature": 0.6
                }
            },
            "quick_story": {
                "id": "quick_story",
                "name": "Quick Story Generator",
                "type": "content_generation",
                "platform": "instagram",
                "config": {
                    "content_type": "story",
                    "duration": 15,
                    "interactive_elements": True,
                    "polls": True,
                    "questions": True,
                    "stickers": True
                },
                "ai_settings": {
                    "creativity": 0.8,
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            }
        }
    
    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific preset"""
        return self.presets.get(preset_id)
    
    def list_presets(self, preset_type: str = None, platform: str = None) -> List[Dict[str, Any]]:
        """List available presets with optional filtering"""
        presets = list(self.presets.values())
        
        if preset_type:
            presets = [p for p in presets if p["type"] == preset_type]
        
        if platform:
            presets = [p for p in presets if p["platform"] == platform or p["platform"] == "multi"]
        
        return presets
    
    def create_preset(self, preset_data: Dict[str, Any]) -> str:
        """Create a new preset"""
        preset_id = preset_data.get("id", str(uuid.uuid4()))
        
        preset = {
            "id": preset_id,
            "name": preset_data["name"],
            "type": preset_data["type"],
            "platform": preset_data["platform"],
            "config": preset_data["config"],
            "ai_settings": preset_data.get("ai_settings", {}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "usage_count": 0
        }
        
        self.presets[preset_id] = preset
        return preset_id
    
    def update_preset(self, preset_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing preset"""
        if preset_id not in self.presets:
            return False
        
        preset = self.presets[preset_id]
        preset.update(updates)
        preset["updated_at"] = datetime.utcnow().isoformat()
        
        return True
    
    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset"""
        if preset_id in self.presets:
            del self.presets[preset_id]
            return True
        return False
    
    def apply_preset(self, preset_id: str, custom_variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply a preset with optional custom variables"""
        preset = self.get_preset(preset_id)
        if not preset:
            raise ValueError(f"Preset {preset_id} not found")
        
        # Increment usage count
        preset["usage_count"] = preset.get("usage_count", 0) + 1
        preset["last_used"] = datetime.utcnow().isoformat()
        
        # Merge config with custom variables
        config = preset["config"].copy()
        if custom_variables:
            config.update(custom_variables)
        
        return {
            "preset_id": preset_id,
            "preset_name": preset["name"],
            "config": config,
            "ai_settings": preset["ai_settings"],
            "platform": preset["platform"],
            "type": preset["type"]
        }
    
    def get_popular_presets(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular presets by usage"""
        presets = list(self.presets.values())
        presets.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        return presets[:limit]
    
    def get_recent_presets(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recently used presets"""
        presets = [p for p in self.presets.values() if "last_used" in p]
        presets.sort(key=lambda x: x["last_used"], reverse=True)
        return presets[:limit]
    
    def duplicate_preset(self, preset_id: str, new_name: str) -> str:
        """Duplicate an existing preset"""
        original_preset = self.get_preset(preset_id)
        if not original_preset:
            raise ValueError(f"Preset {preset_id} not found")
        
        # Create duplicate
        new_preset_data = original_preset.copy()
        new_preset_data["name"] = new_name
        new_preset_data.pop("id", None)  # Remove old ID
        new_preset_data.pop("usage_count", None)  # Reset usage
        new_preset_data.pop("last_used", None)  # Reset last used
        
        return self.create_preset(new_preset_data)
    
    def validate_preset(self, preset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate preset structure"""
        required_fields = ["name", "type", "platform", "config"]
        errors = []
        
        for field in required_fields:
            if field not in preset_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate type
        valid_types = ["content_generation", "campaign", "automation", "analysis"]
        if "type" in preset_data and preset_data["type"] not in valid_types:
            errors.append(f"Invalid type: {preset_data['type']}")
        
        # Validate platform
        valid_platforms = ["instagram", "youtube", "tiktok", "facebook", "twitter", "linkedin", "multi"]
        if "platform" in preset_data and preset_data["platform"] not in valid_platforms:
            errors.append(f"Invalid platform: {preset_data['platform']}")
        
        # Validate config
        if "config" in preset_data and not isinstance(preset_data["config"], dict):
            errors.append("Config must be a dictionary")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def get_preset_recommendations(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get preset recommendations based on user preferences"""
        platform = user_preferences.get("platform")
        content_type = user_preferences.get("content_type")
        experience_level = user_preferences.get("experience_level", "beginner")
        
        recommendations = []
        
        for preset in self.presets.values():
            score = 0
            
            # Platform match
            if platform and (preset["platform"] == platform or preset["platform"] == "multi"):
                score += 10
            
            # Content type match
            if content_type and preset["config"].get("content_type") == content_type:
                score += 8
            
            # Experience level considerations
            if experience_level == "beginner":
                # Prefer simpler presets
                if len(preset["config"]) <= 5:
                    score += 5
            elif experience_level == "advanced":
                # Prefer more complex presets
                if len(preset["config"]) > 5:
                    score += 5
            
            # Popularity bonus
            usage_count = preset.get("usage_count", 0)
            score += min(usage_count / 10, 5)  # Max 5 points for popularity
            
            if score > 0:
                recommendations.append({
                    **preset,
                    "recommendation_score": score
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:5]
    
    def export_presets(self, preset_ids: List[str] = None) -> Dict[str, Any]:
        """Export presets to a portable format"""
        if preset_ids:
            presets_to_export = {pid: self.presets[pid] for pid in preset_ids if pid in self.presets}
        else:
            presets_to_export = self.presets
        
        return {
            "export_version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "presets": presets_to_export
        }
    
    def import_presets(self, preset_data: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """Import presets from exported data"""
        imported_count = 0
        skipped_count = 0
        errors = []
        
        presets_to_import = preset_data.get("presets", {})
        
        for preset_id, preset in presets_to_import.items():
            try:
                if preset_id in self.presets and not overwrite:
                    skipped_count += 1
                    continue
                
                # Validate preset
                validation = self.validate_preset(preset)
                if not validation["valid"]:
                    errors.extend(validation["errors"])
                    continue
                
                # Import preset
                preset["imported_at"] = datetime.utcnow().isoformat()
                self.presets[preset_id] = preset
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error importing preset {preset_id}: {str(e)}")
        
        return {
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors
        }
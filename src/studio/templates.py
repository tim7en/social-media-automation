from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
import uuid

class ContentTemplateManager:
    """Manage content templates for different platforms and content types"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from storage"""
        # Default templates
        return {
            "instagram_reel": {
                "id": "instagram_reel",
                "name": "Instagram Reel Template",
                "platform": "instagram",
                "type": "reel",
                "template": {
                    "hook": "🔥 {hook_text}",
                    "main_content": "{main_content}",
                    "cta": "👆 {cta_text}",
                    "hashtags": ["#reels", "#viral", "#trending", "{topic_hashtag}"]
                },
                "variables": ["hook_text", "main_content", "cta_text", "topic_hashtag"],
                "max_length": 2200
            },
            "youtube_shorts": {
                "id": "youtube_shorts",
                "name": "YouTube Shorts Template",
                "platform": "youtube",
                "type": "shorts",
                "template": {
                    "title": "{title}",
                    "description": "{description}\n\n#shorts #youtube #viral",
                    "script": {
                        "intro": "{intro_text}",
                        "main": "{main_content}",
                        "outro": "Like and subscribe for more!"
                    }
                },
                "variables": ["title", "description", "intro_text", "main_content"],
                "max_duration": 60
            },
            "tiktok_viral": {
                "id": "tiktok_viral",
                "name": "TikTok Viral Template",
                "platform": "tiktok",
                "type": "video",
                "template": {
                    "caption": "{caption} #fyp #viral #trending",
                    "script": {
                        "hook": "{hook}",
                        "content": "{content}",
                        "cta": "Follow for more {topic} content!"
                    }
                },
                "variables": ["caption", "hook", "content", "topic"],
                "max_length": 150
            },
            "multi_platform_post": {
                "id": "multi_platform_post",
                "name": "Multi-Platform Post Template",
                "platform": "multi",
                "type": "post",
                "template": {
                    "content": "{content}",
                    "hashtags": {
                        "instagram": ["#insta", "#post", "{topic}"],
                        "twitter": ["#twitter", "{topic}"],
                        "facebook": ["{topic}"]
                    }
                },
                "variables": ["content", "topic"],
                "platform_variations": {
                    "instagram": {"max_length": 2200},
                    "twitter": {"max_length": 280},
                    "facebook": {"max_length": 5000}
                }
            }
        }
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template"""
        return self.templates.get(template_id)
    
    def list_templates(self, platform: str = None, content_type: str = None) -> List[Dict[str, Any]]:
        """List available templates with optional filtering"""
        templates = list(self.templates.values())
        
        if platform:
            templates = [t for t in templates if t["platform"] == platform or t["platform"] == "multi"]
        
        if content_type:
            templates = [t for t in templates if t["type"] == content_type]
        
        return templates
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create a new template"""
        template_id = template_data.get("id", str(uuid.uuid4()))
        
        template = {
            "id": template_id,
            "name": template_data["name"],
            "platform": template_data["platform"],
            "type": template_data["type"],
            "template": template_data["template"],
            "variables": template_data.get("variables", []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add optional fields
        for field in ["max_length", "max_duration", "platform_variations"]:
            if field in template_data:
                template[field] = template_data[field]
        
        self.templates[template_id] = template
        return template_id
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template"""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        template.update(updates)
        template["updated_at"] = datetime.utcnow().isoformat()
        
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False
    
    def render_template(self, template_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Render a template with provided variables"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Clone template structure
        rendered = json.loads(json.dumps(template["template"]))
        
        # Replace variables recursively
        rendered = self._replace_variables(rendered, variables)
        
        return {
            "template_id": template_id,
            "platform": template["platform"],
            "type": template["type"],
            "content": rendered,
            "variables_used": variables
        }
    
    def _replace_variables(self, obj, variables: Dict[str, Any]):
        """Recursively replace variables in template structure"""
        if isinstance(obj, dict):
            return {key: self._replace_variables(value, variables) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_variables(item, variables) for item in obj]
        elif isinstance(obj, str):
            # Replace {variable} patterns
            for var_name, var_value in variables.items():
                obj = obj.replace(f"{{{var_name}}}", str(var_value))
            return obj
        else:
            return obj
    
    def validate_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template structure"""
        required_fields = ["name", "platform", "type", "template"]
        errors = []
        
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate platform
        valid_platforms = ["instagram", "youtube", "tiktok", "facebook", "twitter", "multi"]
        if "platform" in template_data and template_data["platform"] not in valid_platforms:
            errors.append(f"Invalid platform: {template_data['platform']}")
        
        # Validate variables
        if "variables" in template_data:
            if not isinstance(template_data["variables"], list):
                errors.append("Variables must be a list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about templates"""
        platforms = {}
        types = {}
        
        for template in self.templates.values():
            platform = template["platform"]
            content_type = template["type"]
            
            platforms[platform] = platforms.get(platform, 0) + 1
            types[content_type] = types.get(content_type, 0) + 1
        
        return {
            "total_templates": len(self.templates),
            "by_platform": platforms,
            "by_type": types,
            "most_used_platform": max(platforms.items(), key=lambda x: x[1])[0] if platforms else None,
            "most_used_type": max(types.items(), key=lambda x: x[1])[0] if types else None
        }
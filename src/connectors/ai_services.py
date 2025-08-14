import os
from typing import Dict, Any, Optional
import tempfile

class OpenAIConnector:
    """Wrapper for OpenAI API operations"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
            
    async def generate_text(self, prompt: str, model: str = "gpt-4", max_tokens: int = 2000) -> str:
        """Generate text using OpenAI"""
        # For now, return a mock response - in production this would call OpenAI API
        return f"Generated content for: {prompt[:50]}..."
        
    async def generate_image_prompt(self, description: str) -> str:
        """Generate an image prompt from description"""
        prompt = f"Create a detailed image prompt for: {description}"
        return await self.generate_text(prompt)
        
    async def analyze_content(self, content: str, analysis_type: str = "engagement") -> Dict[str, Any]:
        """Analyze content for various metrics"""
        # Mock analysis - in production would use OpenAI for content analysis
        return {
            "engagement_score": 7.5,
            "readability": "high",
            "sentiment": "positive",
            "keywords": ["content", "social media", "automation"],
            "suggestions": ["Add more emojis", "Include call-to-action"]
        }

class ImageMagickConnector:
    """Wrapper for ImageMagick operations"""
    
    def __init__(self, convert_path: str = "convert"):
        self.convert_path = convert_path
        
    async def create_thumbnail(self, width: int, height: int, text: str, 
                             bg_color: str = "#1e1e1e", text_color: str = "#ffffff") -> str:
        """Create a thumbnail with text overlay"""
        output_path = tempfile.mktemp(suffix=".png")
        
        # For now, use PIL as fallback - in production would use ImageMagick
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default
            try:
                font = ImageFont.truetype("arial.ttf", size=60)
            except:
                font = ImageFont.load_default()
                
            # Get text bounding box
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Center the text
            position = ((width - text_width) // 2, (height - text_height) // 2)
            draw.text(position, text, fill=text_color, font=font)
            
            img.save(output_path)
            return output_path
            
        except ImportError:
            # Fallback if PIL is not available
            raise Exception("PIL is required for image operations")
            
    async def resize_image(self, image_path: str, width: int, height: int, output_path: str = None) -> str:
        """Resize an image"""
        if not output_path:
            output_path = tempfile.mktemp(suffix=".png")
            
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                resized.save(output_path)
                
            return output_path
            
        except ImportError:
            raise Exception("PIL is required for image operations")
from typing import Optional, Dict, Any
import openai
from ..core.config import settings
from ..core.logger import logger


class AIContentGenerator:
    """AI-powered content generation service"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_script(
        self,
        topic: str,
        style: str = "engaging",
        duration: int = 60,
        platform: str = "youtube",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a script for video content"""
        
        # Calculate approximate word count based on duration
        words_per_minute = 150
        target_words = int((duration / 60) * words_per_minute)
        
        prompt = self._build_script_prompt(
            topic, style, target_words, platform, additional_context
        )
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            script = response.choices[0].message.content
            
            # Parse the response to extract different sections
            parsed_script = self._parse_script_response(script)
            
            logger.info(f"Generated script for topic: {topic}")
            
            return {
                "script": script,
                "parsed": parsed_script,
                "word_count": len(script.split()),
                "estimated_duration": len(script.split()) / (words_per_minute / 60)
            }
            
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise
    
    async def generate_title_suggestions(
        self,
        topic: str,
        platform: str = "youtube",
        count: int = 5
    ) -> list[str]:
        """Generate title suggestions for content"""
        
        prompt = f"""
        Generate {count} engaging titles for a {platform} video about: {topic}
        
        Requirements:
        - Titles should be attention-grabbing and clickable
        - Optimized for {platform} audience
        - Include relevant keywords
        - Vary the style (question, statement, how-to, etc.)
        
        Return only the titles, one per line.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=500
            )
            
            titles = response.choices[0].message.content.strip().split('\n')
            return [title.strip('- ').strip() for title in titles if title.strip()]
            
        except Exception as e:
            logger.error(f"Error generating titles: {e}")
            raise
    
    async def generate_description(
        self,
        title: str,
        script: str,
        platform: str = "youtube"
    ) -> str:
        """Generate description for social media post"""
        
        prompt = f"""
        Create an engaging description for a {platform} post with the title: "{title}"
        
        Script excerpt: {script[:500]}...
        
        Requirements:
        - Engaging and informative
        - Include relevant hashtags
        - Encourage engagement (likes, comments, shares)
        - Optimized for {platform}
        - 2-3 paragraphs maximum
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            raise
    
    async def generate_hashtags(
        self,
        topic: str,
        platform: str = "youtube",
        count: int = 10
    ) -> list[str]:
        """Generate relevant hashtags"""
        
        prompt = f"""
        Generate {count} relevant hashtags for {platform} content about: {topic}
        
        Requirements:
        - Mix of popular and niche hashtags
        - Relevant to the topic
        - Optimized for {platform}
        - Include trending hashtags when applicable
        
        Return only hashtags without # symbol, one per line.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=300
            )
            
            hashtags = response.choices[0].message.content.strip().split('\n')
            return [hashtag.strip('#').strip() for hashtag in hashtags if hashtag.strip()]
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for content generation"""
        return """
        You are an expert content creator specializing in engaging short-form video content.
        Your goal is to create scripts that are:
        - Engaging from the first second
        - Informative and valuable
        - Optimized for social media platforms
        - Designed to maximize viewer retention
        - Include clear hooks, main content, and call-to-actions
        
        Always structure your scripts with:
        1. Hook (first 3-5 seconds)
        2. Introduction 
        3. Main content (broken into digestible segments)
        4. Call to action
        5. Conclusion
        """
    
    def _build_script_prompt(
        self,
        topic: str,
        style: str,
        target_words: int,
        platform: str,
        additional_context: Optional[str]
    ) -> str:
        """Build the script generation prompt"""
        
        platform_specifics = {
            "youtube": "YouTube Shorts (vertical video, 60 seconds max)",
            "tiktok": "TikTok (vertical video, engaging, trendy)",
            "instagram": "Instagram Reels (vertical video, visually appealing)",
            "facebook": "Facebook video (can be horizontal or vertical)"
        }
        
        platform_note = platform_specifics.get(platform, platform)
        
        prompt = f"""
        Create an engaging script for {platform_note} about: {topic}
        
        Style: {style}
        Target length: approximately {target_words} words
        Platform: {platform}
        
        {f"Additional context: {additional_context}" if additional_context else ""}
        
        Requirements:
        - Start with a strong hook in the first 3 seconds
        - Keep viewers engaged throughout
        - Include a clear call-to-action
        - Break content into digestible segments
        - Use conversational tone
        - Include timing suggestions for visuals
        
        Format the response with clear sections:
        [HOOK] - First 3-5 seconds
        [INTRO] - Brief introduction
        [MAIN CONTENT] - Core information (break into segments)
        [CTA] - Call to action
        [OUTRO] - Conclusion
        
        Also include [VISUAL NOTES] for each section suggesting what should be shown on screen.
        """
        
        return prompt
    
    def _parse_script_response(self, script: str) -> Dict[str, str]:
        """Parse the script response into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in script.split('\n'):
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[1:-1].lower().replace(' ', '_')
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

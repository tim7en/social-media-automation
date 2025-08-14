"""
Hybrid "Starter Pro" Stack Integration

A beginner-friendly workflow that integrates popular content creation tools
for balanced speed, control, and scalability.

Stack Components:
- Idea & Script: ChatGPT + niche keyword list
- Voice & Scenes: Fliki or HeyGen integration
- Custom Scenes: Runway Gen-3 or Pika Labs
- Editing: CapCut Pro workflow
- Branding: Canva Pro templates
- Posting: Metricool scheduling

Goal: Daily posting on TikTok & YouTube Shorts for first 30 days
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import httpx
import json
from ...core.config import settings
from ...core.logger import logger


class StarterProTool(str, Enum):
    CHATGPT = "chatgpt"
    FLIKI = "fliki"
    HEYGEN = "heygen"
    RUNWAY = "runway"
    PIKA = "pika"
    CAPCUT = "capcut"
    CANVA = "canva"
    METRICOOL = "metricool"


@dataclass
class WorkflowStep:
    step: str
    tool: StarterProTool
    description: str
    purpose: str
    output_type: str
    estimated_time: str


class StarterProWorkflow:
    """
    Hybrid Starter Pro workflow manager for beginners
    Balances speed, control, and scalability
    """
    
    def __init__(self):
        self.workflow_steps = [
            WorkflowStep(
                step="Idea & Script",
                tool=StarterProTool.CHATGPT,
                description="Generate script, title, and tags using ChatGPT with niche keywords",
                purpose="Content ideation and script creation",
                output_type="text",
                estimated_time="5-10 minutes"
            ),
            WorkflowStep(
                step="Voice & Scenes",
                tool=StarterProTool.FLIKI,  # or HEYGEN
                description="Create voiceover with avatar or visuals",
                purpose="Professional voice and initial visuals",
                output_type="video/audio",
                estimated_time="10-15 minutes"
            ),
            WorkflowStep(
                step="Custom Scenes",
                tool=StarterProTool.RUNWAY,  # or PIKA
                description="Generate unique, dynamic B-roll footage",
                purpose="Engaging visual content",
                output_type="video",
                estimated_time="15-20 minutes"
            ),
            WorkflowStep(
                step="Editing",
                tool=StarterProTool.CAPCUT,
                description="Vertical video editing with captions",
                purpose="Professional mobile-first editing",
                output_type="video",
                estimated_time="20-30 minutes"
            ),
            WorkflowStep(
                step="Branding",
                tool=StarterProTool.CANVA,
                description="Consistent intro/outro graphics",
                purpose="Brand consistency and recognition",
                output_type="graphics",
                estimated_time="5-10 minutes"
            ),
            WorkflowStep(
                step="Posting",
                tool=StarterProTool.METRICOOL,
                description="Multi-platform scheduling and analytics",
                purpose="Strategic distribution and tracking",
                output_type="scheduled_posts",
                estimated_time="5 minutes"
            )
        ]
        
        self.posting_schedule = {
            "frequency_goal": "Daily posting for first 30 days",
            "primary_platforms": ["TikTok", "YouTube Shorts"],
            "posting_times": {
                "tiktok": ["15:00", "19:00", "21:00"],
                "youtube_shorts": ["16:00", "20:00", "22:00"]
            },
            "content_types": [
                "Educational tips",
                "Behind-the-scenes",
                "Quick tutorials",
                "Trending topics",
                "Q&A content"
            ]
        }
    
    def get_workflow_overview(self) -> Dict[str, Any]:
        """Get complete workflow overview"""
        return {
            "name": "Hybrid Starter Pro Stack",
            "description": "Balanced speed, control, and scalability for beginners",
            "target_audience": "Content creation beginners",
            "estimated_total_time": "60-90 minutes per video",
            "steps": [
                {
                    "step": step.step,
                    "tool": step.tool.value,
                    "description": step.description,
                    "purpose": step.purpose,
                    "estimated_time": step.estimated_time,
                    "output": step.output_type
                }
                for step in self.workflow_steps
            ],
            "posting_strategy": self.posting_schedule,
            "success_metrics": [
                "Consistent daily posting",
                "Engagement rate improvement",
                "Follower growth",
                "Content quality consistency"
            ]
        }
    
    async def generate_content_plan(
        self,
        niche: str,
        target_keywords: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate 30-day content plan for starter pro workflow"""
        
        try:
            # Generate content ideas using ChatGPT approach
            content_ideas = await self._generate_content_ideas(niche, target_keywords, days)
            
            # Create posting schedule
            posting_schedule = self._create_posting_schedule(content_ideas, days)
            
            # Generate workflow templates
            templates = self._create_workflow_templates()
            
            return {
                "content_plan": {
                    "niche": niche,
                    "keywords": target_keywords,
                    "duration_days": days,
                    "total_videos": len(content_ideas),
                    "ideas": content_ideas
                },
                "posting_schedule": posting_schedule,
                "workflow_templates": templates,
                "tools_setup": self._get_tools_setup_guide(),
                "success_tips": self._get_success_tips()
            }
            
        except Exception as e:
            logger.error(f"Error generating content plan: {e}")
            raise
    
    async def _generate_content_ideas(
        self,
        niche: str,
        keywords: List[str],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate content ideas using keyword-focused approach"""
        
        ideas = []
        
        # Content idea templates for different types
        idea_templates = [
            "How to {keyword} in {timeframe}",
            "5 {keyword} mistakes beginners make",
            "The ultimate {keyword} guide",
            "Why {keyword} matters for {target_audience}",
            "{keyword} vs {alternative} - Which is better?",
            "Behind the scenes: My {keyword} process",
            "Quick {keyword} tips that actually work",
            "The truth about {keyword} nobody tells you",
            "Transform your {keyword} in 60 seconds",
            "Common {keyword} myths debunked"
        ]
        
        content_types = [
            "educational", "tutorial", "tips", "behind_scenes", 
            "comparison", "myth_busting", "quick_wins", "transformation"
        ]
        
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            template = idea_templates[i % len(idea_templates)]
            content_type = content_types[i % len(content_types)]
            
            idea = {
                "day": i + 1,
                "title": template.format(
                    keyword=keyword,
                    timeframe="30 days",
                    target_audience="beginners",
                    alternative=keywords[(i + 1) % len(keywords)]
                ),
                "primary_keyword": keyword,
                "content_type": content_type,
                "platform_focus": "TikTok" if i % 2 == 0 else "YouTube Shorts",
                "hook_suggestions": [
                    f"Did you know that {keyword}...",
                    f"Stop doing {keyword} wrong!",
                    f"The {keyword} secret that changed everything",
                    f"I tried {keyword} for 30 days..."
                ],
                "cta_suggestions": [
                    f"Follow for more {keyword} tips",
                    f"Comment your {keyword} questions below",
                    f"Share if this {keyword} tip helped you",
                    f"Save this {keyword} guide"
                ],
                "estimated_engagement": self._estimate_engagement(content_type),
                "trending_potential": self._assess_trending_potential(keyword, content_type)
            }
            
            ideas.append(idea)
        
        return ideas
    
    def _create_posting_schedule(
        self,
        content_ideas: List[Dict[str, Any]],
        days: int
    ) -> Dict[str, Any]:
        """Create optimized posting schedule"""
        
        schedule = {
            "strategy": "Daily posting for maximum algorithm exposure",
            "primary_times": {
                "tiktok": "15:00 EST (peak engagement)",
                "youtube_shorts": "20:00 EST (evening viewing)"
            },
            "content_distribution": {
                "educational": "40%",
                "entertainment": "30%",
                "trending": "20%",
                "personal/behind_scenes": "10%"
            },
            "weekly_structure": {
                "monday": "Educational content",
                "tuesday": "Tips and tricks",
                "wednesday": "Behind the scenes",
                "thursday": "Trending topics",
                "friday": "Quick wins",
                "saturday": "Entertainment/fun",
                "sunday": "Weekly recap/planning"
            },
            "daily_schedule": []
        }
        
        for i, idea in enumerate(content_ideas[:days]):
            day_schedule = {
                "day": i + 1,
                "date": f"Day {i + 1}",
                "content": idea,
                "posting_times": {
                    "tiktok": "15:00",
                    "youtube_shorts": "20:00"
                },
                "prep_timeline": {
                    "content_creation": "09:00-11:00",
                    "editing": "11:00-12:30", 
                    "review": "13:00-13:30",
                    "scheduling": "14:00-14:30"
                }
            }
            schedule["daily_schedule"].append(day_schedule)
        
        return schedule
    
    def _create_workflow_templates(self) -> Dict[str, Any]:
        """Create workflow templates for each tool"""
        
        return {
            "chatgpt_prompts": {
                "script_generation": """
                Create a 60-second video script for {platform} about {topic}.
                
                Requirements:
                - Hook in first 3 seconds
                - Educational value
                - Strong call-to-action
                - Include keywords: {keywords}
                - Target audience: beginners
                
                Format:
                [HOOK] (0-3 seconds)
                [MAIN CONTENT] (3-55 seconds)
                [CTA] (55-60 seconds)
                """,
                "title_generation": """
                Generate 5 engaging titles for a {platform} video about {topic}.
                Include keywords: {keywords}
                Make them clickable but not clickbait.
                Target audience: beginners
                """,
                "hashtag_research": """
                Research and provide 20 hashtags for {topic} on {platform}.
                Mix of:
                - 5 broad hashtags (1M+ posts)
                - 10 medium hashtags (100K-1M posts)
                - 5 niche hashtags (<100K posts)
                Include trending hashtags when relevant.
                """
            },
            "fliki_workflow": {
                "setup": "Choose AI avatar or voiceover style",
                "script_input": "Paste generated script",
                "voice_selection": "Select voice that matches brand",
                "scene_creation": "Add basic visuals/stock footage",
                "export_settings": "1080x1920 (vertical), MP4, high quality"
            },
            "heygen_workflow": {
                "avatar_selection": "Choose professional avatar",
                "script_input": "Input script with timestamps",
                "customization": "Brand colors, background",
                "rendering": "Generate video with avatar",
                "download": "Export for editing"
            },
            "runway_prompts": {
                "b_roll_generation": "Generate {duration} second video of {description}, cinematic, high quality",
                "style_options": ["realistic", "cinematic", "animated", "abstract"],
                "aspect_ratio": "9:16 (vertical)",
                "duration": "4-6 seconds per clip"
            },
            "capcut_workflow": {
                "import": "Import Fliki/HeyGen video + Runway B-roll",
                "editing_steps": [
                    "Trim and arrange clips",
                    "Add auto-captions",
                    "Insert B-roll during talking points",
                    "Add transitions",
                    "Color correction",
                    "Audio enhancement",
                    "Export 1080x1920"
                ],
                "templates": "Use trending CapCut templates",
                "effects": "Minimal, focus on content"
            },
            "canva_branding": {
                "intro_template": "3-second brand intro",
                "outro_template": "5-second CTA outro",
                "brand_elements": ["logo", "colors", "fonts"],
                "export": "MP4, transparent background if needed"
            },
            "metricool_setup": {
                "account_connection": "Connect TikTok + YouTube",
                "scheduling": "Set optimal posting times",
                "analytics_tracking": "Monitor engagement metrics",
                "hashtag_analysis": "Track hashtag performance"
            }
        }
    
    def _get_tools_setup_guide(self) -> Dict[str, Any]:
        """Provide setup guide for all tools"""
        
        return {
            "required_subscriptions": {
                "chatgpt_plus": "$20/month - For consistent script generation",
                "fliki_pro": "$28/month - For AI voiceovers and avatars",
                "heygen": "$30/month - Alternative for AI avatars",
                "runway_standard": "$15/month - For AI B-roll generation",
                "capcut_pro": "$10/month - For advanced editing features",
                "canva_pro": "$15/month - For brand templates",
                "metricool": "$18/month - For analytics and scheduling"
            },
            "free_alternatives": {
                "chatgpt": "Use free tier with longer prompts",
                "fliki": "Limited free credits available",
                "runway": "Free credits for testing",
                "capcut": "Free version has most features",
                "canva": "Free version with watermarks",
                "metricool": "Free tier for basic scheduling"
            },
            "setup_priority": [
                "1. ChatGPT - Start with script generation",
                "2. CapCut - Essential for editing",
                "3. Fliki/HeyGen - Choose one for voice/avatar",
                "4. Canva - For branding consistency",
                "5. Runway/Pika - Add when budget allows",
                "6. Metricool - For scaling to multiple platforms"
            ],
            "estimated_monthly_cost": {
                "starter": "$45-65/month (ChatGPT + CapCut + basic tools)",
                "intermediate": "$85-120/month (Add Fliki + Canva Pro)",
                "advanced": "$150-200/month (Full stack with all tools)"
            }
        }
    
    def _get_success_tips(self) -> List[str]:
        """Provide success tips for the workflow"""
        
        return [
            "🎯 Consistency is key - Post daily for first 30 days minimum",
            "📊 Track analytics weekly and adjust content based on performance",
            "🔥 Jump on trending topics within 24-48 hours",
            "💬 Engage with comments within first hour of posting",
            "🎨 Develop a recognizable visual style across all content",
            "📝 Batch create content - film 3-5 videos in one session",
            "⏰ Post at optimal times for your audience (test different times)",
            "🔗 Cross-promote between platforms to grow faster",
            "🎯 Focus on one niche initially, expand once established",
            "📈 Repurpose top-performing content into different formats",
            "💡 Always start with a strong hook in first 3 seconds",
            "🎪 Add personality - let your unique voice shine through",
            "📱 Optimize for mobile viewing (vertical format, large text)",
            "🔄 Create series/ongoing content to build anticipation",
            "🎬 Study top creators in your niche and adapt their strategies"
        ]
    
    def _estimate_engagement(self, content_type: str) -> str:
        """Estimate engagement potential based on content type"""
        
        engagement_rates = {
            "educational": "Medium-High (3-8%)",
            "tutorial": "High (5-12%)",
            "tips": "Medium (2-6%)",
            "behind_scenes": "Medium-High (4-9%)",
            "comparison": "Medium (3-7%)",
            "myth_busting": "High (6-15%)",
            "quick_wins": "High (5-10%)",
            "transformation": "Very High (8-20%)"
        }
        
        return engagement_rates.get(content_type, "Medium (3-7%)")
    
    def _assess_trending_potential(self, keyword: str, content_type: str) -> str:
        """Assess trending potential"""
        
        # This would ideally connect to trending APIs
        high_potential_types = ["myth_busting", "transformation", "quick_wins"]
        
        if content_type in high_potential_types:
            return "High"
        elif "tutorial" in content_type or "tips" in content_type:
            return "Medium"
        else:
            return "Low-Medium"

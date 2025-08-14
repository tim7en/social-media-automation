"""
AI Video Generation Tools Integration
Runway Gen-3 and Pika Labs for dynamic B-roll creation
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from ...core.config import settings
from ...core.logger import logger


class RunwayIntegration:
    """Runway Gen-3 integration for AI video generation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'RUNWAY_API_KEY', '')
        self.base_url = "https://api.runway.com/v1"
    
    async def generate_video_from_prompt(
        self,
        prompt: str,
        duration: int = 4,
        aspect_ratio: str = "9:16",
        style: str = "cinematic",
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate video from text prompt using Runway Gen-3"""
        
        try:
            request_data = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "style": style,
                "model": "gen3",
                "quality": "high"
            }
            
            if seed:
                request_data["seed"] = seed
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    task_id = result.get("id")
                    
                    # Wait for generation to complete
                    video_url = await self._wait_for_generation(task_id)
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "video_url": video_url,
                        "prompt": prompt,
                        "duration": duration,
                        "style": style
                    }
                else:
                    logger.error(f"Runway API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating Runway video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_generation(self, task_id: str, max_wait: int = 600) -> Optional[str]:
        """Wait for video generation to complete"""
        
        wait_time = 0
        check_interval = 15  # Check every 15 seconds
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/tasks/{task_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "SUCCEEDED":
                            return data.get("output", {}).get("url")
                        elif status == "FAILED":
                            logger.error(f"Runway generation failed: {data.get('failure_reason')}")
                            return None
                        
                        # Still processing
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                        
                        progress = data.get("progress", 0)
                        logger.info(f"Runway generation {task_id} progress: {progress}% ({wait_time}s)")
                    else:
                        logger.error(f"Error checking generation status: {response.status_code}")
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking generation: {e}")
                return None
        
        logger.error(f"Runway generation {task_id} timeout after {max_wait}s")
        return None
    
    async def generate_b_roll_sequence(
        self,
        script_sections: List[str],
        theme: str = "professional"
    ) -> List[Dict[str, Any]]:
        """Generate B-roll sequence for script sections"""
        
        b_roll_prompts = {
            "professional": [
                "Clean modern office space with natural lighting",
                "Person typing on laptop in coffee shop",
                "Close-up of hands writing notes",
                "Modern workspace with plants and natural light",
                "Abstract geometric shapes in motion",
                "City skyline during golden hour"
            ],
            "lifestyle": [
                "Cozy home interior with warm lighting",
                "Person enjoying morning coffee",
                "Hands organizing desk items",
                "Natural sunlight through window",
                "Minimalist room setup",
                "Outdoor nature scenery"
            ],
            "tech": [
                "Futuristic digital interface animations",
                "Code scrolling on dark screen",
                "High-tech gadgets on desk",
                "Neon lights and digital displays",
                "Abstract data visualization",
                "Modern tech workspace"
            ]
        }
        
        prompts = b_roll_prompts.get(theme, b_roll_prompts["professional"])
        b_roll_videos = []
        
        for i, section in enumerate(script_sections):
            prompt = prompts[i % len(prompts)]
            enhanced_prompt = f"{prompt}, cinematic, high quality, {theme} style"
            
            result = await self.generate_video_from_prompt(
                prompt=enhanced_prompt,
                duration=4,
                style="cinematic"
            )
            
            if result.get("success"):
                b_roll_videos.append({
                    "section_index": i,
                    "script_text": section,
                    "prompt": enhanced_prompt,
                    "video_url": result.get("video_url"),
                    "duration": 4
                })
        
        return b_roll_videos


class PikaIntegration:
    """Pika Labs integration for AI video generation"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'PIKA_API_KEY', '')
        self.base_url = "https://api.pika.art/v1"
    
    async def generate_video_from_image_and_prompt(
        self,
        image_url: str,
        prompt: str,
        duration: float = 3.0,
        motion_strength: float = 0.7
    ) -> Dict[str, Any]:
        """Generate video from image + prompt using Pika"""
        
        try:
            request_data = {
                "input_image": image_url,
                "prompt": prompt,
                "duration": duration,
                "motion_strength": motion_strength,
                "aspect_ratio": "9:16",
                "fps": 24
            }
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job_id = result.get("job_id")
                    
                    # Wait for completion
                    video_url = await self._wait_for_pika_completion(job_id)
                    
                    return {
                        "success": True,
                        "job_id": job_id,
                        "video_url": video_url,
                        "duration": duration
                    }
                else:
                    logger.error(f"Pika API error: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error generating Pika video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_text_to_video(
        self,
        prompt: str,
        style: str = "realistic",
        duration: float = 3.0
    ) -> Dict[str, Any]:
        """Generate video from text prompt only"""
        
        try:
            request_data = {
                "prompt": prompt,
                "style": style,
                "duration": duration,
                "aspect_ratio": "9:16",
                "quality": "high"
            }
            
            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(
                    f"{self.base_url}/text-to-video",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job_id = result.get("job_id")
                    
                    video_url = await self._wait_for_pika_completion(job_id)
                    
                    return {
                        "success": True,
                        "job_id": job_id,
                        "video_url": video_url,
                        "prompt": prompt,
                        "style": style
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error with Pika text-to-video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_pika_completion(self, job_id: str, max_wait: int = 300) -> Optional[str]:
        """Wait for Pika generation to complete"""
        
        wait_time = 0
        check_interval = 10
        
        while wait_time < max_wait:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/jobs/{job_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get("status")
                        
                        if status == "completed":
                            return data.get("video_url")
                        elif status == "failed":
                            logger.error(f"Pika generation failed: {data.get('error')}")
                            return None
                        
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                        
                        logger.info(f"Pika job {job_id} still processing... ({wait_time}s)")
                    else:
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking Pika completion: {e}")
                return None
        
        return None


class AIVideoManager:
    """Manager class for all AI video generation tools"""
    
    def __init__(self):
        self.runway = RunwayIntegration()
        self.pika = PikaIntegration()
    
    async def generate_dynamic_b_roll(
        self,
        script_sections: List[str],
        style: str = "cinematic",
        tool_preference: str = "runway"
    ) -> List[Dict[str, Any]]:
        """Generate dynamic B-roll using preferred tool"""
        
        if tool_preference == "runway":
            return await self.runway.generate_b_roll_sequence(script_sections, style)
        elif tool_preference == "pika":
            return await self._generate_pika_b_roll(script_sections, style)
        else:
            # Try both and return best results
            return await self._generate_hybrid_b_roll(script_sections, style)
    
    async def _generate_pika_b_roll(self, script_sections: List[str], style: str) -> List[Dict[str, Any]]:
        """Generate B-roll using Pika Labs"""
        
        b_roll_videos = []
        
        for i, section in enumerate(script_sections):
            # Create context-aware prompt
            prompt = f"Dynamic visual representing: {section[:100]}..., {style} style, engaging motion"
            
            result = await self.pika.generate_text_to_video(
                prompt=prompt,
                style=style,
                duration=3.0
            )
            
            if result.get("success"):
                b_roll_videos.append({
                    "section_index": i,
                    "script_text": section,
                    "prompt": prompt,
                    "video_url": result.get("video_url"),
                    "duration": 3.0,
                    "tool": "pika"
                })
        
        return b_roll_videos
    
    async def _generate_hybrid_b_roll(self, script_sections: List[str], style: str) -> List[Dict[str, Any]]:
        """Use both tools and combine best results"""
        
        # Generate with both tools in parallel
        runway_task = self.runway.generate_b_roll_sequence(script_sections[:len(script_sections)//2], style)
        pika_task = self._generate_pika_b_roll(script_sections[len(script_sections)//2:], style)
        
        runway_results, pika_results = await asyncio.gather(runway_task, pika_task)
        
        # Combine results
        all_results = runway_results + pika_results
        
        return sorted(all_results, key=lambda x: x.get("section_index", 0))

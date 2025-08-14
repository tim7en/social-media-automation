from typing import Optional, List, Dict, Any
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
from moviepy.video.fx import resize, loop
from PIL import Image, ImageDraw, ImageFont
import requests
from pathlib import Path
import asyncio
import aiofiles
from ..core.config import settings
from ..core.logger import logger


class VideoProcessor:
    """Video processing and generation service"""
    
    def __init__(self):
        self.output_dir = Path(settings.CONTENT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_video_from_script(
        self,
        script_data: Dict[str, Any],
        audio_path: str,
        video_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a complete video from script and audio"""
        
        config = video_config or {}
        
        # Default video settings
        width = config.get("width", 1080)
        height = config.get("height", 1920)  # Vertical video for shorts
        fps = config.get("fps", 30)
        background_color = config.get("background_color", "#000000")
        
        try:
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create background
            background = await self._create_background(
                width, height, duration, background_color, config
            )
            
            # Create text overlays based on script sections
            text_clips = await self._create_text_overlays(
                script_data, width, height, duration, config
            )
            
            # Add visual elements
            visual_clips = await self._create_visual_elements(
                script_data, width, height, duration, config
            )
            
            # Compose final video
            all_clips = [background] + text_clips + visual_clips
            final_video = CompositeVideoClip(all_clips, size=(width, height))
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_fps(fps)
            
            # Output path
            output_path = self.output_dir / f"video_{hash(str(script_data))}.mp4"
            
            # Render video
            await asyncio.to_thread(
                final_video.write_videofile,
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            audio_clip.close()
            final_video.close()
            
            logger.info(f"Video created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            raise
    
    async def _create_background(
        self,
        width: int,
        height: int,
        duration: float,
        background_color: str,
        config: Dict[str, Any]
    ) -> VideoFileClip:
        """Create animated background"""
        
        background_type = config.get("background_type", "solid")
        
        if background_type == "solid":
            # Solid color background
            background = await asyncio.to_thread(
                self._create_solid_background,
                width, height, duration, background_color
            )
        elif background_type == "gradient":
            # Gradient background
            colors = config.get("gradient_colors", [background_color, "#333333"])
            background = await asyncio.to_thread(
                self._create_gradient_background,
                width, height, duration, colors
            )
        elif background_type == "animated":
            # Animated background
            background = await asyncio.to_thread(
                self._create_animated_background,
                width, height, duration, config
            )
        else:
            # Default to solid
            background = await asyncio.to_thread(
                self._create_solid_background,
                width, height, duration, background_color
            )
        
        return background
    
    def _create_solid_background(
        self,
        width: int,
        height: int,
        duration: float,
        color: str
    ) -> ImageClip:
        """Create solid color background"""
        
        # Convert hex color to RGB
        color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        # Create image
        img = Image.new("RGB", (width, height), color_rgb)
        img_array = np.array(img)
        
        # Create video clip
        clip = ImageClip(img_array, duration=duration)
        return clip
    
    def _create_gradient_background(
        self,
        width: int,
        height: int,
        duration: float,
        colors: List[str]
    ) -> ImageClip:
        """Create gradient background"""
        
        # Convert colors to RGB
        rgb_colors = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) for c in colors]
        
        # Create gradient
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)
        
        for i in range(height):
            # Interpolate between colors
            ratio = i / height
            if len(rgb_colors) == 2:
                r = int(rgb_colors[0][0] * (1 - ratio) + rgb_colors[1][0] * ratio)
                g = int(rgb_colors[0][1] * (1 - ratio) + rgb_colors[1][1] * ratio)
                b = int(rgb_colors[0][2] * (1 - ratio) + rgb_colors[1][2] * ratio)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        img_array = np.array(img)
        clip = ImageClip(img_array, duration=duration)
        return clip
    
    def _create_animated_background(
        self,
        width: int,
        height: int,
        duration: float,
        config: Dict[str, Any]
    ) -> VideoFileClip:
        """Create animated background"""
        
        # For now, create a simple moving gradient
        def make_frame(t):
            # Create animated gradient that shifts over time
            img = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(img)
            
            # Calculate shift based on time
            shift = int((t / duration) * height)
            
            for i in range(height):
                ratio = ((i + shift) % height) / height
                r = int(50 + 100 * np.sin(ratio * np.pi))
                g = int(50 + 100 * np.sin(ratio * np.pi + np.pi/3))
                b = int(50 + 100 * np.sin(ratio * np.pi + 2*np.pi/3))
                draw.line([(0, i), (width, i)], fill=(r, g, b))
            
            return np.array(img)
        
        clip = VideoFileClip(make_frame, duration=duration)
        return clip
    
    async def _create_text_overlays(
        self,
        script_data: Dict[str, Any],
        width: int,
        height: int,
        duration: float,
        config: Dict[str, Any]
    ) -> List[TextClip]:
        """Create text overlays for script sections"""
        
        text_clips = []
        
        # Get script sections
        sections = script_data.get("parsed", {})
        if not sections:
            # Fallback to full script
            sections = {"main": script_data.get("script", "")}
        
        # Calculate timing for each section
        section_count = len(sections)
        section_duration = duration / section_count
        
        current_time = 0
        
        for section_name, content in sections.items():
            if not content or section_name in ["visual_notes"]:
                continue
            
            # Clean content
            clean_content = content.replace("[VISUAL NOTES]", "").strip()
            if not clean_content:
                continue
            
            # Create text clip
            text_clip = await asyncio.to_thread(
                self._create_text_clip,
                clean_content,
                width,
                height,
                section_duration,
                current_time,
                config
            )
            
            if text_clip:
                text_clips.append(text_clip)
            
            current_time += section_duration
        
        return text_clips
    
    def _create_text_clip(
        self,
        text: str,
        width: int,
        height: int,
        duration: float,
        start_time: float,
        config: Dict[str, Any]
    ) -> Optional[TextClip]:
        """Create a single text clip"""
        
        try:
            # Text styling
            font_size = config.get("font_size", 60)
            font_color = config.get("font_color", "white")
            font_family = config.get("font_family", "Arial-Bold")
            
            # Create text clip
            text_clip = TextClip(
                text,
                fontsize=font_size,
                color=font_color,
                font=font_family,
                size=(width * 0.8, None),
                method='caption'
            ).set_position('center').set_duration(duration).set_start(start_time)
            
            # Add text animation
            animation = config.get("text_animation", "none")
            if animation == "fade":
                text_clip = text_clip.crossfadein(0.5).crossfadeout(0.5)
            elif animation == "slide":
                text_clip = text_clip.set_position(lambda t: ('center', height/2 - 50*t))
            
            return text_clip
            
        except Exception as e:
            logger.error(f"Error creating text clip: {e}")
            return None
    
    async def _create_visual_elements(
        self,
        script_data: Dict[str, Any],
        width: int,
        height: int,
        duration: float,
        config: Dict[str, Any]
    ) -> List[VideoFileClip]:
        """Create additional visual elements"""
        
        visual_clips = []
        
        # Add particles or other visual effects
        if config.get("add_particles", False):
            particles = await asyncio.to_thread(
                self._create_particle_effect,
                width, height, duration
            )
            if particles:
                visual_clips.append(particles)
        
        # Add brand logo if provided
        logo_path = config.get("logo_path")
        if logo_path and Path(logo_path).exists():
            logo_clip = await asyncio.to_thread(
                self._create_logo_overlay,
                logo_path, width, height, duration, config
            )
            if logo_clip:
                visual_clips.append(logo_clip)
        
        return visual_clips
    
    def _create_particle_effect(
        self,
        width: int,
        height: int,
        duration: float
    ) -> Optional[VideoFileClip]:
        """Create particle effect overlay"""
        
        try:
            def make_frame(t):
                img = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Create random particles
                num_particles = 50
                for _ in range(num_particles):
                    x = int(np.random.random() * width)
                    y = int((np.random.random() + t/duration) * height) % height
                    
                    # Draw particle
                    cv2.circle(img, (x, y), 2, (255, 255, 255), -1)
                
                return img
            
            clip = VideoFileClip(make_frame, duration=duration)
            return clip.set_opacity(0.3)
            
        except Exception as e:
            logger.error(f"Error creating particle effect: {e}")
            return None
    
    def _create_logo_overlay(
        self,
        logo_path: str,
        width: int,
        height: int,
        duration: float,
        config: Dict[str, Any]
    ) -> Optional[ImageClip]:
        """Create logo overlay"""
        
        try:
            logo_size = config.get("logo_size", 0.1)  # 10% of video width
            logo_position = config.get("logo_position", "bottom-right")
            
            logo_clip = ImageClip(logo_path, duration=duration)
            
            # Resize logo
            logo_width = int(width * logo_size)
            logo_clip = logo_clip.resize(width=logo_width)
            
            # Position logo
            if logo_position == "bottom-right":
                logo_clip = logo_clip.set_position(('right', 'bottom')).set_margin(20)
            elif logo_position == "top-right":
                logo_clip = logo_clip.set_position(('right', 'top')).set_margin(20)
            elif logo_position == "bottom-left":
                logo_clip = logo_clip.set_position(('left', 'bottom')).set_margin(20)
            else:
                logo_clip = logo_clip.set_position('center')
            
            return logo_clip.set_opacity(0.8)
            
        except Exception as e:
            logger.error(f"Error creating logo overlay: {e}")
            return None
    
    async def add_subtitles(
        self,
        video_path: str,
        subtitle_text: str,
        output_path: Optional[str] = None
    ) -> str:
        """Add subtitles to video"""
        
        if not output_path:
            output_path = video_path.replace(".mp4", "_subtitled.mp4")
        
        try:
            video = VideoFileClip(video_path)
            
            # Create subtitle clip
            subtitle_clip = TextClip(
                subtitle_text,
                fontsize=50,
                color='white',
                font='Arial-Bold'
            ).set_position(('center', 'bottom')).set_duration(video.duration)
            
            # Add black background to subtitles
            subtitle_bg = TextClip(
                subtitle_text,
                fontsize=50,
                color='black',
                font='Arial-Bold'
            ).set_position(('center', 'bottom')).set_duration(video.duration)
            
            # Composite video
            final_video = CompositeVideoClip([video, subtitle_bg, subtitle_clip])
            
            await asyncio.to_thread(
                final_video.write_videofile,
                output_path,
                verbose=False,
                logger=None
            )
            
            video.close()
            final_video.close()
            
            logger.info(f"Subtitled video created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            raise

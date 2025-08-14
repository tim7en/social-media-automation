import subprocess
import os
import tempfile
from typing import Dict, Any, Optional, List
import asyncio

class FFmpegConnector:
    """Wrapper for FFmpeg operations"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        
    async def extract_audio(self, video_path: str, output_path: str = None) -> str:
        """Extract audio from video"""
        if not output_path:
            output_path = tempfile.mktemp(suffix=".mp3")
            
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-q:a", "2",  # Quality
            output_path
        ]
        
        await self._run_command(cmd)
        return output_path
        
    async def add_subtitles(self, video_path: str, subtitle_path: str, output_path: str = None) -> str:
        """Add subtitles to video"""
        if not output_path:
            output_path = tempfile.mktemp(suffix=".mp4")
            
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vf", f"subtitles={subtitle_path}",
            "-c:a", "copy",
            output_path
        ]
        
        await self._run_command(cmd)
        return output_path
        
    async def resize_video(self, video_path: str, width: int, height: int, output_path: str = None) -> str:
        """Resize video for different platforms"""
        if not output_path:
            output_path = tempfile.mktemp(suffix=".mp4")
            
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vf", f"scale={width}:{height}",
            "-c:a", "copy",
            output_path
        ]
        
        await self._run_command(cmd)
        return output_path
        
    async def create_video_from_images(self, images: List[str], audio_path: str = None, duration: int = 5) -> str:
        """Create slideshow video from images"""
        output_path = tempfile.mktemp(suffix=".mp4")
        
        # Create concat file
        concat_file = tempfile.mktemp(suffix=".txt")
        with open(concat_file, 'w') as f:
            for image in images:
                f.write(f"file '{image}'\n")
                f.write(f"duration {duration}\n")
                
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        if audio_path:
            cmd.extend(["-i", audio_path, "-c:a", "aac", "-shortest"])
            
        await self._run_command(cmd)
        
        # Cleanup
        os.unlink(concat_file)
        
        return output_path
        
    async def _run_command(self, cmd: List[str]):
        """Run FFmpeg command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
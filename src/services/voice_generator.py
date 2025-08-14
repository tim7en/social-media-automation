from typing import Optional, BinaryIO
import httpx
from elevenlabs import generate, Voice, VoiceSettings
from ..core.config import settings
from ..core.logger import logger
import asyncio
from pathlib import Path


class VoiceGenerator:
    """ElevenLabs voice generation service"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.default_voice_id = settings.ELEVENLABS_VOICE_ID
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        output_path: Optional[str] = None
    ) -> str:
        """Generate speech from text"""
        
        voice_id = voice_id or self.default_voice_id
        
        if not voice_id:
            raise ValueError("No voice ID provided and no default voice ID configured")
        
        try:
            # Run the synchronous ElevenLabs function in a thread
            audio = await asyncio.to_thread(
                generate,
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost,
                        style=style,
                        use_speaker_boost=use_speaker_boost
                    )
                ),
                api_key=self.api_key
            )
            
            # Save the audio file
            if not output_path:
                output_path = f"/tmp/speech_{hash(text)}.mp3"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(audio)
            
            logger.info(f"Generated speech audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise
    
    async def get_available_voices(self) -> list[dict]:
        """Get list of available voices"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                
                voices_data = response.json()
                return voices_data.get("voices", [])
                
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            raise
    
    async def clone_voice(
        self,
        name: str,
        description: str,
        audio_files: list[str],
        labels: Optional[dict] = None
    ) -> str:
        """Clone a voice from audio samples"""
        
        try:
            files = []
            for i, audio_file in enumerate(audio_files):
                with open(audio_file, "rb") as f:
                    files.append(("files", (f"sample_{i}.mp3", f.read(), "audio/mpeg")))
            
            data = {
                "name": name,
                "description": description
            }
            
            if labels:
                data["labels"] = str(labels)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    data=data,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                voice_id = result.get("voice_id")
                
                logger.info(f"Voice cloned successfully: {voice_id}")
                return voice_id
                
        except Exception as e:
            logger.error(f"Error cloning voice: {e}")
            raise
    
    async def get_voice_settings(self, voice_id: str) -> dict:
        """Get voice settings"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices/{voice_id}/settings",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting voice settings: {e}")
            raise
    
    async def update_voice_settings(
        self,
        voice_id: str,
        stability: float,
        similarity_boost: float,
        style: Optional[float] = None,
        use_speaker_boost: Optional[bool] = None
    ) -> dict:
        """Update voice settings"""
        
        settings_data = {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
        
        if style is not None:
            settings_data["style"] = style
        if use_speaker_boost is not None:
            settings_data["use_speaker_boost"] = use_speaker_boost
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/voices/{voice_id}/settings/edit",
                    headers={"xi-api-key": self.api_key},
                    json=settings_data
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            raise
    
    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a custom voice"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/voices/{voice_id}",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                
                logger.info(f"Voice deleted: {voice_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting voice: {e}")
            raise
    
    async def get_user_info(self) -> dict:
        """Get user subscription info and usage"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise

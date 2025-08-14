from typing import Optional, BinaryIO, TYPE_CHECKING
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    # Fallback for older versions
    ElevenLabs = None
    VoiceSettings = None
    ELEVENLABS_AVAILABLE = False

if TYPE_CHECKING:
    from elevenlabs.client import ElevenLabs as ElevenLabsType
else:
    ElevenLabsType = None

from ..core.config import settings
from ..core.logger import logger
from .api_key_service import api_key_service
import asyncio
from pathlib import Path


class VoiceGenerator:
    """ElevenLabs voice generation service"""
    
    def __init__(self):
        self.default_voice_id = getattr(settings, 'ELEVENLABS_VOICE_ID', None)
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def _get_elevenlabs_client(self, user_id: int, db: AsyncSession) -> Optional[ElevenLabsType]:
        """Get ElevenLabs client with user-specific API key"""
        api_key = await api_key_service.get_user_api_key(user_id, "elevenlabs", db)
        if not api_key:
            logger.warning(f"No ElevenLabs API key found for user {user_id}")
            return None
        
        if not ELEVENLABS_AVAILABLE:
            logger.error("ElevenLabs library not available")
            return None
        
        try:
            return ElevenLabs(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client for user {user_id}: {e}")
            return None
    
    async def generate_speech(
        self,
        text: str,
        user_id: int,
        db: AsyncSession,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
        output_path: Optional[str] = None
    ) -> str:
        """Generate speech from text"""
        
        client = await self._get_elevenlabs_client(user_id, db)
        if not client:
            raise ValueError("ElevenLabs API key not configured for this user")
        
        voice_id = voice_id or self.default_voice_id
        
        if not voice_id:
            logger.warning("No voice ID provided and no default voice ID configured")
            raise ValueError("No voice ID provided and no default voice ID configured")
        
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            # Use HTTP API directly for better compatibility
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                
                if response.status_code == 200:
                    # Save the audio file
                    if not output_path:
                        output_path = f"/tmp/speech_{hash(text)}.mp3"
                    
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    
                    logger.info(f"Generated speech audio: {output_path}")
                    return output_path
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    raise Exception(f"ElevenLabs API error: {response.status_code}")
            
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

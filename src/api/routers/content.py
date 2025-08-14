from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from ...core.database import get_db
from ...schemas import (
    ContentGenerationRequest,
    ContentItem,
    ContentItemCreate,
    TaskResponse,
    MessageResponse
)
from ...services import AIContentGenerator, VoiceGenerator, VideoProcessor
from ...tasks.content_generation import generate_complete_content
from ...core.logger import logger

router = APIRouter()

ai_generator = AIContentGenerator()
voice_generator = VoiceGenerator()
video_processor = VideoProcessor()


@router.post("/generate", response_model=TaskResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate AI content (script, voice, video)"""
    
    try:
        # Start background task for content generation
        task = generate_complete_content.delay(request.dict())
        
        logger.info(f"Started content generation task: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            message="Content generation started",
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Error starting content generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/script", response_model=Dict[str, Any])
async def generate_script(
    topic: str,
    style: str = "engaging",
    duration: int = 60,
    platform: str = "youtube",
    additional_context: str = None
):
    """Generate just a script"""
    
    try:
        result = await ai_generator.generate_script(
            topic=topic,
            style=style,
            duration=duration,
            platform=platform,
            additional_context=additional_context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/titles", response_model=List[str])
async def generate_titles(
    topic: str,
    platform: str = "youtube",
    count: int = 5
):
    """Generate title suggestions"""
    
    try:
        titles = await ai_generator.generate_title_suggestions(
            topic=topic,
            platform=platform,
            count=count
        )
        
        return titles
        
    except Exception as e:
        logger.error(f"Error generating titles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/description", response_model=str)
async def generate_description(
    title: str,
    script: str,
    platform: str = "youtube"
):
    """Generate description for social media post"""
    
    try:
        description = await ai_generator.generate_description(
            title=title,
            script=script,
            platform=platform
        )
        
        return description
        
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hashtags", response_model=List[str])
async def generate_hashtags(
    topic: str,
    platform: str = "youtube",
    count: int = 10
):
    """Generate relevant hashtags"""
    
    try:
        hashtags = await ai_generator.generate_hashtags(
            topic=topic,
            platform=platform,
            count=count
        )
        
        return hashtags
        
    except Exception as e:
        logger.error(f"Error generating hashtags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice", response_model=Dict[str, str])
async def generate_voice(
    text: str,
    voice_id: str = None,
    stability: float = 0.5,
    similarity_boost: float = 0.75
):
    """Generate voice audio from text"""
    
    try:
        audio_path = await voice_generator.generate_speech(
            text=text,
            voice_id=voice_id,
            stability=stability,
            similarity_boost=similarity_boost
        )
        
        return {"audio_path": audio_path}
        
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices", response_model=List[Dict[str, Any]])
async def get_available_voices():
    """Get list of available ElevenLabs voices"""
    
    try:
        voices = await voice_generator.get_available_voices()
        return voices
        
    except Exception as e:
        logger.error(f"Error fetching voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video", response_model=Dict[str, str])
async def create_video(
    script_data: Dict[str, Any],
    audio_path: str,
    video_config: Dict[str, Any] = None
):
    """Create video from script and audio"""
    
    try:
        video_path = await video_processor.create_video_from_script(
            script_data=script_data,
            audio_path=audio_path,
            video_config=video_config
        )
        
        return {"video_path": video_path}
        
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """Get status of content generation task"""
    
    try:
        from ...core.celery_app import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "progress": getattr(task, 'info', {})
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

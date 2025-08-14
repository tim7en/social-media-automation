from celery import Task
from typing import Dict, Any
from ..core.celery_app import celery_app
from ..services import AIContentGenerator, VoiceGenerator, VideoProcessor
from ..core.logger import logger


class CallbackTask(Task):
    """Custom task class with callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True)
def generate_complete_content(self, content_request: Dict[str, Any]):
    """Generate complete content (script, voice, video)"""
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'step': 'initializing', 'progress': 0}
        )
        
        # Initialize services
        ai_generator = AIContentGenerator()
        voice_generator = VoiceGenerator()
        video_processor = VideoProcessor()
        
        logger.info(f"Starting content generation for: {content_request.get('title')}")
        
        # Step 1: Generate script
        self.update_state(
            state='PROGRESS',
            meta={'step': 'generating_script', 'progress': 20}
        )
        
        script_result = ai_generator.generate_script(
            topic=content_request['topic'],
            style=content_request.get('style', 'engaging'),
            duration=content_request.get('duration', 60),
            platform=content_request.get('target_platforms', ['youtube'])[0],
            additional_context=content_request.get('description')
        )
        
        # Step 2: Generate voice
        self.update_state(
            state='PROGRESS',
            meta={'step': 'generating_voice', 'progress': 40}
        )
        
        audio_path = voice_generator.generate_speech(
            text=script_result['script'],
            voice_id=content_request.get('voice_id'),
            stability=0.5,
            similarity_boost=0.75
        )
        
        # Step 3: Generate additional content
        self.update_state(
            state='PROGRESS',
            meta={'step': 'generating_metadata', 'progress': 60}
        )
        
        # Generate titles, description, hashtags
        titles = ai_generator.generate_title_suggestions(
            topic=content_request['topic'],
            platform=content_request.get('target_platforms', ['youtube'])[0],
            count=5
        )
        
        description = ai_generator.generate_description(
            title=content_request['title'],
            script=script_result['script'],
            platform=content_request.get('target_platforms', ['youtube'])[0]
        )
        
        hashtags = ai_generator.generate_hashtags(
            topic=content_request['topic'],
            platform=content_request.get('target_platforms', ['youtube'])[0],
            count=10
        )
        
        # Step 4: Create video
        self.update_state(
            state='PROGRESS',
            meta={'step': 'creating_video', 'progress': 80}
        )
        
        video_config = {
            "width": 1080,
            "height": 1920,
            "background_type": "gradient",
            "gradient_colors": ["#1a1a2e", "#16213e"],
            "font_size": 60,
            "font_color": "white",
            "text_animation": "fade",
            "add_particles": True
        }
        
        video_path = video_processor.create_video_from_script(
            script_data=script_result,
            audio_path=audio_path,
            video_config=video_config
        )
        
        # Step 5: Complete
        self.update_state(
            state='PROGRESS',
            meta={'step': 'finalizing', 'progress': 100}
        )
        
        result = {
            'success': True,
            'content_id': self.request.id,
            'script': script_result,
            'audio_path': audio_path,
            'video_path': video_path,
            'titles': titles,
            'description': description,
            'hashtags': hashtags,
            'metadata': {
                'duration': script_result.get('estimated_duration'),
                'word_count': script_result.get('word_count'),
                'platforms': content_request.get('target_platforms', [])
            }
        }
        
        logger.info(f"Content generation completed: {self.request.id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in content generation task: {e}")
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'step': 'failed'}
        )
        
        raise


@celery_app.task(base=CallbackTask)
def generate_script_only(topic: str, style: str = "engaging", duration: int = 60, platform: str = "youtube"):
    """Generate only a script"""
    
    try:
        ai_generator = AIContentGenerator()
        
        result = ai_generator.generate_script(
            topic=topic,
            style=style,
            duration=duration,
            platform=platform
        )
        
        logger.info(f"Script generated for topic: {topic}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise


@celery_app.task(base=CallbackTask)
def generate_voice_only(text: str, voice_id: str = None):
    """Generate only voice audio"""
    
    try:
        voice_generator = VoiceGenerator()
        
        audio_path = voice_generator.generate_speech(
            text=text,
            voice_id=voice_id
        )
        
        logger.info(f"Voice generated: {audio_path}")
        
        return {"audio_path": audio_path}
        
    except Exception as e:
        logger.error(f"Error generating voice: {e}")
        raise


@celery_app.task(base=CallbackTask)
def create_video_only(script_data: Dict[str, Any], audio_path: str, video_config: Dict[str, Any] = None):
    """Create only video"""
    
    try:
        video_processor = VideoProcessor()
        
        video_path = video_processor.create_video_from_script(
            script_data=script_data,
            audio_path=audio_path,
            video_config=video_config
        )
        
        logger.info(f"Video created: {video_path}")
        
        return {"video_path": video_path}
        
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        raise

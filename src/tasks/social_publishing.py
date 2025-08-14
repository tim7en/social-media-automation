from celery import Task
from typing import Dict, Any, List
from ..core.celery_app import celery_app
from ..services import SocialMediaPublisher
from ..core.logger import logger


class CallbackTask(Task):
    """Custom task class with callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Publishing task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Publishing task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True)
def publish_content_task(self, video_path: str, platforms: List[str], content_data: Dict[str, Any]):
    """Publish content to multiple platforms"""
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'step': 'initializing', 'progress': 0, 'platforms': platforms}
        )
        
        publisher = SocialMediaPublisher()
        results = {}
        
        total_platforms = len(platforms)
        
        for i, platform in enumerate(platforms):
            try:
                # Update progress
                progress = int((i / total_platforms) * 80) + 10
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'step': f'publishing_to_{platform}',
                        'progress': progress,
                        'current_platform': platform
                    }
                )
                
                logger.info(f"Publishing to {platform}")
                
                if platform == "youtube":
                    result = publisher.publish_to_youtube(
                        video_path=video_path,
                        title=content_data.get("title", ""),
                        description=content_data.get("description", ""),
                        tags=content_data.get("tags", []),
                        privacy_status=content_data.get("privacy_status", "public")
                    )
                elif platform == "facebook":
                    result = publisher.publish_to_facebook(
                        video_path=video_path,
                        message=content_data.get("message", ""),
                        page_id=content_data.get("page_id")
                    )
                elif platform == "instagram":
                    result = publisher.publish_to_instagram(
                        video_path=video_path,
                        caption=content_data.get("caption", ""),
                        hashtags=content_data.get("hashtags", [])
                    )
                elif platform == "tiktok":
                    result = publisher.publish_to_tiktok(
                        video_path=video_path,
                        caption=content_data.get("caption", ""),
                        hashtags=content_data.get("hashtags", [])
                    )
                else:
                    result = {
                        "success": False,
                        "platform": platform,
                        "error": f"Platform {platform} not supported"
                    }
                
                results[platform] = result
                
                if result.get("success"):
                    logger.info(f"Successfully published to {platform}: {result.get('url', 'N/A')}")
                else:
                    logger.error(f"Failed to publish to {platform}: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = {
                    "success": False,
                    "platform": platform,
                    "error": str(e)
                }
        
        # Final update
        self.update_state(
            state='PROGRESS',
            meta={'step': 'completed', 'progress': 100, 'results': results}
        )
        
        # Calculate success rate
        successful_publishes = sum(1 for result in results.values() if result.get("success"))
        success_rate = (successful_publishes / total_platforms) * 100 if total_platforms > 0 else 0
        
        final_result = {
            "success": success_rate > 0,
            "results": results,
            "summary": {
                "total_platforms": total_platforms,
                "successful_publishes": successful_publishes,
                "failed_publishes": total_platforms - successful_publishes,
                "success_rate": success_rate
            }
        }
        
        logger.info(f"Publishing completed. Success rate: {success_rate}%")
        
        return final_result
        
    except Exception as e:
        logger.error(f"Error in publishing task: {e}")
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'step': 'failed'}
        )
        
        raise


@celery_app.task(base=CallbackTask)
def publish_to_single_platform(platform: str, video_path: str, content_data: Dict[str, Any]):
    """Publish content to a single platform"""
    
    try:
        publisher = SocialMediaPublisher()
        
        logger.info(f"Publishing to {platform}")
        
        if platform == "youtube":
            result = publisher.publish_to_youtube(
                video_path=video_path,
                title=content_data.get("title", ""),
                description=content_data.get("description", ""),
                tags=content_data.get("tags", [])
            )
        elif platform == "facebook":
            result = publisher.publish_to_facebook(
                video_path=video_path,
                message=content_data.get("message", ""),
                page_id=content_data.get("page_id")
            )
        elif platform == "instagram":
            result = publisher.publish_to_instagram(
                video_path=video_path,
                caption=content_data.get("caption", ""),
                hashtags=content_data.get("hashtags", [])
            )
        elif platform == "tiktok":
            result = publisher.publish_to_tiktok(
                video_path=video_path,
                caption=content_data.get("caption", ""),
                hashtags=content_data.get("hashtags", [])
            )
        else:
            result = {
                "success": False,
                "platform": platform,
                "error": f"Platform {platform} not supported"
            }
        
        logger.info(f"Publishing to {platform} completed: {'Success' if result.get('success') else 'Failed'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error publishing to {platform}: {e}")
        raise


@celery_app.task(base=CallbackTask, bind=True)
def schedule_content_publishing(self, content_id: int, schedule_config: Dict[str, Any]):
    """Schedule content for future publishing"""
    
    try:
        # TODO: Implement scheduled publishing logic
        # This would involve:
        # 1. Storing the schedule in database
        # 2. Setting up periodic tasks
        # 3. Managing recurring content
        
        logger.info(f"Scheduling content {content_id} for publishing")
        
        # For now, return placeholder
        return {
            "success": True,
            "content_id": content_id,
            "schedule_config": schedule_config,
            "message": "Content scheduled successfully"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling content: {e}")
        raise


@celery_app.task(base=CallbackTask)
def update_content_analytics(post_id: str, platform: str):
    """Update analytics for published content"""
    
    try:
        publisher = SocialMediaPublisher()
        
        logger.info(f"Updating analytics for {platform} post: {post_id}")
        
        analytics = publisher.get_platform_analytics(platform, post_id)
        
        # TODO: Store analytics in database
        
        logger.info(f"Analytics updated for {platform} post: {post_id}")
        
        return {
            "success": True,
            "platform": platform,
            "post_id": post_id,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
        raise

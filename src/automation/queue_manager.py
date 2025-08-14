from typing import Dict, Any, List
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
import json
import uuid
from datetime import datetime, timedelta
import asyncio

# Try to import existing Celery app or create a minimal one
try:
    from ..core.celery_app import celery_app
except ImportError:
    # Fallback Celery setup if not available
    try:
        from celery import Celery
        celery_app = Celery(
            'content_automation',
            broker='redis://localhost:6379/0',
            backend='redis://localhost:6379/1'
        )
    except ImportError:
        celery_app = None

# Celery configuration (only if available)
if celery_app:
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )

def execute_workflow_async(workflow_id: str, context: Dict[str, Any] = None):
    """Execute workflow asynchronously (mock implementation)"""
    # Mock implementation when Celery is not available
    return {"status": "success", "workflow_id": workflow_id, "context": context}

def schedule_content_post(content_id: str, platforms: List[str], scheduled_time: str):
    """Schedule content posting (mock implementation)"""
    return {"status": "scheduled", "platforms": platforms, "time": scheduled_time}

def post_to_platform(content_id: str, platform: str):
    """Post content to specific platform (mock implementation)"""
    return {"status": "success", "platform": platform, "content_id": content_id}

def check_scheduled_posts():
    """Check for posts that need to be published (mock implementation)"""
    return {"checked": True, "pending_posts": 0}

def process_content_queue():
    """Process content generation queue (mock implementation)"""
    return {"processed": True, "message": "Queue processed"}

def update_analytics():
    """Update analytics data from platforms (mock implementation)"""
    return {"updated": True, "platforms": ["instagram", "youtube", "tiktok"]}

# If Celery is available, register tasks
if celery_app:
    @celery_app.task
    def execute_workflow_async_task(workflow_id: str, context: Dict[str, Any] = None):
        """Execute workflow asynchronously"""
        from ..workflows.engine import WorkflowEngine
        import asyncio
        
        engine = WorkflowEngine()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                engine.execute_workflow(workflow_id, context)
            )
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            loop.close()

    @celery_app.task
    def schedule_content_post_task(content_id: str, platforms: List[str], scheduled_time: str):
        """Schedule content posting"""
        eta = datetime.fromisoformat(scheduled_time)
        
        for platform in platforms:
            post_to_platform_task.apply_async(
                args=[content_id, platform],
                eta=eta
            )
        
        return {"status": "scheduled", "platforms": platforms, "time": scheduled_time}

    @celery_app.task
    def post_to_platform_task(content_id: str, platform: str):
        """Post content to specific platform"""
        # Mock implementation
        return {"status": "success", "platform": platform, "content_id": content_id}

    @celery_app.task
    def check_scheduled_posts_task():
        """Check for posts that need to be published"""
        return {"checked": True, "pending_posts": 0}

    @celery_app.task
    def process_content_queue_task():
        """Process content generation queue"""
        queue_manager = QueueManager()
        
        # Process high priority items
        job = queue_manager.get_next_job("content_generation")
        if job:
            return {"processed": True, "job_id": job.get("id")}
        
        return {"processed": False, "message": "No jobs in queue"}

    @celery_app.task
    def update_analytics_task():
        """Update analytics data from platforms"""
        return {"updated": True, "platforms": ["instagram", "youtube", "tiktok"]}

class QueueManager:
    """Manage job queues and priorities"""
    
    def __init__(self):
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
            except Exception:
                # Fallback to None if Redis is not available
                self.redis_client = None
        else:
            self.redis_client = None
        
    def add_to_queue(self, queue_name: str, job_data: Dict[str, Any], priority: int = 5):
        """Add job to queue with priority"""
        job = {
            "id": str(uuid.uuid4()),
            "data": job_data,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        if self.redis_client:
            # Use Redis sorted set for priority queue
            self.redis_client.zadd(
                f"queue:{queue_name}",
                {json.dumps(job): priority}
            )
        else:
            # Fallback to returning job ID without queueing
            pass
            
        return job["id"]
    
    def get_next_job(self, queue_name: str):
        """Get highest priority job from queue"""
        if not self.redis_client:
            return None
            
        result = self.redis_client.zpopmin(f"queue:{queue_name}", count=1)
        
        if result:
            job_json, _ = result[0]
            return json.loads(job_json)
        return None
    
    def get_queue_stats(self, queue_name: str):
        """Get queue statistics"""
        if not self.redis_client:
            return {"queue_name": queue_name, "size": 0, "status": "unavailable"}
            
        queue_size = self.redis_client.zcard(f"queue:{queue_name}")
        
        return {
            "queue_name": queue_name,
            "size": queue_size,
            "oldest_job": self.redis_client.zrange(f"queue:{queue_name}", 0, 0),
            "newest_job": self.redis_client.zrange(f"queue:{queue_name}", -1, -1)
        }
    
    def clear_queue(self, queue_name: str):
        """Clear all jobs from a queue"""
        if self.redis_client:
            self.redis_client.delete(f"queue:{queue_name}")
            return True
        return False
    
    def get_job_status(self, job_id: str):
        """Get status of a specific job"""
        # Mock implementation - in production would track job status
        return {
            "job_id": job_id,
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }
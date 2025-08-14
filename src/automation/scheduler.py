from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import uuid

class ContentScheduler:
    """Advanced content scheduling system"""
    
    def __init__(self, db_session = None):
        self.db = db_session
        self.optimal_times = {
            "instagram": {
                "weekday": ["08:00", "12:00", "17:00", "20:00"],
                "weekend": ["10:00", "14:00", "19:00"]
            },
            "tiktok": {
                "weekday": ["06:00", "10:00", "19:00", "23:00"],
                "weekend": ["09:00", "16:00", "20:00"]
            },
            "youtube": {
                "weekday": ["14:00", "17:00", "20:00"],
                "weekend": ["10:00", "15:00", "20:00"]
            }
        }
        
    async def schedule_content(
        self,
        content_id: str,
        platforms: List[str],
        schedule_type: str = "optimal",  # optimal, specific, recurring
        specific_time: Optional[datetime] = None,
        recurrence: Optional[Dict[str, Any]] = None
    ):
        """Schedule content based on type"""
        
        if schedule_type == "optimal":
            scheduled_times = self.get_optimal_times(platforms)
        elif schedule_type == "specific":
            scheduled_times = {platform: specific_time for platform in platforms}
        elif schedule_type == "recurring":
            scheduled_times = self.calculate_recurring_times(platforms, recurrence)
        else:
            # Default to immediate
            now = datetime.utcnow()
            scheduled_times = {platform: now for platform in platforms}
        
        scheduled_items = []
        for platform, time in scheduled_times.items():
            scheduled_item = {
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "platform": platform,
                "scheduled_time": time,
                "status": "pending",
                "created_at": datetime.utcnow()
            }
            
            # In production, would save to database
            if self.db:
                # Mock database save
                pass
                
            scheduled_items.append(scheduled_item)
        
        return scheduled_items
    
    def get_optimal_times(self, platforms: List[str]) -> Dict[str, datetime]:
        """Get optimal posting times for platforms"""
        now = datetime.utcnow()
        scheduled_times = {}
        
        for platform in platforms:
            platform_times = self.optimal_times.get(platform, {})
            is_weekend = now.weekday() >= 5
            
            times = platform_times.get("weekend" if is_weekend else "weekday", [])
            
            # Find next available optimal time
            for time_str in times:
                hour, minute = map(int, time_str.split(":"))
                scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if scheduled_time <= now:
                    scheduled_time += timedelta(days=1)
                
                # Check if time slot is available (mock implementation)
                if self._is_time_slot_available(platform, scheduled_time):
                    scheduled_times[platform] = scheduled_time
                    break
            
            # Fallback to next hour if no optimal time found
            if platform not in scheduled_times:
                scheduled_times[platform] = now + timedelta(hours=1)
        
        return scheduled_times
    
    def _is_time_slot_available(self, platform: str, scheduled_time: datetime) -> bool:
        """Check if a time slot is available for posting"""
        # Mock implementation - in production would check database
        # for existing scheduled posts in the time window
        return True
    
    def calculate_recurring_times(
        self,
        platforms: List[str],
        recurrence: Dict[str, Any]
    ) -> Dict[str, List[datetime]]:
        """Calculate recurring posting times"""
        frequency = recurrence.get("frequency", "daily")  # daily, weekly, monthly
        interval = recurrence.get("interval", 1)
        end_date = recurrence.get("end_date")
        start_time = recurrence.get("start_time")
        
        if not end_date:
            end_date = datetime.utcnow() + timedelta(days=30)  # Default to 30 days
        elif isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_time:
            start_time = datetime.utcnow()
        elif isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        scheduled_times = {}
        
        for platform in platforms:
            times = []
            current_date = start_time
            
            while current_date <= end_date:
                times.append(current_date)
                
                if frequency == "daily":
                    current_date += timedelta(days=interval)
                elif frequency == "weekly":
                    current_date += timedelta(weeks=interval)
                elif frequency == "monthly":
                    current_date += timedelta(days=30 * interval)
                else:
                    break  # Unknown frequency
            
            # For recurring, return the first scheduled time
            scheduled_times[platform] = times[0] if times else start_time
        
        return scheduled_times
    
    def get_scheduled_content(self, platform: str = None, status: str = "pending") -> List[Dict]:
        """Get scheduled content items"""
        # Mock implementation - in production would query database
        mock_scheduled = [
            {
                "id": "sched_001",
                "content_id": "content_123",
                "platform": "instagram",
                "scheduled_time": datetime.utcnow() + timedelta(hours=2),
                "status": "pending"
            },
            {
                "id": "sched_002", 
                "content_id": "content_124",
                "platform": "youtube",
                "scheduled_time": datetime.utcnow() + timedelta(hours=6),
                "status": "pending"
            }
        ]
        
        # Filter by platform if specified
        if platform:
            mock_scheduled = [item for item in mock_scheduled if item["platform"] == platform]
            
        # Filter by status
        mock_scheduled = [item for item in mock_scheduled if item["status"] == status]
        
        return mock_scheduled
    
    def cancel_scheduled_content(self, schedule_id: str) -> bool:
        """Cancel a scheduled content item"""
        # Mock implementation - in production would update database
        return True
    
    def update_schedule(self, schedule_id: str, new_time: datetime) -> bool:
        """Update scheduled time for content"""
        # Mock implementation - in production would update database
        return True

class ContentQueue:
    """Manage content generation queue"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = False
        
    async def add_to_queue(self, task: Dict[str, Any]):
        """Add task to generation queue"""
        await self.queue.put({
            "id": str(uuid.uuid4()),
            "task": task,
            "added_at": datetime.utcnow(),
            "priority": task.get("priority", 5)
        })
    
    async def process_queue(self):
        """Process content generation queue"""
        self.processing = True
        
        while self.processing:
            try:
                # Get task from queue
                task_data = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Execute task
                await self.execute_task(task_data)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing queue: {e}")
    
    def stop_processing(self):
        """Stop queue processing"""
        self.processing = False
    
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute a single task from queue"""
        task = task_data["task"]
        task_type = task.get("type")
        
        if task_type == "generate_content":
            await self.generate_content(task)
        elif task_type == "process_video":
            await self.process_video(task)
        elif task_type == "schedule_post":
            await self.schedule_post(task)
        else:
            print(f"Unknown task type: {task_type}")
    
    async def generate_content(self, task: Dict[str, Any]):
        """Generate content task"""
        # Mock implementation
        print(f"Generating content for task: {task.get('id')}")
        await asyncio.sleep(1)  # Simulate processing time
    
    async def process_video(self, task: Dict[str, Any]):
        """Process video task"""
        # Mock implementation
        print(f"Processing video for task: {task.get('id')}")
        await asyncio.sleep(2)  # Simulate processing time
    
    async def schedule_post(self, task: Dict[str, Any]):
        """Schedule post task"""
        # Mock implementation
        print(f"Scheduling post for task: {task.get('id')}")
        await asyncio.sleep(0.5)  # Simulate processing time
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def clear_queue(self):
        """Clear all items from queue"""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
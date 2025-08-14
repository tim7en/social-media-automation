from typing import Dict, Any
from .processors import BaseNode

class TriggerNode(BaseNode):
    """Base class for trigger nodes that start workflows"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Triggers typically provide initial data"""
        return inputs

class ScheduleTrigger(TriggerNode):
    """Trigger workflows on a schedule"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        schedule_time = self.config.get("schedule_time")
        
        return {
            "trigger_type": "schedule",
            "scheduled_time": schedule_time,
            "triggered_at": context.get("current_time"),
            **inputs
        }

class WebhookTrigger(TriggerNode):
    """Trigger workflows from webhook events"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        webhook_data = inputs.get("webhook_data", {})
        
        return {
            "trigger_type": "webhook",
            "source": webhook_data.get("source"),
            "event_type": webhook_data.get("event_type"),
            "data": webhook_data.get("data", {}),
            **inputs
        }

class ManualTrigger(TriggerNode):
    """Trigger workflows manually"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "trigger_type": "manual",
            "user_id": context.get("user_id"),
            "triggered_at": context.get("current_time"),
            **inputs
        }

class ContentUploadTrigger(TriggerNode):
    """Trigger when content is uploaded"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        file_path = inputs.get("file_path")
        file_type = inputs.get("file_type")
        
        return {
            "trigger_type": "content_upload",
            "file_path": file_path,
            "file_type": file_type,
            "upload_time": context.get("current_time"),
            **inputs
        }
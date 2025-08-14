from typing import Dict, Any
from .processors import BaseNode

class ActionNode(BaseNode):
    """Base class for action nodes that perform operations"""
    pass

class SendEmailAction(ActionNode):
    """Send email notifications"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        recipient = self.config.get("recipient")
        subject = self.config.get("subject", "Workflow Notification")
        template = self.config.get("template", "default")
        
        # Mock email sending - in production would integrate with email service
        email_data = {
            "recipient": recipient,
            "subject": subject,
            "template": template,
            "data": inputs
        }
        
        return {
            "action": "email_sent",
            "status": "success",
            "email_id": "email_123456",
            **email_data
        }

class SlackNotificationAction(ActionNode):
    """Send Slack notifications"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        channel = self.config.get("channel", "#general")
        message = self.config.get("message", "Workflow completed")
        
        # Format message with input data
        formatted_message = message.format(**inputs)
        
        return {
            "action": "slack_sent",
            "status": "success",
            "channel": channel,
            "message": formatted_message
        }

class WebhookAction(ActionNode):
    """Send webhook to external service"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.get("url")
        method = self.config.get("method", "POST")
        headers = self.config.get("headers", {})
        
        # Mock webhook sending - in production would make HTTP request
        return {
            "action": "webhook_sent",
            "status": "success",
            "url": url,
            "method": method,
            "response_code": 200
        }

class DatabaseAction(ActionNode):
    """Perform database operations"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        operation = self.config.get("operation", "insert")
        table = self.config.get("table")
        data = inputs.get("data", {})
        
        # Mock database operation - in production would interact with database
        return {
            "action": "database_operation",
            "status": "success",
            "operation": operation,
            "table": table,
            "affected_rows": 1
        }

class FileOperationAction(ActionNode):
    """Perform file operations"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        operation = self.config.get("operation", "copy")
        source_path = inputs.get("source_path")
        destination_path = self.config.get("destination_path")
        
        if operation == "copy":
            # Mock file copy
            return {
                "action": "file_copied",
                "status": "success",
                "source": source_path,
                "destination": destination_path
            }
        elif operation == "move":
            # Mock file move
            return {
                "action": "file_moved",
                "status": "success",
                "source": source_path,
                "destination": destination_path
            }
        elif operation == "delete":
            # Mock file delete
            return {
                "action": "file_deleted",
                "status": "success",
                "path": source_path
            }
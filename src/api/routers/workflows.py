from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ...workflows.engine import WorkflowEngine
from ...workflows.templates import WORKFLOW_TEMPLATES
from ...automation.queue_manager import QueueManager, execute_workflow_async
from ...automation.scheduler import ContentScheduler
from ...automation.monitoring import workflow_monitor

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

# Initialize components
workflow_engine = WorkflowEngine()
queue_manager = QueueManager()
scheduler = ContentScheduler()

@router.post("/execute")
async def execute_workflow(
    workflow_id: str,
    context: Dict[str, Any] = None,
    background_tasks: BackgroundTasks = None,
    async_execution: bool = True
):
    """Execute a workflow"""
    try:
        if async_execution:
            # Execute asynchronously using Celery
            task = execute_workflow_async.delay(workflow_id, context)
            return {
                "status": "queued",
                "task_id": task.id,
                "workflow_id": workflow_id,
                "execution_type": "async"
            }
        else:
            # Execute synchronously
            execution_id = str(uuid.uuid4())
            workflow_monitor.track_workflow_start(workflow_id, execution_id, context or {})
            
            try:
                result = await workflow_engine.execute_workflow(workflow_id, context)
                workflow_monitor.track_workflow_completion(execution_id, result)
                
                return {
                    "status": "completed",
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "result": result,
                    "execution_type": "sync"
                }
            except Exception as e:
                workflow_monitor.track_workflow_failure(execution_id, str(e))
                raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}")

@router.get("/status/{execution_id}")
async def get_workflow_status(execution_id: str):
    """Get workflow execution status"""
    status = workflow_monitor.get_workflow_status(execution_id)
    
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    return status

@router.get("/templates")
async def list_workflow_templates():
    """List available workflow templates"""
    templates = []
    
    for template_id, template_data in WORKFLOW_TEMPLATES.items():
        templates.append({
            "id": template_id,
            "name": template_data["name"],
            "description": template_data["description"],
            "node_count": len(template_data["nodes"])
        })
    
    return {"templates": templates}

@router.get("/templates/{template_id}")
async def get_workflow_template(template_id: str):
    """Get a specific workflow template"""
    if template_id not in WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return WORKFLOW_TEMPLATES[template_id]

@router.post("/create-from-template")
async def create_workflow_from_template(
    template_id: str,
    workflow_name: str,
    customizations: Dict[str, Any] = None
):
    """Create a new workflow from a template"""
    if template_id not in WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = WORKFLOW_TEMPLATES[template_id].copy()
    
    # Apply customizations if provided
    if customizations:
        for node in template["nodes"]:
            node_id = node["id"]
            if node_id in customizations:
                node["config"].update(customizations[node_id])
    
    # Create new workflow
    new_workflow_id = str(uuid.uuid4())
    template["id"] = new_workflow_id
    template["name"] = workflow_name
    template["created_at"] = datetime.utcnow().isoformat()
    
    # In production, would save to database
    
    return {
        "workflow_id": new_workflow_id,
        "name": workflow_name,
        "template_id": template_id,
        "status": "created"
    }

@router.post("/schedule")
async def schedule_workflow(
    workflow_id: str,
    schedule_type: str = "optimal",  # optimal, specific, recurring
    platforms: List[str] = None,
    specific_time: Optional[datetime] = None,
    recurrence: Optional[Dict[str, Any]] = None
):
    """Schedule workflow execution"""
    try:
        content_id = f"workflow_{workflow_id}_{uuid.uuid4()}"
        
        scheduled_items = await scheduler.schedule_content(
            content_id=content_id,
            platforms=platforms or ["instagram"],
            schedule_type=schedule_type,
            specific_time=specific_time,
            recurrence=recurrence
        )
        
        return {
            "status": "scheduled",
            "workflow_id": workflow_id,
            "content_id": content_id,
            "scheduled_items": scheduled_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule workflow: {str(e)}")

@router.get("/scheduled")
async def get_scheduled_workflows(platform: str = None):
    """Get scheduled workflow executions"""
    scheduled_content = scheduler.get_scheduled_content(platform=platform)
    
    return {
        "scheduled_workflows": scheduled_content,
        "total": len(scheduled_content)
    }

@router.delete("/scheduled/{schedule_id}")
async def cancel_scheduled_workflow(schedule_id: str):
    """Cancel a scheduled workflow"""
    success = scheduler.cancel_scheduled_content(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Scheduled workflow not found")
    
    return {"status": "cancelled", "schedule_id": schedule_id}

@router.post("/queue/add")
async def add_to_queue(
    queue_name: str,
    job_data: Dict[str, Any],
    priority: int = 5
):
    """Add a job to the workflow queue"""
    job_id = queue_manager.add_to_queue(queue_name, job_data, priority)
    
    return {
        "status": "queued",
        "job_id": job_id,
        "queue_name": queue_name,
        "priority": priority
    }

@router.get("/queue/{queue_name}/stats")
async def get_queue_stats(queue_name: str):
    """Get queue statistics"""
    stats = queue_manager.get_queue_stats(queue_name)
    return stats

@router.post("/queue/{queue_name}/clear")
async def clear_queue(queue_name: str):
    """Clear all jobs from a queue"""
    success = queue_manager.clear_queue(queue_name)
    
    return {
        "status": "cleared" if success else "failed",
        "queue_name": queue_name
    }

@router.get("/monitoring/performance")
async def get_performance_metrics():
    """Get workflow performance metrics"""
    metrics = workflow_monitor.get_performance_metrics()
    return metrics

@router.get("/monitoring/running")
async def get_running_workflows():
    """Get currently running workflows"""
    running = list(workflow_monitor.running_workflows.values())
    return {
        "running_workflows": running,
        "count": len(running)
    }

@router.post("/validate")
async def validate_workflow(workflow_definition: Dict[str, Any]):
    """Validate a workflow definition"""
    try:
        # Basic validation
        required_fields = ["id", "name", "nodes"]
        for field in required_fields:
            if field not in workflow_definition:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        # Validate nodes
        nodes = workflow_definition.get("nodes", [])
        if not nodes:
            return {
                "valid": False,
                "error": "Workflow must have at least one node"
            }
        
        for node in nodes:
            if "id" not in node or "type" not in node:
                return {
                    "valid": False,
                    "error": "Each node must have 'id' and 'type' fields"
                }
        
        return {
            "valid": True,
            "message": "Workflow definition is valid",
            "node_count": len(nodes)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }

@router.post("/test-run")
async def test_workflow(
    workflow_definition: Dict[str, Any],
    test_context: Dict[str, Any] = None
):
    """Test run a workflow with mock data"""
    try:
        # Validate first
        validation = await validate_workflow(workflow_definition)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Create test execution
        execution_id = str(uuid.uuid4())
        workflow_id = workflow_definition["id"]
        
        # Mock execution for testing
        test_result = {
            "status": "test_completed",
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "test_mode": True,
            "nodes_executed": len(workflow_definition["nodes"]),
            "mock_results": {
                node["id"]: f"Mock result for {node['type']}"
                for node in workflow_definition["nodes"]
            }
        }
        
        return test_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@router.get("/nodes/types")
async def get_available_node_types():
    """Get available workflow node types"""
    node_types = {
        "triggers": [
            {"type": "ScheduleTrigger", "description": "Trigger workflows on a schedule"},
            {"type": "WebhookTrigger", "description": "Trigger workflows from webhook events"},
            {"type": "ManualTrigger", "description": "Trigger workflows manually"},
            {"type": "ContentUploadTrigger", "description": "Trigger when content is uploaded"}
        ],
        "processors": [
            {"type": "ContentGeneratorNode", "description": "Generate content using AI"},
            {"type": "VideoProcessorNode", "description": "Process videos using FFmpeg"},
            {"type": "ImageProcessorNode", "description": "Process images"},
            {"type": "BatchProcessorNode", "description": "Process multiple items in batch"},
            {"type": "PlatformOptimizerNode", "description": "Optimize content for platforms"},
            {"type": "TranscriptionNode", "description": "Transcribe audio to text"},
            {"type": "VideoClipperNode", "description": "Extract clips from videos"}
        ],
        "actions": [
            {"type": "SocialMediaPostNode", "description": "Post to social media platform"},
            {"type": "MultiPlatformPostNode", "description": "Post to multiple platforms"},
            {"type": "SendEmailAction", "description": "Send email notifications"},
            {"type": "SlackNotificationAction", "description": "Send Slack notifications"},
            {"type": "WebhookAction", "description": "Send webhook to external service"},
            {"type": "DatabaseAction", "description": "Perform database operations"},
            {"type": "FileOperationAction", "description": "Perform file operations"}
        ],
        "conditions": [
            {"type": "ComparisonCondition", "description": "Compare two values"},
            {"type": "ExistsCondition", "description": "Check if field exists"},
            {"type": "TimeCondition", "description": "Check time-based conditions"},
            {"type": "LogicCondition", "description": "Combine conditions with AND/OR"},
            {"type": "PlatformCondition", "description": "Check platform conditions"},
            {"type": "ContentLengthCondition", "description": "Check content length"}
        ]
    }
    
    return node_types
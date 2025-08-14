import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

class NodeType(Enum):
    TRIGGER = "trigger"
    PROCESSOR = "processor"
    ACTION = "action"
    CONDITION = "condition"
    TOOL = "tool"

@dataclass
class WorkflowNode:
    id: str
    type: NodeType
    name: str
    config: Dict[str, Any]
    inputs: List[str] = None
    outputs: List[str] = None
    
class WorkflowEngine:
    def __init__(self):
        self.nodes = {}
        self.executors = {}
        self.running_workflows = {}
        
    def register_node_type(self, node_type: str, executor_class):
        """Register a new node type with its executor"""
        self.executors[node_type] = executor_class
        
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None):
        """Execute a complete workflow"""
        workflow = await self.load_workflow(workflow_id)
        execution_id = str(uuid.uuid4())
        
        self.running_workflows[execution_id] = {
            "workflow_id": workflow_id,
            "status": "running",
            "started_at": datetime.utcnow(),
            "context": context or {}
        }
        
        try:
            result = await self._execute_nodes(workflow, context)
            self.running_workflows[execution_id]["status"] = "completed"
            return result
        except Exception as e:
            self.running_workflows[execution_id]["status"] = "failed"
            self.running_workflows[execution_id]["error"] = str(e)
            raise
            
    async def load_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Load workflow definition from storage"""
        # For now, return a sample workflow - in production this would load from database
        return {
            "id": workflow_id,
            "name": "Sample Workflow",
            "nodes": []
        }
            
    async def _execute_nodes(self, workflow: Dict, context: Dict):
        """Execute workflow nodes in sequence"""
        results = {}
        
        for node in workflow["nodes"]:
            node_id = node["id"]
            node_type = node["type"]
            
            # Get the executor for this node type
            executor_class = self.executors.get(node_type)
            if not executor_class:
                raise ValueError(f"Unknown node type: {node_type}")
                
            executor = executor_class(node["config"])
            
            # Prepare inputs from previous nodes
            inputs = {}
            for input_key, source in node.get("inputs", {}).items():
                if source.startswith("$"):
                    # Reference to previous node output
                    source_node, source_key = source[1:].split(".")
                    inputs[input_key] = results.get(source_node, {}).get(source_key)
                else:
                    inputs[input_key] = source
                    
            # Execute the node
            result = await executor.execute(inputs, context)
            results[node_id] = result
            
        return results
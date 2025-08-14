from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

class WorkflowMonitor:
    """Monitor workflow execution and performance"""
    
    def __init__(self):
        self.running_workflows = {}
        self.completed_workflows = {}
        self.failed_workflows = {}
        
    def track_workflow_start(self, workflow_id: str, execution_id: str, context: Dict[str, Any]):
        """Track when a workflow starts"""
        self.running_workflows[execution_id] = {
            "workflow_id": workflow_id,
            "started_at": datetime.utcnow(),
            "context": context,
            "status": "running",
            "nodes_completed": 0,
            "current_node": None
        }
    
    def track_node_completion(self, execution_id: str, node_id: str, result: Dict[str, Any]):
        """Track when a workflow node completes"""
        if execution_id in self.running_workflows:
            workflow = self.running_workflows[execution_id]
            workflow["nodes_completed"] += 1
            workflow["current_node"] = node_id
            workflow["last_node_result"] = result
            workflow["last_updated"] = datetime.utcnow()
    
    def track_workflow_completion(self, execution_id: str, result: Dict[str, Any]):
        """Track when a workflow completes successfully"""
        if execution_id in self.running_workflows:
            workflow = self.running_workflows.pop(execution_id)
            workflow["completed_at"] = datetime.utcnow()
            workflow["duration"] = (workflow["completed_at"] - workflow["started_at"]).total_seconds()
            workflow["result"] = result
            workflow["status"] = "completed"
            self.completed_workflows[execution_id] = workflow
    
    def track_workflow_failure(self, execution_id: str, error: str):
        """Track when a workflow fails"""
        if execution_id in self.running_workflows:
            workflow = self.running_workflows.pop(execution_id)
            workflow["failed_at"] = datetime.utcnow()
            workflow["duration"] = (workflow["failed_at"] - workflow["started_at"]).total_seconds()
            workflow["error"] = error
            workflow["status"] = "failed"
            self.failed_workflows[execution_id] = workflow
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if execution_id in self.running_workflows:
            return self.running_workflows[execution_id]
        elif execution_id in self.completed_workflows:
            return self.completed_workflows[execution_id]
        elif execution_id in self.failed_workflows:
            return self.failed_workflows[execution_id]
        else:
            return {"status": "not_found"}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics"""
        total_completed = len(self.completed_workflows)
        total_failed = len(self.failed_workflows)
        total_running = len(self.running_workflows)
        
        if total_completed > 0:
            avg_duration = sum(w["duration"] for w in self.completed_workflows.values()) / total_completed
        else:
            avg_duration = 0
        
        success_rate = total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0
        
        return {
            "total_workflows": total_completed + total_failed + total_running,
            "completed": total_completed,
            "failed": total_failed,
            "running": total_running,
            "success_rate": round(success_rate * 100, 2),
            "average_duration": round(avg_duration, 2)
        }

class SystemMonitor:
    """Monitor system resources and health"""
    
    def __init__(self):
        self.metrics_history = []
        
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        import psutil
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network
        network = psutil.net_io_counters()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": round((disk.used / disk.total) * 100, 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_recv": network.bytes_recv
        }
        
        # Keep last 100 metrics
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
        
        return metrics
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}
        
        latest = self.metrics_history[-1]
        
        # Health thresholds
        cpu_threshold = 80
        memory_threshold = 85
        disk_threshold = 90
        
        issues = []
        status = "healthy"
        
        if latest["cpu_percent"] > cpu_threshold:
            issues.append(f"High CPU usage: {latest['cpu_percent']}%")
            status = "warning"
        
        if latest["memory_percent"] > memory_threshold:
            issues.append(f"High memory usage: {latest['memory_percent']}%")
            status = "warning"
        
        if latest["disk_percent"] > disk_threshold:
            issues.append(f"High disk usage: {latest['disk_percent']}%")
            status = "critical"
        
        return {
            "status": status,
            "issues": issues,
            "metrics": latest
        }

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alert_rules = []
        self.active_alerts = {}
        
    def add_alert_rule(self, name: str, condition: str, severity: str, message: str):
        """Add an alert rule"""
        rule = {
            "name": name,
            "condition": condition,
            "severity": severity,
            "message": message,
            "created_at": datetime.utcnow()
        }
        self.alert_rules.append(rule)
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """Check if any alert conditions are met"""
        for rule in self.alert_rules:
            alert_triggered = self._evaluate_condition(rule["condition"], metrics)
            
            if alert_triggered:
                await self._trigger_alert(rule, metrics)
            elif rule["name"] in self.active_alerts:
                # Alert condition no longer met, resolve alert
                await self._resolve_alert(rule["name"])
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition"""
        # Simple condition evaluation - in production would use a proper parser
        try:
            # Replace metric names with values
            for key, value in metrics.items():
                condition = condition.replace(f"{{{key}}}", str(value))
            
            # Evaluate the condition
            return eval(condition)
        except Exception:
            return False
    
    async def _trigger_alert(self, rule: Dict[str, Any], metrics: Dict[str, Any]):
        """Trigger an alert"""
        if rule["name"] not in self.active_alerts:
            alert = {
                "rule": rule,
                "triggered_at": datetime.utcnow(),
                "metrics": metrics,
                "status": "active"
            }
            
            self.active_alerts[rule["name"]] = alert
            
            # Send notification (mock implementation)
            await self._send_notification(rule, metrics)
    
    async def _resolve_alert(self, rule_name: str):
        """Resolve an active alert"""
        if rule_name in self.active_alerts:
            alert = self.active_alerts.pop(rule_name)
            alert["resolved_at"] = datetime.utcnow()
            alert["status"] = "resolved"
            
            # Send resolution notification (mock implementation)
            print(f"Alert resolved: {rule_name}")
    
    async def _send_notification(self, rule: Dict[str, Any], metrics: Dict[str, Any]):
        """Send alert notification"""
        # Mock implementation - in production would send email, Slack, etc.
        print(f"ALERT [{rule['severity']}]: {rule['message']}")
        print(f"Metrics: {metrics}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        return list(self.active_alerts.values())

# Global instances
workflow_monitor = WorkflowMonitor()
system_monitor = SystemMonitor()
alert_manager = AlertManager()

# Setup default alert rules
alert_manager.add_alert_rule(
    "high_cpu",
    "{cpu_percent} > 80",
    "warning",
    "High CPU usage detected: {cpu_percent}%"
)

alert_manager.add_alert_rule(
    "high_memory",
    "{memory_percent} > 85",
    "warning",
    "High memory usage detected: {memory_percent}%"
)

alert_manager.add_alert_rule(
    "high_disk",
    "{disk_percent} > 90",
    "critical",
    "High disk usage detected: {disk_percent}%"
)
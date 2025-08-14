from typing import Dict, Any
from .processors import BaseNode

class ConditionNode(BaseNode):
    """Base class for condition nodes that control workflow flow"""
    
    async def execute(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        condition_result = await self.evaluate_condition(inputs, context)
        
        return {
            "condition_result": condition_result,
            "condition_type": self.config.get("type"),
            **inputs
        }
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate the condition - to be implemented by subclasses"""
        raise NotImplementedError

class ComparisonCondition(ConditionNode):
    """Compare two values"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        left_value = inputs.get(self.config.get("left_field"))
        right_value = self.config.get("right_value")
        operator = self.config.get("operator", "equals")
        
        if operator == "equals":
            return left_value == right_value
        elif operator == "not_equals":
            return left_value != right_value
        elif operator == "greater_than":
            return left_value > right_value
        elif operator == "less_than":
            return left_value < right_value
        elif operator == "contains":
            return str(right_value) in str(left_value)
        elif operator == "starts_with":
            return str(left_value).startswith(str(right_value))
        elif operator == "ends_with":
            return str(left_value).endswith(str(right_value))
        
        return False

class ExistsCondition(ConditionNode):
    """Check if a field exists and has a value"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        field_name = self.config.get("field_name")
        check_empty = self.config.get("check_empty", True)
        
        if field_name not in inputs:
            return False
        
        value = inputs[field_name]
        
        if check_empty:
            return value is not None and value != "" and value != []
        else:
            return value is not None

class TimeCondition(ConditionNode):
    """Check time-based conditions"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        from datetime import datetime, time
        
        condition_type = self.config.get("time_type", "hour")
        target_value = self.config.get("target_value")
        
        current_time = datetime.utcnow()
        
        if condition_type == "hour":
            return current_time.hour == target_value
        elif condition_type == "day_of_week":
            return current_time.weekday() == target_value
        elif condition_type == "day_of_month":
            return current_time.day == target_value
        elif condition_type == "between_hours":
            start_hour = self.config.get("start_hour", 0)
            end_hour = self.config.get("end_hour", 23)
            return start_hour <= current_time.hour <= end_hour
        
        return False

class LogicCondition(ConditionNode):
    """Combine multiple conditions with AND/OR logic"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        logic_type = self.config.get("logic_type", "and")
        conditions = self.config.get("conditions", [])
        
        results = []
        
        for condition_config in conditions:
            condition_type = condition_config.get("type")
            
            # Create and evaluate sub-condition
            if condition_type == "comparison":
                condition = ComparisonCondition(condition_config)
            elif condition_type == "exists":
                condition = ExistsCondition(condition_config)
            elif condition_type == "time":
                condition = TimeCondition(condition_config)
            else:
                continue
            
            result = await condition.evaluate_condition(inputs, context)
            results.append(result)
        
        if logic_type == "and":
            return all(results)
        elif logic_type == "or":
            return any(results)
        elif logic_type == "not":
            return not all(results)
        
        return False

class PlatformCondition(ConditionNode):
    """Check platform-specific conditions"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        platform = inputs.get("platform")
        allowed_platforms = self.config.get("allowed_platforms", [])
        blocked_platforms = self.config.get("blocked_platforms", [])
        
        if blocked_platforms and platform in blocked_platforms:
            return False
        
        if allowed_platforms and platform not in allowed_platforms:
            return False
        
        return True

class ContentLengthCondition(ConditionNode):
    """Check content length conditions"""
    
    async def evaluate_condition(self, inputs: Dict[str, Any], context: Dict[str, Any]) -> bool:
        content_field = self.config.get("content_field", "content")
        min_length = self.config.get("min_length", 0)
        max_length = self.config.get("max_length", float('inf'))
        
        content = inputs.get(content_field, "")
        content_length = len(str(content))
        
        return min_length <= content_length <= max_length
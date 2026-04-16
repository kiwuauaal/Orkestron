import redis
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SharedState:
    """Shared state management using Redis"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
    
    # Task Management
    def add_task(self, task: Dict):
        """Add a task to the pending queue"""
        task_id = task.get('task_id')
        if not task_id:
            raise ValueError("Task must have a task_id")
        
        task['status'] = 'pending'
        task['created_at'] = datetime.now().isoformat()
        
        self.redis_client.hset(
            "tasks:pending",
            task_id,
            json.dumps(task)
        )
        logger.info(f"Added task: {task_id}")
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        # Check pending tasks
        task_data = self.redis_client.hget("tasks:pending", task_id)
        if task_data:
            return json.loads(task_data)
        
        # Check completed tasks
        task_data = self.redis_client.hget("tasks:completed", task_id)
        if task_data:
            return json.loads(task_data)
        
        return None
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        tasks_dict = self.redis_client.hgetall("tasks:pending")
        return [json.loads(task_data) for task_data in tasks_dict.values()]
    
    def move_task_to_completed(self, task_id: str, result: Dict):
        """Move a task from pending to completed"""
        task_data = self.redis_client.hget("tasks:pending", task_id)
        if task_data:
            task = json.loads(task_data)
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            task['result'] = result
            
            # Remove from pending
            self.redis_client.hdel("tasks:pending", task_id)
            
            # Add to completed
            self.redis_client.hset(
                "tasks:completed",
                task_id,
                json.dumps(task)
            )
            
            logger.info(f"Task {task_id} marked as completed")
    
    def move_task_to_failed(self, task_id: str, error: str):
        """Move a task from pending to failed"""
        task_data = self.redis_client.hget("tasks:pending", task_id)
        if task_data:
            task = json.loads(task_data)
            task['status'] = 'failed'
            task['failed_at'] = datetime.now().isoformat()
            task['error'] = error
            
            # Remove from pending
            self.redis_client.hdel("tasks:pending", task_id)
            
            # Add to failed
            self.redis_client.hset(
                "tasks:failed",
                task_id,
                json.dumps(task)
            )
            
            logger.info(f"Task {task_id} marked as failed")
    
    # Agent Status Management
    def update_agent_status(self, agent: str, status: str):
        """Update agent status"""
        self.redis_client.hset(
            "agents:status",
            agent,
            json.dumps({
                "status": status,
                "updated_at": datetime.now().isoformat()
            })
        )
    
    def get_agent_status(self, agent: str) -> Dict:
        """Get agent status"""
        status_data = self.redis_client.hget("agents:status", agent)
        return json.loads(status_data) if status_data else {"status": "unknown"}
    
    def get_all_agents_status(self) -> Dict:
        """Get status of all agents"""
        agents_dict = self.redis_client.hgetall("agents:status")
        return {
            agent: json.loads(status_data)
            for agent, status_data in agents_dict.items()
        }
    
    # Cycle Management
    def update_cycle_status(self, phase: str):
        """Update current cycle phase"""
        self.redis_client.set("cycle:current_phase", phase)
        self.redis_client.set("cycle:last_updated", datetime.now().isoformat())
    
    def get_cycle_status(self) -> Dict:
        """Get current cycle status"""
        return {
            "phase": self.redis_client.get("cycle:current_phase") or "idle",
            "last_updated": self.redis_client.get("cycle:last_updated")
        }
    
    # Metrics Management
    def set_metric(self, key: str, value):
        """Set a metric value"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        else:
            value = str(value)
        
        self.redis_client.set(f"metrics:{key}", value)
    
    def get_metric(self, key: str) -> Optional[str]:
        """Get a metric value"""
        value = self.redis_client.get(f"metrics:{key}")
        return value
    
    def get_all_metrics(self) -> Dict:
        """Get all metrics"""
        metrics_keys = self.redis_client.keys("metrics:*")
        metrics = {}
        
        for key in metrics_keys:
            metric_key = key.replace("metrics:", "")
            value = self.redis_client.get(key)
            try:
                metrics[metric_key] = json.loads(value)
            except:
                metrics[metric_key] = value
        
        return metrics
    
    # Logs Management
    def add_log(self, log_entry: Dict):
        """Add a log entry"""
        log_entry['timestamp'] = datetime.now().isoformat()
        self.redis_client.lpush(
            "logs:system",
            json.dumps(log_entry)
        )
        # Keep only last 1000 logs
        self.redis_client.ltrim("logs:system", 0, 999)
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        logs = self.redis_client.lrange("logs:system", 0, limit - 1)
        return [json.loads(log) for log in logs]
    
    # Deployment Status
    def update_deployment_status(self, status: str, details: Optional[Dict] = None):
        """Update deployment status"""
        deployment_data = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
            "details": details or {}
        }
        self.redis_client.set("deployment:status", json.dumps(deployment_data))
    
    def get_deployment_status(self) -> Dict:
        """Get deployment status"""
        status_data = self.redis_client.get("deployment:status")
        return json.loads(status_data) if status_data else {"status": "unknown"}
    
    # Utility Methods
    def clear_all(self):
        """Clear all data (use with caution!)"""
        self.redis_client.flushdb()
        logger.warning("All shared state cleared")
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return self.redis_client.ping()
        except:
            return False

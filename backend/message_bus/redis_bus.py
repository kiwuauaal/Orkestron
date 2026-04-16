import redis
import json
from typing import Callable
from datetime import datetime


class RedisMessageBus:
    """Redis-based message bus for agent communication"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db,
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
    
    def publish(self, channel: str, message: dict):
        """Publish a message to a channel"""
        message['timestamp'] = datetime.now().isoformat()
        self.redis_client.publish(channel, json.dumps(message))
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to a channel and process messages"""
        self.pubsub.subscribe(channel)
        for msg in self.pubsub.listen():
            if msg['type'] == 'message':
                callback(json.loads(msg['data']))
    
    def publish_task(self, agent_name: str, task: dict):
        """Publish a task to a specific agent"""
        channel = f"agent:{agent_name}:tasks"
        self.publish(channel, task)
    
    def get_agent_status(self, agent_name: str) -> dict:
        """Get current status of an agent"""
        status = self.redis_client.hget("agents:status", agent_name)
        return json.loads(status) if status else {}
    
    def set_agent_status(self, agent_name: str, status: str):
        """Set agent status"""
        self.redis_client.hset(
            "agents:status", 
            agent_name, 
            json.dumps({
                "status": status,
                "updated_at": datetime.now().isoformat()
            })
        )

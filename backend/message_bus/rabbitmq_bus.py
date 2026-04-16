import pika
import json
from typing import Callable
from datetime import datetime


class RabbitMQBus:
    """RabbitMQ-based message bus for reliable task queue management"""
    
    def __init__(self, host='localhost', port=5672):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port
            )
        )
        self.channel = self.connection.channel()
    
    def send_task(self, queue: str, task: dict):
        """Send a task to a specific queue"""
        self.channel.queue_declare(queue=queue, durable=True)
        task['timestamp'] = datetime.now().isoformat()
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(task),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
    
    def receive_task(self, queue: str, callback: Callable):
        """Receive tasks from a queue"""
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=self.__wrap_callback(callback)
        )
        self.channel.start_consuming()
    
    def __wrap_callback(self, callback: Callable):
        """Wrap callback to handle message acknowledgment"""
        def wrapper(ch, method, properties, body):
            try:
                task = json.loads(body)
                callback(task)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        return wrapper
    
    def create_queue(self, queue_name: str):
        """Create a new queue"""
        self.channel.queue_declare(queue=queue_name, durable=True)
    
    def get_queue_size(self, queue_name: str) -> int:
        """Get the number of messages in a queue"""
        result = self.channel.queue_declare(queue=queue_name, passive=True)
        return result.method.message_count
    
    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

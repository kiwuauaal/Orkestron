from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import json
import asyncio
import logging
import os
from datetime import datetime
from pydantic import BaseModel

from orchestrator.central_ai import CentralOrchestrator
from shared_memory.state import SharedState
from message_bus.redis_bus import RedisMessageBus

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Orkestron API",
    description="Multi-agent orchestration system API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized in startup)
orchestrator: Optional[CentralOrchestrator] = None
shared_state: Optional[SharedState] = None
message_bus: Optional[RedisMessageBus] = None
connected_clients: List[WebSocket] = []


class TaskInput(BaseModel):
    task_id: str
    title: str
    description: str
    type: str = "backend"
    priority: str = "medium"
    dependencies: List[str] = []


class RequirementsInput(BaseModel):
    requirements: str
    project_type: str = "web_application"


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global orchestrator, shared_state, message_bus
    
    try:
        # Import backend components
        from orchestrator.central_ai import CentralOrchestrator
        from shared_memory.state import SharedState
        from message_bus.redis_bus import RedisMessageBus
        
        # Initialize with environment variables or defaults
        api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
        
        orchestrator = CentralOrchestrator(api_key=api_key)
        shared_state = SharedState()
        message_bus = RedisMessageBus()
        
        logger.info("Orkestron API started")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Orkestron API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "redis_connected": shared_state.health_check() if shared_state else False
    }


# Task Management Endpoints
@app.post("/tasks")
async def create_task(task: TaskInput):
    """Create a new task"""
    task_data = task.dict()
    shared_state.add_task(task_data)
    
    # Publish to message bus
    message_bus.publish("tasks:new", task_data)
    
    return {"status": "created", "task_id": task.task_id}


@app.get("/tasks/pending")
async def get_pending_tasks():
    """Get all pending tasks"""
    tasks = shared_state.get_pending_tasks()
    return {"tasks": tasks, "count": len(tasks)}


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    task = shared_state.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}


@app.post("/tasks/submit")
async def submit_requirements(input: RequirementsInput):
    """Submit project requirements for processing"""
    # Use planner to break down requirements into tasks
    from agents.planner.planner import PlannerAgent
    
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    planner = PlannerAgent(api_key=api_key)
    
    tasks = planner.map_tasks(input.requirements)
    
    # Add all tasks to shared state
    for task in tasks:
        shared_state.add_task(task)
    
    return {
        "status": "processed",
        "tasks_created": len(tasks),
        "tasks": tasks
    }


# Agent Status Endpoints
@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return shared_state.get_all_agents_status()


@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    return shared_state.get_agent_status(agent_name)


# Cycle Management Endpoints
@app.get("/cycle/status")
async def get_cycle_status():
    """Get current cycle status"""
    return shared_state.get_cycle_status()


@app.get("/metrics")
async def get_metrics():
    """Get all metrics"""
    return shared_state.get_all_metrics()


# Logs Endpoints
@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent logs"""
    return shared_state.get_logs(limit=limit)


# Deployment Endpoints
@app.get("/deployment/status")
async def get_deployment_status():
    """Get deployment status"""
    return shared_state.get_deployment_status()


@app.post("/deployment/update")
async def update_deployment(status: str, details: Optional[Dict] = None):
    """Update deployment status"""
    shared_state.update_deployment_status(status, details)
    return {"status": "updated"}


# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Broadcast to all clients
            for client in connected_clients:
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info("Client disconnected")


async def broadcast_message(message: Dict):
    """Broadcast message to all connected WebSocket clients"""
    message_str = json.dumps(message)
    disconnected = []
    
    for client in connected_clients:
        try:
            await client.send_text(message_str)
        except:
            disconnected.append(client)
    
    # Remove disconnected clients
    for client in disconnected:
        if client in connected_clients:
            connected_clients.remove(client)


# Orchestration Endpoints
@app.post("/orchestrate")
async def orchestrate_tasks():
    """Trigger orchestration of pending tasks"""
    pending_tasks = shared_state.get_pending_tasks()
    
    if not pending_tasks:
        return {"status": "no_tasks", "message": "No pending tasks to orchestrate"}
    
    assignments = orchestrator.assign_tasks(pending_tasks)
    
    return {
        "status": "orchestrated",
        "assignments": assignments
    }


@app.post("/cycle/start")
async def start_cycle():
    """Start a new execution cycle"""
    from cycle_manager.cycle_executor import CycleExecutor
    from agents.planner.planner import PlannerAgent
    from agents.builder.builder import BuilderAgent
    from agents.tester.tester import TesterAgent
    from agents.guard.guard import GuardAgent
    from agents.designer.designer import DesignerAgent
    
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    
    agents = {
        'planner': PlannerAgent(api_key=api_key),
        'builder': BuilderAgent(api_key=api_key),
        'tester': TesterAgent(api_key=api_key),
        'guard': GuardAgent(api_key=api_key),
        'designer': DesignerAgent(api_key=api_key)
    }
    
    executor = CycleExecutor(orchestrator, agents, message_bus, shared_state)
    
    # Start cycle in background
    import threading
    cycle_thread = threading.Thread(target=executor.execute_cycle, daemon=True)
    cycle_thread.start()
    
    return {"status": "cycle_started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

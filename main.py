"""  
Orkestron - Main Entry Point
Multi-agent orchestration system for autonomous full-stack development
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/swarmai.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for SwarmAI Builder"""
    logger.info("=" * 60)
    logger.info("Orkestron - Multi-Agent Orchestration System")
    logger.info("=" * 60)
    
    # Initialize components
    from orchestrator.central_ai import CentralOrchestrator
    from agents.planner.planner import PlannerAgent
    from agents.builder.builder import BuilderAgent
    from agents.tester.tester import TesterAgent
    from agents.guard.guard import GuardAgent
    from agents.designer.designer import DesignerAgent
    from shared_memory.state import SharedState
    from message_bus.redis_bus import RedisMessageBus
    from cycle_manager.cycle_executor import CycleExecutor
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Using demo mode.")
        api_key = "demo-key"
    
    # Initialize orchestrator
    logger.info("Initializing Central Orchestrator...")
    orchestrator = CentralOrchestrator(api_key=api_key)
    
    # Initialize agents
    logger.info("Initializing Agents...")
    agents = {
        'planner': PlannerAgent(api_key=api_key),
        'builder': BuilderAgent(api_key=api_key),
        'tester': TesterAgent(api_key=api_key),
        'guard': GuardAgent(api_key=api_key),
        'designer': DesignerAgent(api_key=api_key)
    }
    
    # Initialize shared state and message bus
    logger.info("Initializing Shared State and Message Bus...")
    shared_state = SharedState()
    message_bus = RedisMessageBus()
    
    # Initialize cycle executor
    logger.info("Initializing Cycle Executor...")
    executor = CycleExecutor(
        orchestrator=orchestrator,
        agents=agents,
        message_bus=message_bus,
        shared_state=shared_state
    )
    
    logger.info("All components initialized successfully!")
    logger.info("Starting autonomous execution cycle...")
    
    # Start execution cycle
    try:
        executor.execute_cycle()
    except KeyboardInterrupt:
        logger.info("Shutting down SwarmAI Builder...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


class CycleExecutor:
    """Manages the 30-minute autonomous execution cycle"""
    
    INTERVAL_MINUTES = 30
    
    def __init__(self, orchestrator, agents: Dict, message_bus, shared_state):
        self.orchestrator = orchestrator
        self.agents = agents
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.current_cycle = 0
        self.cycle_start_time = None
    
    def execute_cycle(self):
        """Full cycle: trigger → check → brain → build → guard → sleep"""
        while True:
            try:
                self.current_cycle += 1
                self.cycle_start_time = datetime.now()
                logger.info(f"=== Starting Cycle {self.current_cycle} ===")
                
                # Phase 1: Trigger
                self._phase_trigger()
                
                # Phase 2: Check
                pending_tasks = self._phase_check()
                
                if not pending_tasks:
                    logger.info("No pending tasks, skipping to sleep")
                    self._phase_sleep({"status": "no_tasks"})
                    continue
                
                # Phase 3: Brain
                assignments = self._phase_brain(pending_tasks)
                
                # Phase 4: Build (70 min total)
                build_results = self._phase_build(assignments)
                
                # Phase 5: Guard
                guard_results = self._phase_guard(build_results)
                
                # Phase 6: Sleep
                self._phase_sleep({
                    "cycle": self.current_cycle,
                    "build_results": build_results,
                    "guard_results": guard_results
                })
                
                # Wait for next cycle
                sleep_seconds = self.INTERVAL_MINUTES * 60
                logger.info(f"Cycle {self.current_cycle} complete. Sleeping for {self.INTERVAL_MINUTES} minutes.")
                time.sleep(sleep_seconds)
                
            except Exception as e:
                logger.error(f"Cycle {self.current_cycle} failed: {e}")
                self._handle_cycle_failure(e)
                time.sleep(60)  # Wait 1 minute before retry
    
    def _phase_trigger(self):
        """Wake, cron ping, init cycle"""
        logger.info("[Phase 1] Trigger - Initializing cycle")
        self.shared_state.update_cycle_status("trigger")
        self.shared_state.set_metric(f"cycle.{self.current_cycle}.start_time", datetime.now().isoformat())
    
    def _phase_check(self) -> List[Dict]:
        """Scan pending tasks, validate inputs, assign ready tasks"""
        logger.info("[Phase 2] Check - Scanning for pending tasks")
        self.shared_state.update_cycle_status("check")
        
        pending_tasks = self.shared_state.get_pending_tasks()
        logger.info(f"Found {len(pending_tasks)} pending tasks")
        
        # Validate inputs
        ready_tasks = [
            task for task in pending_tasks
            if self._validate_task_input(task)
        ]
        
        logger.info(f"{len(ready_tasks)} tasks ready for execution")
        return ready_tasks
    
    def _phase_brain(self, tasks: List[Dict]) -> Dict:
        """Planner maps tasks, orchestrator selects next move, assign agents"""
        logger.info("[Phase 3] Brain - Planning and assigning tasks")
        self.shared_state.update_cycle_status("brain")
        
        # Use orchestrator to assign tasks
        assignments = self.orchestrator.assign_tasks(tasks)
        
        # Store assignments
        self.shared_state.set_metric(
            f"cycle.{self.current_cycle}.assignments",
            json.dumps(assignments)
        )
        
        logger.info(f"Assigned {len(assignments.get('assignments', []))} tasks to agents")
        return assignments
    
    def _phase_build(self, assignments: Dict) -> Dict:
        """Execute build phase: database, backend, pages, tests, deploy"""
        logger.info("[Phase 4] Build - Executing tasks")
        self.shared_state.update_cycle_status("build")
        
        results = {
            "completed": [],
            "failed": [],
            "in_progress": []
        }
        
        for assignment in assignments.get('assignments', []):
            task_id = assignment.get('task_id')
            agent_name = assignment.get('agent')
            
            try:
                # Update agent status
                self.message_bus.set_agent_status(agent_name, "working")
                
                # Execute task with appropriate agent
                result = self._execute_task_with_agent(task_id, agent_name)
                
                if result.get('success'):
                    results['completed'].append({
                        'task_id': task_id,
                        'agent': agent_name,
                        'result': result
                    })
                else:
                    results['failed'].append({
                        'task_id': task_id,
                        'agent': agent_name,
                        'error': result.get('error')
                    })
                
                # Update agent status
                self.message_bus.set_agent_status(agent_name, "idle")
                
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                results['failed'].append({
                    'task_id': task_id,
                    'agent': agent_name,
                    'error': str(e)
                })
        
        logger.info(f"Build complete: {len(results['completed'])} succeeded, {len(results['failed'])} failed")
        return results
    
    def _phase_guard(self, build_results: Dict) -> Dict:
        """Run quality checks: lint, type check, clean build, no secrets, test suite"""
        logger.info("[Phase 5] Guard - Running quality checks")
        self.shared_state.update_cycle_status("guard")
        
        guard_agent = self.agents.get('guard')
        if not guard_agent:
            return {"passed": False, "error": "Guard agent not available"}
        
        # Run guard checks on completed builds
        all_files = []
        for completed in build_results.get('completed', []):
            if 'files' in completed.get('result', {}):
                all_files.extend(completed['result']['files'])
        
        guard_results = guard_agent.run_full_guard_suite(all_files)
        
        logger.info(f"Guard checks: {guard_results['passed_files']}/{guard_results['total_files']} passed")
        return guard_results
    
    def _phase_sleep(self, cycle_summary: Dict):
        """Log results, store metrics, rest until next cycle"""
        logger.info("[Phase 6] Sleep - Logging and storing results")
        self.shared_state.update_cycle_status("sleep")
        
        # Store cycle metrics
        self.shared_state.set_metric(
            f"cycle.{self.current_cycle}.summary",
            json.dumps(cycle_summary)
        )
        
        # Log cycle duration
        if self.cycle_start_time:
            duration = (datetime.now() - self.cycle_start_time).total_seconds()
            logger.info(f"Cycle {self.current_cycle} duration: {duration:.2f} seconds")
    
    def _execute_task_with_agent(self, task_id: str, agent_name: str) -> Dict:
        """Execute a task with the appropriate agent"""
        task = self.shared_state.get_task(task_id)
        if not task:
            return {"success": False, "error": f"Task {task_id} not found"}
        
        if agent_name == 'planner':
            agent = self.agents.get('planner')
            if agent:
                tasks = agent.map_tasks(task.get('description', ''))
                return {"success": True, "tasks": tasks}
        
        elif agent_name == 'builder':
            agent = self.agents.get('builder')
            if agent:
                result = agent.generate_code(task)
                return {"success": True, "files": result.get('files', [])}
        
        elif agent_name == 'designer':
            agent = self.agents.get('designer')
            if agent:
                result = agent.build_ui(task)
                return {"success": True, "components": result.get('components', [])}
        
        elif agent_name == 'tester':
            agent = self.agents.get('tester')
            if agent:
                # Validation would happen here
                return {"success": True}
        
        return {"success": False, "error": f"Agent {agent_name} not available"}
    
    def _validate_task_input(self, task: Dict) -> bool:
        """Validate that a task has all required inputs"""
        required_fields = ['task_id', 'title', 'description']
        return all(field in task for field in required_fields)
    
    def _handle_cycle_failure(self, error: Exception):
        """Handle cycle failure and log error"""
        logger.error(f"Cycle {self.current_cycle} failed with error: {error}")
        self.shared_state.set_metric(
            f"cycle.{self.current_cycle}.error",
            str(error)
        )
        
        # Notify via message bus
        self.message_bus.publish("system:errors", {
            "type": "cycle_failure",
            "cycle": self.current_cycle,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

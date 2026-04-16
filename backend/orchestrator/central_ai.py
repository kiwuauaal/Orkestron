from openai import OpenAI
import requests
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CentralOrchestrator:
    """Central AI orchestrator for task assignment and coordination"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.public_apis = self.load_public_apis()
        self.model = "gpt-3.5-turbo"
    
    def load_public_apis(self) -> List[Dict]:
        """Fetch available public APIs from public-apis repository"""
        try:
            response = requests.get('https://api.publicapis.org/entries')
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Loaded {len(data.get('entries', []))} public APIs")
                return data.get('entries', [])
        except Exception as e:
            logger.error(f"Failed to load public APIs: {e}")
        return []
    
    def assign_tasks(self, pending_tasks: List[Dict]) -> Dict:
        """Use LLM to analyze and assign tasks to agents"""
        prompt = f"""
        You are the central orchestrator for a multi-agent swarm system.
        
        Analyze these pending tasks and assign them to the most appropriate agents:
        {json.dumps(pending_tasks, indent=2)}
        
        Available agents:
        - planner: Task mapping and decomposition
        - builder: Code generation (backend/frontend)
        - tester: Quality assurance and testing
        - guard: Quality gatekeeper and security
        - designer: UI/UX construction
        
        Return a JSON object with the following structure:
        {{
            "assignments": [
                {{
                    "task_id": "...",
                    "agent": "planner|builder|tester|guard|designer",
                    "priority": "high|medium|low",
                    "reasoning": "..."
                }}
            ]
        }}
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert task orchestrator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Task assignment failed: {e}")
            return {"assignments": []}
    
    def get_next_action(self, cycle_state: Dict) -> Dict:
        """Determine the next action based on current cycle state"""
        prompt = f"""
        Current cycle state:
        {json.dumps(cycle_state, indent=2)}
        
        What should be the next action? Consider:
        - Pending tasks
        - Agent availability
        - Current phase (trigger/check/brain/build/guard/sleep)
        - Previous failures
        
        Return JSON with:
        {{
            "action": "...",
            "target_agent": "...",
            "parameters": {{}}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to get next action: {e}")
            return {"action": "wait", "target_agent": None, "parameters": {}}
    
    def evaluate_task_result(self, task: Dict, result: Dict) -> Dict:
        """Evaluate if a task result meets quality standards"""
        prompt = f"""
        Task: {json.dumps(task, indent=2)}
        Result: {json.dumps(result, indent=2)}
        
        Evaluate if this result is acceptable:
        - Does it meet the requirements?
        - Are there any issues?
        - Should it pass or fail the quality gate?
        
        Return JSON:
        {{
            "passed": true/false,
            "score": 0-100,
            "feedback": "..."
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Task evaluation failed: {e}")
            return {"passed": False, "score": 0, "feedback": str(e)}

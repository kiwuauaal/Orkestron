from openai import OpenAI
import json
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for task mapping and decomposition"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def map_tasks(self, requirements: str) -> List[Dict]:
        """Analyze requirements and break into executable tasks"""
        prompt = f"""
        You are a task planning expert. Analyze the following requirements and break them down into specific, executable tasks.
        
        Requirements:
        {requirements}
        
        Return a JSON array of tasks with this structure:
        [
            {{
                "task_id": "unique_id",
                "title": "Task title",
                "description": "Detailed description",
                "type": "database|backend|frontend|testing|deployment",
                "estimated_duration_minutes": 30,
                "dependencies": ["task_id_1", "task_id_2"],
                "priority": "high|medium|low",
                "acceptance_criteria": ["criterion 1", "criterion 2"]
            }}
        ]
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert task planner."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            tasks = json.loads(response.choices[0].message.content)
            logger.info(f"Planner created {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            return []
    
    def refine_task(self, task: Dict, feedback: str) -> Dict:
        """Refine a task based on feedback"""
        prompt = f"""
        Original task:
        {json.dumps(task, indent=2)}
        
        Feedback:
        {feedback}
        
        Improve the task definition based on the feedback. Return the updated task as JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Task refinement failed: {e}")
            return task
    
    def validate_task_dependencies(self, tasks: List[Dict]) -> Dict:
        """Validate that task dependencies are correct"""
        task_ids = {task['task_id'] for task in tasks}
        invalid_deps = []
        
        for task in tasks:
            for dep in task.get('dependencies', []):
                if dep not in task_ids:
                    invalid_deps.append({
                        'task_id': task['task_id'],
                        'invalid_dependency': dep
                    })
        
        return {
            'valid': len(invalid_deps) == 0,
            'invalid_dependencies': invalid_deps
        }

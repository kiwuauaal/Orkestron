from openai import OpenAI
import json
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class BuilderAgent:
    """Agent responsible for code generation (backend/frontend)"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.output_dir = "generated_code"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_code(self, task: Dict) -> Dict:
        """Generate backend/frontend code based on task"""
        task_type = task.get('type', 'backend')
        
        if task_type in ['backend', 'database']:
            return self._generate_backend_code(task)
        elif task_type == 'frontend':
            return self._generate_frontend_code(task)
        else:
            return self._generate_generic_code(task)
    
    def _generate_backend_code(self, task: Dict) -> Dict:
        """Generate backend code"""
        prompt = f"""
        You are an expert backend developer. Generate production-ready code for the following task:
        
        Task Title: {task.get('title', '')}
        Description: {task.get('description', '')}
        Acceptance Criteria: {task.get('acceptance_criteria', [])}
        
        Requirements:
        - Use Python FastAPI framework
        - Include proper error handling
        - Add comprehensive comments
        - Follow best practices
        - Include type hints
        
        Return JSON with:
        {{
            "files": [
                {{
                    "filename": "path/to/file.py",
                    "content": "complete file content",
                    "language": "python"
                }}
            ],
            "dependencies": ["package1", "package2"],
            "setup_instructions": "How to set up and run this code"
        }}
        
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, task)
    
    def _generate_frontend_code(self, task: Dict) -> Dict:
        """Generate frontend code"""
        prompt = f"""
        You are an expert frontend developer. Generate production-ready code for the following task:
        
        Task Title: {task.get('title', '')}
        Description: {task.get('description', '')}
        Acceptance Criteria: {task.get('acceptance_criteria', [])}
        
        Requirements:
        - Use React with TypeScript
        - Include proper component structure
        - Add responsive design
        - Follow modern React patterns (hooks)
        - Include error boundaries
        
        Return JSON with:
        {{
            "files": [
                {{
                    "filename": "path/to/component.tsx",
                    "content": "complete file content",
                    "language": "typescript"
                }}
            ],
            "dependencies": ["react", "react-dom"],
            "setup_instructions": "How to set up and run this code"
        }}
        
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, task)
    
    def _generate_generic_code(self, task: Dict) -> Dict:
        """Generate generic code"""
        prompt = f"""
        You are an expert software developer. Generate production-ready code for:
        
        Task: {json.dumps(task, indent=2)}
        
        Return JSON with:
        {{
            "files": [
                {{
                    "filename": "path/to/file",
                    "content": "complete file content",
                    "language": "language"
                }}
            ],
            "dependencies": [],
            "setup_instructions": "..."
        }}
        
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, task)
    
    def _generate_with_llm(self, prompt: str, task: Dict) -> Dict:
        """Generate code using LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Save generated files
            self._save_generated_files(result.get('files', []))
            
            logger.info(f"Builder generated code for task: {task.get('task_id')}")
            return result
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return {
                "files": [],
                "dependencies": [],
                "setup_instructions": "",
                "error": str(e)
            }
    
    def _save_generated_files(self, files: List[Dict]):
        """Save generated files to disk"""
        for file_info in files:
            filepath = os.path.join(self.output_dir, file_info['filename'])
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            logger.info(f"Saved file: {filepath}")

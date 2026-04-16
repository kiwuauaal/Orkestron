from openai import OpenAI
import json
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class DesignerAgent:
    """Agent responsible for UI/UX construction"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.output_dir = "generated_ui"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def build_ui(self, requirements: Dict) -> Dict:
        """Construct user interface components"""
        ui_type = requirements.get('type', 'dashboard')
        
        if ui_type == 'dashboard':
            return self._generate_dashboard(requirements)
        elif ui_type == 'form':
            return self._generate_form(requirements)
        elif ui_type == 'landing_page':
            return self._generate_landing_page(requirements)
        else:
            return self._generate_generic_ui(requirements)
    
    def _generate_dashboard(self, requirements: Dict) -> Dict:
        """Generate dashboard UI"""
        prompt = f"""
        You are an expert UI/UX designer and frontend developer. Create a modern, responsive dashboard component.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Specifications:
        - Use React with TypeScript
        - Use Tailwind CSS for styling
        - Include responsive design
        - Add proper loading states
        - Include error boundaries
        - Use modern React patterns (hooks, context)
        
        Return JSON with:
        {{
            "components": [
                {{
                    "name": "ComponentName",
                    "filename": "path/to/component.tsx",
                    "content": "complete component code",
                    "description": "What this component does"
                }}
            ],
            "styles": "any custom CSS if needed",
            "dependencies": ["react", "tailwindcss"],
            "preview_description": "Description of the UI"
        }}
        
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, requirements)
    
    def _generate_form(self, requirements: Dict) -> Dict:
        """Generate form UI"""
        prompt = f"""
        Create a modern, accessible form component.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Specifications:
        - Use React Hook Form
        - Include form validation
        - Add proper error messages
        - Ensure accessibility (ARIA labels)
        - Responsive design
        
        Return JSON with components array and dependencies.
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, requirements)
    
    def _generate_landing_page(self, requirements: Dict) -> Dict:
        """Generate landing page UI"""
        prompt = f"""
        Create a stunning, modern landing page.
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Specifications:
        - Hero section with compelling CTA
        - Features section
        - Testimonials (if applicable)
        - Footer with links
        - Smooth animations
        - Mobile-first responsive design
        
        Return JSON with components array and dependencies.
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, requirements)
    
    def _generate_generic_ui(self, requirements: Dict) -> Dict:
        """Generate generic UI component"""
        prompt = f"""
        Create a modern UI component based on these requirements:
        
        {json.dumps(requirements, indent=2)}
        
        Use React, TypeScript, and Tailwind CSS.
        Return JSON with components array.
        Only return valid JSON.
        """
        
        return self._generate_with_llm(prompt, requirements)
    
    def _generate_with_llm(self, prompt: str, requirements: Dict) -> Dict:
        """Generate UI using LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert UI/UX designer and React developer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Save generated components
            self._save_components(result.get('components', []))
            
            logger.info(f"Designer generated UI for: {requirements.get('title', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"UI generation failed: {e}")
            return {
                "components": [],
                "styles": "",
                "dependencies": [],
                "error": str(e)
            }
    
    def _save_components(self, components: List[Dict]):
        """Save generated UI components to disk"""
        for component in components:
            filepath = os.path.join(self.output_dir, component.get('filename', 'component.tsx'))
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(component['content'])
            
            logger.info(f"Saved UI component: {filepath}")
    
    def suggest_improvements(self, current_ui: str, feedback: str) -> Dict:
        """Suggest UI/UX improvements"""
        prompt = f"""
        Current UI Code:
        {current_ui}
        
        User Feedback:
        {feedback}
        
        Suggest specific improvements:
        1. Visual design enhancements
        2. UX improvements
        3. Accessibility fixes
        4. Performance optimizations
        
        Return JSON with improved code and explanations.
        Only return valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"UI improvement suggestion failed: {e}")
            return {"improvements": [], "error": str(e)}

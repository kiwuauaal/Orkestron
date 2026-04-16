from openai import OpenAI
import json
from typing import Dict, List
import logging
import subprocess
import os

logger = logging.getLogger(__name__)


class TesterAgent:
    """Agent responsible for quality assurance and testing"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def validate_code(self, code: str, task: Dict) -> Dict:
        """Identify bugs and validate functionality"""
        prompt = f"""
        You are an expert code reviewer and tester. Review the following code for:
        
        Task Requirements:
        {json.dumps(task, indent=2)}
        
        Code:
        {code}
        
        Analyze for:
        1. Syntax errors
        2. Logic bugs
        3. Edge cases not handled
        4. Performance issues
        5. Security vulnerabilities
        6. Best practices violations
        
        Return JSON with:
        {{
            "passed": true/false,
            "bugs_found": [
                {{
                    "severity": "critical|high|medium|low",
                    "line": line_number,
                    "description": "bug description",
                    "suggestion": "how to fix"
                }}
            ],
            "test_cases": [
                {{
                    "name": "test name",
                    "input": "test input",
                    "expected_output": "expected result"
                }}
            ],
            "coverage_estimate": 0-100,
            "overall_score": 0-100
        }}
        
        Only return valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code tester."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Tester validated code: {result.get('overall_score')} score")
            return result
        except Exception as e:
            logger.error(f"Code validation failed: {e}")
            return {
                "passed": False,
                "bugs_found": [],
                "test_cases": [],
                "coverage_estimate": 0,
                "overall_score": 0,
                "error": str(e)
            }
    
    def run_unit_tests(self, test_files: List[str]) -> Dict:
        """Run actual unit tests"""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                results["errors"].append(f"Test file not found: {test_file}")
                continue
            
            try:
                # Run pytest
                result = subprocess.run(
                    ["pytest", test_file, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                results["total"] += 1
                if result.returncode == 0:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "file": test_file,
                        "output": result.stdout,
                        "errors": result.stderr
                    })
            except Exception as e:
                results["errors"].append(f"Failed to run {test_file}: {str(e)}")
        
        return results
    
    def generate_test_suite(self, code: str, language: str = "python") -> str:
        """Generate test suite for the code"""
        prompt = f"""
        Generate a comprehensive test suite for the following {language} code:
        
        {code}
        
        Requirements:
        - Use pytest framework
        - Include unit tests for all functions/methods
        - Test edge cases
        - Test error handling
        - Include mock objects where necessary
        - Aim for 90%+ code coverage
        
        Return only the test code, no explanations.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {language} test writer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            test_code = response.choices[0].message.content
            logger.info("Generated test suite")
            return test_code
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return ""

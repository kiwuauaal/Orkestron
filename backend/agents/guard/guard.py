from openai import OpenAI
import json
from typing import Dict, List
import logging
import re
import os

logger = logging.getLogger(__name__)


class GuardAgent:
    """Agent responsible for quality gatekeeping and security"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    def quality_check(self, code: str, language: str = "python") -> Dict:
        """Verify standards, security, and compliance"""
        checks = {
            "lint_check": self.lint_check(code, language),
            "type_check": self.type_check(code, language),
            "security_scan": self.security_scan(code),
            "no_secrets_exposed": self.check_for_secrets(code),
            "code_quality": self.assess_code_quality(code, language)
        }
        
        all_passed = all(check['passed'] for check in checks.values())
        
        return {
            "passed": all_passed,
            "checks": checks,
            "overall_score": sum(check.get('score', 0) for check in checks.values()) / len(checks)
        }
    
    def lint_check(self, code: str, language: str) -> Dict:
        """Run linting checks"""
        issues = []
        
        if language == "python":
            # Check for common Python issues
            if len(code.split('\n')) > 200:
                issues.append("File too long (>200 lines)")
            
            # Check for proper imports
            if 'import *' in code:
                issues.append("Wildcard import detected")
            
            # Check line length
            for i, line in enumerate(code.split('\n'), 1):
                if len(line) > 120:
                    issues.append(f"Line {i} too long ({len(line)} chars)")
                    break
        
        elif language in ["typescript", "javascript"]:
            # Check for common JS/TS issues
            if 'var ' in code:
                issues.append("Use 'let' or 'const' instead of 'var'")
            
            if '==' in code and '===' not in code:
                issues.append("Consider using strict equality (===)")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 if len(issues) == 0 else max(0, 100 - len(issues) * 20)
        }
    
    def type_check(self, code: str, language: str) -> Dict:
        """Check type safety"""
        issues = []
        
        if language == "python":
            # Check for type hints
            if 'def ' in code and '->' not in code and ': str' not in code and ': int' not in code:
                issues.append("Missing type hints")
        
        elif language == "typescript":
            # Check for 'any' type usage
            any_count = code.count(': any')
            if any_count > 0:
                issues.append(f"Found {any_count} uses of 'any' type")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 if len(issues) == 0 else max(0, 100 - len(issues) * 25)
        }
    
    def security_scan(self, code: str) -> Dict:
        """Scan for security vulnerabilities"""
        vulnerabilities = []
        
        # Check for SQL injection risks
        if re.search(r'(execute|query)\s*\(.*%.*\)', code, re.IGNORECASE):
            vulnerabilities.append("Potential SQL injection risk")
        
        # Check for eval usage
        if 'eval(' in code:
            vulnerabilities.append("Use of eval() is dangerous")
        
        # Check for hardcoded credentials patterns
        if re.search(r'(password|secret|key)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
            vulnerabilities.append("Possible hardcoded credentials")
        
        # Check for unsafe deserialization
        if 'pickle.loads' in code or 'yaml.load(' in code:
            vulnerabilities.append("Unsafe deserialization detected")
        
        return {
            "passed": len(vulnerabilities) == 0,
            "vulnerabilities": vulnerabilities,
            "score": 100 if len(vulnerabilities) == 0 else 0
        }
    
    def check_for_secrets(self, code: str) -> Dict:
        """Check for exposed secrets"""
        secret_patterns = [
            r'AKIA[0-9A-Z]{16}',  # AWS Access Key
            r'(?:password|passwd|pwd)\s*[:=]\s*\S+',
            r'api[_-]?key\s*[:=]\s*\S+',
            r'token\s*[:=]\s*[\'"][^\'"]{20,}[\'"]',
            r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'
        ]
        
        found_secrets = []
        for pattern in secret_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            found_secrets.extend(matches)
        
        return {
            "passed": len(found_secrets) == 0,
            "secrets_found": len(found_secrets),
            "score": 0 if found_secrets else 100
        }
    
    def assess_code_quality(self, code: str, language: str) -> Dict:
        """Assess overall code quality using LLM"""
        prompt = f"""
        Review the following {language} code for overall quality:
        
        {code}
        
        Assess:
        1. Code organization and structure
        2. Naming conventions
        3. DRY principle adherence
        4. Error handling
        5. Comments and documentation
        6. Maintainability
        
        Return JSON:
        {{
            "score": 0-100,
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "recommendations": ["recommendation 1", "recommendation 2"]
        }}
        
        Only return valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code quality assessor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Code quality assessment failed: {e}")
            return {
                "score": 50,
                "strengths": [],
                "weaknesses": ["Assessment failed"],
                "recommendations": ["Manual review recommended"]
            }
    
    def run_full_guard_suite(self, files: List[Dict]) -> Dict:
        """Run complete guard checks on all files"""
        results = {
            "total_files": len(files),
            "passed_files": 0,
            "failed_files": 0,
            "file_results": []
        }
        
        for file_info in files:
            file_result = self.quality_check(
                file_info.get('content', ''),
                file_info.get('language', 'python')
            )
            
            results["file_results"].append({
                "filename": file_info.get('filename'),
                "result": file_result
            })
            
            if file_result["passed"]:
                results["passed_files"] += 1
            else:
                results["failed_files"] += 1
        
        results["all_passed"] = results["failed_files"] == 0
        return results

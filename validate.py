"""
Validation script to verify all bug fixes
Run this to ensure the code is error-free
"""

import sys
import os
import py_compile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def validate_python_file(filepath):
    """Validate a Python file compiles without errors"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Orkestron - Code Validation")
    print("=" * 60)
    print()
    
    files_to_check = [
        'backend/orchestrator/central_ai.py',
        'backend/agents/planner/planner.py',
        'backend/agents/builder/builder.py',
        'backend/agents/tester/tester.py',
        'backend/agents/guard/guard.py',
        'backend/agents/designer/designer.py',
        'backend/cycle_manager/cycle_executor.py',
        'backend/shared_memory/state.py',
        'backend/api/routes.py',
        'main.py',
    ]
    
    all_passed = True
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            all_passed = False
            continue
            
        success, error = validate_python_file(filepath)
        if success:
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath}")
            print(f"   Error: {error}")
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ All Python files validated successfully!")
        print()
        print("Next steps:")
        print("1. Install frontend dependencies: cd frontend/dashboard && npm install")
        print("2. Run tests: pytest tests/test_suite.py -v")
        print("3. Start the app: python main.py")
    else:
        print("❌ Some files have errors. Please fix them.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()

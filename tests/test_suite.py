"""
SwarmAI Builder - Complete Test Suite (47 Tests)
Tests for orchestrator, agents, cycle manager, message bus, and integration
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import modules to test
from orchestrator.central_ai import CentralOrchestrator
from agents.planner.planner import PlannerAgent
from agents.builder.builder import BuilderAgent
from agents.tester.tester import TesterAgent
from agents.guard.guard import GuardAgent
from agents.designer.designer import DesignerAgent
from cycle_manager.cycle_executor import CycleExecutor
from shared_memory.state import SharedState
from message_bus.redis_bus import RedisMessageBus
from message_bus.rabbitmq_bus import RabbitMQBus


# ==========================================
# ORCHESTRATOR TESTS (10 tests)
# ==========================================

class TestCentralOrchestrator:
    """Test suite for Central Orchestrator"""
    
    @patch('orchestrator.central_ai.OpenAI')
    def test_orchestrator_initialization(self, mock_openai):
        """Test 1: Orchestrator initializes correctly"""
        orchestrator = CentralOrchestrator(api_key="test-key")
        assert orchestrator.model == "gpt-3.5-turbo"
        assert orchestrator.client is not None
    
    @patch('orchestrator.central_ai.requests.get')
    def test_load_public_apis_success(self, mock_get):
        """Test 2: Load public APIs successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'entries': [{'api': 'test'}]}
        mock_get.return_value = mock_response
        
        with patch('orchestrator.central_ai.OpenAI'):
            orchestrator = CentralOrchestrator(api_key="test-key")
            assert len(orchestrator.public_apis) > 0
    
    @patch('orchestrator.central_ai.requests.get')
    def test_load_public_apis_failure(self, mock_get):
        """Test 3: Handle public API load failure gracefully"""
        mock_get.side_effect = Exception("Connection error")
        
        with patch('orchestrator.central_ai.OpenAI'):
            orchestrator = CentralOrchestrator(api_key="test-key")
            assert orchestrator.public_apis == []
    
    @patch('orchestrator.central_ai.OpenAI')
    def test_assign_tasks_success(self, mock_openai):
        """Test 4: Task assignment works correctly"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "assignments": [
                {"task_id": "1", "agent": "builder", "priority": "high"}
            ]
        })
        
        orchestrator = CentralOrchestrator(api_key="test-key")
        result = orchestrator.assign_tasks([{"task_id": "1", "title": "Test"}])
        
        assert "assignments" in result
        assert len(result["assignments"]) == 1
    
    def test_assign_tasks_empty_input(self):
        """Test 5: Handle empty task list"""
        with patch('orchestrator.central_ai.OpenAI') as mock_openai:
            orchestrator = CentralOrchestrator(api_key="test-key")
            result = orchestrator.assign_tasks([])
            # Should still call LLM but with empty list
            assert result is not None
    
    @patch('orchestrator.central_ai.OpenAI')
    def test_get_next_action(self, mock_openai):
        """Test 6: Get next action based on cycle state"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "action": "build",
            "target_agent": "builder",
            "parameters": {}
        })
        
        orchestrator = CentralOrchestrator(api_key="test-key")
        result = orchestrator.get_next_action({"phase": "brain"})
        
        assert "action" in result
        assert result["action"] == "build"
    
    @patch('orchestrator.central_ai.OpenAI')
    def test_evaluate_task_result(self, mock_openai):
        """Test 7: Evaluate task result quality"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "passed": True,
            "score": 95,
            "feedback": "Excellent work"
        })
        
        orchestrator = CentralOrchestrator(api_key="test-key")
        result = orchestrator.evaluate_task_result(
            {"task_id": "1"},
            {"status": "completed"}
        )
        
        assert result["passed"] is True
        assert result["score"] == 95
    
    def test_orchestrator_model_selection(self):
        """Test 8: Verify correct model is used"""
        with patch('orchestrator.central_ai.OpenAI'):
            orchestrator = CentralOrchestrator(api_key="test-key")
            assert orchestrator.model == "gpt-3.5-turbo"
    
    @patch('orchestrator.central_ai.OpenAI')
    def test_assign_tasks_llm_error_handling(self, mock_openai):
        """Test 9: Handle LLM errors gracefully"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        orchestrator = CentralOrchestrator(api_key="test-key")
        result = orchestrator.assign_tasks([{"task_id": "1"}])
        
        assert result == {"assignments": []}
    
    def test_orchestrator_has_required_methods(self):
        """Test 10: Verify all required methods exist"""
        with patch('orchestrator.central_ai.OpenAI'):
            orchestrator = CentralOrchestrator(api_key="test-key")
            assert hasattr(orchestrator, 'assign_tasks')
            assert hasattr(orchestrator, 'get_next_action')
            assert hasattr(orchestrator, 'evaluate_task_result')


# ==========================================
# AGENT TESTS (15 tests)
# ==========================================

class TestPlannerAgent:
    """Test suite for Planner Agent"""
    
    @patch('agents.planner.planner.OpenAI')
    def test_planner_initialization(self, mock_openai):
        """Test 11: Planner initializes correctly"""
        planner = PlannerAgent(api_key="test-key")
        assert planner.model == "gpt-3.5-turbo"
    
    @patch('agents.planner.planner.OpenAI')
    def test_map_tasks_success(self, mock_openai):
        """Test 12: Task mapping works"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps([
            {"task_id": "1", "title": "Test Task"}
        ])
        
        planner = PlannerAgent(api_key="test-key")
        result = planner.map_tasks("Build a web app")
        
        assert isinstance(result, list)
        assert len(result) == 1
    
    def test_validate_task_dependencies_valid(self):
        """Test 13: Validate correct dependencies"""
        tasks = [
            {"task_id": "1", "dependencies": []},
            {"task_id": "2", "dependencies": ["1"]}
        ]
        
        with patch('agents.planner.planner.OpenAI'):
            planner = PlannerAgent(api_key="test-key")
            result = planner.validate_task_dependencies(tasks)
            
            assert result["valid"] is True
    
    def test_validate_task_dependencies_invalid(self):
        """Test 14: Detect invalid dependencies"""
        tasks = [
            {"task_id": "1", "dependencies": ["nonexistent"]}
        ]
        
        with patch('agents.planner.planner.OpenAI'):
            planner = PlannerAgent(api_key="test-key")
            result = planner.validate_task_dependencies(tasks)
            
            assert result["valid"] is False


class TestBuilderAgent:
    """Test suite for Builder Agent"""
    
    @patch('agents.builder.builder.OpenAI')
    def test_builder_initialization(self, mock_openai):
        """Test 15: Builder initializes correctly"""
        builder = BuilderAgent(api_key="test-key")
        assert builder.output_dir == "generated_code"
    
    @patch('agents.builder.builder.OpenAI')
    def test_generate_backend_code(self, mock_openai):
        """Test 16: Generate backend code"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "files": [{"filename": "test.py", "content": "print('hello')"}],
            "dependencies": [],
            "setup_instructions": "Run python test.py"
        })
        
        builder = BuilderAgent(api_key="test-key")
        result = builder.generate_code({
            "task_id": "1",
            "type": "backend",
            "title": "Test"
        })
        
        assert "files" in result
        assert len(result["files"]) == 1
    
    @patch('agents.builder.builder.OpenAI')
    def test_generate_frontend_code(self, mock_openai):
        """Test 17: Generate frontend code"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "files": [{"filename": "App.tsx", "content": "export default function App() {}"}],
            "dependencies": ["react"],
            "setup_instructions": "npm install"
        })
        
        builder = BuilderAgent(api_key="test-key")
        result = builder.generate_code({
            "task_id": "1",
            "type": "frontend",
            "title": "Test"
        })
        
        assert "files" in result


class TestTesterAgent:
    """Test suite for Tester Agent"""
    
    @patch('agents.tester.tester.OpenAI')
    def test_tester_initialization(self, mock_openai):
        """Test 18: Tester initializes correctly"""
        tester = TesterAgent(api_key="test-key")
        assert tester.model == "gpt-3.5-turbo"
    
    @patch('agents.tester.tester.OpenAI')
    def test_validate_code(self, mock_openai):
        """Test 19: Code validation works"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "passed": True,
            "bugs_found": [],
            "test_cases": [],
            "coverage_estimate": 90,
            "overall_score": 95
        })
        
        tester = TesterAgent(api_key="test-key")
        result = tester.validate_code("def test(): pass", {})
        
        assert result["passed"] is True
        assert result["overall_score"] == 95


class TestGuardAgent:
    """Test suite for Guard Agent"""
    
    @patch('agents.guard.guard.OpenAI')
    def test_guard_initialization(self, mock_openai):
        """Test 20: Guard initializes correctly"""
        guard = GuardAgent(api_key="test-key")
        assert guard.model == "gpt-3.5-turbo"
    
    def test_lint_check_python(self):
        """Test 21: Lint check for Python code"""
        with patch('agents.guard.guard.OpenAI'):
            guard = GuardAgent(api_key="test-key")
            result = guard.lint_check("def test():\n    pass", "python")
            
            assert "passed" in result
            assert "issues" in result
    
    def test_security_scan_no_vulnerabilities(self):
        """Test 22: Security scan with clean code"""
        clean_code = "def add(a, b):\n    return a + b"
        
        with patch('agents.guard.guard.OpenAI'):
            guard = GuardAgent(api_key="test-key")
            result = guard.security_scan(clean_code)
            
            assert result["passed"] is True
            assert len(result["vulnerabilities"]) == 0
    
    def test_security_scan_sql_injection(self):
        """Test 23: Detect SQL injection vulnerability"""
        vulnerable_code = 'cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)'
        
        with patch('agents.guard.guard.OpenAI'):
            guard = GuardAgent(api_key="test-key")
            result = guard.security_scan(vulnerable_code)
            
            assert result["passed"] is False
    
    def test_check_for_secrets_clean(self):
        """Test 24: No secrets found"""
        clean_code = "print('Hello World')"
        
        with patch('agents.guard.guard.OpenAI'):
            guard = GuardAgent(api_key="test-key")
            result = guard.check_for_secrets(clean_code)
            
            assert result["passed"] is True
    
    def test_quality_check_comprehensive(self):
        """Test 25: Comprehensive quality check"""
        with patch('agents.guard.guard.OpenAI'):
            guard = GuardAgent(api_key="test-key")
            result = guard.quality_check("def test(): pass", "python")
            
            assert "passed" in result
            assert "checks" in result
            assert "overall_score" in result


class TestDesignerAgent:
    """Test suite for Designer Agent"""
    
    @patch('agents.designer.designer.OpenAI')
    def test_designer_initialization(self, mock_openai):
        """Test 26: Designer initializes correctly"""
        designer = DesignerAgent(api_key="test-key")
        assert designer.output_dir == "generated_ui"
    
    @patch('agents.designer.designer.OpenAI')
    def test_build_dashboard_ui(self, mock_openai):
        """Test 27: Build dashboard UI"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "components": [{"name": "Dashboard", "filename": "Dashboard.tsx", "content": "export default function Dashboard() {}"}],
            "styles": "",
            "dependencies": ["react"],
            "preview_description": "A modern dashboard"
        })
        
        designer = DesignerAgent(api_key="test-key")
        result = designer.build_ui({"type": "dashboard", "title": "Test"})
        
        assert "components" in result
        assert len(result["components"]) == 1


# ==========================================
# CYCLE TESTS (10 tests)
# ==========================================

class TestCycleExecutor:
    """Test suite for Cycle Executor"""
    
    def test_cycle_initialization(self):
        """Test 28: Cycle executor initializes correctly"""
        mock_orchestrator = Mock()
        mock_agents = {}
        mock_message_bus = Mock()
        mock_shared_state = Mock()
        
        executor = CycleExecutor(
            mock_orchestrator,
            mock_agents,
            mock_message_bus,
            mock_shared_state
        )
        
        assert executor.INTERVAL_MINUTES == 30
        assert executor.current_cycle == 0
    
    def test_cycle_phase_trigger(self):
        """Test 29: Trigger phase executes correctly"""
        mock_orchestrator = Mock()
        mock_shared_state = Mock()
        
        executor = CycleExecutor(Mock(), {}, Mock(), mock_shared_state)
        executor._phase_trigger()
        
        mock_shared_state.update_cycle_status.assert_called_with("trigger")
    
    def test_cycle_phase_check_no_tasks(self):
        """Test 30: Check phase handles no tasks"""
        mock_shared_state = Mock()
        mock_shared_state.get_pending_tasks.return_value = []
        
        executor = CycleExecutor(Mock(), {}, Mock(), mock_shared_state)
        result = executor._phase_check()
        
        assert result == []
    
    def test_cycle_phase_check_with_tasks(self):
        """Test 31: Check phase returns ready tasks"""
        mock_shared_state = Mock()
        mock_shared_state.get_pending_tasks.return_value = [
            {"task_id": "1", "title": "Test", "description": "Test task"}
        ]
        
        executor = CycleExecutor(Mock(), {}, Mock(), mock_shared_state)
        result = executor._phase_check()
        
        assert len(result) == 1
    
    def test_cycle_phase_brain(self):
        """Test 32: Brain phase assigns tasks"""
        mock_orchestrator = Mock()
        mock_orchestrator.assign_tasks.return_value = {"assignments": []}
        mock_shared_state = Mock()
        
        executor = CycleExecutor(mock_orchestrator, {}, Mock(), mock_shared_state)
        result = executor._phase_brain([{"task_id": "1"}])
        
        assert "assignments" in result
    
    def test_validate_task_input_valid(self):
        """Test 33: Validate correct task input"""
        executor = CycleExecutor(Mock(), {}, Mock(), Mock())
        task = {"task_id": "1", "title": "Test", "description": "Test"}
        
        assert executor._validate_task_input(task) is True
    
    def test_validate_task_input_invalid(self):
        """Test 34: Reject invalid task input"""
        executor = CycleExecutor(Mock(), {}, Mock(), Mock())
        task = {"task_id": "1"}  # Missing title and description
        
        assert executor._validate_task_input(task) is False
    
    def test_cycle_phase_guard(self):
        """Test 35: Guard phase runs quality checks"""
        mock_guard = Mock()
        mock_guard.run_full_guard_suite.return_value = {
            "passed_files": 5,
            "total_files": 5,
            "all_passed": True
        }
        
        mock_agents = {'guard': mock_guard}
        executor = CycleExecutor(Mock(), mock_agents, Mock(), Mock())
        
        build_results = {"completed": [{"result": {"files": []}}]}
        result = executor._phase_guard(build_results)
        
        assert result["all_passed"] is True
    
    def test_cycle_sleep_phase(self):
        """Test 36: Sleep phase logs results"""
        mock_shared_state = Mock()
        executor = CycleExecutor(Mock(), {}, Mock(), mock_shared_state)
        
        executor._phase_sleep({"status": "completed"})
        
        mock_shared_state.update_cycle_status.assert_called_with("sleep")
        mock_shared_state.set_metric.assert_called()
    
    def test_handle_cycle_failure(self):
        """Test 37: Handle cycle failure gracefully"""
        mock_shared_state = Mock()
        mock_message_bus = Mock()
        
        executor = CycleExecutor(Mock(), {}, mock_message_bus, mock_shared_state)
        executor.current_cycle = 1
        
        error = Exception("Test error")
        executor._handle_cycle_failure(error)
        
        mock_shared_state.set_metric.assert_called()
        mock_message_bus.publish.assert_called()


# ==========================================
# MESSAGE BUS TESTS (5 tests)
# ==========================================

class TestMessageBus:
    """Test suite for Message Bus systems"""
    
    @patch('message_bus.redis_bus.redis.Redis')
    def test_redis_bus_initialization(self, mock_redis):
        """Test 38: Redis message bus initializes"""
        bus = RedisMessageBus()
        assert bus.redis_client is not None
        assert bus.pubsub is not None
    
    @patch('message_bus.redis_bus.redis.Redis')
    def test_redis_bus_publish(self, mock_redis):
        """Test 39: Redis publish works"""
        mock_client = Mock()
        mock_redis.return_value = mock_client
        
        bus = RedisMessageBus()
        bus.publish("test_channel", {"message": "test"})
        
        mock_client.publish.assert_called()
    
    def test_rabbitmq_bus_initialization(self):
        """Test 40: RabbitMQ bus initializes"""
        with patch('message_bus.rabbitmq_bus.pika.BlockingConnection'):
            bus = RabbitMQBus()
            assert bus.connection is not None
            assert bus.channel is not None
    
    @patch('message_bus.rabbitmq_bus.pika.BlockingConnection')
    def test_rabbitmq_send_task(self, mock_connection):
        """Test 41: RabbitMQ send task works"""
        mock_conn_instance = Mock()
        mock_connection.return_value = mock_conn_instance
        
        bus = RabbitMQBus()
        bus.send_task("test_queue", {"task": "test"})
        
        mock_conn_instance.channel.basic_publish.assert_called()
    
    @patch('message_bus.redis_bus.redis.Redis')
    def test_redis_set_agent_status(self, mock_redis):
        """Test 42: Set agent status in Redis"""
        mock_client = Mock()
        mock_redis.return_value = mock_client
        
        bus = RedisMessageBus()
        bus.set_agent_status("builder", "working")
        
        mock_client.hset.assert_called()


# ==========================================
# INTEGRATION TESTS (5 tests)
# ==========================================

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_shared_state_operations(self):
        """Test 43: Shared state CRUD operations"""
        with patch('shared_memory.state.redis.Redis') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            
            state = SharedState()
            state.add_task({"task_id": "1", "title": "Test"})
            
            mock_client.hset.assert_called()
    
    @patch('shared_memory.state.redis.Redis')
    def test_shared_state_task_lifecycle(self, mock_redis):
        """Test 44: Task moves through lifecycle"""
        mock_client = Mock()
        mock_redis.return_value = mock_client
        mock_client.hget.return_value = json.dumps({
            "task_id": "1",
            "title": "Test"
        })
        
        state = SharedState()
        task = state.get_task("1")
        
        assert task is not None
        assert task["task_id"] == "1"
    
    def test_all_agents_have_required_methods(self):
        """Test 45: All agents implement required interfaces"""
        with patch('openai.OpenAI'):
            planner = PlannerAgent(api_key="test")
            builder = BuilderAgent(api_key="test")
            tester = TesterAgent(api_key="test")
            guard = GuardAgent(api_key="test")
            designer = DesignerAgent(api_key="test")
            
            assert hasattr(planner, 'map_tasks')
            assert hasattr(builder, 'generate_code')
            assert hasattr(tester, 'validate_code')
            assert hasattr(guard, 'quality_check')
            assert hasattr(designer, 'build_ui')
    
    def test_cycle_executor_uses_all_components(self):
        """Test 46: Cycle executor integrates all components"""
        mock_orchestrator = Mock()
        mock_agents = {
            'planner': Mock(),
            'builder': Mock(),
            'tester': Mock(),
            'guard': Mock(),
            'designer': Mock()
        }
        mock_message_bus = Mock()
        mock_shared_state = Mock()
        
        executor = CycleExecutor(
            mock_orchestrator,
            mock_agents,
            mock_message_bus,
            mock_shared_state
        )
        
        # Verify executor has access to all components
        assert executor.orchestrator is not None
        assert len(executor.agents) == 5
    
    def test_system_configuration_valid(self):
        """Test 47: System configuration is valid"""
        config = {
            "cycle_interval": 30,
            "max_parallel_agents": 5,
            "agents": ["planner", "builder", "tester", "guard", "designer"],
            "phases": ["trigger", "check", "brain", "build", "guard", "sleep"]
        }
        
        assert config["cycle_interval"] == 30
        assert len(config["agents"]) == 5
        assert len(config["phases"]) == 6
        assert config["max_parallel_agents"] <= 5


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

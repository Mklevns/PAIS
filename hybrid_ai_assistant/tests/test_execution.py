"""
Unit tests for execution node functionality.
"""
import pytest
from unittest.mock import Mock, patch
from hybrid_ai_assistant.nodes.execution import execution_node
from hybrid_ai_assistant.state.state import ProjectState, PlanOption


@pytest.fixture
def mock_state_with_plan():
    """Create a mock project state with a selected plan."""
    plan = PlanOption(
        tech_stack="Python Flask REST API",
        why_fits="Simple and well-documented framework",
        pros=["Easy to learn", "Flexible"],
        cons=["Less automatic features"],
        estimated_complexity="medium"
    )
    
    return ProjectState(
        objective="Build a REST API with Python",
        selected_plan=plan,
        logs=[],
        execution_steps=[],
        current_step=0,
        created_files=[],
        completed_steps=[]
    )


@pytest.fixture
def mock_state_no_plan():
    """Create a mock project state without a selected plan."""
    return ProjectState(
        objective="Build a REST API with Python",
        selected_plan=None,
        logs=[],
        execution_steps=[],
        current_step=0,
        created_files=[]
    )


class TestExecutionNode:
    """Tests for the execution node."""
    
    @patch('hybrid_ai_assistant.nodes.execution.Ollama')
    @patch('hybrid_ai_assistant.nodes.execution.write_file')
    def test_execution_node_with_plan(self, mock_write_file, mock_ollama_class, mock_state_with_plan):
        """Test execution node with a valid plan."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm.invoke.return_value = "STEP 1: Create main.py file\nSTEP 2: Create requirements.txt"
        mock_ollama_class.return_value = mock_llm
        mock_write_file.return_value = {"success": True, "path": "main.py", "size": 100}
        
        # Execute
        result = execution_node(mock_state_with_plan)
        
        # Assertions
        assert "execution_steps" in result
        assert "current_step" in result
        assert "logs" in result
        assert len(result["logs"]) > 0
    
    def test_execution_node_without_plan(self, mock_state_no_plan):
        """Test execution node without a selected plan."""
        # Execute
        result = execution_node(mock_state_no_plan)
        
        # Assertions
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "No plan selected" in result["errors"][0]
    
    @patch('hybrid_ai_assistant.nodes.execution.Ollama')
    def test_execution_node_fallback_to_cloud(self, mock_ollama_class, mock_state_with_plan):
        """Test that execution node falls back to cloud model if Ollama fails."""
        # Setup mock to fail
        mock_ollama_class.side_effect = Exception("Ollama not available")
        
        with patch('hybrid_ai_assistant.nodes.execution.ChatOpenAI') as mock_openai:
            mock_llm = Mock()
            mock_llm.invoke.return_value = "STEP 1: Create files"
            mock_openai.return_value = mock_llm
            
            # Execute
            result = execution_node(mock_state_with_plan)
            
            # Should have logs mentioning fallback
            assert any("Falling back" in log for log in result["logs"])
    
    @patch('hybrid_ai_assistant.nodes.execution.Ollama')
    def test_execution_creates_steps(self, mock_ollama_class, mock_state_with_plan):
        """Test that execution node creates execution steps."""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = "STEP 1: Create main.py\nSTEP 2: Create config.py\nSTEP 3: Run tests"
        mock_ollama_class.return_value = mock_llm
        
        # Execute
        result = execution_node(mock_state_with_plan)
        
        # Assertions
        assert len(result["execution_steps"]) > 0
        assert all(hasattr(step, "step_number") for step in result["execution_steps"])
        assert all(hasattr(step, "action") for step in result["execution_steps"])
        assert all(hasattr(step, "status") for step in result["execution_steps"])
    
    @patch('hybrid_ai_assistant.nodes.execution.Ollama')
    @patch('hybrid_ai_assistant.nodes.execution.write_file')
    def test_execution_tracks_created_files(self, mock_write_file, mock_ollama_class, mock_state_with_plan):
        """Test that execution node tracks created files."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm.invoke.return_value = "STEP 1: Create file main.py"
        mock_ollama_class.return_value = mock_llm
        mock_write_file.return_value = {"success": True, "path": "main.py", "size": 100}
        
        # Execute
        result = execution_node(mock_state_with_plan)
        
        # Verify created_files is tracked
        assert "created_files" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

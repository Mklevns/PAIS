"""
Unit tests for research node functionality.
"""
import pytest
from unittest.mock import Mock, patch
from hybrid_ai_assistant.nodes.research import research_node
from hybrid_ai_assistant.state.state import ProjectState


@pytest.fixture
def mock_state():
    """Create a mock project state for testing."""
    return ProjectState(
        objective="Build a REST API with Python",
        logs=[],
        research_memory=[],
        completed_steps=[]
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    mock = Mock()
    mock.content = "Query 1: Python REST API best practices\nQuery 2: Flask vs FastAPI comparison\nQuery 3: API authentication methods"
    return mock


@pytest.fixture
def mock_search_results():
    """Mock search results."""
    return [
        {
            "query": "Python REST API best practices",
            "title": "Building REST APIs with Python",
            "content": "Best practices for building REST APIs include proper error handling, versioning, and documentation.",
            "url": "https://example.com/rest-api"
        },
        {
            "query": "Flask vs FastAPI comparison",
            "title": "Flask vs FastAPI: A Comprehensive Comparison",
            "content": "FastAPI offers better performance and automatic documentation, while Flask is more mature and flexible.",
            "url": "https://example.com/flask-vs-fastapi"
        }
    ]


class TestResearchNode:
    """Tests for the research node."""
    
    @patch('hybrid_ai_assistant.nodes.research.ChatOpenAI')
    @patch('hybrid_ai_assistant.nodes.research.search_web')
    def test_research_node_success(self, mock_search, mock_llm_class, mock_state, mock_llm_response, mock_search_results):
        """Test successful research execution."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_llm_class.return_value = mock_llm
        mock_search.return_value = mock_search_results
        
        # Execute research node
        result = research_node(mock_state)
        
        # Assertions
        assert "research_queries" in result
        assert "research_memory" in result
        assert "research_synthesis" in result
        assert len(result["research_queries"]) > 0
        assert len(result["logs"]) > 0
        assert "research" in result["completed_steps"]
    
    @patch('hybrid_ai_assistant.nodes.research.ChatOpenAI')
    def test_research_node_error_handling(self, mock_llm_class, mock_state):
        """Test research node error handling."""
        # Setup mock to raise exception
        mock_llm_class.side_effect = Exception("API Error")
        
        # Execute research node
        result = research_node(mock_state)
        
        # Assertions
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "Research error" in result["errors"][0]
    
    def test_research_updates_state(self, mock_state):
        """Test that research node properly updates state."""
        with patch('hybrid_ai_assistant.nodes.research.ChatOpenAI') as mock_llm_class, \
             patch('hybrid_ai_assistant.nodes.research.search_web') as mock_search:
            
            # Setup mocks
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Query: test query"
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm
            mock_search.return_value = []
            
            # Execute
            result = research_node(mock_state)
            
            # Verify state updates
            assert isinstance(result["research_queries"], list)
            assert isinstance(result["research_memory"], list)
            assert isinstance(result["logs"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

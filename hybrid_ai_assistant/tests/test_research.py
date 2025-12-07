import unittest
from hybrid_ai_assistant.nodes.research import perform_research

class TestResearch(unittest.TestCase):
    def test_research_execution(self):
        state = {"query": "Test"}
        result = perform_research(state)
        self.assertIn("research_notes", result)

if __name__ == '__main__':
    unittest.main()

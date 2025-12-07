import unittest
from hybrid_ai_assistant.nodes.execution import execute_plan

class TestExecution(unittest.TestCase):
    def test_execution_node(self):
        state = {"selected_option": {}}
        result = execute_plan(state)
        self.assertIn("execution_results", result)

if __name__ == '__main__':
    unittest.main()

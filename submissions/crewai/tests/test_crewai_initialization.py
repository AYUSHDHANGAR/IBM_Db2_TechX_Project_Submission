"""
Test initialization of CrewAI agents, tasks, and DB2VectorSearchTool custom embedding function.
"""

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.match_to_proposal.crew import MatchToDb2PositionsCrew


class TestCrewInitialization(unittest.TestCase):
    """Test CrewAI agents and tasks setup."""

    def test_crew_instantiation(self):
        """Verify CrewBase, agents, and tasks load correctly."""
        crew_instance = MatchToDb2PositionsCrew()
        self.assertIsNotNone(crew_instance.agents_config)
        self.assertIsNotNone(crew_instance.tasks_config)

        # Test agent instantiation
        cv_reader = crew_instance.cv_reader()
        matcher = crew_instance.matcher()

        self.assertIsNotNone(cv_reader)
        self.assertIsNotNone(matcher)
        self.assertEqual(len(matcher.tools), 1)

        # Test task instantiation
        read_task = crew_instance.read_cv_task()
        match_task = crew_instance.match_cv_task()

        self.assertIsNotNone(read_task)
        self.assertIsNotNone(match_task)

        # Test crew assembly
        assembled_crew = crew_instance.crew()
        self.assertEqual(len(assembled_crew.agents), 2)
        self.assertEqual(len(assembled_crew.tasks), 2)
        print(" CrewAI agents, tasks, and DB2VectorSearchTool assembled successfully!")


if __name__ == "__main__":
    unittest.main()

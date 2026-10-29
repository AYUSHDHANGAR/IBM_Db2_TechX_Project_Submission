#!/usr/bin/env python
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from src.match_to_proposal.crew import MatchToDb2PositionsCrew


def run():
    """Run the CrewAI profile matching pipeline."""
    # Resolve CV path relative to project root
    workspace_root = Path(__file__).resolve().parent.parent.parent
    cv_path = os.getenv("CV_PATH", str(workspace_root / "data" / "cv.md"))

    if not os.path.exists(cv_path):
        print(f"Error: Candidate CV file not found at: {cv_path}")
        sys.exit(1)

    inputs = {
        "path_to_cv": cv_path,
    }

    print("==================================================")
    print("🚀 Starting CrewAI + IBM Db2 Profile Matching Crew")
    print(f"📄 Candidate CV: {cv_path}")
    print("==================================================\n")

    result = MatchToDb2PositionsCrew().crew().kickoff(inputs=inputs)

    print("\n==================================================")
    print("🎯 JOB MATCHING EVALUATION REPORT")
    print("==================================================\n")
    print(result)


if __name__ == "__main__":
    run()

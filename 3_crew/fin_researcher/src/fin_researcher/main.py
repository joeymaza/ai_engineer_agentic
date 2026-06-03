#!/usr/bin/env python
import os
import sys
import warnings
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from fin_researcher.crew import FinResearcher

_project_dir = Path(__file__).resolve().parents[2]
_repo_dir = _project_dir.parent.parent
load_dotenv(_project_dir / ".env")
load_dotenv(_repo_dir / ".env", override=True)

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)





def run():
    """
    Run the financial researcher crew.
    """
    inputs = {
        'company': 'Tesla',
        'current_date': datetime.now().strftime('%Y-%m-%d')
    }

    # Create and run the crew
    result = FinResearcher().crew().kickoff(inputs=inputs)
    print(result.raw)

if __name__ == "__main__":
    run()


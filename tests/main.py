import pytest
import sys
import os

if __name__ == "__main__":
    # Get the directory where main.py is located, which is the 'tests' directory.
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # You might need to add the parent directory of 'libs' to sys.path
    # if the tests need to import modules from 'libs/*'
    # For example:
    project_root = os.path.dirname(tests_dir)
    sys.path.insert(0, project_root)
    # This allows imports like 'from libs.datastore import ...' if your libs are structured that way
    # and not installed as packages in the environment.
    # However, if 'uv sync' correctly installs all local packages (libs) in editable mode
    # or as part of the workspace, explicit sys.path modification might not be needed.
    # For now, we'll keep it simple and assume pytest handles discovery within the tests_dir.

    # Run pytest, collecting tests from the 'tests_dir'.
    # Pytest will discover files like *_tests.py or test_*.py automatically.
    # The exit code from pytest.main will be used as the script's exit code.
    exit_code = pytest.main([tests_dir])
    sys.exit(exit_code)

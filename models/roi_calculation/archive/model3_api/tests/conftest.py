"""
Pytest configuration and shared fixtures.

This file ensures proper path setup for imports when running tests
from the project root.
"""

import sys
from pathlib import Path

# Ensure the app directory is in the Python path
# This allows imports to work when running from project root
_app_dir = Path(__file__).parent.parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))


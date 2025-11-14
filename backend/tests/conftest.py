"""
Pytest configuration and shared fixtures for database model tests.

This module provides common test fixtures and configuration for all database
model unit tests in the backend.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Set environment variables for testing
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

pytest_plugins = []
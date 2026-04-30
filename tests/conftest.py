"""
Pytest configuration and fixtures for FastAPI tests.

Provides:
- TestClient instance for FastAPI app
- Test data fixtures with isolated activity data
- Setup/teardown for test data isolation
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture: Returns a TestClient instance for the FastAPI app.
    
    This fixture does not modify the app state, allowing direct testing
    of the application's current behavior.
    """
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Fixture: Provides isolated test activity data.
    
    Creates a minimal set of test activities for testing purposes,
    separate from the app's hardcoded activities.
    """
    return {
        "Test Chess": {
            "description": "Test chess club",
            "schedule": "Monday 3:00 PM",
            "max_participants": 2,
            "participants": ["alice@test.edu"]
        },
        "Test Programming": {
            "description": "Test programming class",
            "schedule": "Tuesday 3:00 PM",
            "max_participants": 3,
            "participants": []
        }
    }


@pytest.fixture
def isolated_activities_for_testing(test_activities):
    """
    Fixture: Temporarily replaces the app's activities dict with test data,
    then restores the original after the test completes.
    
    This provides test isolation - each test gets a fresh copy of test data
    without interfering with other tests or the app's state.
    
    Arrange phase setup for tests that need isolated data.
    """
    # Store original activities
    original_activities = deepcopy(activities)
    
    # Replace with test data (shallow copy to avoid reference issues)
    activities.clear()
    activities.update(deepcopy(test_activities))
    
    # Yield to the test
    yield activities
    
    # Teardown: restore original activities
    activities.clear()
    activities.update(original_activities)

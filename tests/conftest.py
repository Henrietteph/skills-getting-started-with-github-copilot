"""Pytest configuration and fixtures for the FastAPI application tests."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test.
    
    This fixture ensures test isolation by resetting the in-memory activities
    dictionary to its original state before each test runs.
    """
    # Store the original activities data
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball": {
            "description": "Team sport and basketball tournaments",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis": {
            "description": "Tennis lessons and match play",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["noah@mergington.edu"]
        },
        "Art Club": {
            "description": "Drawing, painting, and visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "ava@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Orchestra and band performances",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu"]
        },
        "Math Club": {
            "description": "Problem solving and mathematical competitions",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, labs, and science fair preparation",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu"]
        }
    }
    
    yield
    
    # After test runs, reset the activities dictionary
    activities.clear()
    activities.update(deepcopy(original_activities))

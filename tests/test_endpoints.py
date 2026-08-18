"""Comprehensive tests for all FastAPI endpoints."""

import pytest


class TestRootRedirect:
    """Tests for the GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [307, 308]
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client):
        """Verify that GET /activities returns status 200."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client):
        """Verify that all 9 activities are returned."""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
    
    def test_get_activities_returns_correct_activity_names(self, client):
        """Verify that all expected activity names are present."""
        response = client.get("/activities")
        activities = response.json()
        expected_names = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball",
            "Tennis",
            "Art Club",
            "Music Ensemble",
            "Math Club",
            "Science Club"
        }
        assert set(activities.keys()) == expected_names
    
    def test_get_activities_returns_correct_structure(self, client):
        """Verify that each activity has the expected fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["max_participants"], int)
            assert isinstance(details["participants"], list)
    
    def test_get_activities_participants_are_emails(self, client):
        """Verify that participants are stored as email strings."""
        response = client.get("/activities")
        activities = response.json()
        
        for name, details in activities.items():
            for participant in details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_valid_student_succeeds(self, client):
        """Verify that a new student can successfully sign up for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu",
            json={}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client):
        """Verify that signup actually adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}", json={})
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Verify that signing up a student twice returns 400 error."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}", json={})
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Verify that signing up for non-existent activity returns 404."""
        response = client.post(
            "/activities/NonExistent Activity/signup?email=student@mergington.edu",
            json={}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_returns_success_message(self, client):
        """Verify that signup returns a success message with activity name and email."""
        response = client.post(
            "/activities/Tennis/signup?email=newplayer@mergington.edu",
            json={}
        )
        message = response.json()["message"]
        assert "newplayer@mergington.edu" in message
        assert "Tennis" in message
    
    def test_signup_persists_across_requests(self, client):
        """Verify that participant remains signed up after signup."""
        email = "persistent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}", json={})
        
        # Fetch activities multiple times and verify persistence
        for _ in range(3):
            response = client.get("/activities")
            assert email in response.json()["Basketball"]["participants"]
    
    def test_signup_different_students_same_activity(self, client):
        """Verify that multiple different students can sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        client.post(f"/activities/Art Club/signup?email={email1}", json={})
        client.post(f"/activities/Art Club/signup?email={email2}", json={})
        
        response = client.get("/activities")
        participants = response.json()["Art Club"]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestDeleteParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_delete_participant_succeeds(self, client):
        """Verify that a participant can be successfully deleted from an activity."""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_delete_removes_participant_from_activity(self, client):
        """Verify that delete actually removes the participant."""
        email = "daniel@mergington.edu"  # In Chess Club
        client.delete(f"/activities/Chess Club/participants/{email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
    
    def test_delete_nonexistent_activity_returns_404(self, client):
        """Verify that deleting from non-existent activity returns 404."""
        response = client.delete(
            "/activities/NonExistent Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_nonexistent_participant_returns_404(self, client):
        """Verify that deleting a non-existent participant returns 404."""
        response = client.delete(
            "/activities/Chess Club/participants/nothere@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_delete_returns_success_message(self, client):
        """Verify that delete returns a success message with activity and email."""
        email = "michael@mergington.edu"
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        message = response.json()["message"]
        assert email in message
        assert "Chess Club" in message
        assert "Unregistered" in message
    
    def test_delete_other_participants_remain(self, client):
        """Verify that deleting one participant doesn't affect others."""
        # Chess Club has michael and daniel
        client.delete("/activities/Chess Club/participants/michael@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in participants
        assert "michael@mergington.edu" not in participants


class TestDataPersistence:
    """Tests for data consistency and persistence."""
    
    def test_signup_then_delete_removes_participant(self, client):
        """Verify sign up followed by delete works correctly."""
        email = "tempstudent@mergington.edu"
        activity = "Music Ensemble"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}", json={})
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Delete
        client.delete(f"/activities/{activity}/participants/{email}")
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_operations_maintain_state(self, client):
        """Verify that multiple operations maintain correct state."""
        activity = "Science Club"
        student1 = "alice@mergington.edu"
        student2 = "bob@mergington.edu"
        
        # Initial state
        response = client.get("/activities")
        initial_participants = set(response.json()[activity]["participants"])
        
        # Add two students
        client.post(f"/activities/{activity}/signup?email={student1}", json={})
        client.post(f"/activities/{activity}/signup?email={student2}", json={})
        
        response = client.get("/activities")
        assert student1 in response.json()[activity]["participants"]
        assert student2 in response.json()[activity]["participants"]
        
        # Remove first student
        client.delete(f"/activities/{activity}/participants/{student1}")
        
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert student1 not in participants
        assert student2 in participants

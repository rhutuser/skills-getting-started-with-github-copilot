import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        # Arrange
        # No setup needed for this simple test
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        # Arrange
        # No setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
    
    def test_get_activities_contains_required_fields(self):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_successful(self):
        """Test successful signup for a new participant"""
        # Arrange
        email = "newstudent@example.com"
        activity_name = "Chess%20Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_to_nonexistent_activity_returns_404(self):
        """Test signup to an activity that doesn't exist returns 404"""
        # Arrange
        email = "test@example.com"
        nonexistent_activity = "FakeActivity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email_returns_400(self):
        """Test that the same student cannot sign up twice for same activity"""
        # Arrange
        email = "duplicate@example.com"
        activity_name = "Chess%20Club"
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Act - Second signup attempt with same email
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_successful(self):
        """Test successful unregistration of an existing participant"""
        # Arrange
        email = "unregister@example.com"
        activity_name = "Chess%20Club"
        
        # Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self):
        """Test unregister from an activity that doesn't exist returns 404"""
        # Arrange
        email = "test@example.com"
        nonexistent_activity = "FakeActivity"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant_returns_404(self):
        """Test unregister when participant is not registered returns 404"""
        # Arrange
        email = "notregistered@example.com"
        activity_name = "Chess%20Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self):
        """Test that root endpoint redirects to static/index.html"""
        # Arrange
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        redirect_location = response.headers.get("location", "")
        
        # Assert
        assert response.status_code == 307
        assert expected_redirect_path in redirect_location

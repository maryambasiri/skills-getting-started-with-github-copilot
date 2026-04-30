"""
Backend FastAPI tests for the Mergington High School API.

Tests follow the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the action being tested
- Assert: Verify the results
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_list(self, client, isolated_activities_for_testing):
        """
        GIVEN the API is running with test activities
        WHEN a GET request is made to /activities
        THEN return a successful response with all activities
        """
        # Arrange
        expected_activity_count = 2
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) == expected_activity_count

    def test_get_activities_contains_correct_activity_structure(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN the API is running with test activities
        WHEN a GET request is made to /activities
        THEN each activity has the required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_get_activities_returns_participants_list(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN test activities with some having registered participants
        WHEN a GET request is made to /activities
        THEN return activities with their current participant lists
        """
        # Arrange
        expected_participants_in_chess = ["alice@test.edu"]
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        chess_activity = activities_data.get("Test Chess")
        
        # Assert
        assert chess_activity is not None
        assert chess_activity["participants"] == expected_participants_in_chess


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_when_activity_exists_and_email_not_registered(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN an activity exists with available slots
        AND the student email is not already registered
        WHEN a POST request is made to signup
        THEN the student is added to participants and success message is returned
        """
        # Arrange
        activity_name = "Test Programming"
        student_email = "bob@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert student_email in response.json().get("message", "")
        
        # Verify signup persisted
        verify_response = client.get("/activities")
        assert student_email in verify_response.json()[activity_name]["participants"]

    def test_signup_fails_when_activity_not_found(self, client, isolated_activities_for_testing):
        """
        GIVEN an activity name that does not exist
        WHEN a POST request is made to signup for that activity
        THEN return 404 error with appropriate message
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        student_email = "bob@test.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_when_student_already_registered(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN a student is already registered for an activity
        WHEN a POST request is made to signup again for the same activity
        THEN return 400 error indicating duplicate signup
        """
        # Arrange
        activity_name = "Test Chess"
        student_email = "alice@test.edu"  # Already registered in test data
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    @pytest.mark.parametrize("student_email", [
        "student1@test.edu",
        "student2@test.edu",
    ])
    def test_signup_multiple_students_successfully(
        self, client, isolated_activities_for_testing, student_email
    ):
        """
        GIVEN different students signing up for the same activity
        WHEN POST requests are made for each student
        THEN all students are successfully added to the activity
        """
        # Arrange
        activity_name = "Test Programming"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert student_email in response.json().get("message", "")


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_when_student_is_registered(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN a student is registered for an activity
        WHEN a DELETE request is made to unregister
        THEN the student is removed from participants and success message is returned
        """
        # Arrange
        activity_name = "Test Chess"
        student_email = "alice@test.edu"  # Already registered in test data
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert student_email in response.json().get("message", "")
        
        # Verify unregister persisted
        verify_response = client.get("/activities")
        assert student_email not in verify_response.json()[activity_name]["participants"]

    def test_unregister_fails_when_activity_not_found(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN an activity name that does not exist
        WHEN a DELETE request is made to unregister from that activity
        THEN return 404 error with appropriate message
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        student_email = "alice@test.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_fails_when_student_not_registered(
        self, client, isolated_activities_for_testing
    ):
        """
        GIVEN a student is not registered for an activity
        WHEN a DELETE request is made to unregister
        THEN return 400 error indicating student is not registered
        """
        # Arrange
        activity_name = "Test Programming"
        student_email = "notregistered@test.edu"  # Not in participants
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    @pytest.mark.parametrize("student_email,activity_name", [
        ("alice@test.edu", "Test Chess"),
    ])
    def test_unregister_removes_from_participants_list(
        self, client, isolated_activities_for_testing, student_email, activity_name
    ):
        """
        GIVEN a registered student in an activity
        WHEN the student unregisters
        THEN they are completely removed from the participants list
        """
        # Arrange (verify pre-condition)
        activities_before = client.get("/activities").json()
        assert student_email in activities_before[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        activities_after = client.get("/activities").json()
        assert student_email not in activities_after[activity_name]["participants"]


class TestRootEndpoint:
    """Test suite for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        GIVEN a request to the root path
        WHEN a GET request is made to /
        THEN return a redirect response to /static/index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url

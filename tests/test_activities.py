import pytest


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        for activity in expected_activities:
            assert activity in data

    def test_activities_contain_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"

    def test_participants_field_is_list(self, client):
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"participants field in {activity_name} is not a list"


class TestActivitySignup:
    def test_signup_for_available_activity_succeeds(self, client):
        # Arrange
        email = "newstudent@school.edu"
        activity = "Basketball Team"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_duplicate_signup_is_rejected(self, client):
        # Arrange
        email = "duplicate@school.edu"
        activity = "Chess Club"

        # Act - First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Act - Duplicate signup attempt
        response2 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_for_nonexistent_activity_fails(self, client):
        # Arrange
        email = "test@school.edu"
        activity = "NonexistentClub"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_adds_participant_to_activity(self, client):
        # Arrange
        email = "participant@school.edu"
        activity = "Soccer Club"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity]["participants"]
        assert email in participants

    def test_signup_response_contains_confirmation_message(self, client):
        # Arrange
        email = "confirm@school.edu"
        activity = "Programming Class"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert activity in data["message"]
        assert email in data["message"]


class TestActivityRemoval:
    def test_remove_participant_succeeds(self, client):
        # Arrange
        email = "toremove@school.edu"
        activity = "Drama Club"
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()

    def test_remove_unsigned_participant_fails(self, client):
        # Arrange
        email = "notsignup@school.edu"
        activity = "Art Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_remove_from_nonexistent_activity_fails(self, client):
        # Arrange
        email = "test@school.edu"
        activity = "FakeClub"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_removal_removes_participant_from_list(self, client):
        # Arrange
        email = "verify@school.edu"
        activity = "Science Club"
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_removal_response_contains_confirmation_message(self, client):
        # Arrange
        email = "removeconfirm@school.edu"
        activity = "Debate Club"
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

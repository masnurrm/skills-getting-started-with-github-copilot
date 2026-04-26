import pytest
from fastapi.testclient import TestClient

# Arrange-Act-Assert (AAA) pattern is used in all tests

def test_root_redirect(client):
    # Arrange
    # (client fixture provides TestClient)
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200 or response.status_code == 307
    assert "text/html" in response.headers.get("content-type", "")

def test_list_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_signup_success(client):
    # Arrange
    activity = list(client.get("/activities").json().keys())[0]
    email = "student1@example.com"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Fetch activity to confirm participant was added
    activity_data = client.get("/activities").json()[activity]
    assert email in activity_data["participants"]

def test_signup_duplicate(client):
    # Arrange
    activity = list(client.get("/activities").json().keys())[0]
    email = "student2@example.com"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.text

def test_signup_nonexistent_activity(client):
    # Arrange
    activity = "nonexistent"
    email = "student3@example.com"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    assert "not found" in response.text.lower()

def test_remove_participant_success(client):
    # Arrange
    activity = list(client.get("/activities").json().keys())[0]
    email = "student4@example.com"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    response = client.request(
        "DELETE",
        f"/activities/{activity}/participant",
        json={"email": email}
    )
    # Assert
    assert response.status_code == 200
    assert f"Removed {email} from {activity}" in response.json()["message"]
    # Fetch activity to confirm participant was removed
    activity_data = client.get("/activities").json()[activity]
    assert email not in activity_data["participants"]

def test_remove_participant_not_found(client):
    # Arrange
    activity = list(client.get("/activities").json().keys())[0]
    email = "student5@example.com"
    # Act
    response = client.request(
        "DELETE",
        f"/activities/{activity}/participant",
        json={"email": email}
    )
    # Assert
    assert response.status_code == 404
    assert "not found" in response.text.lower()

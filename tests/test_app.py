from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_all():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant_cycle():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Arrange
    # use list operations since participants is a list
    participants = activities[activity]["participants"]
    if email in participants:
        participants.remove(email)
    signup_url = f"/activities/{activity}/signup"
    remove_url = f"/activities/{activity}/participant"

    # Act - sign up
    resp = client.post(signup_url, params={"email": email})
    # Assert sign up
    assert resp.status_code == 200
    assert email in participants
    assert "Signed up" in resp.json()["message"]

    # Act - remove
    resp2 = client.delete(remove_url, params={"email": email})
    # Assert removal
    assert resp2.status_code == 200
    assert email not in participants
    assert "Removed" in resp2.json()["message"]


def test_error_when_removing_nonexistent_participant():
    activity = "Chess Club"
    fake = "ghost@mergington.edu"

    # Arrange
    # make sure the fake address isn't in the list before acting
    if fake in activities[activity]["participants"]:
        activities[activity]["participants"].remove(fake)
    url = f"/activities/{activity}/participant"

    # Act
    resp = client.delete(url, params={"email": fake})

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not registered"


def test_signup_duplicate_fails():
    activity = "Programming Class"
    # Arrange
    existing = activities[activity]["participants"][0]
    url = f"/activities/{activity}/signup"

    # Act
    resp = client.post(url, params={"email": existing})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]

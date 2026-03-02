from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Should contain at least one known activity
    assert "Chess Club" in data


def test_signup_and_remove_participant_cycle():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # ensure not already in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # sign up the user
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json()["message"]

    # removing them should work
    resp2 = client.delete(f"/activities/{activity}/participant", params={"email": email})
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]
    assert "Removed" in resp2.json()["message"]


def test_error_when_removing_nonexistent_participant():
    activity = "Chess Club"
    fake = "ghost@mergington.edu"
    if fake in activities[activity]["participants"]:
        activities[activity]["participants"].remove(fake)
    resp = client.delete(f"/activities/{activity}/participant", params={"email": fake})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not registered"


def test_signup_duplicate_fails():
    activity = "Programming Class"
    present = activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup", params={"email": present})
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]

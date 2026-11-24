import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "description": "Play chess",
                "schedule": "Fridays",
                "max_participants": 12,
                "participants": ["student@mergington.edu"],
            }
        },
    )
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_root_redirects_to_homepage(client):
    url = "/"

    response = client.get(url, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_details_and_participants(client):
    expected = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["student@mergington.edu"],
        }
    }

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client):
    email = "new-student@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert app_module.activities["Chess Club"]["participants"] == [
        "student@mergington.edu",
        email,
    ]


def test_signup_rejects_duplicate_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert app_module.activities["Chess Club"]["participants"] == [email]


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_registration_returns_not_found_for_unknown_activity(client, method):
    email = "student@mergington.edu"

    response = client.request(
        method,
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert app_module.activities["Chess Club"]["participants"] == [email]
    assert "Unknown Club" not in app_module.activities


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_registration_requires_email(client, method):
    url = "/activities/Chess%20Club/signup"

    response = client.request(method, url)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]
    assert app_module.activities["Chess Club"]["participants"] == [
        "student@mergington.edu"
    ]


def test_unregister_removes_participant(client):
    email = "student@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@mergington.edu from Chess Club"
    }
    assert app_module.activities["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_participant(client):
    email = "unknown@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert app_module.activities["Chess Club"]["participants"] == [
        "student@mergington.edu"
    ]

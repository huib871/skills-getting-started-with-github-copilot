from fastapi.testclient import TestClient

from src import app as app_module


def test_unregister_removes_participant(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "participants": ["student@mergington.edu"],
            }
        },
    )
    client = TestClient(app_module.app)

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@mergington.edu from Chess Club"
    }
    assert app_module.activities["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_participant(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "participants": [],
            }
        },
    )
    client = TestClient(app_module.app)

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"

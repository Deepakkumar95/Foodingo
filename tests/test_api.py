import os
import sys

from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from live_app import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health", headers={"host": "127.0.0.1"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert "app_time" in payload


def test_token_endpoint_for_admin():
    with TestClient(app) as client:
        response = client.post(
            "/token",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded", "host": "127.0.0.1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data


def test_admin_system_health_requires_admin_token():
    with TestClient(app) as client:
        token_response = client.post(
            "/token",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded", "host": "127.0.0.1"},
        )
        assert token_response.status_code == 200
        access_token = token_response.json()["access_token"]

        health_response = client.get(
            "/admin/system_health",
            headers={
                "Authorization": f"Bearer {access_token}",
                "host": "127.0.0.1"
            },
        )

        assert health_response.status_code == 200
        health_payload = health_response.json()
        assert health_payload["success"] is True
        assert "health" in health_payload
        assert isinstance(health_payload["health"], dict)


def test_admin_system_health_denies_unauthorized_access():
    with TestClient(app) as client:
        response = client.get(
            "/admin/system_health",
            headers={"host": "127.0.0.1"},
        )
        assert response.status_code == 401
        payload = response.json()
        assert payload["detail"] == "Not authenticated"


def test_admin_system_health_rejects_invalid_bearer_token():
    with TestClient(app) as client:
        response = client.get(
            "/admin/system_health",
            headers={
                "Authorization": "Bearer invalid.token.value",
                "host": "127.0.0.1"
            },
        )
        assert response.status_code == 401
        payload = response.json()
        assert payload["detail"] == "Could not validate credentials"

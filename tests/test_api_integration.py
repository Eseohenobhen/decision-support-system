from decimal import Decimal

import pytest

from app.models.property import Property


def test_login_returns_token(client):
    response = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_fails_with_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "wrongpass"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_current_user(client, admin_user):
    response = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


def test_create_property_requires_admin(client, manager_user):
    response = client.post("/api/v1/auth/login", data={"username": "manager@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/properties/",
        json={
            "code": "PROP-NEW",
            "name": "New Property",
            "address": "123 Main St",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria",
            "total_units": 5,
            "manager_id": manager_user.id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_create_property_as_admin(client, admin_user, manager_user):
    response = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/properties/",
        json={
            "code": "PROP-NEW",
            "name": "New Property",
            "address": "123 Main St",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria",
            "total_units": 5,
            "manager_id": manager_user.id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["code"] == "PROP-NEW"


def test_list_properties_manager_filter(client, manager_user, db_session):
    response = client.post("/api/v1/auth/login", data={"username": "manager@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.get("/api/v1/properties/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_maintenance_request(client, manager_user, property_with_fund):
    property_, _ = property_with_fund
    response = client.post("/api/v1/auth/login", data={"username": "manager@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/maintenance-requests/",
        json={
            "property_id": property_.id,
            "title": "Fix broken window",
            "description": "Living room window needs repair",
            "priority": "high",
            "priority_score": 75,
            "estimated_cost": 5000.0,
            "required_by": None,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Fix broken window"
    assert response.json()["status"] == "pending"


def test_dss_rank_endpoint(client, manager_user):
    response = client.post("/api/v1/auth/login", data={"username": "manager@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.post(
        "/api/v1/maintenance-allocations/dss/rank",
        json={
            "items": [
                {"item_id": 1, "title": "Item A", "urgency": 8.0, "impact": 7.0, "asset_importance": 6.0, "cost": 2000.0},
                {"item_id": 2, "title": "Item B", "urgency": 6.0, "impact": 6.0, "asset_importance": 6.0, "cost": 500.0},
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "formula" in response.json()
    assert "items" in response.json()
    assert len(response.json()["items"]) == 2


def test_fund_allocation_report(client, manager_user):
    response = client.post("/api/v1/auth/login", data={"username": "manager@example.com", "password": "pass123"})
    token = response.json()["access_token"]

    response = client.get(
        "/api/v1/reports/property-summary?format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] in ["application/pdf", "application/octet-stream"]

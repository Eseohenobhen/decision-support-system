from decimal import Decimal

import pytest

from app.models.property import Property
from app.models.user import User, UserRole
from app.core.security import password_context


def _login(client, username: str) -> str:
    response = client.post("/api/v1/auth/login", data={"username": username, "password": "pass123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_returns_token(client, admin_user):
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


def test_admin_assigns_property_to_manager(client, admin_user, manager_user, property_with_fund):
    property_, _ = property_with_fund
    token = _login(client, "admin@example.com")

    response = client.post(
        "/api/v1/manager-properties",
        json={"manager_id": manager_user.id, "property_id": property_.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["manager_id"] == manager_user.id
    assert body["property_id"] == property_.id
    assert body["manager"]["email"] == "manager@example.com"
    assert body["property"]["code"] == property_.code


def test_manager_cannot_assign_property(client, manager_user, property_with_fund):
    property_, _ = property_with_fund
    token = _login(client, "manager@example.com")

    response = client.post(
        "/api/v1/manager-properties",
        json={"manager_id": manager_user.id, "property_id": property_.id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_manager_funds_dashboard_only_returns_own_properties(client, db_session, admin_user, manager_user, property_with_fund):
    property_, fund = property_with_fund
    other_manager = User(
        email="other-manager@example.com",
        full_name="Other Manager",
        hashed_password=password_context.hash("pass123"),
        role=UserRole.PROPERTY_MANAGER,
        is_active=True,
    )
    db_session.add(other_manager)
    db_session.commit()
    db_session.refresh(other_manager)

    admin_token = _login(client, "admin@example.com")
    response = client.post(
        "/api/v1/manager-properties",
        json={"manager_id": manager_user.id, "property_id": property_.id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201

    manager_token = _login(client, "manager@example.com")
    response = client.get(
        "/api/v1/dashboard/manager-funds",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["manager"]["id"] == manager_user.id
    assert body["total_funds_managed"] == str(Decimal(fund.current_balance).quantize(Decimal("0.01")))
    assert [item["id"] for item in body["assigned_properties"]] == [property_.id]

    response = client.get(
        f"/api/v1/dashboard/manager-funds?manager_id={other_manager.id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 403

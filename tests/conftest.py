import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import password_context
from app.db.base import Base
from app.main import app
from app.models.property import Property
from app.models.property_fund import PropertyFund
from app.models.user import User, UserRole


TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine, monkeypatch):
    connection = engine.connect()
    transaction = connection.begin()
    testing_session = sessionmaker(bind=connection, autocommit=False, autoflush=False)

    monkeypatch.setattr("app.api.deps.SessionLocal", testing_session)
    monkeypatch.setattr("app.db.session.SessionLocal", testing_session)

    session = testing_session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=password_context.hash("pass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def manager_user(db_session):
    user = User(
        email="manager@example.com",
        full_name="Manager User",
        hashed_password=password_context.hash("pass123"),
        role=UserRole.PROPERTY_MANAGER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def property_with_fund(db_session, manager_user):
    property_ = Property(
        code="PROP-01",
        name="Sample Asset",
        address="100 Demo Street",
        city="Lagos",
        state="Lagos",
        country="Nigeria",
        total_units=10,
        manager_id=manager_user.id,
    )
    db_session.add(property_)
    db_session.commit()
    db_session.refresh(property_)

    fund = PropertyFund(
        property_id=property_.id,
        fiscal_year=2026,
        annual_budget=100000,
        current_balance=90000,
        reserved_balance=10000,
        currency="NGN",
    )
    db_session.add(fund)
    db_session.commit()
    db_session.refresh(fund)
    return property_, fund

from fastapi.testclient import TestClient
from sqlalchemy import select

from job_aggregator.api.dependencies import get_db
from job_aggregator.db.models.user import User
from job_aggregator.main import app

client = TestClient(app)


def test_register_user(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new-user@example.com",
            "password": "Strong-password-123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"
    assert "id" in response.json()
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()

    user = db_session.scalars(
        select(User).where(User.email == "new-user@example.com")
    ).one()
    assert user.hashed_password != "Strong-password-123!"


def test_register_duplicate_email(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "email": "duplicate@example.com",
        "password": "Strong-password-123!",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login_success(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    registration_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Strong-password-123!",
        },
    )
    assert registration_response.status_code == 201

    response = client.post(
        "/api/v1/auth/token",
        json={
            "email": "login@example.com",
            "password": "Strong-password-123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)
    assert response.json()["access_token"]


def test_login_wrong_password(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    registration_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong-password@example.com",
            "password": "Strong-password-123!",
        },
    )
    assert registration_response.status_code == 201

    response = client.post(
        "/api/v1/auth/token",
        json={
            "email": "wrong-password@example.com",
            "password": "Wrong-password-456!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_unknown_email():
    response = client.post(
        "/api/v1/auth/token",
        json={
            "email": "does-not-exist@example.com",
            "password": "Some-password-123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

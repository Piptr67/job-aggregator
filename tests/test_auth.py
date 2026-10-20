import time

from fastapi.testclient import TestClient
import jwt
from sqlalchemy import select

from job_aggregator.api.dependencies import get_db
from job_aggregator.core.config import settings
from job_aggregator.core.security import create_verification_token, create_access_token
from job_aggregator.core.passwords import hash_password
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

    user = db_session.scalar(
    select(User).where(User.email == "login@example.com")
    )
    assert user is not None
    user.is_verified = True
    db_session.commit()

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


def test_verify_email(client, db_session):
    user = User(
        email="verify@example.com",
        hashed_password="test-hash",
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()

    token = create_verification_token(user.email)

    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": token},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Email verified successfully"
    }

    db_session.refresh(user)
    assert user.is_verified is True


def test_verify_email_invalid_token(client):
    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": "not-a-valid-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification link"


def test_verify_email_rejects_access_token(client):
    token = create_access_token("verify@example.com")

    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": token},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification link"


def test_verify_email_expired_token(client):
    token = jwt.encode(
        {
            "sub": "verify@example.com",
            "purpose": "email_verification",
            "exp": int(time.time()) - 60,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/auth/verify-email",
        params={"token": token},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification link"


def test_login_unverified_user(client, db_session):
    user = User(
        email="unverified@example.com",
        hashed_password=hash_password("correct-password"),
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/token",
        json={
            "email": "unverified@example.com",
            "password": "correct-password",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Please verify your email before logging in"
    )

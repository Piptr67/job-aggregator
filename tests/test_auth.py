import time
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select

from job_aggregator.api.dependencies import get_db
from job_aggregator.core.config import settings
from job_aggregator.core.passwords import hash_password
from job_aggregator.core.security import (
    create_access_token,
    create_verification_token,
)
from job_aggregator.db.models.user import User
from job_aggregator.main import app

client = TestClient(app)


def test_register_user(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("job_aggregator.api.routes.auth.send_verification_email") as mock_send:
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
    mock_send.assert_called_once()


def test_register_invalid_email():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Strong-password-123!",
        },
    )

    assert response.status_code == 422


def test_register_password_too_short():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short-password@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_register_duplicate_email(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "email": "duplicate@example.com",
        "password": "Strong-password-123!",
    }

    with patch("job_aggregator.api.routes.auth.send_verification_email") as mock_send:
        first_response = client.post("/api/v1/auth/register", json=payload)
        second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"
    mock_send.assert_called_once()


def test_login_success(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with patch("job_aggregator.api.routes.auth.send_verification_email"):
        registration_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "Strong-password-123!",
            },
        )

    assert registration_response.status_code == 201

    user = db_session.scalar(select(User).where(User.email == "login@example.com"))
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

    with patch("job_aggregator.api.routes.auth.send_verification_email"):
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
    assert response.json() == {"message": "Email verified successfully"}

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
    assert response.json()["detail"] == ("Please verify your email before logging in")


def test_google_login_creates_new_user(client, db_session):
    google_user = {
        "email": "google@example.com",
        "email_verified": True,
        "sub": "google-user-123",
    }

    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value=google_user,
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    user = db_session.query(User).filter_by(email="google@example.com").one()
    assert user.is_verified is True
    assert user.hashed_password is None


def test_google_login_rejects_invalid_token(client):
    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        side_effect=ValueError("Invalid token"),
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "invalid-token"},
        )

    assert response.status_code == 401


def test_google_login_reuses_existing_user(client, db_session):
    user = User(
        email="existing@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    user_id = user.id

    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value={
            "email": "existing@example.com",
            "email_verified": True,
            "sub": "google-user-456",
        },
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )

    assert response.status_code == 200

    users = db_session.query(User).filter_by(email="existing@example.com").all()
    assert len(users) == 1
    assert users[0].id == user_id


def test_google_login_clears_password_for_unverified_existing_user(client, db_session):
    attacker_password = "Attacker-controlled-password-123!"

    user = User(
        email="victim@example.com",
        hashed_password=hash_password(attacker_password),
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()

    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value={
            "email": "victim@example.com",
            "email_verified": True,
            "sub": "victim-google-id",
        },
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )

    assert response.status_code == 200

    db_session.refresh(user)
    assert user.is_verified is True
    assert user.hashed_password is None

    login_response = client.post(
        "/api/v1/auth/token",
        json={
            "email": "victim@example.com",
            "password": attacker_password,
        },
    )
    assert login_response.status_code == 401


def test_google_login_rejects_missing_email(client):
    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value={"sub": "google-user-no-email"},
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Google account has no valid email"


def test_google_login_rejects_empty_email(client):
    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value={"email": ""},
    ):
        response = client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Google account has no valid email"

import time

import jwt
import pytest
from sqlalchemy import select

from job_aggregator.core.config import settings
from job_aggregator.core.passwords import hash_password
from job_aggregator.core.security import create_access_token, create_verification_token
from job_aggregator.db.models.user import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/token"
VERIFY_URL = "/api/v1/auth/verify-email"
PASSWORD = "Strong-password-123!"


def register(client, email, password=PASSWORD):
    return client.post(REGISTER_URL, json={"email": email, "password": password})


def login(client, email, password=PASSWORD):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


def test_register_user(client, mock_verification_email):
    response = register(client, "new-user@example.com")

    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"
    assert not {"password", "hashed_password"} & response.json().keys()
    mock_verification_email.assert_called_once()


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("not-an-email", PASSWORD),
        ("short-password@example.com", "short"),
    ],
)
def test_register_validation(client, email, password):
    assert register(client, email, password).status_code == 422


def test_register_duplicate_email(client, mock_verification_email):
    email = "duplicate@example.com"

    assert register(client, email).status_code == 201
    response = register(client, email)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"
    mock_verification_email.assert_called_once()


def test_login_success(client, db_session):
    email = "login@example.com"
    assert register(client, email).status_code == 201

    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    user.is_verified = True
    db_session.commit()

    response = login(client, email)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


@pytest.mark.parametrize(
    ("email", "password", "verified"),
    [
        ("unknown@example.com", PASSWORD, True),
        ("wrong-password@example.com", "Wrong-password-456!", True),
    ],
)
def test_login_rejects_invalid_credentials(
    client, db_session, email, password, verified
):
    if email != "unknown@example.com":
        db_session.add(
            User(
                email=email,
                hashed_password=hash_password(PASSWORD),
                is_verified=verified,
            )
        )
        db_session.commit()

    response = login(client, email, password)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_unverified_user(client, db_session):
    user = User(
        email="unverified@example.com",
        hashed_password=hash_password("correct-password"),
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()

    response = login(client, user.email, "correct-password")

    assert response.status_code == 403
    assert response.json()["detail"] == "Please verify your email before logging in"


def test_verify_email(client, db_session):
    user = User(
        email="verify@example.com",
        hashed_password="test-hash",
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.get(
        VERIFY_URL,
        params={"token": create_verification_token(user.email)},
    )

    assert response.status_code == 200
    db_session.refresh(user)
    assert user.is_verified


@pytest.mark.parametrize(
    "token",
    [
        "not-a-valid-token",
        create_access_token("verify@example.com"),
        jwt.encode(
            {
                "sub": "verify@example.com",
                "purpose": "email_verification",
                "exp": int(time.time()) - 60,
            },
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        ),
    ],
    ids=["malformed", "access-token", "expired"],
)
def test_verify_email_rejects_invalid_tokens(client, token):
    response = client.get(VERIFY_URL, params={"token": token})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification link"

from unittest.mock import patch

import pytest
from sqlalchemy import select

from job_aggregator.db.models.user import User


def google_login(client, google_user):
    with patch(
        "job_aggregator.api.routes.auth.verify_google_token",
        return_value=google_user,
    ):
        return client.post(
            "/api/v1/auth/google",
            json={"id_token": "fake-google-token"},
        )


def test_google_login_creates_user(client, db_session):
    response = google_login(
        client,
        {
            "email": "google@example.com",
            "email_verified": True,
            "sub": "google-user-123",
        },
    )

    user = db_session.scalar(select(User).where(User.email == "google@example.com"))

    assert response.status_code == 200
    assert user is not None
    assert user.is_verified
    assert user.hashed_password is None


def test_google_login_reuses_existing_user(client, db_session):
    user = User(
        email="existing@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    response = google_login(
        client,
        {
            "email": user.email,
            "email_verified": True,
            "sub": "google-user-456",
        },
    )

    users = db_session.scalars(select(User).where(User.email == user.email)).all()

    assert response.status_code == 200
    assert len(users) == 1
    assert users[0].id == user_id


@pytest.mark.parametrize(
    "google_user",
    [{"sub": "missing-email"}, {"email": ""}],
    ids=["missing-email", "empty-email"],
)
def test_google_login_rejects_invalid_email(client, google_user):
    response = google_login(client, google_user)

    assert response.status_code == 401
    assert response.json()["detail"] == "Google account has no valid email"


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

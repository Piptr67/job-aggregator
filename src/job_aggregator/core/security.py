from datetime import datetime, timedelta, timezone

import jwt

from job_aggregator.core.config import settings


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def create_verification_token(email: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": email,
        "purpose": "email_verification",
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_verification_token(token: str) -> str:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    if payload.get("purpose") != "email_verification":
        raise jwt.InvalidTokenError("Invalid verification token")

    email = payload.get("sub")
    if not isinstance(email, str) or not email:
        raise jwt.InvalidTokenError("Invalid verification token")

    return email

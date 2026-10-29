from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from job_aggregator.core.config import settings


def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "exp": expires_at,
    }

    return _encode(payload)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
    )

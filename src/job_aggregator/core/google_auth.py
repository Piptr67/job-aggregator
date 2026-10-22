from google.auth.transport import requests
from google.oauth2 import id_token

from job_aggregator.core.config import settings


def verify_google_token(token: str) -> dict:
    id_info = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.google_client_id,
    )

    if not id_info.get("email_verified"):
        raise ValueError("Google email is not verified")

    return id_info

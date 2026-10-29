from unittest.mock import patch

import requests

from job_aggregator.core.security import create_access_token
from job_aggregator.db.models.user import User


def authenticated_headers(db_session) -> dict[str, str]:
    user = User(
        email="ingestion-route-test@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def test_ingestion_himalayas_success(client, db_session):
    headers = authenticated_headers(db_session)

    with patch(
        "job_aggregator.api.routes.ingestion.SOURCE_REGISTRY"
    ) as registry:
        registry.get.return_value = lambda db: 3

        response = client.post("/api/v1/ingestion/himalayas", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"jobs_processed": 3}


def test_ingestion_arbeitnow_success(client, db_session):
    headers = authenticated_headers(db_session)

    with patch(
        "job_aggregator.api.routes.ingestion.SOURCE_REGISTRY"
    ) as registry:
        registry.get.return_value = lambda db: 2

        response = client.post("/api/v1/ingestion/arbeitnow", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"jobs_processed": 2}


def test_ingestion_unsupported_source(client, db_session):
    headers = authenticated_headers(db_session)

    response = client.post("/api/v1/ingestion/unknown", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Unsupported ingestion source: unknown"


def test_ingestion_upstream_failure_returns_502(client, db_session):
    headers = authenticated_headers(db_session)

    def raise_connection_error(db):
        raise requests.ConnectionError("Upstream unavailable")

    with patch(
        "job_aggregator.api.routes.ingestion.SOURCE_REGISTRY"
    ) as registry:
        registry.get.return_value = raise_connection_error

        response = client.post("/api/v1/ingestion/himalayas", headers=headers)

    assert response.status_code == 502
    assert response.json()["detail"] == "Failed to fetch jobs from himalayas"


def test_ingestion_requires_authentication(client):
    response = client.post("/api/v1/ingestion/himalayas")

    assert response.status_code == 401

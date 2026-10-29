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
        "job_aggregator.api.routes.ingestion.ingest_himalayas",
        return_value=3,
    ):
        response = client.post("/api/v1/ingestion/himalayas", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"jobs_processed": 3}


def test_ingestion_arbeitnow_success(client, db_session):
    headers = authenticated_headers(db_session)

    with patch(
        "job_aggregator.api.routes.ingestion.ingest_arbeitnow",
        return_value=2,
    ):
        response = client.post("/api/v1/ingestion/arbeitnow", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"jobs_processed": 2}


def test_ingestion_all_sources_success(client, db_session):
    headers = authenticated_headers(db_session)

    with (
        patch(
            "job_aggregator.api.routes.ingestion.ingest_himalayas",
            return_value=3,
        ),
        patch(
            "job_aggregator.api.routes.ingestion.ingest_arbeitnow",
            return_value=2,
        ),
    ):
        response = client.post("/api/v1/ingestion/all", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"jobs_processed": 5}


def test_ingestion_unsupported_source(client, db_session):
    headers = authenticated_headers(db_session)

    response = client.post("/api/v1/ingestion/unknown", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Unsupported ingestion source: unknown"


def test_ingestion_upstream_failure_returns_502(client, db_session):
    headers = authenticated_headers(db_session)

    with patch(
        "job_aggregator.api.routes.ingestion.ingest_himalayas",
        side_effect=requests.ConnectionError("Upstream unavailable"),
    ):
        response = client.post("/api/v1/ingestion/himalayas", headers=headers)

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "jobs_processed": 0,
        "failed_sources": ["himalayas"],
    }


def test_ingestion_requires_authentication(client):
    response = client.post("/api/v1/ingestion/himalayas")

    assert response.status_code == 401

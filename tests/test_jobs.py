import pytest

from job_aggregator.db.models.job import Job


def create_job(db_session):
    job = Job(
        title="Test Python Developer",
        company="Test Company",
        url="https://example.com/test-python-developer-2",
        source="test",
    )
    db_session.add(job)
    db_session.commit()
    return job


@pytest.mark.parametrize(
    "headers",
    [
        None,
        {"Authorization": "Bearer definitely-not-a-valid-token"},
    ],
    ids=["missing-token", "invalid-token"],
)
def test_get_jobs_rejects_invalid_auth(client, headers):
    response = client.get("/api/v1/jobs", headers=headers or {})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_get_jobs(client, db_session, auth_headers):
    job = create_job(db_session)
    headers = auth_headers()

    response = client.get("/api/v1/jobs", headers=headers)

    assert response.status_code == 200
    assert response.json()["jobs"] == [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
        }
    ]


def test_get_job(client, db_session, auth_headers):
    job = create_job(db_session)

    response = client.get(
        f"/api/v1/jobs/{job.id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": None,
        "url": job.url,
        "description": None,
        "source": job.source,
        "published_at": None,
    }


def test_get_job_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/jobs/999999",
        headers=auth_headers(),
    )

    assert response.status_code == 404

from fastapi.testclient import TestClient

from job_aggregator.api.dependencies import get_db
from job_aggregator.db.models.job import Job
from job_aggregator.main import app

client = TestClient(app)


def test_get_jobs(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    job = Job(
        title="Test Python Developer",
        company="Test Company",
        url="https://example.com/test-python-developer-2",
        source="test",
    )

    db_session.add(job)
    db_session.commit()

    response = client.get("/api/v1/jobs")
    assert response.status_code == 200

    response = client.get("/api/v1/jobs")

    assert response.status_code == 200

    data = response.json()

    assert data["jobs"] == [
        {
            "id": job.id,
            "title": "Test Python Developer",
            "company": "Test Company",
            "location": None,
            "work_mode": None,
        }
    ]

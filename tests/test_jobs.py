from fastapi.testclient import TestClient

from job_aggregator.api.dependencies import get_db
from job_aggregator.core.security import create_access_token
from job_aggregator.db.models.job import Job
from job_aggregator.db.models.user import User
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

    user = User(
        email="jobs-test@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))

    response = client.get("/api/v1/jobs", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    data = response.json()

    assert data["jobs"] == [
        {
            "id": job.id,
            "title": "Test Python Developer",
            "company": "Test Company",
            "location": None,
        }
    ]


def test_get_jobs_without_token():
    response = client.get("/api/v1/jobs")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_get_jobs_with_invalid_token():
    response = client.get(
        "/api/v1/jobs",
        headers={"Authorization": "Bearer definitely-not-a-valid-token"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_get_job(db_session):
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

    user = User(
        email="jobs-test@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))

    response = client.get(
        f"/api/v1/jobs/{job.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "id": job.id,
        "title": "Test Python Developer",
        "company": "Test Company",
        "location": None,
        "url": "https://example.com/test-python-developer-2",
        "description": None,
        "source": "test",
        "published_at": None,
    }


def test_get_job_not_found(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    user = User(
        email="jobs-test@example.com",
        hashed_password=None,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=str(user.id))

    response = client.get(
        "/api/v1/jobs/999999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_get_job_without_token():
    response = client.get("/api/v1/jobs/1")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

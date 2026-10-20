from fastapi.testclient import TestClient

from pydantic_settings import BaseSettings
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from job_aggregator.api.dependencies import get_db
from job_aggregator.db.models.job import Job
from job_aggregator.db.models.user import User
from job_aggregator.main import app


class TestSettings(BaseSettings):
    test_database_url: str

    model_config = {
        "env_file": ".env.test",
    }


settings = TestSettings()  # type: ignore[call-arg]

test_engine = create_engine(settings.test_database_url)

TestSessionLocal = sessionmaker[Session](bind=test_engine)


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.query(Job).delete()
        db.query(User).delete()
        db.commit()
        db.close()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

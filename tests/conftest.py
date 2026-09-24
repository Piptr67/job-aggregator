from pydantic_settings import BaseSettings
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from job_aggregator.db.models.job import Job
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
        db.commit()
        db.close()


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()

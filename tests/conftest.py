from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from job_aggregator.api.dependencies import get_db
from job_aggregator.core.config import settings
from job_aggregator.core.security import create_access_token
from job_aggregator.db.base import Base
from job_aggregator.db.models.job import Job
from job_aggregator.db.models.user import User
from job_aggregator.main import app


class TestSettings(BaseSettings):
    test_database_url: str

    model_config = {
        "env_file": ".env.test",
        "extra": "ignore",
    }


test_settings = TestSettings()  # type: ignore[call-arg]


def database_target(url: str) -> tuple[str | None, int | None, str | None]:
    parsed = make_url(url)
    return parsed.host, parsed.port, parsed.database


if database_target(test_settings.test_database_url) == database_target(
    settings.database_url
):
    raise RuntimeError(
        "TEST_DATABASE_URL points to the development database. "
        "Configure a separate test database before running tests."
    )


test_engine = create_engine(test_settings.test_database_url)
TestSessionLocal = sessionmaker(bind=test_engine, class_=Session)


def pytest_sessionstart(session: pytest.Session) -> None:
    Base.metadata.create_all(bind=test_engine)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    test_engine.dispose()


@pytest.fixture
def db_session() -> Iterator[Session]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.execute(delete(Job))
        db.execute(delete(User))
        db.commit()
        db.close()


@pytest.fixture(autouse=True)
def clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def create_user(db_session: Session):
    def _create_user(
        email: str = "jobs-test@example.com",
    ) -> User:
        user = User(
            email=email,
            hashed_password=None,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def auth_headers(create_user):
    def _auth_headers(email: str = "jobs-test@example.com") -> dict[str, str]:
        user = create_user(email=email)
        token = create_access_token(subject=str(user.id))
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def authenticated_headers(auth_headers):
    return auth_headers

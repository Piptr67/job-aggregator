from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion import service
from job_aggregator.ingestion.schemas import ParsedJob


def make_job(**overrides: Any) -> ParsedJob:
    data: dict[str, Any] = {
        "title": "Python Developer",
        "company": "Example Tech",
        "description": "Build Python applications.",
        "location": "Poland",
        "url": "https://example.com/python-developer",
        "source": "himalayas",
        "published_at": None,
    }
    data.update(overrides)
    return ParsedJob(**data)


def test_parsed_job_rejects_invalid_title():
    with pytest.raises(ValidationError):
        make_job(title="X" * 300)


def test_save_jobs(db_session):
    jobs = [
        make_job(url="https://example.com/python"),
        make_job(title="Backend Engineer", url="https://example.com/backend"),
    ]

    assert service.save_jobs(db_session, jobs) == 2
    assert set(db_session.scalars(select(Job.url))) == {
        "https://example.com/python",
        "https://example.com/backend",
    }


@pytest.mark.parametrize(
    ("source", "fetch_name", "parse_name", "fetch_result", "job_source", "base_url"),
    [
        (
            "himalayas",
            "fetch_feed",
            "parse_jobs",
            "<rss>dummy</rss>",
            "himalayas",
            "https://example.com/jobs",
        ),
        (
            "arbeitnow",
            "fetch_jobs",
            "parse_jobs",
            {"data": [{"title": "Python Developer"}]},
            "arbeitnow",
            "https://arbeitnow.com/jobs",
        ),
    ],
)
def test_ingest_source(
    db_session,
    monkeypatch,
    source,
    fetch_name,
    parse_name,
    fetch_result,
    job_source,
    base_url,
):
    from job_aggregator.ingestion import arbeitnow, himalayas

    parsed_jobs = [
        make_job(url=f"{base_url}/python-dev", source=job_source),
        make_job(
            title="Backend Engineer",
            company="Another Tech",
            location="Germany",
            url=f"{base_url}/backend-eng",
            source=job_source,
        ),
    ]

    source_module = {
        "himalayas": himalayas,
        "arbeitnow": arbeitnow,
    }[source]

    monkeypatch.setattr(source_module, fetch_name, lambda: fetch_result)
    monkeypatch.setattr(source_module, parse_name, lambda _: parsed_jobs)

    ingest = {
        "himalayas": service.ingest_himalayas,
        "arbeitnow": service.ingest_arbeitnow,
    }[source]

    assert ingest(db_session) == 2

    saved_jobs = db_session.scalars(select(Job)).all()
    assert len(saved_jobs) == 2
    assert {job.source for job in saved_jobs} == {job_source}

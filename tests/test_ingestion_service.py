import pytest
from pydantic import ValidationError
from sqlalchemy import select

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion import service
from job_aggregator.ingestion.schemas import ParsedJob
from job_aggregator.ingestion.service import (
    ingest_arbeitnow,
    ingest_himalayas,
    save_job,
)


def make_job(**overrides) -> ParsedJob:
    data = {
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


def test_save_job(db_session):
    parsed = make_job()

    job, inserted = save_job(db_session, parsed)

    assert inserted
    assert job.id is not None
    assert job.title == parsed.title
    assert job.company == parsed.company
    assert job.description == parsed.description
    assert job.location == parsed.location
    assert job.url == parsed.url
    assert job.source == parsed.source
    assert job.published_at is None


def test_save_job_duplicate_url(db_session):
    first, inserted_first = save_job(db_session, make_job())
    second, inserted_second = save_job(db_session, make_job())

    assert inserted_first and not inserted_second
    assert first.id == second.id
    assert db_session.scalar(select(Job.id)) == first.id


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
            "parse_himalayas_jobs",
            "<rss>dummy</rss>",
            "himalayas",
            "https://example.com/jobs",
        ),
        (
            "arbeitnow",
            "fetch_arbeitnow_jobs",
            "parse_arbeitnow_jobs",
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
    monkeypatch.setattr(service, fetch_name, lambda: fetch_result)
    monkeypatch.setattr(service, parse_name, lambda _: parsed_jobs)

    ingest = {
        "himalayas": ingest_himalayas,
        "arbeitnow": ingest_arbeitnow,
    }[source]

    assert ingest(db_session) == 2

    saved_jobs = db_session.scalars(select(Job)).all()
    assert len(saved_jobs) == 2
    assert {job.source for job in saved_jobs} == {job_source}

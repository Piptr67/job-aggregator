from datetime import datetime

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


def make_job(
    title: str = "Python Developer",
    company: str = "Example Tech",
    description: str | None = "Build Python applications.",
    location: str | None = "Poland",
    url: str = "https://example.com/python-developer",
    source: str = "himalayas",
    published_at: datetime | None = None,
) -> ParsedJob:
    return ParsedJob(
        title=title,
        company=company,
        description=description,
        location=location,
        url=url,
        source=source,
        published_at=published_at,
    )


def test_save_job(db_session):
    parsed_job = make_job()

    job, inserted = save_job(db_session, parsed_job)

    assert inserted is True
    assert job.id is not None
    assert job.title == "Python Developer"
    assert job.company == "Example Tech"
    assert job.description == "Build Python applications."
    assert job.location == "Poland"
    assert job.url == "https://example.com/python-developer"
    assert job.source == "himalayas"
    assert job.published_at is None


def test_save_job_duplicate_url(db_session):
    parsed_job = make_job()

    first_job, first_inserted = save_job(db_session, parsed_job)
    second_job, second_inserted = save_job(db_session, parsed_job)

    assert first_inserted is True
    assert second_inserted is False
    assert first_job.id == second_job.id

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 1


def test_parsed_job_rejects_invalid_title():
    with pytest.raises(ValidationError):
        make_job(title="X" * 300)


def test_save_jobs_skips_invalid_job(db_session):
    valid_job_1 = make_job(url="https://example.com/python")
    valid_job_2 = make_job(
        title="Backend Engineer",
        url="https://example.com/backend",
    )

    inserted_count = service.save_jobs(
        db_session,
        [valid_job_1, valid_job_2],
    )

    saved_jobs = db_session.scalars(select(Job)).all()

    assert inserted_count == 2
    assert len(saved_jobs) == 2
    assert {job.url for job in saved_jobs} == {
        "https://example.com/python",
        "https://example.com/backend",
    }


def test_ingest_himalayas(db_session, monkeypatch):
    feed = "<rss>dummy</rss>"

    parsed_jobs = [
        make_job(url="https://example.com/python-dev"),
        make_job(
            title="Backend Engineer",
            company="Another Tech",
            location="Germany",
            url="https://example.com/backend-eng",
        ),
    ]

    monkeypatch.setattr(service, "fetch_feed", lambda: feed)
    monkeypatch.setattr(service, "parse_himalayas_jobs", lambda _: parsed_jobs)

    job_count = ingest_himalayas(db_session)

    assert job_count == 2

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 2


def test_ingest_arbeitnow(db_session, monkeypatch):
    data = {"data": [{"title": "Python Developer"}]}

    parsed_jobs = [
        make_job(
            url="https://arbeitnow.com/jobs/python-dev",
            source="arbeitnow",
        ),
        make_job(
            title="Backend Engineer",
            company="Another Tech",
            location="Germany",
            url="https://arbeitnow.com/jobs/backend-eng",
            source="arbeitnow",
        ),
    ]

    monkeypatch.setattr(service, "fetch_arbeitnow_jobs", lambda: data)
    monkeypatch.setattr(service, "parse_arbeitnow_jobs", lambda _: parsed_jobs)

    job_count = ingest_arbeitnow(db_session)

    assert job_count == 2

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 2
    assert all(job.source == "arbeitnow" for job in jobs)

from sqlalchemy import select

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion import service
from job_aggregator.ingestion.service import (
    ingest_arbeitnow,
    ingest_himalayas,
    save_job,
)


def test_save_job(db_session):
    parsed_job: service.ParsedJob = {
        "title": "Python Developer",
        "company": "Example Tech",
        "description": "Build Python applications.",
        "location": "Poland",
        "url": "https://example.com/python-developer",
        "source": "himalayas",
        "published_at": None,
    }

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
    parsed_job: service.ParsedJob = {
        "title": "Python Developer",
        "company": "Example Tech",
        "description": "Build Python applications.",
        "location": "Poland",
        "url": "https://example.com/python-developer",
        "source": "himalayas",
        "published_at": None,
    }

    first_job, first_inserted = save_job(db_session, parsed_job)
    second_job, second_inserted = save_job(db_session, parsed_job)

    assert first_inserted is True
    assert second_inserted is False
    assert first_job.id == second_job.id

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 1


def test_save_jobs_skips_invalid_job(db_session, caplog):
    valid_job_1: service.ParsedJob = {
        "title": "Python Developer",
        "company": "Example Tech",
        "description": "Build Python applications.",
        "location": "Poland",
        "url": "https://example.com/python",
        "source": "himalayas",
        "published_at": None,
    }
    invalid_job = {
        **valid_job_1,
        "title": "X" * 300,
        "url": "https://example.com/invalid",
    }
    valid_job_2 = {
        **valid_job_1,
        "title": "Backend Engineer",
        "url": "https://example.com/backend",
    }

    inserted_count = service.save_jobs(
        db_session,
        [valid_job_1, invalid_job, valid_job_2],
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

    parsed_jobs: list[service.ParsedJob] = [
        {
            "title": "Python Developer",
            "company": "Example Tech",
            "description": "Build Python applications.",
            "location": "Poland",
            "url": "https://example.com/python-dev",
            "source": "himalayas",
            "published_at": None,
        },
        {
            "title": "Backend Engineer",
            "company": "Another Tech",
            "description": "Build backend systems.",
            "location": "Germany",
            "url": "https://example.com/backend-eng",
            "source": "himalayas",
            "published_at": None,
        },
    ]

    monkeypatch.setattr(service, "fetch_feed", lambda: feed)
    monkeypatch.setattr(service, "parse_himalayas_jobs", lambda _: parsed_jobs)

    job_count = ingest_himalayas(db_session)

    assert job_count == 2

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 2


def test_ingest_arbeitnow(db_session, monkeypatch):
    data = {"data": [{"title": "Python Developer"}]}

    parsed_jobs: list[service.ParsedJob] = [
        {
            "title": "Python Developer",
            "company": "Example Tech",
            "description": "Build Python applications.",
            "location": "Poland",
            "url": "https://arbeitnow.com/jobs/python-dev",
            "source": "arbeitnow",
            "published_at": None,
        },
        {
            "title": "Backend Engineer",
            "company": "Another Tech",
            "description": "Build backend systems.",
            "location": "Germany",
            "url": "https://arbeitnow.com/jobs/backend-eng",
            "source": "arbeitnow",
            "published_at": None,
        },
    ]

    monkeypatch.setattr(service, "fetch_arbeitnow_jobs", lambda: data)
    monkeypatch.setattr(service, "parse_arbeitnow_jobs", lambda _: parsed_jobs)

    job_count = ingest_arbeitnow(db_session)

    assert job_count == 2

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 2
    assert all(job.source == "arbeitnow" for job in jobs)

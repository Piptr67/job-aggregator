from sqlalchemy import select

from job_aggregator.ingestion import service
from job_aggregator.ingestion.service import ingest_himalayas, save_job
from job_aggregator.db.models.job import Job


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

    job = save_job(db_session, parsed_job)

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

    first_job = save_job(db_session, parsed_job)
    second_job = save_job(db_session, parsed_job)

    assert first_job.id == second_job.id

    jobs = db_session.scalars(select(Job)).all()

    assert len(jobs) == 1


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
    monkeypatch.setattr(service, "parse_jobs", lambda _: parsed_jobs)

    job_count = ingest_himalayas(db_session)

    assert job_count == 2

    jobs = db_session.scalars(select(Job)).all()
    assert len(jobs) == 2

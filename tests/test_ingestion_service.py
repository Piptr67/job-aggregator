from sqlalchemy import select

from job_aggregator.ingestion.himalayas import ParsedJob
from job_aggregator.ingestion.service import save_job
from job_aggregator.db.models.job import Job


def test_save_job(db_session):
    parsed_job: ParsedJob = {
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
    parsed_job: ParsedJob = {
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

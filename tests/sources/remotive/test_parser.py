import pytest

from exceptions import ParserError
from sources.remotive.parser import RemotiveParser


def test_parse_job():
    data = {
        "jobs": [
            {
                "title": "Backend Engineer",
                "description": "Python backend role",
                "url": "https://example.com/job",
                "publication_date": "2026-01-01T12:00:00",
                "company_name": "Acme Corp",
            }
        ]
    }

    parser = RemotiveParser()
    jobs = parser.parse(data)

    assert len(jobs) == 1

    job = jobs[0]

    assert job.title == "Backend Engineer"
    assert job.description == "Python backend role"
    assert job.link == "https://example.com/job"
    assert job.pub_date == "2026-01-01T12:00:00"
    assert job.company == "Acme Corp"


def test_parse_multiple_jobs():
    data = {
        "jobs": [
            {
                "title": "Backend Engineer",
                "description": "Python backend role",
                "url": "https://example.com/backend",
                "publication_date": "2026-01-01T12:00:00",
                "company_name": "Acme Corp",
            },
            {
                "title": "Frontend Engineer",
                "description": "React frontend role",
                "url": "https://example.com/frontend",
                "publication_date": "2026-01-02T12:00:00",
                "company_name": "Example Inc",
            },
        ]
    }

    parser = RemotiveParser()
    jobs = parser.parse(data)

    assert len(jobs) == 2

    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].company == "Acme Corp"
    assert jobs[0].link == "https://example.com/backend"

    assert jobs[1].title == "Frontend Engineer"
    assert jobs[1].company == "Example Inc"
    assert jobs[1].link == "https://example.com/frontend"


def test_parse_empty_jobs():
    data = {"jobs": []}

    parser = RemotiveParser()
    jobs = parser.parse(data)

    assert jobs == []


def test_parse_missing_jobs_key():
    data = {}

    parser = RemotiveParser()

    with pytest.raises(ParserError, match="Missing jobs data"):
        parser.parse(data)


def test_parse_job_missing_required_field():
    data = {
        "jobs": [
            {
                "description": "Python backend role",
                "url": "https://example.com/job",
                "publication_date": "2026-01-01T12:00:00",
                "company_name": "Acme Corp",
            }
        ]
    }

    parser = RemotiveParser()

    with pytest.raises(ParserError, match="Missing required job field"):
        parser.parse(data)

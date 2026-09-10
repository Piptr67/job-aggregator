import pytest

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
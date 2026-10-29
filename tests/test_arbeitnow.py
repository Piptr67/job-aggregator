from datetime import UTC, datetime

import pytest
import requests

from job_aggregator.ingestion import arbeitnow
from job_aggregator.ingestion.arbeitnow import parse_jobs


def test_parse_jobs():
    data = {
        "data": [
            {
                "title": "Python Developer",
                "company_name": "Example Tech",
                "description": "Python apps.",
                "location": "Poland",
                "url": "https://example.com/python-developer",
                "created_at": 1791474099,
            },
            {
                "title": "Backend Engineer",
                "company_name": "Another Tech",
                "description": "Backend systems.",
                "location": "Germany",
                "url": "https://example.com/backend-engineer",
                "created_at": 1791532800,
            },
        ]
    }

    jobs = parse_jobs(data)

    assert len(jobs) == 2

    job = jobs[0]

    assert job.title == "Python Developer"
    assert job.company == "Example Tech"
    assert job.location == "Poland"
    assert job.url == "https://example.com/python-developer"
    assert job.source == "arbeitnow"
    assert job.description == "Python apps."
    assert job.published_at == datetime.fromtimestamp(1791474099, tz=UTC)
    assert job.published_at.tzinfo is not None

    second_job = jobs[1]

    assert second_job.title == "Backend Engineer"
    assert second_job.company == "Another Tech"
    assert second_job.location == "Germany"
    assert second_job.url == "https://example.com/backend-engineer"
    assert second_job.source == "arbeitnow"
    assert second_job.description == "Backend systems."
    assert second_job.published_at == datetime.fromtimestamp(1791532800, tz=UTC)


def test_parse_jobs_skips_invalid_records():
    data = {
        "data": [
            {
                "title": "",
                "company_name": "Example Tech",
                "url": "https://example.com/invalid",
                "created_at": 1791474099,
            },
            {
                "title": "Valid Developer",
                "company_name": "Example Tech",
                "url": "https://example.com/valid",
                "created_at": 1791474099,
            },
        ]
    }

    jobs = parse_jobs(data)

    assert len(jobs) == 1
    assert jobs[0].title == "Valid Developer"


def test_fetch_jobs(monkeypatch):
    expected_data = {"data": [{"title": "Python Developer"}]}

    class FakeResponse:
        def json(self):
            return expected_data

        def raise_for_status(self):
            pass

    def fake_get(url, timeout):
        assert url == arbeitnow.settings.arbeitnow_json_url
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr(arbeitnow.requests, "get", fake_get)

    data = arbeitnow.fetch_jobs()

    assert data == expected_data


def test_fetch_jobs_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise requests.HTTPError("500 Server Error")

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(arbeitnow.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        arbeitnow.fetch_jobs()


def test_fetch_jobs_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise requests.Timeout("Request timed out")

    monkeypatch.setattr(arbeitnow.requests, "get", fake_get)

    with pytest.raises(requests.Timeout):
        arbeitnow.fetch_jobs()

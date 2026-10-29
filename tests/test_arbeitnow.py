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
    for job, expected in zip(jobs, data["data"], strict=True):
        assert job.title == expected["title"]
        assert job.company == expected["company_name"]
        assert job.description == expected["description"]
        assert job.location == expected["location"]
        assert job.url == expected["url"]
        assert job.source == "arbeitnow"
        assert job.published_at == datetime.fromtimestamp(
            expected["created_at"], tz=UTC
        )


def test_parse_jobs_skips_invalid_records():
    jobs = parse_jobs(
        {
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
    )

    assert [job.title for job in jobs] == ["Valid Developer"]


def test_fetch_jobs(monkeypatch):
    expected = {"data": [{"title": "Python Developer"}]}

    class FakeResponse:
        def json(self):
            return expected

        def raise_for_status(self):
            pass

    def fake_get(url, timeout):
        assert url == arbeitnow.settings.arbeitnow_json_url
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr(arbeitnow.requests, "get", fake_get)

    assert arbeitnow.fetch_jobs() == expected


@pytest.mark.parametrize(
    "error",
    [
        requests.HTTPError("500 Server Error"),
        requests.Timeout("Request timed out"),
    ],
    ids=["http-error", "timeout"],
)
def test_fetch_jobs_errors(monkeypatch, error):
    def fake_get(url, timeout):
        if isinstance(error, requests.HTTPError):

            class FakeResponse:
                def raise_for_status(self):
                    raise error

            return FakeResponse()
        raise error

    monkeypatch.setattr(arbeitnow.requests, "get", fake_get)

    with pytest.raises(type(error)):
        arbeitnow.fetch_jobs()

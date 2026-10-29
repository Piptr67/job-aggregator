import pytest
import requests

from job_aggregator.ingestion import himalayas
from job_aggregator.ingestion.errors import IngestionError
from job_aggregator.ingestion.himalayas import parse_jobs

FEED = """
<rss version="2.0"
    xmlns:himalayasJobs="https://himalayas.app/ns/jobs"
    xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel>
        <item>
            <title>Python Developer</title>
            <link>https://example.com/python-developer</link>
            <pubDate>Thu, 08 Oct 2026 15:41:39 GMT</pubDate>
            <himalayasJobs:companyName>Example Tech</himalayasJobs:companyName>
            <himalayasJobs:locationRestriction>Poland</himalayasJobs:locationRestriction>
            <content:encoded><![CDATA[Python apps.]]></content:encoded>
        </item>
        <item>
            <title>Backend Engineer</title>
            <link>https://example.com/backend-engineer</link>
            <pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate>
            <himalayasJobs:companyName>Another Tech</himalayasJobs:companyName>
            <himalayasJobs:locationRestriction>Germany</himalayasJobs:locationRestriction>
            <content:encoded><![CDATA[Backend systems.]]></content:encoded>
        </item>
    </channel>
</rss>
"""


def test_parse_jobs():
    jobs = parse_jobs(FEED)

    assert len(jobs) == 2
    assert jobs[0].model_dump() == {
        "title": "Python Developer",
        "company": "Example Tech",
        "location": "Poland",
        "url": "https://example.com/python-developer",
        "source": "himalayas",
        "description": "Python apps.",
        "published_at": jobs[0].published_at,
    }
    assert jobs[0].published_at.isoformat() == "2026-10-08T15:41:39+00:00"
    assert jobs[1].title == "Backend Engineer"
    assert jobs[1].company == "Another Tech"
    assert jobs[1].location == "Germany"
    assert jobs[1].url == "https://example.com/backend-engineer"
    assert jobs[1].published_at.isoformat() == "2026-10-09T10:00:00+00:00"


def test_parse_jobs_skips_invalid_records():
    feed = """
    <rss version="2.0" xmlns:himalayasJobs="https://himalayas.app/ns/jobs">
        <channel>
            <item><title></title><link>https://example.com/invalid</link></item>
            <item>
                <title>Valid Developer</title>
                <link>https://example.com/valid</link>
                <himalayasJobs:companyName>Example Tech</himalayasJobs:companyName>
            </item>
        </channel>
    </rss>
    """

    jobs = parse_jobs(feed)

    assert [job.title for job in jobs] == ["Valid Developer"]


def test_parse_jobs_missing_published_at():
    feed = """
    <rss version="2.0" xmlns:himalayas="https://himalayas.app/ns/jobs">
        <channel>
            <item>
                <title>Python Developer</title>
                <himalayas:companyName>Example Tech</himalayas:companyName>
                <link>https://example.com/python-developer</link>
            </item>
        </channel>
    </rss>
    """

    assert parse_jobs(feed)[0].published_at is None


class FakeResponse:
    text = "<rss>test feed</rss>"

    def raise_for_status(self):
        pass


def test_fetch_feed(monkeypatch):
    def fake_get(url, timeout):
        assert url == himalayas.settings.himalayas_rss_url
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr(himalayas.requests, "get", fake_get)

    assert himalayas.fetch_feed() == FakeResponse.text


@pytest.mark.parametrize(
    "error",
    [
        requests.HTTPError("500 Server Error"),
        requests.Timeout("Request timed out"),
    ],
)
def test_fetch_feed_errors(monkeypatch, error):
    def fake_get(url, timeout):
        raise error

    monkeypatch.setattr(himalayas.requests, "get", fake_get)

    with pytest.raises(IngestionError) as exc_info:
        himalayas.fetch_feed()

    assert isinstance(exc_info.value.__cause__, requests.RequestException)

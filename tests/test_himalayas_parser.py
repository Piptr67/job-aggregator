import pytest
from himalayas_parser import HimalayasParser


def test_parse_job():
    content = b"""
    <rss>
        <channel>
            <item>
                <title>Backend Engineer</title>
                <description>Python backend role</description>
                <link>https://example.com/job</link>
                <pubDate>Mon, 01 Jan 2026 12:00:00 GMT</pubDate>
                <himalayas:companyName
                    xmlns:himalayas="https://himalayas.app/ns/jobs"
                >Acme Corp</himalayas:companyName>
            </item>
        </channel>
    </rss>
    """

    parser = HimalayasParser()
    jobs = parser.parse(content)

    assert len(jobs) == 1

    job = jobs[0]

    assert job.title == "Backend Engineer"
    assert job.description == "Python backend role"
    assert job.link == "https://example.com/job"
    assert job.pub_date == "Mon, 01 Jan 2026 12:00:00 GMT"
    assert job.company == "Acme Corp"


def test_parse_malformed_xml():
    parser = HimalayasParser()
    content = b"<rss><channel>"

    with pytest.raises(ValueError, match="Malformed XML"):
        parser.parse(content)


def test_parse_skips_job_without_link():
    parser = HimalayasParser()

    content = b"""
    <rss>
        <channel>
            <item>
                <title>Backend Engineer</title>
                <description>Python backend role</description>
            </item>
        </channel>
    </rss>
    """

    jobs = parser.parse(content)

    assert jobs == []


def test_parse_missing_channel():
    parser = HimalayasParser()
    content = b"<rss></rss>"

    with pytest.raises(ValueError, match="RSS feed is missing channel"):
        parser.parse(content)


def test_parse_job_with_missing_optional_fields():
    parser = HimalayasParser()

    content = b"""
    <rss>
        <channel>
            <item>
                <link>https://example.com/job</link>
            </item>
        </channel>
    </rss>
    """

    jobs = parser.parse(content)

    assert len(jobs) == 1
    assert jobs[0].title == "Unknown"
    assert jobs[0].description == "Unknown"
    assert jobs[0].pub_date == "Unknown"
    assert jobs[0].company == "Unknown"


def test_parse_empty_feed():
    parser = HimalayasParser()

    content = b"""
    <rss>
        <channel>
        </channel>
    </rss>
    """

    jobs = parser.parse(content)

    assert jobs == []


def test_parse_empty_content():
    parser = HimalayasParser()

    with pytest.raises(ValueError, match="Malformed XML"):
        parser.parse(b"")


def test_parse_multiple_jobs_skips_invalid_job():
    parser = HimalayasParser()

    content = b"""
    <rss>
        <channel>
            <item>
                <title>Backend Engineer</title>
                <link>https://example.com/backend</link>
            </item>
            <item>
                <title>Missing Link Job</title>
            </item>
            <item>
                <title>Frontend Engineer</title>
                <link>https://example.com/frontend</link>
            </item>
        </channel>
    </rss>
    """

    jobs = parser.parse(content)

    assert len(jobs) == 2
    assert jobs[0].title == "Backend Engineer"
    assert jobs[1].title == "Frontend Engineer"
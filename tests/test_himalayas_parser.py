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
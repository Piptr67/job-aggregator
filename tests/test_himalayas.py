from job_aggregator.ingestion.himalayas import parse_jobs


def test_parse_jobs():
    feed = """\
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

    jobs = parse_jobs(feed)

    assert len(jobs) == 2

    job = jobs[0]

    assert job["title"] == "Python Developer"
    assert job["company"] == "Example Tech"
    assert job["location"] == "Poland"
    assert job["url"] == "https://example.com/python-developer"
    assert job["source"] == "himalayas"
    assert job["description"] == "Python apps."

    assert job["published_at"] is not None
    assert job["published_at"].year == 2026
    assert job["published_at"].month == 10
    assert job["published_at"].day == 8

    assert job["published_at"].hour == 15
    assert job["published_at"].minute == 41
    assert job["published_at"].second == 39
    assert job["published_at"].tzinfo is not None

    second_job = jobs[1]

    assert second_job["title"] == "Backend Engineer"
    assert second_job["company"] == "Another Tech"
    assert second_job["location"] == "Germany"
    assert second_job["url"] == "https://example.com/backend-engineer"

    assert second_job["published_at"] is not None
    assert second_job["published_at"].year == 2026
    assert second_job["published_at"].day == 9


def test_parse_published_at_missing():
    feed = """\
        <rss version="2.0">
            <channel>
                <item>
                    <title>Python Developer</title>
                    <link>https://example.com/python-developer</link>
                </item>
            </channel>
        </rss>
    """

    jobs = parse_jobs(feed)

    assert len(jobs) == 1
    assert jobs[0]["published_at"] is None

from database import get_jobs, init_db, save_jobs
from himalayas_parser import HimalayasParser


def test_parse_and_save_jobs(tmp_path):
    db_name = str(tmp_path / "test.db")

    content = b"""
    <rss>
        <channel>
            <item>
                <title>Backend Engineer</title>
                <description>Python backend role</description>
                <link>https://example.com/backend</link>
                <pubDate>Mon, 01 Jan 2026 12:00:00 GMT</pubDate>
                <himalayas:companyName
                    xmlns:himalayas="https://himalayas.app/ns/jobs"
                >Acme Corp</himalayas:companyName>
            </item>
            <item>
                <title>Frontend Engineer</title>
                <description>React frontend role</description>
                <link>https://example.com/frontend</link>
                <pubDate>Tue, 02 Jan 2026 12:00:00 GMT</pubDate>
                <himalayas:companyName
                    xmlns:himalayas="https://himalayas.app/ns/jobs"
                >Example Corp</himalayas:companyName>
            </item>
        </channel>
    </rss>
    """

    init_db(db_name)

    parser = HimalayasParser()
    jobs = parser.parse(content)

    inserted = save_jobs(jobs, db_name)
    saved_jobs = get_jobs(50, db_name)

    assert inserted == 2
    assert len(saved_jobs) == 2
    assert saved_jobs[0].title == "Frontend Engineer"
    assert saved_jobs[1].title == "Backend Engineer"
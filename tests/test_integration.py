from database import get_jobs, init_db, save_jobs
from sources.himalayas.parser import HimalayasParser
from sources.remotive.parser import RemotiveParser


def test_parse_and_save_himalayas_jobs(tmp_path):
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


def test_parse_and_save_remotive_jobs(tmp_path):
    db_name = str(tmp_path / "test.db")

    data = {
        "jobs": [
            {
                "title": "Backend Engineer",
                "description": "Python backend role",
                "url": "https://example.com/backend",
                "publication_date": "2026-01-01T12:00:00Z",
                "company_name": "Acme Corp",
            },
            {
                "title": "Frontend Engineer",
                "description": "React frontend role",
                "url": "https://example.com/frontend",
                "publication_date": "2026-01-02T12:00:00Z",
                "company_name": "Example Corp",
            },
        ]
    }

    init_db(db_name)

    parser = RemotiveParser()
    jobs = parser.parse(data)

    inserted = save_jobs(jobs, db_name)
    saved_jobs = get_jobs(50, db_name)

    assert inserted == 2
    assert len(saved_jobs) == 2
    assert saved_jobs[0].title == "Frontend Engineer"
    assert saved_jobs[1].title == "Backend Engineer"
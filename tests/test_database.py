from job import Job
from database import init_db, save_jobs, get_jobs, search_jobs

def test_save_jobs(tmp_path):
    db_name = str(tmp_path / "test.db")

    init_db(db_name)

    jobs = [
        Job(
            title="Backend Engineer",
            description="Python backend role",
            link="https://example.com/backend",
            pub_date="2026-01-01",
            company="Acme Corp",
        ),
        Job(
            title="Frontend Developer",
            description="React frontend role",
            link="https://example.com/frontend",
            pub_date="2026-01-02",
            company="DesignCo",
        ),
    ]

    inserted = save_jobs(jobs, db_name)

    assert inserted == 2

def test_save_jobs_ignores_duplicates(tmp_path):
    db_name = str(tmp_path / "test.db")

    init_db(db_name)

    job = Job(
        title="Backend Engineer",
        description="Python backend role",
        link="https://example.com/backend",
        pub_date="2026-01-01",
        company="Acme Corp",
    )

    first_insert = save_jobs([job], db_name)
    second_insert = save_jobs([job], db_name)

    assert first_insert == 1
    assert second_insert == 0

def test_get_jobs(tmp_path):
    db_name = str(tmp_path / "test.db")

    init_db(db_name)

    jobs = [
        Job(
            title="Backend Engineer",
            description="Python backend role",
            link="https://example.com/backend",
            pub_date="2026-01-01",
            company="Acme Corp",
        ),
        Job(
            title="Frontend Developer",
            description="React frontend role",
            link="https://example.com/frontend",
            pub_date="2026-01-02",
            company="DesignCo",
        ),
    ]

    save_jobs(jobs, db_name)

    saved_jobs = get_jobs(db_name=db_name)

    assert len(saved_jobs) == 2
    assert saved_jobs[0].title == "Frontend Developer"
    assert saved_jobs[1].title == "Backend Engineer"

def test_search_jobs(tmp_path):
    db_name = str(tmp_path / "test.db")

    init_db(db_name)

    jobs = [
        Job(
            title="Python Backend Engineer",
            description="Build APIs",
            link="https://example.com/python",
            pub_date="2026-01-01",
            company="Acme Corp",
        ),
        Job(
            title="Frontend Developer",
            description="Build React applications",
            link="https://example.com/frontend",
            pub_date="2026-01-02",
            company="DesignCo",
        ),
    ]

    save_jobs(jobs, db_name)

    results = search_jobs("python", db_name=db_name)

    assert len(results) == 1
    assert results[0].title == "Python Backend Engineer"
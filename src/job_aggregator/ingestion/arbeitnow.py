import requests

from datetime import datetime, timezone

from job_aggregator.ingestion.schemas import ParsedJob
from job_aggregator.core.config import settings


def fetch_jobs() -> dict:
    response = requests.get(settings.arbeitnow_json_url, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_jobs(data: dict) -> list[ParsedJob]:
    jobs = data["data"]

    parsed_jobs: list[ParsedJob] = []

    for job in jobs:
        parsed_job: ParsedJob = {
            "title": job["title"],
            "company": job["company_name"],
            "description": job["description"],
            "location": job["location"],
            "url": job["url"],
            "source": "arbeitnow",
            "published_at": datetime.fromtimestamp(
                job["created_at"],
                tz=timezone.utc,
            ),
        }

        parsed_jobs.append(parsed_job)

    return parsed_jobs

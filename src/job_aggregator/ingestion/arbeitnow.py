import requests

from datetime import datetime, timezone
from pydantic import ValidationError

from job_aggregator.ingestion.schemas import ParsedJob
from job_aggregator.core.config import settings


def fetch_jobs() -> dict:
    response = requests.get(settings.arbeitnow_json_url, timeout=10)
    response.raise_for_status()
    return response.json()


def parse_jobs(data: dict) -> list[ParsedJob]:
    jobs = data.get("data", [])
    parsed_jobs: list[ParsedJob] = []

    for job in jobs:
        try:
            parsed_job = ParsedJob(
                title=job.get("title"),
                company=job.get("company_name"),
                description=job.get("description"),
                location=job.get("location"),
                url=job.get("url"),
                source="arbeitnow",
                published_at=datetime.fromtimestamp(
                    job["created_at"],
                    tz=timezone.utc,
                ),
            )
        except (ValidationError, KeyError, TypeError, ValueError, OverflowError):
            continue

        parsed_jobs.append(parsed_job)

    return parsed_jobs

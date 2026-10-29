from datetime import UTC, datetime

import requests
from pydantic import ValidationError

from job_aggregator.core.config import settings
from job_aggregator.ingestion.errors import IngestionError
from job_aggregator.ingestion.schemas import ParsedJob


def fetch_jobs() -> dict:
    try:
        response = requests.get(settings.arbeitnow_json_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise IngestionError("Failed to fetch or decode Arbeitnow response") from exc

    if not isinstance(data, dict) or not isinstance(data.get("data", []), list):
        raise IngestionError("Invalid Arbeitnow response structure")

    return data


def parse_jobs(data: dict) -> list[ParsedJob]:
    if not isinstance(data, dict) or not isinstance(data.get("data", []), list):
        raise IngestionError("Invalid Arbeitnow response structure")

    parsed_jobs: list[ParsedJob] = []
    for job in data.get("data", []):
        if not isinstance(job, dict):
            continue
        title = job.get("title")
        company = job.get("company_name")
        url = job.get("url")
        if not isinstance(title, str) or not isinstance(company, str):
            continue
        if not isinstance(url, str):
            continue

        try:
            parsed_job = ParsedJob(
                title=title,
                company=company,
                description=job.get("description"),
                location=job.get("location"),
                url=url,
                source="arbeitnow",
                published_at=datetime.fromtimestamp(job["created_at"], tz=UTC),
            )
        except (ValidationError, KeyError, TypeError, ValueError, OverflowError):
            continue
        parsed_jobs.append(parsed_job)

    return parsed_jobs

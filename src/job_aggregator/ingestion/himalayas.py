from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
from defusedxml import ElementTree as ET
from pydantic import ValidationError

from job_aggregator.core.config import settings
from job_aggregator.ingestion.schemas import ParsedJob

NAMESPACES = {
    "himalayas": "https://himalayas.app/ns/jobs",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def fetch_feed() -> str:
    response = requests.get(settings.himalayas_rss_url, timeout=10)
    response.raise_for_status()
    return response.text


def parse_jobs(feed: str) -> list[ParsedJob]:
    root = ET.fromstring(feed)
    channel = root.find("channel")

    if channel is None:
        raise ValueError("RSS feed is missing channel")

    jobs: list[ParsedJob] = []

    for item in channel.findall("item"):
        title = item.findtext("title")
        company = item.findtext(
            "himalayas:companyName",
            namespaces=NAMESPACES,
        )
        url = item.findtext("link")

        if not title or not title.strip():
            continue
        if not company or not company.strip():
            continue
        if not url or not url.strip():
            continue

        try:
            job = ParsedJob(
                title=title,
                company=company,
                description=item.findtext(
                    "content:encoded",
                    namespaces=NAMESPACES,
                ),
                location=item.findtext(
                    "himalayas:locationRestriction",
                    namespaces=NAMESPACES,
                ),
                url=url,
                source="himalayas",
                published_at=parse_published_at(item.findtext("pubDate")),
            )
        except (ValidationError, TypeError, ValueError, OverflowError):
            continue

        jobs.append(job)

    return jobs


def parse_published_at(value: str | None) -> datetime | None:
    if value is None or not value.strip():
        return None

    return parsedate_to_datetime(value)

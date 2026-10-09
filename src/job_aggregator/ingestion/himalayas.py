import xml.etree.ElementTree as ET

from datetime import datetime
from email.utils import parsedate_to_datetime
import requests
from typing import TypedDict

from job_aggregator.core.config import settings

NAMESPACES = {
    "himalayas": "https://himalayas.app/ns/jobs",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def fetch_feed() -> str:
    response = requests.get(settings.himalayas_rss_url, timeout=10)
    response.raise_for_status()
    return response.text


def parse_feed(feed: str) -> ET.Element:
    return ET.fromstring(feed)


class ParsedJob(TypedDict):
    title: str | None
    company: str | None
    description: str | None
    location: str | None
    url: str | None
    source: str
    published_at: datetime | None


def parse_jobs(feed: str) -> list[ParsedJob]:
    root = parse_feed(feed)
    channel = root.find("channel")

    if channel is None:
        raise ValueError("RSS feed is missing channel")

    items = channel.findall("item")

    jobs: list[ParsedJob] = []

    for item in items:
        jobs.append(
            {
                "title": item.findtext("title"),
                "company": item.findtext(
                    "himalayas:companyName", namespaces=NAMESPACES
                ),
                "description": item.findtext("content:encoded", namespaces=NAMESPACES),
                "location": item.findtext(
                    "himalayas:locationRestriction", namespaces=NAMESPACES
                ),
                "url": item.findtext("link"),
                "source": "himalayas",
                "published_at": parse_published_at(item.findtext("pubDate")),
            }
        )

    return jobs


def parse_published_at(value: str | None) -> datetime | None:
    if value is None:
        return None

    return parsedate_to_datetime(value)

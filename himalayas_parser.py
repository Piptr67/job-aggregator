import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class HimalayasParser:
    def __init__(self):
        self.namespaces = {
            "himalayas": "https://himalayas.app/ns/jobs"
        }

    def parse(self, content: bytes) -> list[dict]:
        items = self._extract_items(content)

        jobs = []
        for item in items:
            try:
                jobs.append(self._item_to_job(item))
            except ValueError as e:
                logger.warning("Skipping item: %s", e)

        return jobs

    def _extract_items(self, content: bytes) -> list[ET.Element]:
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise ValueError(f"Malformed XML: {e}") from e

        channel = root.find("channel")
        if channel is None:
            raise ValueError("RSS feed is missing channel")

        return channel.findall("item")

    def _item_to_job(self, item: ET.Element) -> dict:
        link = item.findtext("link")

        if link is None:
            raise ValueError("Job is missing link")

        return {
            "title": item.findtext("title", default="Unknown"),
            "description": item.findtext("description", default="Unknown"),
            "link": link,
            "pubDate": item.findtext("pubDate", default="Unknown"),
            "company": item.findtext(
                "himalayas:companyName",
                default="Unknown",
                namespaces=self.namespaces,
            ),
        }
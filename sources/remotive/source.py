import logging

import requests

from exceptions import FetchError, ParserError
from job import Job
from sources.remotive.parser import RemotiveParser
from sources.source import Source

logger = logging.getLogger(__name__)

class RemotiveSource(Source):
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        self.parser = RemotiveParser()

    def fetch(self) -> list[Job]:
        try:
            response = self._fetch_url()
        except requests.RequestException as e:
            match e:
                case requests.HTTPError():
                    msg = f"Fetching failed for URL: {self.url}"
                case requests.Timeout():
                    msg = f"Fetching took too long for URL: {self.url}"
                case requests.ConnectionError():
                    msg = f"Could not reach the network for URL: {self.url}"
                case _:
                    msg = f"Unexpected request error for URL: {self.url}"
            logger.error("%s | Details: %s", msg, e)
            raise FetchError(msg) from e

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            msg = f"Invalid JSON response from URL: {self.url}"
            logger.error("%s | Details: %s", msg, e)
            raise FetchError(msg) from e

        try:
            return self.parser.parse(data)
        except ParserError as e:
            logger.error("Invalid job data from URL: %s: %s", self.url, e)
            raise

    def _fetch_url(self) -> requests.Response:
        res = requests.get(self.url, timeout=self.timeout)
        res.raise_for_status()
        return res
import logging
from abc import ABC, abstractmethod

import requests

from job import Job
from himalayas_parser import HimalayasParser
from exceptions import FetchError

logger = logging.getLogger(__name__)

class Source(ABC):
    @abstractmethod
    def fetch(self) -> list[Job]:
        pass

class HimalayasSource(Source):
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        self.parser = HimalayasParser()
        
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
            return self.parser.parse(response.content)
        except ValueError as e:
            logger.error("Invalid RSS feed from URL: %s: %s", self.url, e)
            return []
        
    def _fetch_url(self) -> requests.Response:
        res = requests.get(self.url, timeout=self.timeout)
        res.raise_for_status()
        return res
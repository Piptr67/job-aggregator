import logging
from abc import ABC, abstractmethod

import requests

from himalayas_parser import HimalayasParser


logger = logging.getLogger(__name__)

class Source(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        pass

class HimalayasSource(Source):
    def __init__(self, url: str):
        self.url = url
        self.parser = HimalayasParser()
        
    def fetch(self) -> list[dict]:
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
            logger.error(msg) 
            return []
        
        try:
            return self.parser.parse(response.content)
        except ValueError as e:
            logger.error("Invalid RSS feed from URL: %s: %s", self.url, e)
            return []
        
    def _fetch_url(self) -> requests.Response:
        res = requests.get(self.url, timeout=10)
        res.raise_for_status()
        return res

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    source = HimalayasSource("https://himalayas.app/jobs/rss")
    jobs = source.fetch()

    print(f"Fetched {len(jobs)} jobs")
    print(jobs[:1])
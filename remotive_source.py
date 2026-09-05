import requests

from job import Job
from source import Source

class RemotiveSource(Source):
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def fetch(self) -> list[Job]:
        response = self._fetch_url()
        data = response.json()

    def _fetch_url(self) -> requests.Response:
        res = requests.get(self.url, timeout=self.timeout)
        res.raise_for_status()
        return res
    
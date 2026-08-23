from abc import ABC, abstractmethod
import requests
import xml.etree.ElementTree as ET

namespaces = {"himalayas": "https://himalayas.app/ns/jobs"}

class Source(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]:
        pass

class HimalayasSource(Source):
    def __init__(self, url: str):
        self.url = url

    def fetch(self) -> list[dict]:
        try: 
            response = self.fetch_url()
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
            print(msg) 
            return []
    
        try:
            items = extract_items(response)
        except ET.ParseError:
            print(f"Could not parse XML from URL: {self.url}")
            return []
        except ValueError:
            print(f"Invalid RSS feed from URL: {self.url}")
            return []
    
        jobs = []
        for item in items:
            try:
                jobs.append(item_to_job(item))
            except ValueError as e:
                print(f"Skipping item: {e}")

        return jobs

    def fetch_url(self) -> requests.Response:
        res = requests.get(self.url, timeout=10)
        res.raise_for_status()
        return res

def extract_items(response: requests.Response) -> list[ET.Element]:
        root = ET.fromstring(response.content)

        channel = root.find("channel")
        if channel is None:
            raise ValueError("RSS feed is missing channel")
        return channel.findall("item")

def item_to_job(item: ET.Element) -> dict:
        link = item.findtext("link")

        if link is None:
            raise ValueError("Job is missing link")
        
        return  {
            "title": item.findtext("title", default="Unknown"),
            "description": item.findtext("description", default="Unknown"),
            "link": link,
            "pubDate": item.findtext("pubDate", default="Unknown"),
            "company": item.findtext(
                "himalayas:companyName",
                default="Unknown",
                namespaces=namespaces,
            ),
        } 
if __name__ == "__main__":
    source = HimalayasSource("https://himalayas.app/jobs/rss")
    jobs = source.fetch()

    print(f"Fetched {len(jobs)} jobs")
    print(jobs[:1])
import requests
import xml.etree.ElementTree as ET

namespaces = {"himalayas": "https://himalayas.app/ns/jobs"}

def fetch_url(url: str) -> requests.Response:
    return requests.get(url, timeout=10)

def extract_items(response: requests.Response) -> list[ET.Element]:
    root = ET.fromstring(response.text)
    return root.find("channel").findall("item")

def item_to_job(item: ET.Element) -> dict:
    return  {
        "title": item.findtext("title"),
        "description": item.findtext("description"),
        "link": item.findtext("link"),
        "pubDate": item.findtext("pubDate"),
        "company": item.findtext(
            "himalayas:companyName",
            namespaces=namespaces,
        ),
    } 

response = fetch_url("https://himalayas.app/jobs/rss")

jobs = [item_to_job(item) for item in extract_items(response)]
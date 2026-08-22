import requests
import xml.etree.ElementTree as ET

url = "https://himalayas.app/jobs/rss"
response = requests.get(url, timeout=10)

root = ET.fromstring(response.text)
channel = root.find("channel")
items = channel.findall("item")

namespaces = {"himalayas": "https://himalayas.app/ns/jobs"}

jobs = [
    {
        "title": item.findtext("title"),
        "description": item.findtext("description"),
        "link": item.findtext("link"),
        "pubDate": item.findtext("pubDate"),
        "company": item.findtext(
            "himalayas:companyName",
            namespaces=namespaces,
        ),
    } 
    for item in items
]
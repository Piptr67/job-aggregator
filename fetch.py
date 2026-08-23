import requests
import xml.etree.ElementTree as ET

namespaces = {"himalayas": "https://himalayas.app/ns/jobs"}

def fetch_url(url: str) -> requests.Response:
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res

def extract_items(response: requests.Response) -> list[ET.Element]:
    root = ET.fromstring(response.text)

    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS feed is missing channel")
    return channel.findall("item")

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

def main():
    url = "https://himalayas.app/jobs/rss"

    try:
        response = fetch_url(url)
    except requests.HTTPError:
        print(f"Fetching failed for URL: {url}")
        return
    except requests.Timeout:
        print(f"Fetching took too long for URL: {url}")
        return
    except requests.ConnectionError:
        print(f"Could not reach the network for URL: {url}")
        return
    except requests.RequestException:
        print(f"Unexpected request error for URL: {url}")
        return

    try:
        items = extract_items(response)
    except ET.ParseError:
        print(f"Could not parse XML from URL: {url}")
        return
    except ValueError:
        print(f"Invalid RSS feed from URL: {url}")
        return

    jobs = [item_to_job(item) for item in items]

if __name__ == "__main__":
    main()
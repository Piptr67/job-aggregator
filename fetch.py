import requests

url = "https://himalayas.app/jobs/rss"
response = requests.get(url, timeout=10)

print(response)
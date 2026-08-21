import requests
import re
from urllib.parse import urljoin

URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/"

print("=" * 60)
print("EFFIS RESOURCE TEST")
print("=" * 60)

response = requests.get(URL, timeout=60)

print("HTTP:", response.status_code)

html = response.text

print("=" * 60)
print("RESOURCE URLS")
print("=" * 60)

urls = re.findall(
    r'(?:src|href)=["\']([^"\']+)["\']',
    html,
    re.IGNORECASE
)

found = set()

for item in urls:
    full_url = urljoin(URL, item)

    if (
        ".js" in full_url.lower()
        or
        ".json" in full_url.lower()
        or
        "api" in full_url.lower()
        or
        "fdf" in full_url.lower()
        or
        "forecast" in full_url.lower()
    ):
        found.add(full_url)

for url in sorted(found):
    print(url)

print("=" * 60)
print("TOTAL:", len(found))
print("=" * 60)

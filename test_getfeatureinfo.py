import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/"

print("=" * 50)
print("EFFIS JAVASCRIPT FILES")
print("=" * 50)

response = requests.get(URL, timeout=60)

print("HTTP:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

for script in soup.find_all("script", src=True):
    url = urljoin(URL, script["src"])
    print(url)

print("=" * 50)
print("END")
print("=" * 50)

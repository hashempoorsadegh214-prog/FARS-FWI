import requests

URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/"

print("=" * 50)
print("EFFIS VIEWER TEST")
print("=" * 50)

response = requests.get(URL, timeout=60)

print("HTTP:", response.status_code)
print("CONTENT TYPE:", response.headers.get("content-type"))

print("=" * 50)
print("HTML")
print("=" * 50)

print(response.text[:20000])

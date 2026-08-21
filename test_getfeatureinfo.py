import requests
from datetime import datetime, timedelta, timezone

WMS_URL = "https://maps.effis.emergency.copernicus.eu/effis"

LAYER = "mf010.fwi"

LON = 52.5837
LAT = 29.5918

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

now = datetime.now(IRAN_TZ)
target = now.date() + timedelta(days=1)
target_date = target.strftime("%Y-%m-%d")

print("================================")
print("EFFIS GetFeatureInfo TEST")
print("================================")
print("Current Iran:", now.strftime("%Y-%m-%d %H:%M"))
print("Forecast:", target_date)
print("Layer:", LAYER)
print("Point:", LAT, LON)
print("================================")

params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetFeatureInfo",

    "LAYERS": LAYER,
    "QUERY_LAYERS": LAYER,

    "STYLES": "",
    "SRS": "EPSG:4326",

    "BBOX": "52.50,29.50,52.67,29.67",

    "WIDTH": "1000",
    "HEIGHT": "1000",

    "X": "492",
    "Y": "492",

    "INFO_FORMAT": "text/html",

    "FEATURE_COUNT": "10",

    "TIME": target_date
}

print("Requesting EFFIS...")

response = requests.get(
    WMS_URL,
    params=params,
    timeout=120
)

print("HTTP status:", response.status_code)
print(
    "Content-Type:",
    response.headers.get("Content-Type", "")
)

print("================================")
print("RAW RESPONSE")
print("================================")

print(response.text[:10000])

print("================================")
print("END TEST")
print("================================")

if response.status_code != 200:
    raise RuntimeError(
        f"EFFIS returned HTTP {response.status_code}"
    )

import requests
import math
from datetime import datetime, timedelta, timezone


WMS_URL = "https://maps.effis.emergency.copernicus.eu/gwis"

LAYER = "ecmwf.fwi"
QUERY_LAYER = "ecmwf.query"

LON = 52.5837
LAT = 29.5918

IRAN_TZ = timezone(
    timedelta(hours=3, minutes=30)
)

now = datetime.now(IRAN_TZ)
target = now.date() + timedelta(days=1)
target_date = target.strftime("%Y-%m-%d")


def lonlat_to_webmercator(lon, lat):

    x = lon * 20037508.34 / 180.0

    y = math.log(
        math.tan(
            math.radians(lat) / 2.0
            + math.pi / 4.0
        )
    )

    y = y * 20037508.34 / math.pi

    return x, y


x, y = lonlat_to_webmercator(
    LON,
    LAT
)

delta = 5000

bbox = (
    f"{x-delta},"
    f"{y-delta},"
    f"{x+delta},"
    f"{y+delta}"
)

print("=" * 60)
print("EFFIS ECMWF FWI QUERY TEST")
print("=" * 60)

print("Iran current:", now.strftime("%Y-%m-%d %H:%M"))
print("Forecast:", target_date)
print("Point:", LAT, LON)
print("Layer:", LAYER)
print("Query layer:", QUERY_LAYER)
print("CRS: EPSG:3857")

print("=" * 60)

params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetFeatureInfo",

    "LAYERS": LAYER,
    "QUERY_LAYERS": QUERY_LAYER,

    "STYLES": "",

    "SRS": "EPSG:3857",

    "BBOX": bbox,

    "WIDTH": "101",
    "HEIGHT": "101",

    "X": "50",
    "Y": "50",

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
    response.headers.get(
        "Content-Type",
        ""
    )
)

print("=" * 60)
print("RAW RESPONSE")
print("=" * 60)

print(
    response.text[:10000]
)

print("=" * 60)
print("END TEST")
print("=" * 60)

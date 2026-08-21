import requests
import math
from datetime import datetime, timedelta, timezone


WMS_URL = "https://maps.effis.emergency.copernicus.eu/gwis"

LON = 52.5837
LAT = 29.5918

WIDTH = 1000
HEIGHT = 1000

IRAN_TZ = timezone(
    timedelta(hours=3, minutes=30)
)

now = datetime.now(IRAN_TZ)
target = now.date() + timedelta(days=1)
target_date = target.strftime("%Y-%m-%d")


def lonlat_to_3857(lon, lat):

    x = lon * 20037508.34 / 180.0

    y = math.log(
        math.tan(
            math.radians(lat) / 2.0
            + math.pi / 4.0
        )
    )

    y = y * 20037508.34 / math.pi

    return x, y


x, y = lonlat_to_3857(
    LON,
    LAT
)

half_size = 50000

minx = x - half_size
maxx = x + half_size
miny = y - half_size
maxy = y + half_size

bbox = (
    f"{minx},"
    f"{miny},"
    f"{maxx},"
    f"{maxy}"
)

pixel_x = int(
    ((x - minx) / (maxx - minx)) * WIDTH
)

pixel_y = int(
    ((maxy - y) / (maxy - miny)) * HEIGHT
)


base = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetFeatureInfo",
    "QUERY_LAYERS": "ecmwf.query",
    "STYLES": "",
    "SRS": "EPSG:3857",
    "BBOX": bbox,
    "WIDTH": str(WIDTH),
    "HEIGHT": str(HEIGHT),
    "X": str(pixel_x),
    "Y": str(pixel_y),
    "INFO_FORMAT": "text/html",
    "FEATURE_COUNT": "10",
    "FORMAT": "image/png",
    "TRANSPARENT": "TRUE",
    "TIME": target_date
}


print("=" * 70)
print("EFFIS QUERY TEST")
print("=" * 70)
print("Point:", LAT, LON)
print("Forecast:", target_date)
print("BBOX:", bbox)
print("X:", pixel_x)
print("Y:", pixel_y)
print("=" * 70)


# ---------------------------------------------------------
# TEST 1
# ---------------------------------------------------------

params1 = dict(base)

params1["LAYERS"] = "ecmwf.fwi"

print("TEST 1")
print("LAYERS = ecmwf.fwi")
print("QUERY_LAYERS = ecmwf.query")
print("=" * 70)

r1 = requests.get(
    WMS_URL,
    params=params1,
    timeout=120
)

print("HTTP:", r1.status_code)
print("Content-Type:", r1.headers.get("Content-Type"))
print("URL:")
print(r1.url)

print("RESPONSE:")
print(r1.text[:10000])

print("=" * 70)


# ---------------------------------------------------------
# TEST 2
# ---------------------------------------------------------

params2 = dict(base)

params2["LAYERS"] = "ecmwf.query"
params2["QUERY_LAYERS"] = "ecmwf.query"

print("TEST 2")
print("LAYERS = ecmwf.query")
print("QUERY_LAYERS = ecmwf.query")
print("=" * 70)

r2 = requests.get(
    WMS_URL,
    params=params2,
    timeout=120
)

print("HTTP:", r2.status_code)
print("Content-Type:", r2.headers.get("Content-Type"))
print("URL:")
print(r2.url)

print("RESPONSE:")
print(r2.text[:10000])

print("=" * 70)
print("END")
print("=" * 70)

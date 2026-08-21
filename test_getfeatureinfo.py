import requests
import math
from datetime import datetime, timedelta, timezone


WMS_URL = "https://maps.effis.emergency.copernicus.eu/gwis"

LAYER = "ecmwf.fwi"
QUERY_LAYER = "ecmwf.query"

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


# محدوده بزرگ‌تر اطراف نقطه،
# برای شبیه‌سازی viewport نقشه Viewer
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


# مختصات نقطه داخل تصویر
pixel_x = int(
    ((x - minx) / (maxx - minx)) * WIDTH
)

pixel_y = int(
    ((maxy - y) / (maxy - miny)) * HEIGHT
)


print("=" * 70)
print("EFFIS VIEWER-STYLE GETFEATUREINFO TEST")
print("=" * 70)

print("Current Iran:", now.strftime("%Y-%m-%d %H:%M"))
print("Forecast:", target_date)
print("Point:", LAT, LON)
print("Layer:", LAYER)
print("Query layer:", QUERY_LAYER)
print("CRS: EPSG:3857")
print("BBOX:", bbox)
print("X:", pixel_x)
print("Y:", pixel_y)

print("=" * 70)


params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetFeatureInfo",

    "LAYERS": LAYER,
    "QUERY_LAYERS": QUERY_LAYER,

    "STYLES": "",

    "SRS": "EPSG:3857",

    "BBOX": bbox,

    "WIDTH": str(WIDTH),
    "HEIGHT": str(HEIGHT),

    "X": str(pixel_x),
    "Y": str(pixel_y),

    "INFO_FORMAT": "text/html",

    "TIME": target_date,

    "FEATURE_COUNT": "10",

    "FORMAT": "image/png",
    "TRANSPARENT": "TRUE"
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

print("Final URL:")
print(response.url)

print("=" * 70)
print("RAW RESPONSE")
print("=" * 70)

print(
    response.text[:20000]
)

print("=" * 70)
print("END TEST")
print("=" * 70)

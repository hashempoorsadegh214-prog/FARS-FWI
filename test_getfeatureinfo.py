import requests
import re

JS_URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/static/js/app.bundle-2.11.4.js"

print("=" * 60)
print("SEARCHING EFFIS VIEWER JAVASCRIPT")
print("=" * 60)

response = requests.get(JS_URL, timeout=120)

print("HTTP:", response.status_code)
print("SIZE:", len(response.text))

js = response.text

keywords = [
    "fdf_sources",
    "fdf_indexes",
    "selectedSource",
    "selectedIndex",
    "ecmwf",
    "mf010",
    "fire danger",
    "forecast"
]

for keyword in keywords:

    print("=" * 60)
    print("KEYWORD:", keyword)
    print("=" * 60)

    matches = list(
        re.finditer(
            re.escape(keyword),
            js,
            re.IGNORECASE
        )
    )

    print("FOUND:", len(matches))

    for match in matches[:10]:

        start = max(
            0,
            match.start() - 500
        )

        end = min(
            len(js),
            match.end() + 1000
        )

        print(js[start:end])
        print()

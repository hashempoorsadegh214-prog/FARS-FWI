import requests
import re

JS_URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/static/js/app.bundle-2.11.4.js"

response = requests.get(JS_URL, timeout=120)

print("=" * 70)
print("SEARCHING ECMWF FWI LAYER CONFIG")
print("=" * 70)

js = response.text

patterns = [
    "ecmwf_fwi",
    "ecmwf.fwi",
    "fdf.wms",
    "wms",
    "urlinfo",
    "url:",
    "layers:"
]

for pattern in patterns:

    print("=" * 70)
    print("PATTERN:", pattern)
    print("=" * 70)

    matches = list(
        re.finditer(
            re.escape(pattern),
            js,
            re.IGNORECASE
        )
    )

    print("FOUND:", len(matches))

    for match in matches[:8]:

        start = max(
            0,
            match.start() - 1500
        )

        end = min(
            len(js),
            match.end() + 3000
        )

        print(js[start:end])
        print("\n" + "-" * 30 + "\n")

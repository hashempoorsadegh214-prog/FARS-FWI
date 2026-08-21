import requests
import re

JS_URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/static/js/app.bundle-2.11.4.js"

response = requests.get(JS_URL, timeout=120)

print("=" * 60)
print("SEARCH FWI CONFIG")
print("=" * 60)

js = response.text

patterns = [
    r"ecmwf_indexes",
    r"fdf\s*:",
    r"fdf\s*=",
    r"sources\s*:",
    r"widgets\s*:",
]

for pattern in patterns:

    print("=" * 60)
    print("SEARCH:", pattern)
    print("=" * 60)

    matches = list(
        re.finditer(
            pattern,
            js,
            re.IGNORECASE
        )
    )

    print("FOUND:", len(matches))

    for match in matches[:5]:

        start = max(0, match.start() - 1000)
        end = min(len(js), match.end() + 2500)

        print(js[start:end])
        print()

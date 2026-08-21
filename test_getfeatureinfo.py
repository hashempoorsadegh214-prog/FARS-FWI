import requests
import re

JS_URL = "https://forest-fire.emergency.copernicus.eu/apps/gwis_current_situation/static/js/app.bundle-2.11.4.js"

response = requests.get(JS_URL, timeout=120)

js = response.text

print("=" * 70)
print("SEARCHING VIEWER QUERY FUNCTION")
print("=" * 70)

patterns = [
    "updateLayer:function",
    "updateLayer:",
    "GetFeatureInfo",
    "defaultlayerinfoparams",
    "info_layer",
    "query_proxy"
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

    for match in matches[:5]:

        start = max(0, match.start() - 2000)
        end = min(len(js), match.end() + 5000)

        print(js[start:end])
        print("\n" + "-" * 40 + "\n")

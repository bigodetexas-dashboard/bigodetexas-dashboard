import requests

urls = [
    "https://tiles.dayz.gg/chernarus/0/0/0.png",
    "https://tiles.dayz.gg/chernarus/1/0/0.png",
    "https://maps.izurvive.com/chernarusplussat/tiles/0/0/0.png",
    "https://maps.izurvive.com/chernarusplussat/0/0/0.png",
    "https://static.izurvive.com/maps/chernarusplussat/0/0/0.png",
    "https://static.izurvive.com/maps/chernarusplussat/tiles/0/0/0.png",
    "https://dayz.ginfo.gg/tiles/chernarusplus/0/0/0.png"
]

print("Testing Tile URLs...")
for url in urls:
    try:
        r = requests.head(url, timeout=2)
        print(f"{url}: {r.status_code}")
    except Exception as e:
        print(f"{url}: Error {e}")

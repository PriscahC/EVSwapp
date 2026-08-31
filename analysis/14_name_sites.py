import geopandas as gpd
import requests
import time

sites = gpd.read_file("data/processed/proposed_sites.geojson").to_crs(epsg=4326)

headers = {"User-Agent": "nairobi-emobility-hackathon/1.0 (I4C hackathon entry)"}

def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 16, "addressdetails": 1}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        addr = r.json().get("address", {})
        return (addr.get("suburb") or addr.get("neighbourhood") or addr.get("quarter")
                or addr.get("residential") or addr.get("village") or addr.get("town")
                or addr.get("road"))
    except Exception as e:
        print(f"  geocode failed for ({lat:.4f},{lon:.4f}): {e}")
        return None

names = []
for i, row in sites.iterrows():
    lon, lat = row.geometry.x, row.geometry.y
    name = reverse_geocode(lat, lon) or f"Site {row['rank']}"
    print(f"[{i+1}/{len(sites)}] rank {row['rank']}: {name}")
    names.append(name)
    time.sleep(1.1)  # Nominatim usage policy: max 1 req/sec

# de-duplicate (two sites can land in the same suburb)
seen, final_names = {}, []
for n in names:
    seen[n] = seen.get(n, 0) + 1
    final_names.append(n if seen[n] == 1 else f"{n} ({seen[n]})")

sites["site_name"] = final_names
sites.to_file("data/processed/proposed_sites.geojson", driver="GeoJSON")
print(sites[["rank", "site_name"]])
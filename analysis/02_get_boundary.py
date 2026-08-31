import osmnx as ox

place = "Nairobi, Kenya"
print(f"Fetching boundary for {place}...")
boundary = ox.geocode_to_gdf(place)

boundary.to_file("data/raw/nairobi_boundary.geojson", driver="GeoJSON")
print("Saved boundary to data/raw/nairobi_boundary.geojson")
print(boundary.total_bounds)  # sanity check: [minx, miny, maxx, maxy]
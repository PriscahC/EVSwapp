import osmnx as ox

# Nairobi, Kenya — bounding place query
place = "Nairobi, Kenya"

print(f"Downloading road network for {place}...")
G = ox.graph_from_place(place, network_type="drive")

# Convert to GeoDataFrames (nodes + edges) and save edges as our roads layer
nodes, edges = ox.graph_to_gdfs(G)

edges.to_file("data/raw/nairobi_roads.geojson", driver="GeoJSON")
print(f"Saved {len(edges)} road segments to data/raw/nairobi_roads.geojson")
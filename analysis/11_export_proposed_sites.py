import geopandas as gpd
import pandas as pd

hex_gdf = gpd.read_file("data/processed/nairobi_h3_grid.geojson")

TOP_N = 20
top = hex_gdf.nlargest(TOP_N, "need_score").copy()
top["rank"] = range(1, len(top) + 1)

# Recommendation logic: high peak transit frequency -> bus charging candidate
# (it's already a matatu corridor/interchange, buses serve it directly);
# lower transit frequency but still high need -> e-bike/motorcycle swap
# (residential demand not yet on a major transit corridor)
transit_threshold = hex_gdf["peak_transit_vph"].quantile(0.75)

def recommend(row):
    if row["peak_transit_vph"] >= transit_threshold:
        return "Bus charging depot (high-frequency transit corridor)"
    else:
        return "E-bike/motorcycle swap station (residential demand)"

top["recommended_infrastructure"] = top.apply(recommend, axis=1)

# Use hexagon centroid as the proposed site point
# top["geometry"] = top.geometry.centroid
# Calculate centroids in a projected CRS suitable for Nairobi
top_projected = top.to_crs(epsg=32737)  # WGS 84 / UTM zone 37S

top_projected["geometry"] = top_projected.geometry.centroid

# Convert centroid points back to WGS84 for GeoJSON / mapping
top = top_projected.to_crs(epsg=4326)


proposed = top[[
    "rank", "hex_id", "geometry", "population", "peak_transit_vph",
    "existing_coverage", "need_score", "recommended_infrastructure",
]]

proposed.to_file("data/processed/proposed_sites.geojson", driver="GeoJSON")

# Also a CSV for quick reading / dropping into the deck
proposed.drop(columns="geometry").to_csv("data/processed/proposed_sites.csv", index=False)

print(f"Exported {len(proposed)} proposed sites")
print(proposed.drop(columns="geometry")[["rank", "recommended_infrastructure", "population", "need_score"]].to_string(index=False))
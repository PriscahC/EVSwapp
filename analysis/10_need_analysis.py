import pandas as pd
import geopandas as gpd

hex_gdf = gpd.read_file("data/processed/nairobi_h3_grid.geojson")

# Make this script safe to re-run: drop any columns it computed on a previous run
computed_cols = [
    "existing_coverage", "peak_transit_vph", "pop_norm",
    "transit_norm", "coverage_norm", "demand_score", "need_score",
]
hex_gdf = hex_gdf.drop(columns=[c for c in computed_cols if c in hex_gdf.columns])

# --- Load charging infrastructure ---
charging = pd.read_csv("data/processed/nairobi_ev_charging_swap_infrastructure.csv")

# Exclude network_density rows (no real coordinates) from point-based coverage scoring
point_stations = charging[charging["data_layer"] == "point_station"].copy()
points_gdf = gpd.GeoDataFrame(
    point_stations,
    geometry=gpd.points_from_xy(point_stations.longitude, point_stations.latitude),
    crs="EPSG:4326",
)

# --- Spatial join: which hexagon is each station in? ---
joined = gpd.sjoin(points_gdf, hex_gdf[["hex_id", "geometry"]], how="inner", predicate="within")

# Existing coverage per hexagon = sum of priority_weight of stations inside it
coverage = joined.groupby("hex_id")["priority_weight"].sum().reset_index()
coverage.columns = ["hex_id", "existing_coverage"]

hex_gdf = hex_gdf.merge(coverage, on="hex_id", how="left")
hex_gdf["existing_coverage"] = hex_gdf["existing_coverage"].fillna(0)

# --- Build the need score ---
hex_gdf["peak_transit_vph"] = hex_gdf[["vph_am_peak", "vph_pm_peak"]].max(axis=1)

def normalize(col):
    return (col - col.min()) / (col.max() - col.min())

hex_gdf["pop_norm"] = normalize(hex_gdf["population"])
hex_gdf["transit_norm"] = normalize(hex_gdf["peak_transit_vph"])
hex_gdf["coverage_norm"] = normalize(hex_gdf["existing_coverage"])

hex_gdf["demand_score"] = 0.6 * hex_gdf["pop_norm"] + 0.4 * hex_gdf["transit_norm"]
hex_gdf["need_score"] = hex_gdf["demand_score"] * (1 - hex_gdf["coverage_norm"])

print(f"Total point_stations loaded: {len(points_gdf)}")
print(f"Stations successfully matched to a hexagon: {len(joined)}")
print(f"Hexagons with existing_coverage > 0: {(hex_gdf['existing_coverage'] > 0).sum()} of {len(hex_gdf)}")
print(hex_gdf[hex_gdf['existing_coverage'] > 0][['hex_id', 'existing_coverage']].head(10))
print()
print("Top 10 highest-need hexagons:")
print(hex_gdf.nlargest(10, "need_score")[
    ["hex_id", "population", "peak_transit_vph", "existing_coverage", "need_score"]
])

hex_gdf.to_file("data/processed/nairobi_h3_grid.geojson", driver="GeoJSON")
print("Saved need_score to nairobi_h3_grid.geojson")
import geopandas as gpd
import pandas as pd

hex_gdf = gpd.read_file("data/processed/nairobi_h3_grid.geojson")
stops = gpd.read_file("data/processed/nairobi_stop_frequency.geojson")

# Spatial join: which hexagon does each stop fall in?
joined = gpd.sjoin(stops, hex_gdf[["hex_id", "geometry"]], how="inner", predicate="within")

# Sum frequency across all stops within each hexagon, per time band
hex_transit = (
    joined.groupby("hex_id")[["vph_am_peak", "vph_midday", "vph_pm_peak"]]
    .sum()
    .reset_index()
)

hex_gdf = hex_gdf.merge(hex_transit, on="hex_id", how="left")
hex_gdf[["vph_am_peak", "vph_midday", "vph_pm_peak"]] = hex_gdf[
    ["vph_am_peak", "vph_midday", "vph_pm_peak"]
].fillna(0)

print(f"{(hex_gdf['vph_am_peak'] > 0).sum()} of {len(hex_gdf)} hexagons have transit stops")
print(hex_gdf.nlargest(5, "vph_am_peak")[["hex_id", "population", "vph_am_peak", "vph_pm_peak"]])

hex_gdf.to_file("data/processed/nairobi_h3_grid.geojson", driver="GeoJSON")
print("Updated nairobi_h3_grid.geojson with transit frequency columns")
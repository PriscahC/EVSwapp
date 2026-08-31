import pandas as pd
import geopandas as gpd

gtfs_dir = "data/raw/nairobi_gtfs"

stops = pd.read_csv(f"{gtfs_dir}/stops.txt")
stop_times = pd.read_csv(f"{gtfs_dir}/stop_times.txt")
freq = pd.read_csv(f"{gtfs_dir}/frequencies.txt")

# Which stops does each trip serve? (drop duplicate stop visits per trip)
trip_stops = stop_times[["trip_id", "stop_id"]].drop_duplicates()

# Attach frequency bands to each trip
trip_freq = trip_stops.merge(freq, on="trip_id", how="inner")

# vehicles per hour for this trip, in this time band
trip_freq["vph"] = 3600 / trip_freq["headway_secs"]

# Sum vehicles/hour across all trips serving each stop, per time band
stop_freq = (
    trip_freq.groupby(["stop_id", "start_time"])["vph"]
    .sum()
    .reset_index()
    .pivot(index="stop_id", columns="start_time", values="vph")
    .fillna(0)
    .reset_index()
)
stop_freq.columns = ["stop_id", "vph_am_peak", "vph_midday", "vph_pm_peak"]

# Attach coordinates and save as GeoDataFrame
stop_freq = stop_freq.merge(stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]], on="stop_id")
gdf = gpd.GeoDataFrame(
    stop_freq,
    geometry=gpd.points_from_xy(stop_freq.stop_lon, stop_freq.stop_lat),
    crs="EPSG:4326",
)

print(f"{len(gdf)} stops with frequency data")
print(gdf[["stop_name", "vph_am_peak", "vph_midday", "vph_pm_peak"]].sort_values("vph_am_peak", ascending=False).head(10))

gdf.to_file("data/processed/nairobi_stop_frequency.geojson", driver="GeoJSON")
print("Saved to data/processed/nairobi_stop_frequency.geojson")
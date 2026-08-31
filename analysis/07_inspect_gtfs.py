import pandas as pd

gtfs_dir = "data/raw/nairobi_gtfs"

stops = pd.read_csv(f"{gtfs_dir}/stops.txt")
trips = pd.read_csv(f"{gtfs_dir}/trips.txt")
freq = pd.read_csv(f"{gtfs_dir}/frequencies.txt")
routes = pd.read_csv(f"{gtfs_dir}/routes.txt")

print("STOPS:", stops.shape)
print(stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].head())
print()
print("ROUTES:", routes.shape)
print()
print("TRIPS:", trips.shape)
print(trips.head())
print()
print("FREQUENCIES:", freq.shape)
print(freq.head(10))
print()
print("Unique start_times in frequencies.txt (this tells us the time bands used):")
print(sorted(freq["start_time"].unique()))
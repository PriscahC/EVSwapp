import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

df = pd.read_csv("data/processed/nairobi_ev_charging_swap_infrastructure.csv")
df = df[df["geocode_status"].notna() & df["latitude"].notna() & df["longitude"].notna()]

gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])],
    crs="EPSG:4326",
)
gdf.to_file("data/processed/existing_infra.geojson", driver="GeoJSON")
print(f"Exported {len(gdf)} points")
import geopandas as gpd
from rasterstats import zonal_stats

hex_gdf = gpd.read_file("data/processed/nairobi_h3_grid.geojson")

print("Running zonal stats — this sums raster population values inside each hexagon...")
stats = zonal_stats(
    hex_gdf,
    "data/raw/ken_population_2020.tif",
    stats=["sum"],
    nodata=-99999,  # WorldPop's typical nodata value
)

hex_gdf["population"] = [s["sum"] if s["sum"] is not None else 0 for s in stats]

print(f"Total population across all hexagons: {hex_gdf['population'].sum():,.0f}")
print(f"Top 5 most populated hexagons:")
print(hex_gdf.nlargest(5, "population")[["hex_id", "population"]])

hex_gdf.to_file("data/processed/nairobi_h3_grid.geojson", driver="GeoJSON")
print("Updated data/processed/nairobi_h3_grid.geojson with population column")
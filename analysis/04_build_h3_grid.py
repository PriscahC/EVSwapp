import geopandas as gpd
import h3
from shapely.geometry import Polygon

RES = 8  # ~0.7 km² hexagons — right grain for city-scale siting

boundary = gpd.read_file("data/raw/nairobi_boundary.geojson")
geom = boundary.geometry.iloc[0]

def to_latlng_poly(polygon):
    exterior = [(lat, lng) for lng, lat in polygon.exterior.coords]
    holes = [[(lat, lng) for lng, lat in interior.coords] for interior in polygon.interiors]
    return h3.LatLngPoly(exterior, *holes)

polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)

cells = set()
for poly in polys:
    cells.update(h3.polygon_to_cells(to_latlng_poly(poly), RES))

print(f"Generated {len(cells)} H3 res-{RES} hexagons covering Nairobi")

records = []
for cell in cells:
    coords = h3.cell_to_boundary(cell)  # (lat, lng) pairs
    poly = Polygon([(lng, lat) for lat, lng in coords])
    records.append({"hex_id": cell, "geometry": poly})

hex_gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
hex_gdf.to_file("data/processed/nairobi_h3_grid.geojson", driver="GeoJSON")
print("Saved to data/processed/nairobi_h3_grid.geojson")
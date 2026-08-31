import geopandas as gpd
import pandas as pd

sites = gpd.read_file("data/processed/proposed_sites.geojson")            # from step 11
hexes_growth = gpd.read_file("data/processed/nairobi_h3_grid_with_growth.geojson")

# proposed_sites are hex centroids -> spatial-join back onto the hex they came from
sites = gpd.sjoin(
    sites,
    hexes_growth[["geometry", "growth_delta", "growth_norm", "cagr_2015_2020", "pilot_phase"]],
    how="left", predicate="within",
)

# need_score stays the primary driver (it dominates); growth_delta only
# breaks ties among similarly-ranked sites, consistent with the finding above
sites = sites.sort_values(["need_score", "growth_delta"], ascending=[False, False]).reset_index(drop=True)
sites["pilot_month_block"] = pd.cut(
    sites.index, bins=[-1, 6, 13, 19], labels=["Months 1-2", "Months 3-4", "Months 5-6"]
)

sites.to_file("data/processed/proposed_sites_phased.geojson", driver="GeoJSON")
print(sites[["rank", "recommended_infrastructure", "population", "need_score", "growth_delta", "pilot_month_block"]])
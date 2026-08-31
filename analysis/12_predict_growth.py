"""
12_predict_growth.py

Forecasts per-hexagon population growth using WorldPop's consistent
unconstrained annual series (2015 -> 2020), extrapolates to the pilot's
mid-2026 window, and produces a growth-informed 6-month pilot phasing.

Caveat for the deck: this is a 5-year trend extrapolation, not a
demographic microsimulation. It assumes recent growth patterns continue
and doesn't model migration shocks, new housing developments, or policy
change. Treat it as a phasing heuristic, not a hard population forecast.
"""

import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
from rasterstats import zonal_stats

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
RAW.mkdir(parents=True, exist_ok=True)

URLS = {
    2015: "https://data.worldpop.org/GIS/Population/Global_2000_2020/2015/KEN/ken_ppp_2015_UNadj.tif",
    2020: "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/KEN/ken_ppp_2020_UNadj.tif",
}


def download(year, url):
    dest = RAW / f"ken_ppp_{year}_UNadj_unconstrained.tif"
    if dest.exists():
        print(f"[skip] {dest} already exists")
        return dest
    print(f"Downloading {year} unconstrained population raster...")
    urllib.request.urlretrieve(url, dest)
    print(f"  -> saved to {dest}")
    return dest


def zonal_pop(hex_gdf, raster_path):
    stats = zonal_stats(hex_gdf, str(raster_path), stats="sum", nodata=-99999)
    return np.array([s["sum"] if s["sum"] is not None else 0.0 for s in stats])


def main():
    hexes = gpd.read_file(PROCESSED / "nairobi_h3_grid.geojson")
    # re-load population/need_score if they live in a separate processed file --
    # adjust this path if 10_need_analysis.py wrote them elsewhere
    if "population" not in hexes.columns or "need_score" not in hexes.columns:
        raise SystemExit("Run 05_add_population.py and 10_need_analysis.py first.")

    r2015 = download(2015, URLS[2015])
    r2020 = download(2020, URLS[2020])

    print("Zonal population sums, unconstrained 2015...")
    pop_2015 = zonal_pop(hexes, r2015)
    print("Zonal population sums, unconstrained 2020...")
    pop_2020_unc = zonal_pop(hexes, r2020)

    valid = pop_2015 > 10  # avoid divide-by-zero / noise on near-empty hexes
    cagr = np.full(len(hexes), np.nan)
    cagr[valid] = (pop_2020_unc[valid] / pop_2015[valid]) ** (1 / 5) - 1
    cagr = np.where(np.isnan(cagr), np.nanmedian(cagr), cagr)
    cagr = np.clip(cagr, -0.05, 0.15)  # sanity bound on per-hex growth

    years_forward = 2026.5 - 2020
    pop_2026_pred = hexes["population"].to_numpy() * (1 + cagr) ** years_forward
    growth_delta = pop_2026_pred - hexes["population"].to_numpy()

    hexes["cagr_2015_2020"] = cagr
    hexes["pop_2026_predicted"] = pop_2026_pred
    hexes["growth_delta"] = growth_delta
    hexes["growth_norm"] = (growth_delta - growth_delta.min()) / (
        growth_delta.max() - growth_delta.min()
    )

    need_t1, need_t2 = hexes["need_score"].quantile([1 / 3, 2 / 3])
    growth_t2 = hexes["growth_norm"].quantile(2 / 3)

    def phase(row):
        if row["need_score"] >= need_t2:
            return "Phase 1: needed now"
        if row["need_score"] >= need_t1 and row["growth_norm"] >= growth_t2:
            return "Phase 2: compounding demand"
        if row["growth_norm"] >= growth_t2:
            return "Phase 3: get ahead of growth"
        return "Not phased (low current + low growth)"

    hexes["pilot_phase"] = hexes.apply(phase, axis=1)

    out_path = PROCESSED / "nairobi_h3_grid_with_growth.geojson"
    hexes.to_file(out_path, driver="GeoJSON")
    print(f"Wrote {out_path}")
    print(hexes["pilot_phase"].value_counts())
    print("\nTop 10 hexagons by predicted growth (2020 -> mid-2026):")
    print(
        hexes.sort_values("growth_delta", ascending=False)
        .head(10)[["population", "need_score", "cagr_2015_2020", "growth_delta", "pilot_phase"]]
    )


if __name__ == "__main__":
    main()
import requests

url = "https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/2020/maxar_v1/KEN/ken_ppp_2020_UNadj_constrained.tif"
out_path = "data/raw/ken_population_2020.tif"

print("Downloading WorldPop Kenya population raster (~36 MB)...")
r = requests.get(url, stream=True)
r.raise_for_status()

with open(out_path, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"Saved to {out_path}")
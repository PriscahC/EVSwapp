import requests
import zipfile
import os

url = "https://gitlab.com/digitaltransport/data/africa/nairobi/-/raw/master/Data/GTFS.zip"
zip_path = "data/raw/nairobi_gtfs.zip"
extract_dir = "data/raw/nairobi_gtfs"

print("Downloading Nairobi GTFS feed...")
r = requests.get(url, stream=True)
r.raise_for_status()

with open(zip_path, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print("Extracting...")
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(extract_dir)

print("Files extracted:", os.listdir(extract_dir))
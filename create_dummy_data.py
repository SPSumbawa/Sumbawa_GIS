import os
import zipfile
import geopandas as gpd
from shapely.geometry import Polygon
import shutil

# Config
TARGET_DIR = r"D:\projek\Unduh_Persil\backend\data_shps"
NUM_FILES = 2

def create_dummy():
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR)

    for i in range(NUM_FILES):
        # Create some dummy rectangles
        # Coords around Sumbawa (approx Lat -8.5, Lon 117.4)
        lat_start = -8.5 + (i * 0.01)
        lon_start = 117.4 + (i * 0.01)
        
        polys = []
        nibs = []
        for j in range(5):
            poly = Polygon([
                (lon_start + j*0.001, lat_start),
                (lon_start + j*0.001 + 0.001, lat_start),
                (lon_start + j*0.001 + 0.001, lat_start + 0.001),
                (lon_start + j*0.001, lat_start + 0.001),
                (lon_start + j*0.001, lat_start)
            ])
            polys.append(poly)
            nibs.append(f"12345{i}{j}") # Dummy NIB

        gdf = gpd.GeoDataFrame({
            'NIB': nibs, 
            'Desa': [f'Desa_{i}']*5
        }, geometry=polys, crs="EPSG:4326")

        # Save to SHP temp
        shp_name = "persilunduh.shp"
        temp_dir = f"temp_{i}"
        os.makedirs(temp_dir, exist_ok=True)
        gdf.to_file(os.path.join(temp_dir, shp_name))

        # Zip it
        zip_name = os.path.join(TARGET_DIR, f"kecamatan_{i}.zip")
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            for f in os.listdir(temp_dir):
                zipf.write(os.path.join(temp_dir, f), arcname=f)
        
        # Cleanup temp
        shutil.rmtree(temp_dir)
        print(f"Created {zip_name}")

if __name__ == "__main__":
    create_dummy()

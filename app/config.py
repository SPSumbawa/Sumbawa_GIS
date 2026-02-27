import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folder containing ZIP files (SHP)
# For now, we point to a 'data' folder inside backend. 
# In production, change this to the NAS path e.g., r"\\192.168.1.x\Data"
DATA_DIR = os.path.join(BASE_DIR, "data_shps")

# Index file path (GeoPackage)
INDEX_FILE = os.path.join(BASE_DIR, "index.gpkg")

# Coordinate Systems
EPSG_WGS84 = "EPSG:4326"

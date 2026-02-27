import geopandas as gpd
import os
from app.config import INDEX_FILE

def diagnose():
    print(f"Checking {INDEX_FILE}...")
    if not os.path.exists(INDEX_FILE):
        print("Index file not found!")
        return

    try:
        # 1. Read Raw 1 row
        print("Reading 1st row...")
        gdf = gpd.read_file(INDEX_FILE, rows=1)
        print("Columns found:", list(gdf.columns))
        
        # 2. Test Filters
        print("\nTesting Filters...")
        
        # Check NIB column
        nib_col = None
        for c in gdf.columns:
            if c.upper() == 'NIB': nib_col = c
        
        print(f"NIB Column identified as: {nib_col}")
        
        # Check Desa Column
        desa_col = None
        for c in gdf.columns:
            if c.upper() in ['DESA', 'KELURAHAN']: 
                print(f"Found Potential Desa Column: {c}")
                desa_col = c

        if not nib_col:
            print("CRITICAL: No NIB column found!")
        else:
            print("SQL Test using pyogrio...")
            try:
                # Try SQL
                sql = f"SELECT * FROM persil WHERE {nib_col} IS NOT NULL LIMIT 1"
                gpd.read_file(INDEX_FILE, sql=sql, engine="pyogrio")
                print("SQL Query OK.")
            except Exception as e:
                print(f"SQL Fail: {e}")

    except Exception as e:
        print(f"Read Error: {e}")

if __name__ == "__main__":
    diagnose()

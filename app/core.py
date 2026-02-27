from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import os
import json
import glob
import shutil
import datetime
import geopandas as gpd
from shapely.geometry import Point, mapping
from pyproj import Transformer
from app.config import DATA_DIR, INDEX_FILE, EPSG_WGS84
from app.static_data import get_regions_hierarchy

router = APIRouter()

def get_all_zip_files(directory):
    return glob.glob(os.path.join(directory, "*.zip"))

@router.get("/refresh-index")
@router.post("/refresh-index")
async def refresh_index():
    """
    Scans DATA_DIR for .zip files containing 'persilunduh.shp', 
    merges them, reprojects to WGS84, and saves to a GeoPackage index.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        return {"status": "error", "message": f"Data directory not found. Created {DATA_DIR}."}

    zip_files = get_all_zip_files(DATA_DIR)
    if not zip_files:
        return {"status": "warning", "message": "No ZIP files found in data directory."}

    gdfs = []
    errors = []

    for zip_path in zip_files:
        try:
            # Read SHP from ZIP. 
            # Note: We assume the structure is flat or the SHP is discoverable.
            # Using 'zip://' + absolute path
            # We specifically look for the layer if multiple exist, or just read default.
            # User said: "Setiap zip berisi file SHP dengan nama yang sama (persilunduh.shp)"
            
            # Construct URI correctly for Windows: zip:///D:/path/to/file.zip
            # Geopandas uses fiona which handles zip:// paths.
            # On Windows, we need forward slashes for the URI usually.
            zip_uri = f"zip://{zip_path.replace(os.sep, '/')}"
            
            gdf = gpd.read_file(zip_uri)
            
            # Reproject to WGS84 if not already
            if gdf.crs is not None:
                if gdf.crs.to_string() != EPSG_WGS84:
                    gdf = gdf.to_crs(EPSG_WGS84)
            else:
                # Fallback: assume TM3-50.1 or we cannot process safely.
                # Ideally, the .prj file is in the zip.
                errors.append(f"{os.path.basename(zip_path)}: CRS not found")
                continue

            # Add source filename for tracking
            gdf['source_file'] = os.path.basename(zip_path)
            gdfs.append(gdf)

        except Exception as e:
            errors.append(f"{os.path.basename(zip_path)}: {str(e)}")

    if not gdfs:
        return {"status": "error", "message": "Failed to read any valid SHP files", "errors": errors}

    # Merge all
    full_gdf = gpd.pd.concat(gdfs, ignore_index=True)
    
    # Save to GeoPackage (Spatialite)
    # Using 'GPKG' driver
    try:
        full_gdf.to_file(INDEX_FILE, driver="GPKG", layer="persil")
    except Exception as e:
        return {"status": "error", "message": f"Failed to save index: {str(e)}"}

    return {
        "status": "success", 
        "total_files": len(zip_files),
        "total_records": len(full_gdf),
        "errors": errors
    }

@router.get("/search/radius")
def search_radius(
    lat: Optional[float] = None, 
    lon: Optional[float] = None,
    x: Optional[float] = None,
    y: Optional[float] = None,
    zone: Optional[str] = Query(None, description="TM3 Zone: 50.1 or 50.2"), 
    radius: float = Query(..., description="Radius in meters")
):
    """
    Search parcels within radius.
    Accepts either (lat, lon) OR (x, y, zone).
    """
    if not os.path.exists(INDEX_FILE):
        raise HTTPException(status_code=404, detail="Index not found. Run /refresh-index first.")

    # Handle Coordinate Input
    if x is not None and y is not None and zone is not None:
        # Convert TM3 -> WGS84
        # 50.1 = EPSG:23837, 50.2 = EPSG:23838
        epsg_source = "EPSG:23837" if "50.1" in zone else "EPSG:23838"
        transformer = Transformer.from_crs(epsg_source, EPSG_WGS84, always_xy=True)
        lon, lat = transformer.transform(x, y)
    
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Must provide (lat, lon) OR (x, y, zone)")

    # 1. Create Buffer/BBox in WGS84 (Rough approximation: 1 degree ~ 111km)
    # 0.001 degree ~ 100m. 
    # Safety margin: convert radius (m) to degrees roughly.
    buffer_deg = (radius / 111000.0) * 1.5 
    
    bbox = (
        lon - buffer_deg, 
        lat - buffer_deg, 
        lon + buffer_deg, 
        lat + buffer_deg
    )

    try:
        # Load only data in BBOX
        gdf = gpd.read_file(INDEX_FILE, bbox=bbox)
    except Exception as e:
        # If file is empty or other error
        return {"type": "FeatureCollection", "features": []}

    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}

    # 2. Precise Filter
    # Project to a metric CRS to calculate distance. 
    # Auto-estimate UTM zone or use Web Mercator (3857) for simplicity in distance calc
    # For high accuracy in Indonesia, TM3 is best, but 3857 is 'good enough' for radius check usually, 
    # or we construct a local orthopedic projection.
    # Let's use EPSG:3857 (Web Mercator) for distance filtering.
    
    center_point = Point(lon, lat)
    
    # Temporary Reprojection
    gdf_metric = gdf.to_crs(epsg=3857)
    center_metric = gpd.GeoSeries([center_point], crs=EPSG_WGS84).to_crs(epsg=3857).iloc[0]
    
    # Calculate distance
    gdf_metric['distance'] = gdf_metric.geometry.distance(center_metric)
    
    # Filter
    result_gdf = gdf_metric[gdf_metric['distance'] <= radius]
    
    # Return to WGS84 for GeoJSON output
    final_gdf = result_gdf.to_crs(EPSG_WGS84)
    
    return final_gdf.__geo_interface__

@router.get("/search/nib")
def search_nib(nib: str = Query(..., description="NIB to search"), desa: Optional[str] = Query(None, description="Nama Desa/Kelurahan filter")):
    if not os.path.exists(INDEX_FILE):
        raise HTTPException(status_code=404, detail="Index not found. Run /refresh-index first.")

    try:
        file_layer = "persil"
        gdf = gpd.GeoDataFrame() # Initialize empty
        
        # 1. Load by NIB (SQL)
        # Using simplified query to avoid syntax errors
        sql = f"SELECT * FROM {file_layer} WHERE NIB = '{nib}'"
        
        try:
             # Try fast SQL load
             gdf = gpd.read_file(INDEX_FILE, sql=sql, engine="pyogrio")
        except Exception as sql_ex:
             print(f"SQL Read Failed: {sql_ex}. Trying fallback...")
             try:
                 # Fallback: Read full file (slow)
                 gdf = gpd.read_file(INDEX_FILE)
                 
                 # Manual Filter NIB
                 # Check column existence case-insensitive
                 nib_col = None
                 for c in gdf.columns:
                     if c.upper() == 'NIB':
                         nib_col = c
                         break
                 
                 if nib_col:
                     gdf = gdf[gdf[nib_col] == nib]
                 else:
                     print("Warning: NIB column not found in fallback read.")
                     gdf = gpd.GeoDataFrame() # Empty
             except Exception as fb_ex:
                 print(f"Fallback Read Failed: {fb_ex}")
                 # If both fail, return empty or raise?
                 # Return empty to communicate 'not found' instead of crash
                 return {"type": "FeatureCollection", "features": []}

        if gdf.empty:
             return {"type": "FeatureCollection", "features": []}

        # 2. Filter by KELURAHAN
        if desa:
            try:
                d_upper = desa.strip().upper()
                col_map = {c.upper(): c for c in gdf.columns}
                
                if 'KELURAHAN' in col_map:
                    real_col = col_map['KELURAHAN']
                    gdf = gdf[gdf[real_col].fillna('').astype(str).str.upper() == d_upper]
                elif 'DESA' in col_map: # Fallback check for DESA column too
                    real_col = col_map['DESA']
                    gdf = gdf[gdf[real_col].fillna('').astype(str).str.upper() == d_upper]
            except Exception as filter_ex:
                print(f"Filter Error: {filter_ex}")
                # Don't crash on filter error, just return current result (or handle accordingly)
                # For safety, let's just proceed with NIB filtered results
                pass

        if gdf.empty:
             return {"type": "FeatureCollection", "features": []}
             
        if gdf.crs and gdf.crs.to_string() != EPSG_WGS84:
            gdf = gdf.to_crs(EPSG_WGS84)
        
        # Ensure result is valid JSON
        return json.loads(gdf.to_json())

    except Exception as e:
         import traceback
         traceback.print_exc() # Print full trace to console
         print(f"Error in search_nib: {str(e)}")
         raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}
        
    return gdf.__geo_interface__

@router.get("/regions")
def get_regions():
    """
    Get list of Kecamatan and Desa.
    """
    return get_regions_hierarchy()

import requests
import json

BASE_URL = "http://localhost:8000/api"

def refresh_and_check():
    print("Refreshing index...")
    try:
        # Refresh
        resp = requests.post(f"{BASE_URL}/refresh-index")
        print("Refresh Result:", json.dumps(resp.json(), indent=2))
        
        # Check static regions vs loaded data?
        # The index stores 'source_file'. 
        # We don't have an endpoint to list all index contents, but the refresh result returns file count.
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    refresh_and_check()

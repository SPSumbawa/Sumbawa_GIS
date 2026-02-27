import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_test():
    print("1. Testing Refresh Index...")
    try:
        resp = requests.post(f"{BASE_URL}/refresh-index")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 200:
            return False
    except Exception as e:
        print(f"Failed: {e}")
        return False
    
    time.sleep(1) # Wait for index write
    
    print("\n2. Testing Search Radius...")
    # Dummy data created at Lat -8.5, Lon 117.4
    resp = requests.get(f"{BASE_URL}/search/radius", params={"lat": -8.5, "lon": 117.4, "radius": 500})
    data = resp.json()
    print(f"Found features: {len(data.get('features', []))}")
    if len(data.get('features', [])) == 0:
        print("Expected features but got none!")
        return False
        
    print("\n3. Testing Search NIB...")
    # Dummy NIB: 1234500
    resp = requests.get(f"{BASE_URL}/search/nib", params={"nib": "1234500"})
    data = resp.json()
    print(f"Found features: {len(data.get('features', []))}")
    if len(data.get('features', [])) == 0:
        print("Expected features but got none!")
        return False
    
    return True

if __name__ == "__main__":
    if run_test():
        print("\nALL TESTS PASSED")
    else:
        print("\nTESTS FAILED")

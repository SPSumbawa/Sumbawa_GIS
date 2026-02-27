import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_regions():
    print("Testing /regions endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/regions")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Got data for {len(data)} sub-districts.")
            if "Alas" in data:
                print("Validation: 'Alas' found.")
                return True
            else:
                print("Validation: 'Alas' NOT found.")
                return False
        else:
            print(f"Error: {resp.text}")
            return False
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_regions()

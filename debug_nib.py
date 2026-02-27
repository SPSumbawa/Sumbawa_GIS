import requests
import json

BASE_URL = "http://localhost:8000/api"

def debug_search(nib, desa):
    print(f"Testing Search: NIB={nib}, Desa={desa}")
    url = f"{BASE_URL}/search/nib"
    params = {"nib": nib, "desa": desa}
    
    try:
        resp = requests.get(url, params=params)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Success!")
            # print(resp.json()) 
        else:
            print("Response Text:")
            print(resp.text)
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    # Ganti nilai ini dengan data sampel yang user coba
    # Saya pakai dummy dulu atau coba nilai umum
    debug_search("12345", "TEST_DESA") 

import requests

try:
    print("Testing GET /refresh-index...")
    resp = requests.get("http://localhost:8000/api/refresh-index")
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text[:100]}...")
except Exception as e:
    print(f"Error: {e}")

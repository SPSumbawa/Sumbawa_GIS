import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def refresh_data():
    print("="*40)
    print("      SUMBAWA GIS DATA REFRESHER      ")
    print("="*40)
    print("Menghubungi Server API...")
    
    try:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/refresh-index")
        
        if resp.status_code == 200:
            data = resp.json()
            print("\nSUKSES! Data berhasil diperbarui.")
            print(f"Total File ZIP ditemukan : {data.get('total_files', 0)}")
            print(f"Total Bidang Persil      : {data.get('total_records', 0)}")
            
            errors = data.get('errors', [])
            if errors:
                print("\nPERINGATAN: Ada beberapa file yang gagal diproses:")
                for err in errors:
                    print(f" - {err}")
        else:
            print(f"\nGAGAL. Status Code: {resp.status_code}")
            print(resp.text)
            
        print(f"\nWaktu proses: {time.time() - start_time:.2f} detik")

    except Exception as e:
        print("\nERROR: Tidak dapat menghubungi server.")
        print("Pastikan 'run_server.bat' sudah dijalankan sebelumnya.")
        print(f"Detail: {e}")

    print("\nTekan Enter untuk keluar...")
    input()

if __name__ == "__main__":
    refresh_data()

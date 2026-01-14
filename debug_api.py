import requests
import sys

def check_backend():
    print("Checking Backend connectivity (http://localhost:8000)...")
    try:
        r = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Backend is UP (Status: {r.status_code})")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"❌ Backend is DOWN: {e}")
        return False
    
    print("\nChecking KPI Analytics endpoint...")
    try:
        r = requests.get("http://localhost:8000/api/v1/kpis/overview", timeout=5)
        if r.status_code == 200:
            print("✅ KPI Data is available!")
            print(f"Sample Data: {r.json()}")
        else:
            print(f"⚠️ API returned {r.status_code}. Data probably still loading.")
    except Exception as e:
        print(f"❌ API Error: {e}")
    
    return True

if __name__ == "__main__":
    check_backend()

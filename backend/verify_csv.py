import os
import sys
import time
import httpx

API_URL = "http://127.0.0.1:8000/api/v1"
CSV_PATH = "/Users/anujsule/Downloads/NATWEST/bank_transactions_data_2 (1).csv"

def run_test():
    with httpx.Client(timeout=120) as client:
        print("1. Registering test user...")
        res = client.post(f"{API_URL}/auth/register", json={
            "email": "testuser_demo2@natwest.com",
            "password": "password123",
            "full_name": "Test User"
        })
        if res.status_code == 400 and "already registered" in res.text:
            print("User already exists, proceeding to login.")
        else:
            res.raise_for_status()
            
        print("2. Logging in...")
        res = client.post(f"{API_URL}/auth/login", json={
            "email": "testuser_demo2@natwest.com",
            "password": "password123"
        })
        res.raise_for_status()
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"3. Uploading {CSV_PATH}...")
        with open(CSV_PATH, "rb") as f:
            files = {"file": ("bank_transactions.csv", f, "text/csv")}
            res = client.post(f"{API_URL}/datasets/upload", headers=headers, files=files)
            
        print("Upload Response:", res.status_code, res.text)
        res.raise_for_status()
        
        dataset_id = res.json()["id"]
        print(f"4. Processing Dataset {dataset_id}...")
        
        ready = False
        for _ in range(30):
            res = client.get(f"{API_URL}/datasets/{dataset_id}", headers=headers)
            status = res.json()["status"]
            print(f"   Status: {status}")
            if status == "ready":
                ready = True
                break
            elif status == "failed":
                print("Processing failed!", res.text)
                sys.exit(1)
            time.sleep(1)
            
        if not ready:
            print("Processing timed out.")
            sys.exit(1)
            
        print("5. Running Query...")
        res = client.post(f"{API_URL}/queries/{dataset_id}", headers=headers, json={
            "question": "What is the total transaction amount?"
        })
        res.raise_for_status()
        print("\n=== SUCCESS ===")
        print("Query Answer:", res.json().get("answer"))
        print("SQL Executed:", res.json().get("sql_executed"))

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)

import requests
import time
import os

BASE_URL = "http://localhost:8000/api/v1"

def run_flow():
    print("=== End-to-End Flow Validation ===")
    session = requests.Session()
    
    # 1. Register / Login
    email = "e2e_autotest@example.com"
    pw = "Password123!"
    
    print("1. Registering...")
    res = session.post(f"{BASE_URL}/auth/register", json={
        "email": email, "password": pw, "full_name": "E2E Test User"
    })
    # Ignore 400 if already exists
    
    print("2. Logging in...")
    res = session.post(f"{BASE_URL}/auth/login", json={
        "email": email, "password": pw
    })
    res.raise_for_status()
    tokens = res.json()
    token = tokens["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get /auth/me
    print("3. Validating /auth/me...")
    res = session.get(f"{BASE_URL}/auth/me", headers=headers)
    res.raise_for_status()
    print("   Welcome,", res.json()["full_name"])
    
    # 4. List Datasets
    print("4. Listing datasets...")
    res = session.get(f"{BASE_URL}/datasets/", headers=headers)
    res.raise_for_status()
    print("   Datasets found:", len(res.json()))
    
    # 5. Upload Dataset
    file_path = r"C:\Users\Hritesh\Downloads\bank_transactions_data_2.csv"
    if not os.path.exists(file_path):
        print(f"ERROR: Dataset not found at {file_path}")
        return
        
    print(f"5. Uploading dataset: {file_path}...")
    with open(file_path, "rb") as f:
        files = {"file": ("bank_transactions_data_2.csv", f, "text/csv")}
        data = {"name": "End to End Test Dataset", "description": "Testing the flow"}
        res = session.post(f"{BASE_URL}/datasets/upload", headers=headers, files=files, data=data)
        
    res.raise_for_status()
    dataset_id = res.json()["dataset_id"]
    print(f"   Uploaded! Dataset ID: {dataset_id}")
    
    # 6. Poll for status
    print("6. Waiting for processing to complete...")
    for i in range(30):
        # The GET endpoint is /datasets/{id}
        res = session.get(f"{BASE_URL}/datasets/{dataset_id}", headers=headers)
        res.raise_for_status()
        status = res.json()["status"]
        print(f"   Status: {status}")
        
        if status == "ready":
            print("   Processing completed successfully!")
            break
        elif status == "failed":
            print(f"   ERROR: Processing failed: {res.json().get('error')}")
            return
            
        time.sleep(2)
    else:
        print("   ERROR: Processing timed out!")
        return
        
    # 7. Ask a Question
    print("7. Querying the dataset...")
    q = "What is the total transaction amount by category?"
    print(f"   Question: {q}")
    
    res = session.post(f"{BASE_URL}/queries/{dataset_id}", headers=headers, json={"question": q})
    try:
        res.raise_for_status()
        answer = res.json()
        print("\n=== AI ANSWER ===")
        print(answer.get("answer"))
        print("\n=== CHART SPEC ===")
        print(answer.get("chart_spec"))
        print("\n=== SQL EXECUTED ===")
        print(answer.get("sql_executed"))
        print("=================")
    except Exception as e:
        print("ERROR Querying:", e)
        print("Response:", res.text)

if __name__ == "__main__":
    run_flow()

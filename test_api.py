import requests
import json

try:
    print("Testing /api/v1/health...")
    r = requests.get("http://localhost:8000/api/v1/health")
    print(f"Status: {r.status_code}")
    print(f"Headers: {r.headers}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Error connecting: {e}")

try:
    print("\nTesting root /...")
    r = requests.get("http://localhost:8000/")
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Error connecting: {e}")

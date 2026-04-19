import asyncio
import os
from httpx import AsyncClient

async def run():
    # Attempt to login using the test account from earlier
    async with AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as client:
        # Login
        response = await client.post("/auth/login", json={
            "email": "test58@example.com",
            "password": "password123"
        })
        if response.status_code != 200:
            print("Login failed:", response.text)
            return

        token = response.json().get("access_token")
        
        # Upload a dummy CSV file
        headers = {"Authorization": f"Bearer {token}"}
        # A simple CSV payload
        files = {
            "file": ("test.csv", b"id,name\n1,Alice\n2,Bob", "text/csv")
        }
        data = {
            "name": "Dummy Test Dataset",
            "description": "Mock dataset"
        }
        
        print("Uploading...")
        upload_response = await client.post("/datasets/upload", headers=headers, files=files, data=data)
        print("Upload Response:", upload_response.status_code)
        try:
            print(upload_response.json())
        except Exception:
            print(upload_response.text)

if __name__ == "__main__":
    asyncio.run(run())

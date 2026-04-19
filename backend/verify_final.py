import asyncio
import uuid
import json
from sqlalchemy import text, select
from app.database import async_session_factory
from app.models.user import User

async def verify_final():
    email = f"final_test_{uuid.uuid4().hex[:6]}@example.com"
    pw = "password"
    
    async with async_session_factory() as db:
        # 1. Manually insert a user with hex ID
        uid = uuid.uuid4()
        hex_id = uid.hex
        print(f"Testing with User ID: {uid} (Hex: {hex_id})")
        
        await db.execute(text(
            "INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, created_at, updated_at) "
            "VALUES (:id, :email, :pw, 'Final Test', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ), {"id": hex_id, "email": email, "pw": "hash"})
        
        # 2. Simulate Dataset insertion for this user
        did = uuid.uuid4().hex
        await db.execute(text(
            "INSERT INTO datasets (id, user_id, name, file_type, file_path, file_size_bytes, status, created_at, updated_at) "
            "VALUES (:id, :uid, 'Test Data', 'csv', 'path', 100, 'ready', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ), {"id": did, "uid": hex_id})
        await db.commit()
        
        # 3. Simulate the Dashboard Fetch logic (what I just fixed)
        # Assuming current_user.id returns the OBJECT (uid)
        user_id_obj = uid
        u_id_filter = user_id_obj.hex if db.bind.dialect.name == "sqlite" else str(user_id_obj)
        
        print(f"Dashboard Filtering by: {u_id_filter}")
        result = await db.execute(text("SELECT id FROM datasets WHERE user_id = :uid"), {"uid": u_id_filter})
        rows = result.fetchall()
        
        if rows:
            print(f"VERIFICATION SUCCESS: Found {len(rows)} datasets!")
        else:
            print("VERIFICATION FAILED: Could not find datasets with this filter.")

if __name__ == "__main__":
    asyncio.run(verify_final())

import asyncio
import uuid
import json
from app.api.v1.auth import register, login, get_me
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.database import async_session_factory
from sqlalchemy import text

async def test_flow():
    email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    pw = "password123"
    
    async with async_session_factory() as db:
        # 1. Register
        print("Registering...")
        reg_req = UserRegisterRequest(email=email, password=pw, full_name="Test User")
        user = await register(reg_req, db)
        print(f"Registered user: {user.id}")
        
        # 2. Login
        print("Logging in...")
        login_req = UserLoginRequest(email=email, password=pw)
        tokens = await login(login_req, db)
        print(f"Login success. Access Token: {tokens.access_token[:20]}...")
        
        # 3. Get Me (Simulate Dependency)
        print("Verifying 'Me' endpoint logic...")
        from app.utils.security import verify_access_token
        user_id_str = verify_access_token(tokens.access_token)
        print(f"Verified Subject from Token: {user_id_str}")
        
        # Check if we can find the user in DB using this string
        try:
            from sqlalchemy import select
            from app.models.user import User
            from uuid import UUID
            
            # The logic in dependencies.py:
            user_uuid = UUID(user_id_str)
            print(f"Checking for UUID: {user_uuid} (type: {type(user_uuid)})")
            
            result = await db.execute(select(User).where(User.id == user_uuid))
            found_user = result.scalar_one_or_none()
            
            if found_user:
                print(f"FOUND USER IN DB! Name: {found_user.full_name}")
            else:
                print("USER NOT FOUND IN DB! (This is likely the issue)")
                
                # Check raw DB content
                raw = await db.execute(text("SELECT id FROM users"))
                all_ids = raw.fetchall()
                print(f"All IDs in DB: {[str(r[0]) for r in all_ids]}")
                
        except Exception as e:
            print(f"Verification FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_flow())

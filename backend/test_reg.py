import asyncio
from app.api.v1.auth import register
from app.schemas.auth import UserRegisterRequest
from app.database import async_session_factory
from sqlalchemy import text

async def test_register():
    # Use a dummy session
    async with async_session_factory() as db:
        try:
            # Check if test user exists
            res = await db.execute(text("DELETE FROM users WHERE email='test_bot@example.com'"))
            await db.commit()
            
            # Simulated request
            req = UserRegisterRequest(
                email="test_bot@example.com",
                password="password123",
                full_name="Test Bot"
            )
            
            # Pass the session directly since Depends(get_db) won't work in script
            result = await register(req, db)
            print(f"REGISTER SUCCESS: {result.email}")
            
        except Exception as e:
            print(f"REGISTER FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_register())

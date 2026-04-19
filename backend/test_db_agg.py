import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import uuid

URL = "postgresql+asyncpg://neondb_owner:npg_9JcXeO6jAnbt@ep-snowy-frost-abhs3qci.eu-west-2.aws.neon.tech/neondb?ssl=require"

async def test():
    print("Testing connection...")
    engine = create_async_engine(URL, connect_args={"ssl": False}) # Try without SSL context
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            print("Session opened. Executing query...")
            res = await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=5)
            print(f"QUERY OK: {res.scalar()}")
            
            # Try to register a user
            print("Attempting to insert user...")
            uid = uuid.uuid4()
            await session.execute(text(
                "INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified, created_at, updated_at) "
                "VALUES (:id, :email, :pw, :name, true, false, NOW(), NOW())"
            ), {
                "id": uid,
                "email": f"test_{uid.hex[:6]}@example.com",
                "pw": "test",
                "name": "Test User"
            })
            await session.commit()
            print("INSERT OK")
            
    except Exception as e:
        print(f"TEST FAILED: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())

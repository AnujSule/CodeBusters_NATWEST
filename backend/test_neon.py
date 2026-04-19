"""Quick test: verify Neon PostgreSQL connectivity."""
import asyncio
import ssl
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        "postgresql+asyncpg://neondb_owner:npg_9JcXeO6jAnbt@ep-snowy-frost-abhs3qci.eu-west-2.aws.neon.tech/neondb?ssl=require",
        connect_args={"ssl": ctx},
    )

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB CONNECTION OK:", result.fetchone())

    await engine.dispose()
    print("Neon PostgreSQL is reachable!")

asyncio.run(test_connection())

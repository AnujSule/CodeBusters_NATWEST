"""List all tables in Neon database."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def list_tables():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = result.fetchall()
        print("TABLES IN PUBLIC SCHEMA:", tables)
        
        result2 = await conn.execute(text(
            "SELECT * FROM alembic_version"
        ))
        print("ALEMBIC VERSION:", result2.fetchall())
    await engine.dispose()

asyncio.run(list_tables())

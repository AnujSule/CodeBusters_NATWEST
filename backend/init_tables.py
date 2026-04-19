"""Initialize the database correctly with models imported."""
import asyncio
from app.database import engine, Base
# IMPORTANT: import all models to populate Base.metadata
from app.models.user import User
from app.models.dataset import Dataset
from app.models.query_log import QueryLog
from app.models.metric_definition import MetricDefinition

async def do_init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("TABLES CREATED!")

asyncio.run(do_init())

import sys
import importlib
import asyncio
import uuid
from sqlalchemy import select

async def check_all():
    print(f"Python: {sys.version}")
    
    deps = ["fastapi", "sqlalchemy", "asyncpg", "sentence_transformers", "pdfplumber", "duckdb", "pandas"]
    for d in deps:
        try:
            importlib.import_module(d)
            print(f"[OK] {d}")
        except Exception as e:
            print(f"[FAIL] {d}: {e}")
            
    print("-" * 20)
    
    try:
        from app.database import async_session_factory
        from app.models.dataset import Dataset
        
        async with async_session_factory() as s:
            result = await s.execute(select(Dataset).order_by(Dataset.created_at.desc()).limit(1))
            d = result.scalar()
            if d:
                print(f"Latest Dataset: {d.name}")
                print(f"  ID: {d.id}")
                print(f"  Type: {d.file_type}")
                print(f"  Status: {d.status}")
                print(f"  Path: {d.file_path}")
            else:
                print("No datasets found.")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_all())

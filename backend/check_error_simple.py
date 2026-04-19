import os
import sys
import asyncio
from sqlalchemy import create_engine, text

# Use sync engine for simple check
URL = "postgresql://neondb_owner:npg_9JcXeO6jAnbt@ep-snowy-frost-abhs3qci.eu-west-2.aws.neon.tech/neondb?sslmode=require"

def check_error():
    engine = create_engine(URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name, status, error, id FROM datasets ORDER BY created_at DESC LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"Dataset: {row[0]}")
            print(f"Status: {row[1]}")
            print(f"Error: {row[2]}")
            print(f"ID: {row[3]}")
        else:
            print("No datasets found.")

if __name__ == "__main__":
    check_error()

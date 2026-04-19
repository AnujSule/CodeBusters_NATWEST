import sys
import importlib

dependencies = [
    "fastapi",
    "sqlalchemy",
    "asyncpg",
    "sentence_transformers",
    "pdfplumber",
    "duckdb",
    "pydantic",
    "bcrypt",
    "langchain"
]

print(f"Python version: {sys.version}")
print("-" * 20)

for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"[OK] {dep}")
    except ImportError as e:
        print(f"[FAIL] {dep}: {e}")

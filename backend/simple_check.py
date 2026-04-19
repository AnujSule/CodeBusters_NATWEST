import os
import sys

def check_simple():
    print(f"Python: {sys.version}")
    print(f"CWD: {os.getcwd()}")
    
    # Check if packages are in pip list without importing
    import subprocess
    result = subprocess.run(["pip", "list"], capture_output=True, text=True)
    pkgs = ["pdfplumber", "sentence-transformers", "torch", "duckdb"]
    for pkg in pkgs:
        if pkg in result.stdout:
            print(f"[FOUND] {pkg}")
        else:
            print(f"[MISSING] {pkg}")

if __name__ == "__main__":
    check_simple()

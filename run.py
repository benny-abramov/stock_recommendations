"""Single-command runner for the Alpha Convergence Daily Stock Recommendation Hub."""

import os
import sys

# Ensure UTF-8 output encoding for Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Alpha Convergence Engine & Daily Stock Recommendation Hub")
    print("Local URL: http://127.0.0.1:8000")
    print("API Docs:  http://127.0.0.1:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

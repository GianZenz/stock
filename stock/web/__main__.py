import importlib
import subprocess
import sys
from typing import List


REQUIRED: List[str] = [
    "fastapi",
    "uvicorn",
    "jinja2",
]


def ensure_deps() -> None:
    missing = []
    for name in REQUIRED:
        try:
            importlib.import_module(name)
        except Exception:
            missing.append(name)
    if not missing:
        return
    print(f"Installing missing packages: {', '.join(missing)}")
    for pkg in missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        except Exception as e:
            print(f"Failed to install {pkg}: {e}")
            print("You can install dependencies manually: pip install fastapi uvicorn jinja2")
            raise SystemExit(1)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the Stock Trend Advisor web UI (FastAPI)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    args = parser.parse_args()

    ensure_deps()

    # After ensuring deps, run the server via uvicorn
    import uvicorn

    uvicorn.run("stock.web.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()


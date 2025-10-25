import importlib
import subprocess
import sys
import threading
import time
import webbrowser
from typing import List
import socket
import ctypes


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
    parser.add_argument("--lang", choices=["en", "it"], default="en", help="Default language to open (en/it)")
    args = parser.parse_args()

    # In a frozen EXE (PyInstaller), dependencies are bundled: skip pip
    is_frozen = getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS")
    if not is_frozen:
        ensure_deps()

    # After ensuring deps, run the server via uvicorn
    import uvicorn
    # Import ASGI app directly to avoid string-based import issues in frozen builds
    from .server import app as asgi_app

    # Find a free port (auto-retry if busy)
    def find_free_port(host: str, start: int, tries: int = 3) -> int | None:
        for p in range(start, start + max(1, tries)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, p))
                s.close()
                return p
            except OSError:
                continue
        return None

    chosen_port = find_free_port(args.host, args.port, tries=3) or args.port
    if chosen_port != args.port:
        # Show a small dialog (Windows) informing the port change
        try:
            ctypes.windll.user32.MessageBoxW(0, f"La porta {args.port} era occupata. Uso la porta {chosen_port}.", "Stock Advisor", 0)
        except Exception:
            print(f"Port {args.port} busy, switching to {chosen_port}")

    # Open browser shortly after server start (non-blocking)
    def _open(port: int):
        time.sleep(0.8)
        try:
            path = "/it" if args.lang == "it" else "/"
            webbrowser.open_new(f"http://{args.host}:{port}{path}")
        except Exception:
            pass
    threading.Thread(target=_open, args=(chosen_port,), daemon=True).start()

    uvicorn.run(asgi_app, host=args.host, port=chosen_port, reload=args.reload)


if __name__ == "__main__":
    main()

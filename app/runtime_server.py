"""``uv run python -m app.runtime_server`` — runtime server entry point.

Boots the FastAPI app from `app.runtime.server` via uvicorn, bound to
127.0.0.1 only per NFR-S2. The integration test in
`tests/integration/runtime/test_fastapi_server.py` spawns this entry point
as a subprocess, probes ``/health`` + ``/invoke``, and asserts SIGTERM /
``terminate()`` clean shutdown within 2 seconds.

Port resolution: ``RUNTIME_PORT`` env var, defaulting to 8765.
"""

from __future__ import annotations

import os
import sys

import uvicorn

from app.runtime.server import DEFAULT_BIND_HOST, DEFAULT_BIND_PORT


def _resolve_port() -> int:
    raw = os.getenv("RUNTIME_PORT")
    if not raw:
        return DEFAULT_BIND_PORT
    try:
        port = int(raw)
    except ValueError:
        print(
            f"runtime_server: RUNTIME_PORT={raw!r} is not an int; aborting.",
            file=sys.stderr,
        )
        raise SystemExit(2) from None
    if not (1 <= port <= 65535):
        print(
            f"runtime_server: RUNTIME_PORT={port} out of range 1-65535; aborting.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return port


def main() -> None:
    uvicorn.run(
        "app.runtime.server:app",
        host=DEFAULT_BIND_HOST,
        port=_resolve_port(),
        log_level="warning",
    )


if __name__ == "__main__":
    main()

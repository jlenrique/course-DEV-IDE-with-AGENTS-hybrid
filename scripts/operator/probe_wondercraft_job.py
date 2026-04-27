"""Wondercraft job-status probe — fetches one polling response and dumps it.

Use to discover the actual response shape so we can patch the M2 ceremony
script's terminal-state detection. Auto-loads .env.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\probe_wondercraft_job.py <job_id>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: probe_wondercraft_job.py <job_id>", file=sys.stderr)
        return 2

    job_id = sys.argv[1]
    print(f"Probing /podcast/{job_id} ...")
    print()

    from scripts.api_clients.wondercraft_client import WondercraftClient

    client = WondercraftClient()
    try:
        response = client.get(f"/podcast/{job_id}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Raw response:")
    print("-" * 60)
    print(json.dumps(response, indent=2, default=str))
    print("-" * 60)
    print()
    print("Top-level keys:", list(response.keys()) if isinstance(response, dict) else "(not a dict)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

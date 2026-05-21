"""Scite MCP discovery probe — discovers what tools the live Scite MCP exposes.

Auto-loads .env. Tries TWO connection modes:
  1. NO AUTH (per PulseMCP "open server" doc)
  2. HTTP BASIC auth using SCITE_USER_NAME + SCITE_PASSWORD (per existing
     SciteProvider assumption)

Prints the discovered tools list (names + descriptions + parameter schemas)
under whichever mode succeeds. We need this BEFORE running the M3 ceremony
because the existing `SciteProvider._SCITE_TOOL_SEARCH = 'search'` is
explicitly labeled "to be verified at first-live-run" — going in blind is
exactly the A16 (Composition-vs-Component Audit Gap) anti-pattern.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\probe_scite_mcp.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

SCITE_MCP_URL = os.environ.get("SCITE_MCP_URL", "https://api.scite.ai/mcp")


def probe_no_auth() -> dict | None:
    """Try MCP tools/list with no authentication."""
    import httpx

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
    }
    try:
        response = httpx.post(SCITE_MCP_URL, json=payload, headers=headers, timeout=30, follow_redirects=True)
    except Exception as exc:
        return {"_error": f"network: {exc}"}

    return {
        "_status": response.status_code,
        "_headers_subset": {
            k: v
            for k, v in response.headers.items()
            if k.lower() in ("content-type", "www-authenticate", "x-mcp-session-id")
        },
        "_body": _safe_parse(response.text),
    }


def probe_with_basic_auth() -> dict | None:
    """Try MCP tools/list with HTTP Basic auth from SCITE_USER_NAME + SCITE_PASSWORD."""
    import httpx

    user = os.environ.get("SCITE_USER_NAME", "")
    pw = os.environ.get("SCITE_PASSWORD", "")
    if not user or not pw:
        return {"_error": "SCITE_USER_NAME or SCITE_PASSWORD missing"}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
    }
    try:
        response = httpx.post(
            SCITE_MCP_URL,
            json=payload,
            headers=headers,
            auth=(user, pw),
            timeout=30,
            follow_redirects=True,
        )
    except Exception as exc:
        return {"_error": f"network: {exc}"}

    return {
        "_status": response.status_code,
        "_headers_subset": {
            k: v
            for k, v in response.headers.items()
            if k.lower() in ("content-type", "www-authenticate", "x-mcp-session-id")
        },
        "_body": _safe_parse(response.text),
    }


def _safe_parse(text: str) -> object:
    """Parse JSON if possible; otherwise return raw text (truncated)."""
    try:
        return json.loads(text)
    except Exception:
        return text[:500] + ("..." if len(text) > 500 else "")


def main() -> int:
    print("=" * 60)
    print("SCITE MCP DISCOVERY PROBE")
    print("=" * 60)
    print(f"Endpoint: {SCITE_MCP_URL}")
    print()

    print("Mode A: NO AUTH (per PulseMCP 'open server' doc)")
    print("-" * 60)
    result_a = probe_no_auth()
    print(json.dumps(result_a, indent=2, default=str))
    print()

    print("Mode B: HTTP BASIC AUTH (SCITE_USER_NAME + SCITE_PASSWORD)")
    print("-" * 60)
    result_b = probe_with_basic_auth()
    print(json.dumps(result_b, indent=2, default=str))
    print()

    print("=" * 60)
    print("INTERPRETATION GUIDE")
    print("=" * 60)
    print("- Status 200 + body containing 'tools' array = success; that mode works.")
    print("- Status 401/403 = auth required (or wrong creds) for that mode.")
    print("- Status 404 = wrong endpoint URL.")
    print("- Status 405 = wrong HTTP method (MCP requires POST).")
    print("- 'Accept' header issue → may need 'text/event-stream' (Streamable HTTP).")
    print("- Other status / network error → see _error field.")
    print()
    print("Whichever mode returns a 'tools' array is the right one to use for M3.")
    print("Compare the discovered tool names against SciteProvider's hardcoded:")
    print("  - _SCITE_TOOL_SEARCH = 'search'")
    print("  - _SCITE_TOOL_PAPER = 'paper_metadata'")
    print("  - _SCITE_TOOL_CITATIONS = 'citation_contexts'")
    print("If the names differ, that's an A16 instance — patch SciteProvider OR work around in M3 ceremony script.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

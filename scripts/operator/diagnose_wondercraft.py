"""Wondercraft auth/permission diagnostic.

Walks through the Wondercraft API in increasing privilege:
  1. Auth header verification (does X-API-KEY get accepted at ALL?)
  2. Read-only connectivity (GET /podcast — list endpoint; lowest privilege)
  3. List episodes (GET /podcast?page=1 — confirms account access)
  4. Pre-flight scripted-podcast (does the endpoint exist for your account?)

Each step prints OK/FAIL + interpretation. Determines whether the 403 from
create_scripted_podcast is endpoint-specific (account-tier restriction) or
broader (auth-header / key value / base-URL issue).
"""

from __future__ import annotations

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

sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    print("=" * 60)
    print("WONDERCRAFT DIAGNOSTIC")
    print("=" * 60)

    # Step 1 — env vars
    api_key = os.environ.get("WONDERCRAFT_API_KEY", "")
    base_url = os.environ.get("WONDERCRAFT_BASE_URL", "https://api.wondercraft.ai/v1")
    if not api_key or api_key.startswith("<"):
        print("FAIL — WONDERCRAFT_API_KEY missing or placeholder")
        return 1
    print(f"OK   — WONDERCRAFT_API_KEY present ({api_key[:8]}...{api_key[-4:]})")
    print(f"OK   — WONDERCRAFT_BASE_URL = {base_url}")
    print()

    # Step 2 — instantiate client
    from scripts.api_clients.wondercraft_client import WondercraftClient

    try:
        client = WondercraftClient()
    except Exception as exc:
        print(f"FAIL — client instantiation: {exc}")
        return 1
    print(f"OK   — WondercraftClient instantiated; base_url={client.base_url}")
    print(f"       auth_header session: X-API-KEY = {client.session.headers.get('X-API-KEY', '(MISSING)')[:8]}...")
    print()

    # Step 3 — connectivity check (uses GET /podcast?page=1&pageSize=1)
    print("Step 3: connectivity check (GET /podcast)...")
    try:
        result = client.check_connectivity()
        print(f"       result: {result}")
        if result.get("reachable"):
            print(f"OK   — API reachable; status={result['status_code']}")
        else:
            print(f"FAIL — API not reachable; status={result['status_code']}")
            print(f"       URL tried: {result.get('url')}")
            return 1
    except Exception as exc:
        print(f"FAIL — connectivity exception: {exc}")
        return 1
    print()

    # Step 4 — list episodes (read-only, low privilege)
    print("Step 4: list episodes (GET /podcast page=1)...")
    try:
        episodes = client.list_episodes(page=1, page_size=5)
        print(f"OK   — list_episodes returned {len(episodes)} episode(s)")
        if episodes:
            first = episodes[0]
            episode_id = first.get("id") or first.get("episodeId") or "(no id field)"
            episode_title = first.get("title") or "(no title field)"
            print(f"       sample episode: id={episode_id}, title={episode_title!r}")
    except Exception as exc:
        print(f"FAIL — list_episodes exception: {exc}")
        print()
        print("Interpretation: account-level read access is denied.")
        print("Possible causes:")
        print("  - API key from a different Wondercraft account")
        print("  - Account suspended / inactive")
        print("  - Free-tier account without /podcast read access")
        return 1
    print()

    # Step 5 — pre-flight create_scripted_podcast (POST /podcast/scripted with minimal payload)
    # Use a 1-line script + dry-run-ish minimal payload to surface if endpoint exists
    print("Step 5: probe POST /podcast/scripted endpoint (minimal payload)...")
    print("       (this attempts to start a real job; if 403, endpoint is account-restricted)")
    print()
    confirm = input("Probe with minimal payload? (will start a real cheap job) Type 'yes': ").strip().lower()
    if confirm != "yes":
        print("Skipped.")
        return 0

    try:
        result = client.create_scripted_podcast(
            title="Wondercraft auth diagnostic probe",
            script="This is a one-line auth probe.",
        )
        print(f"OK   — create_scripted_podcast returned: {result}")
        print()
        print("Interpretation: scripted-podcast endpoint IS accessible to your account.")
        print("The earlier 403 may have been transient or specific to the script content.")
        print("Try the M2 ceremony script again.")
        return 0
    except Exception as exc:
        print(f"FAIL — create_scripted_podcast: {exc}")
        print()
        msg = str(exc)
        if "403" in msg:
            print("Interpretation: Wondercraft account does NOT have access to /podcast/scripted.")
            print()
            print("Possible causes:")
            print("  - Free-tier account; scripted-podcast is paid-feature")
            print("  - Account hasn't been provisioned for this endpoint")
            print("  - Endpoint moved (try /podcast simple or /podcast/convo-mode/user-scripted)")
            print()
            print("Workarounds for M2 ceremony:")
            print("  - Try create_podcast (simple/AI-generated) instead of create_scripted_podcast")
            print("    Cost: $1-2 fallback per M2 spec.")
            print("  - Defer M2 ceremony until Wondercraft account is upgraded.")
            print("  - Operator-decision: which path?")
        elif "401" in msg:
            print("Interpretation: API key is being rejected at auth layer.")
            print("Possible causes: key revoked, key from wrong account, wrong base_url.")
        elif "404" in msg:
            print("Interpretation: endpoint /podcast/scripted does not exist on this base_url.")
            print("Possible causes: Wondercraft API path changed, base_url misconfigured.")
        else:
            print("Interpretation: unexpected error class. Paste full output for diagnosis.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

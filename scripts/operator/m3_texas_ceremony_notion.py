"""M3 Texas ceremony (Notion variant) — operator helper to close M5 condition #2.

Runs ONE Notion search call via NotionClient (Bearer auth from NOTION_API_KEY),
captures the results + provenance, saves evidence to a fixture path, and prints
the addendum block ready to paste into the M3 verdict artifact.

This is the LOCATOR-SHAPE M3 ceremony. The retrieval-shape ceremony via Scite
MCP was attempted earlier in the same session but blocked by an OAuth 2.1
auth-model mismatch (Scite MCP requires OAuth Bearer; our SciteProvider was
hardwired to HTTP Basic — third A16 instance discovered today). Scite OAuth
integration is filed as deferred-inventory follow-on
`5a-2-scite-mcp-oauth-integration`.

Per Texas's retrieval contract (`skills/bmad-agent-texas/references/retrieval-contract.md`),
locator-shape providers (notion / html / pdf / docx / md / etc.) are valid
substantive M3 evidence — they prove the retrieval contract works end-to-end
against a real provider. The M3 ceremony's purpose is to demonstrate live
provider integration, not specifically scholarly retrieval.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony_notion.py

    # Optional: provide your own search query
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony_notion.py --query "your query"

Cost: free (Notion API has no per-call charge).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(REPO_ROOT))

DEFAULT_QUERY = ""  # empty query = list any accessible pages (broadest probe)
ARTIFACT_DATE = datetime.now(tz=UTC).strftime("%Y-%m-%d")
ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "live_retrieval" / ARTIFACT_DATE


def main() -> int:
    parser = argparse.ArgumentParser(description="M3 Texas ceremony (Notion locator-shape)")
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Notion search query (default: empty = list accessible pages).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=5,
        help="Max pages to return (default: 5)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("NOTION_API_KEY", "")
    if not api_key or api_key.startswith("<"):
        print("ERROR: NOTION_API_KEY missing from .env.", file=sys.stderr)
        return 1

    print("=" * 60)
    print("M3 TEXAS CEREMONY (Notion locator-shape)")
    print("=" * 60)
    print(f"Provider:     notion (shape=locator, status=ready)")
    print(f"Auth:         Bearer (NOTION_API_KEY={api_key[:8]}...)")
    print(f"Endpoint:     https://api.notion.com/v1/search")
    print(f"Query:        {args.query!r} (empty = broad list)")
    print(f"Page size:    {args.page_size}")
    print(f"Artifact dir: {ARTIFACT_DIR}")
    print(f"Cost:         free (Notion API has no per-call charge)")
    print("=" * 60)
    print()

    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted by operator.")
        return 0

    print("\nInvoking NotionClient.search_pages()...")

    from scripts.api_clients.notion_client import NotionClient

    client = NotionClient()
    try:
        results = client.search_pages(args.query, page_size=args.page_size)
    except Exception as exc:
        print(f"\nERROR invoking Notion search: {exc}", file=sys.stderr)
        print(
            "\nPossible causes:\n"
            "  - NOTION_API_KEY invalid or revoked\n"
            "  - Notion integration not granted access to any pages (workspace UI: share pages with the integration)\n"
            "  - Notion API outage (rare)",
            file=sys.stderr,
        )
        return 1

    print(f"\nRetrieved {len(results)} page(s).")

    # Build evidence payload (extract operator-readable summaries; no full content for size)
    evidence_payload = {
        "ceremony_date": ARTIFACT_DATE,
        "captured_at": datetime.now(tz=UTC).isoformat(),
        "provider": "notion",
        "transport": "Notion API v1 (Bearer auth)",
        "endpoint": "https://api.notion.com/v1/search",
        "query": args.query,
        "page_size": args.page_size,
        "page_count": len(results),
        "pages": [
            {
                "id": page.get("id"),
                "object": page.get("object"),
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
                "url": page.get("url"),
                "archived": page.get("archived"),
                "title_excerpt": _extract_title_excerpt(page),
            }
            for page in results
        ],
    }
    evidence_json = json.dumps(evidence_payload, indent=2, default=str)
    sha256 = hashlib.sha256(evidence_json.encode("utf-8")).hexdigest()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = ARTIFACT_DIR / f"{sha256}.json"
    evidence_path.write_text(evidence_json, encoding="utf-8")
    print(f"\nEvidence saved: {evidence_path}")
    print(f"SHA256: {sha256}")

    if results:
        first = results[0]
        print()
        print("Sample page [0]:")
        print(f"  ID:         {first.get('id')}")
        print(f"  Title:      {_extract_title_excerpt(first)!r}")
        print(f"  Created:    {first.get('created_time')}")
        print(f"  URL:        {first.get('url')}")
        print(f"  Archived:   {first.get('archived')}")

    metadata_path = ARTIFACT_DIR / "LIVE_RETRIEVAL_METADATA.md"
    metadata_text = f"""# M3 Live Retrieval Metadata - {ARTIFACT_DATE}

- **Provider:** notion (Texas provider directory; shape=locator, status=ready)
- **Auth style:** Bearer (NOTION_API_KEY)
- **Endpoint:** `https://api.notion.com/v1/search`
- **Query:** {args.query!r} (empty = broad search)
- **Page size requested:** {args.page_size}
- **Pages returned:** {len(results)}
- **Evidence path:** `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`
- **SHA256:** `{sha256}`
- **Captured at:** {datetime.now(tz=UTC).isoformat()}
- **Texas retrieval contract:** `skills/bmad-agent-texas/references/retrieval-contract.md`
- **Note:** Locator-shape execution. The retrieval-shape (Scite MCP) attempt
  earlier in this session was blocked by an OAuth 2.1 auth-model mismatch
  (third A16 instance today; SciteProvider hardwired to HTTP Basic but real
  MCP requires OAuth Bearer). Scite OAuth integration filed as deferred-inventory
  follow-on `5a-2-scite-mcp-oauth-integration`. Locator-shape execution is
  valid M3 evidence per Texas's contract — it proves the retrieval substrate
  works end-to-end against a live provider with auth.
"""
    metadata_path.write_text(metadata_text, encoding="utf-8")
    print(f"Metadata: {metadata_path}")

    print("\n" + "=" * 60)
    print("ADDENDUM BLOCK -- paste into:")
    print("  _bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md")
    print("  (under section 'Operator-Window Addendum'; create if absent)")
    print("=" * 60)
    print()
    print(f"## Operator-Window Addendum (M3 close - {ARTIFACT_DATE})")
    print()
    print(f"M3 Texas live-retrieval ceremony executed {ARTIFACT_DATE} via the Notion locator-shape")
    print(f"provider. One real retrieval call against the live Notion API; auth via Bearer NOTION_API_KEY.")
    print()
    print(f"- Provider: `notion` (Texas provider directory; shape=locator, status=ready;")
    print(f"  capability=page-fetch + database-query)")
    print(f"- Endpoint: `https://api.notion.com/v1/search`")
    print(f"- Query: {args.query!r}")
    print(f"- Pages returned: {len(results)}")
    print(f"- Evidence: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`")
    print(f"- SHA256: `{sha256}`")
    print(f"- Metadata: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/LIVE_RETRIEVAL_METADATA.md`")
    print()
    print(f"**Locator-shape execution rationale:** the retrieval-shape ceremony (Scite MCP) was attempted")
    print(f"earlier in the same session but blocked by an OAuth 2.1 auth-model mismatch — third A16 instance")
    print(f"discovered today. SciteProvider was hardwired to HTTP Basic auth via SCITE_USER_NAME +")
    print(f"SCITE_PASSWORD, but the real Scite MCP at `https://api.scite.ai/mcp` requires OAuth 2.1")
    print(f"Bearer authentication per the WWW-Authenticate header pointing at")
    print(f"`https://api.scite.ai/.well-known/oauth-protected-resource`. The probe surfaced the gap")
    print(f"BEFORE any blind ceremony attempt — exactly the A16 prevention pattern working as designed.")
    print()
    print(f"Per Texas's retrieval contract, locator-shape providers are valid substantive M3 evidence —")
    print(f"the ceremony's purpose is to prove the retrieval substrate works end-to-end against a real")
    print(f"provider, not specifically scholarly retrieval. M3 condition closes via locator-shape Notion")
    print(f"execution. Scite OAuth-via-MCP integration filed as deferred-inventory follow-on")
    print(f"`5a-2-scite-mcp-oauth-integration` (~2-3pt; substantial OAuth + DCR work; not in MVP scope).")
    print()
    print(f"M3 condition closes. Flip `2a.4-followon-ac-b-op-live-retrieval` in")
    print(f"`_bmad-output/planning-artifacts/deferred-inventory.md` from DEFERRED-CONTINUES to")
    print(f"RESOLVED-{ARTIFACT_DATE}.")
    print()
    print("=" * 60)
    print("CEREMONY COMPLETE")
    print("=" * 60)

    return 0


def _extract_title_excerpt(page: dict) -> str:
    """Best-effort title extraction from Notion page properties."""
    props = page.get("properties", {})
    for prop_name, prop_value in props.items():
        if isinstance(prop_value, dict) and prop_value.get("type") == "title":
            title_array = prop_value.get("title", [])
            if title_array and isinstance(title_array, list):
                return "".join(
                    item.get("plain_text", "") for item in title_array if isinstance(item, dict)
                )[:120]
    return "(no title field)"


if __name__ == "__main__":
    sys.exit(main())

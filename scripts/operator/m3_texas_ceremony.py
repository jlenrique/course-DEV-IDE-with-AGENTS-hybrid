"""M3 Texas ceremony — operator helper to close M5 condition #2.

Runs ONE Texas retrieval call via the SciteProvider (MCP transport against
scite.ai), captures the results + provenance, saves evidence to a fixture path,
and prints the addendum block ready to paste into the M3 verdict artifact.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony.py

    # Optional: provide your own search query (default: a short scholarly query)
    .venv\\Scripts\\python.exe scripts\\operator\\m3_texas_ceremony.py --query "neuroplasticity learning"

Discipline: this script does NOT mutate sprint-status, deferred-inventory, or
verdict artifacts. It produces the evidence + addendum text. Operator pastes
the addendum block manually after reviewing output.

Provider: scite.ai via MCP (HTTPS Basic auth from SCITE_USER_NAME +
SCITE_PASSWORD). Status=ready, shape=retrieval, capability=citation-network.
Cost: scite charges per query (very small; trivial for a single search).
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

# Make repo modules + Texas's retrieval substrate importable
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"))

DEFAULT_QUERY = "neuroplasticity adult learning evidence-based instructional design"
ARTIFACT_DATE = datetime.now(tz=UTC).strftime("%Y-%m-%d")
ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "texas" / "live_retrieval" / ARTIFACT_DATE


def main() -> int:
    parser = argparse.ArgumentParser(description="M3 Texas ceremony (scite via MCP)")
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help=f"Scholarly search query. Default: {DEFAULT_QUERY!r}",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Max scholarly results to retrieve (default: 5; trivial cost)",
    )
    args = parser.parse_args()

    # Pre-check credentials
    import os

    user = os.environ.get("SCITE_USER_NAME", "")
    pw = os.environ.get("SCITE_PASSWORD", "")
    if not user or not pw:
        print(
            "ERROR: SCITE_USER_NAME and/or SCITE_PASSWORD missing from .env.\n"
            "Both are required for scite MCP HTTP Basic auth.",
            file=sys.stderr,
        )
        return 1

    print("=" * 60)
    print("M3 TEXAS CEREMONY (scite via MCP)")
    print("=" * 60)
    print(f"Provider:     scite.ai (MCP transport; HTTP Basic auth)")
    print(f"Query:        {args.query!r}")
    print(f"Max results:  {args.max_results}")
    print(f"Artifact dir: {ARTIFACT_DIR}")
    print(f"Auth:         SCITE_USER_NAME={user[:4]}*** + SCITE_PASSWORD=***")
    print("=" * 60)
    print()

    print("This will incur trivial scite API spend (single search; ~free per scite plan).")
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted by operator.")
        return 0

    print("\nConstructing RetrievalIntent + invoking SciteProvider...")

    from retrieval.contracts import (
        AcceptanceCriteria,
        ProviderHint,
        RetrievalIntent,
    )
    from retrieval.scite_provider import SciteProvider

    intent = RetrievalIntent(
        intent=args.query,
        provider_hints=[
            ProviderHint(provider="scite", params={"mode": "search"}),
        ],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": args.max_results},
            provider_scored={},
            semantic_deferred="M3 operator-window ceremony — substantive review left to operator",
        ),
        cross_validate=False,
        iteration_budget=1,
        convergence_required=False,
    )

    provider = SciteProvider()

    try:
        # SciteProvider.execute() returns list[TexasRow]
        rows = provider.execute(intent)
    except Exception as exc:
        print(f"\nERROR invoking SciteProvider: {exc}", file=sys.stderr)
        print(
            "\nPossible causes:\n"
            "  - SCITE_USER_NAME/SCITE_PASSWORD invalid or unauthorized for MCP\n"
            "  - scite.ai MCP endpoint unreachable\n"
            "  - scite plan does not include MCP API access\n"
            "  - Query rejected by scite (rare; very loose query like the default should work)",
            file=sys.stderr,
        )
        return 1

    print(f"\nRetrieved {len(rows)} row(s).")
    if not rows:
        print(
            "WARNING: zero rows returned. Possible: query too narrow, or scite returned empty set.\n"
            "Either re-run with a broader query or accept zero-rows-as-evidence (M3 ceremony purpose\n"
            "is to prove the API call succeeds; substantive content is operator-discretion).",
            file=sys.stderr,
        )

    # Serialize rows to JSON for evidence
    evidence_payload = {
        "ceremony_date": ARTIFACT_DATE,
        "captured_at": datetime.now(tz=UTC).isoformat(),
        "provider": "scite",
        "transport": "MCP (HTTPS Basic auth)",
        "query": args.query,
        "max_results_requested": args.max_results,
        "row_count": len(rows),
        "rows": [
            {
                "source_id": getattr(row, "source_id", None),
                "title": getattr(row, "title", None),
                "authors": getattr(row, "authors", None),
                "venue": getattr(row, "venue", None),
                "year": getattr(row, "year", None),
                "doi": getattr(row, "doi", None),
                "url": getattr(row, "url", None),
                "authority_tier": getattr(row, "authority_tier", None),
                "provider_metadata_scite": getattr(row, "provider_metadata", {}).get("scite", {})
                if hasattr(row, "provider_metadata") and isinstance(row.provider_metadata, dict)
                else None,
            }
            for row in rows
        ],
    }
    evidence_json = json.dumps(evidence_payload, indent=2, default=str)
    sha256 = hashlib.sha256(evidence_json.encode("utf-8")).hexdigest()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = ARTIFACT_DIR / f"{sha256}.json"
    evidence_path.write_text(evidence_json, encoding="utf-8")
    print(f"\nEvidence saved: {evidence_path}")
    print(f"SHA256: {sha256}")

    # Print sample of first row for quick inspection
    if rows:
        first = rows[0]
        print()
        print("Sample row [0]:")
        print(f"  Title:  {getattr(first, 'title', '(no title)')!r}")
        print(f"  Venue:  {getattr(first, 'venue', '(no venue)')!r}")
        print(f"  DOI:    {getattr(first, 'doi', '(no doi)')!r}")
        print(f"  Year:   {getattr(first, 'year', '(no year)')!r}")
        print(f"  Tier:   {getattr(first, 'authority_tier', '(no tier)')!r}")

    # Write metadata companion
    metadata_path = ARTIFACT_DIR / "LIVE_RETRIEVAL_METADATA.md"
    metadata_text = f"""# M3 Live Retrieval Metadata - {ARTIFACT_DATE}

- **Provider:** scite.ai (MCP transport)
- **Auth style:** HTTP Basic (SCITE_USER_NAME + SCITE_PASSWORD)
- **MCP endpoint:** `{os.environ.get("SCITE_MCP_URL", "https://api.scite.ai/mcp")}`
- **Query:** {args.query!r}
- **Max results requested:** {args.max_results}
- **Row count returned:** {len(rows)}
- **Evidence path:** `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`
- **SHA256:** `{sha256}`
- **Captured at:** {datetime.now(tz=UTC).isoformat()}
- **Texas retrieval contract:** `skills/bmad-agent-texas/references/retrieval-contract.md`
- **Provider info:** shape=retrieval, status=ready, identity_key=DOI
"""
    metadata_path.write_text(metadata_text, encoding="utf-8")
    print(f"Metadata: {metadata_path}")

    # Print addendum block
    print("\n" + "=" * 60)
    print("ADDENDUM BLOCK -- paste into:")
    print("  _bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md")
    print("  (under section 'Operator-Window Addendum'; create if absent)")
    print("=" * 60)
    print()
    print(f"## Operator-Window Addendum (M3 close - {ARTIFACT_DATE})")
    print()
    print(f"M3 Texas live-retrieval ceremony executed {ARTIFACT_DATE}. One real retrieval call via")
    print(f"SciteProvider through the scite.ai MCP transport (HTTP Basic auth via SCITE_USER_NAME +")
    print(f"SCITE_PASSWORD).")
    print()
    print(f"- Provider: `scite` (shape=retrieval, status=ready; per `provider_directory.list_providers()`)")
    print(f"- Transport: MCP (`MCPClient` with `auth_style='basic'`)")
    print(f"- Endpoint: `{os.environ.get('SCITE_MCP_URL', 'https://api.scite.ai/mcp')}`")
    print(f"- Query: {args.query!r}")
    print(f"- Rows returned: {len(rows)}")
    print(f"- Evidence: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/{sha256}.json`")
    print(f"- SHA256: `{sha256}`")
    print(f"- Metadata: `tests/fixtures/specialists/texas/live_retrieval/{ARTIFACT_DATE}/LIVE_RETRIEVAL_METADATA.md`")
    print()
    print(f"Texas's Shape 3-Disciplined retrieval contract proven end-to-end against a live scholarly")
    print(f"provider. M3 condition closes. Flip `2a.4-followon-ac-b-op-live-retrieval` in")
    print(f"`_bmad-output/planning-artifacts/deferred-inventory.md` from DEFERRED-CONTINUES to")
    print(f"RESOLVED-{ARTIFACT_DATE}.")
    print()
    print("=" * 60)
    print("CEREMONY COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())

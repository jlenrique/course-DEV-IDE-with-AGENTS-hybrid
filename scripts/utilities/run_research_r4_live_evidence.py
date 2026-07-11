#!/usr/bin/env python3
"""R4 live evidence — credibility fields on minted research_entries.

Dispatches Scite∩Consensus corroborate, triangulates with title-bridge, mints
cited entries, and asserts every row carries hierarchy tier + peer-review +
provenance (non-vacuous).

Usage::

    python scripts/utilities/run_research_r4_live_evidence.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "bmad-agent-texas" / "scripts"))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=True)
os.environ["MARCUS_RESEARCH_DETECTIVE_LIVE"] = "1"

from retrieval.consensus_provider import ensure_consensus_bearer_from_mcp_auth  # noqa: E402
from retrieval.dispatcher import dispatch as dispatch_intent  # noqa: E402
from retrieval.triangulator import triangulate_texas_rows  # noqa: E402

from app.marcus.orchestrator.research_citation import (  # noqa: E402
    apply_triangulation_to_entries,
    assert_credibility_fields,
    mint_cited_entry,
)
from app.marcus.orchestrator.research_wiring import (  # noqa: E402
    DeterministicPostureSelector,
    consensus_creds_present,
)


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _scite_creds_present() -> bool:
    return bool(
        os.environ.get("SCITE_USER_NAME", "").strip()
        and os.environ.get("SCITE_PASSWORD", "").strip()
    )


def main() -> int:
    oauth_loaded = ensure_consensus_bearer_from_mcp_auth()
    os.environ.setdefault("CONSENSUS_MCP_URL", "https://mcp.consensus.app/mcp")
    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r4-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    if not _scite_creds_present():
        missing.append("SCITE_USER_NAME/SCITE_PASSWORD")
    if not consensus_creds_present():
        missing.append("CONSENSUS_API_KEY or mcp-remote OAuth")
    if missing:
        verdict = {"story": "research-r4", "pass": False, "fence": "creds-absent", "missing": missing}
        (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        return 2

    selector = DeterministicPostureSelector()
    intent = selector.select_posture(
        {
            "gap_type": "evidence",
            "claim": "Worked examples improve novice transfer in introductory instruction.",
            "source_context": "Need a supporting citation for the worked-example rationale.",
            "scope_decision": "in-scope",
            "evidence_bolster": True,
            "research_goal_id": "r4-live-credibility",
        }
    )

    error = None
    entries_dump: list[dict] = []
    try:
        result = dispatch_intent(intent)
        results = result if isinstance(result, list) else [result]
        rows = []
        for pr in results:
            rows.extend(list(getattr(pr, "rows", []) or []))
        receipt = triangulate_texas_rows(
            rows, query_intent=intent.intent, title_bridge=True, max_bridge_titles=5
        )
        entries = [
            mint_cited_entry(row, citation_index=i)
            for i, row in enumerate(rows, start=1)
        ]
        entries = apply_triangulation_to_entries(entries, receipt)
        for entry in entries:
            assert_credibility_fields(entry)
        entries_dump = [e.model_dump(mode="json") for e in entries]
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    non_vacuous = [
        e
        for e in entries_dump
        if e.get("evidence_hierarchy_tier")
        and e.get("provider_provenance")
        and e.get("triangulation_status")
    ]
    has_dual = any(e.get("triangulation_status") == "dual_provider" for e in entries_dump)
    overall = error is None and len(non_vacuous) == len(entries_dump) > 0

    sample = non_vacuous[:5]
    verdict = {
        "story": "research-r4",
        "oauth_cache_loaded": oauth_loaded,
        "entry_count": len(entries_dump),
        "non_vacuous_count": len(non_vacuous),
        "has_dual_provider_entry": has_dual,
        "sample": sample,
        "error": error,
        "pass": overall,
    }
    (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (out_dir / "entries.json").write_text(json.dumps(entries_dump, indent=2), encoding="utf-8")
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# PROOF R4 credibility surfacing",
                "",
                f"pass={overall} entries={len(entries_dump)} non_vacuous={len(non_vacuous)}",
                f"has_dual_provider_entry={has_dual}",
                "",
                *[
                    f"- `{e.get('citation_id')}` tier={e.get('evidence_hierarchy_tier')} "
                    f"peer={e.get('peer_reviewed')} provenance={e.get('provider_provenance')} "
                    f"tri={e.get('triangulation_status')} score={e.get('reliability_score')}"
                    for e in sample
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {out_dir}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())

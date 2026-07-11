#!/usr/bin/env python3
"""R6 live evidence — Irene intake consumes real wrangled research rows.

Dispatches Scite∩Consensus (detective + bolster), mints entries, builds intake
packet, and proves fabricate-cite path stays RED against the live set.

Usage::

    python scripts/utilities/run_research_r6_live_evidence.py
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


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    from retrieval.consensus_provider import ensure_consensus_bearer_from_mcp_auth
    from retrieval.dispatcher import dispatch as dispatch_intent
    from retrieval.triangulator import triangulate_texas_rows

    from app.marcus.orchestrator.research_citation import (
        apply_triangulation_to_entries,
        assert_credibility_fields,
        mint_cited_entry,
    )
    from app.marcus.orchestrator.research_wiring import (
        DeterministicPostureSelector,
        consensus_creds_present,
    )
    from app.specialists._shared.research_intake import (
        FabricatedCitationError,
        assert_no_fabricated_citations,
        consume_research_entries,
    )

    oauth = ensure_consensus_bearer_from_mcp_auth()
    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r6-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    scite_ok = bool(
        os.environ.get("SCITE_USER_NAME", "").strip()
        and os.environ.get("SCITE_PASSWORD", "").strip()
    )
    if not scite_ok or not consensus_creds_present():
        verdict = {
            "story": "research-r6",
            "pass": False,
            "fence": "creds-absent",
            "oauth_cache_loaded": oauth,
        }
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
            "research_goal_id": "r6-live-intake",
        }
    )

    error = None
    packet_dump: dict = {}
    fabricate_red = False
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
        entry_dicts = [e.model_dump(mode="json") for e in entries]
        packet = consume_research_entries(
            entry_dicts,
            cluster_id="r6-live",
            intake_mode="corroborate",
            evidence_bolster_active=True,
        )
        packet_dump = packet.model_dump(mode="json")
        # Prove real ids resolve; fabricated id stays RED.
        real_ids = [e["source_id"] for e in entry_dicts[:3]]
        assert_no_fabricated_citations(real_ids, entry_dicts)
        try:
            assert_no_fabricated_citations(["10.9999/FABRICATED-CITE"], entry_dicts)
        except FabricatedCitationError:
            fabricate_red = True
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    overall = (
        error is None
        and packet_dump.get("entries_consumed", 0) >= 1
        and fabricate_red
        and not packet_dump.get("known_losses")
    )
    verdict = {
        "story": "research-r6",
        "oauth_cache_loaded": oauth,
        "entries_consumed": packet_dump.get("entries_consumed"),
        "attribution_phrases": packet_dump.get("attribution_phrases"),
        "fabricate_cite_path_red": fabricate_red,
        "error": error,
        "pass": overall,
    }
    (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (out_dir / "intake.json").write_text(json.dumps(packet_dump, indent=2), encoding="utf-8")
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# PROOF R6 Irene retrieval intake",
                "",
                f"pass={overall} consumed={packet_dump.get('entries_consumed')}",
                f"fabricate_cite_path_red={fabricate_red}",
                f"phrases={packet_dump.get('attribution_phrases')}",
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

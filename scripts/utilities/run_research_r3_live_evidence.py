#!/usr/bin/env python3
"""R3 live evidence — triangulator dual_provider via title-bridge.

Authentic live-test for Agentic Research Foundations story R3.
Dispatches Scite∩Consensus corroborate (evidence_bolster), then triangulates
with ``title_bridge=True`` so Consensus markdown titles resolve through Scite.

Usage (repo root)::

    python scripts/utilities/run_research_r3_live_evidence.py
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

from retrieval.consensus_provider import (  # noqa: E402
    ensure_consensus_bearer_from_mcp_auth,
)
from retrieval.dispatcher import dispatch as dispatch_intent  # noqa: E402
from retrieval.triangulator import (  # noqa: E402
    corroborate_requires_triangulation,
    triangulate_texas_rows,
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
        / f"research-r3-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    if not _scite_creds_present():
        missing.append("SCITE_USER_NAME/SCITE_PASSWORD")
    if not consensus_creds_present():
        missing.append("CONSENSUS_API_KEY or mcp-remote OAuth token (~/.mcp-auth)")
    if missing:
        verdict = {
            "story": "research-r3",
            "pass": False,
            "fence": "creds-absent",
            "missing": missing,
            "oauth_cache_loaded": oauth_loaded,
        }
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8"
        )
        (out_dir / "PROOF.md").write_text(
            "# PROOF R3 — FENCED\n\n"
            f"Missing credentials: {', '.join(missing)}\n",
            encoding="utf-8",
        )
        print(json.dumps(verdict, indent=2))
        return 2

    selector = DeterministicPostureSelector()
    brief = {
        "gap_type": "evidence",
        "claim": (
            "Worked examples improve novice transfer in introductory instruction."
        ),
        "source_context": (
            "Need a supporting citation for the worked-example rationale."
        ),
        "scope_decision": "in-scope",
        "evidence_bolster": True,
        "research_goal_id": "r3-live-triangulate",
    }
    intent = selector.select_posture(brief)

    error = None
    receipt_dump: dict = {}
    gate_ok = False
    gate_reason = ""
    try:
        result = dispatch_intent(intent)
        results = result if isinstance(result, list) else [result]
        rows = []
        for provider_result in results:
            rows.extend(list(getattr(provider_result, "rows", []) or []))
        receipt = triangulate_texas_rows(
            rows,
            query_intent=intent.intent,
            title_bridge=True,
            max_bridge_titles=5,
        )
        gate_ok, gate_reason = corroborate_requires_triangulation(receipt)
        receipt_dump = receipt.model_dump(mode="json")
    except Exception as exc:  # noqa: BLE001 — evidence capture
        error = f"{type(exc).__name__}: {exc}"

    meta = receipt_dump.get("metadata") or {}
    dual_count = int(meta.get("dual_provider_count") or 0)
    overall = (
        error is None
        and gate_ok
        and gate_reason == "dual_provider"
        and dual_count >= 1
    )

    dual_examples = []
    for row in receipt_dump.get("triangulated_rows") or []:
        if row.get("triangulation_status") != "dual_provider":
            continue
        dual_examples.append(
            {
                "identity_key": row.get("identity_key"),
                "source_id": row.get("source_id"),
                "reliability_score": row.get("reliability_score"),
                "providers": sorted((row.get("rows_by_provider") or {}).keys()),
                "contradiction_flags": row.get("contradiction_flags") or [],
            }
        )
        if len(dual_examples) >= 3:
            break

    verdict = {
        "story": "research-r3",
        "flag_detective": "MARCUS_RESEARCH_DETECTIVE_LIVE=1",
        "oauth_cache_loaded": oauth_loaded,
        "title_bridge": True,
        "gate_ok": gate_ok,
        "gate_reason": gate_reason,
        "metadata": meta,
        "dual_provider_examples": dual_examples,
        "error": error,
        "pass": overall,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    (out_dir / "receipt.json").write_text(
        json.dumps(receipt_dump, indent=2), encoding="utf-8"
    )
    (out_dir / "command-transcript.md").write_text(
        "\n".join(
            [
                "# R3 live command transcript",
                "",
                "```",
                "python scripts/utilities/run_research_r3_live_evidence.py",
                "```",
                "",
                f"Overall PASS={overall} reason={gate_reason}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    lines = [
        "# PROOF R3 live triangulation",
        "",
        f"pass={overall} reason={gate_reason}",
        f"metadata={meta}",
        "",
    ]
    for ex in dual_examples:
        lines.append(
            f"- dual `{ex.get('identity_key')}` providers={ex.get('providers')} "
            f"score={ex.get('reliability_score')}"
        )
    if error:
        lines.append(f"- error: `{error}`")
    lines.append("")
    (out_dir / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {out_dir}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())

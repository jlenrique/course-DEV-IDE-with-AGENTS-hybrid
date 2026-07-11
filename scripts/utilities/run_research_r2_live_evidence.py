#!/usr/bin/env python3
"""R2 live evidence — Scite∩Consensus corroborate via evidence_bolster.

Authentic live-test binding for Agentic Research Foundations story R2.
Shapes a corroborate intent with ``evidence_bolster=True`` through
``DeterministicPostureSelector``, then dispatches via Texas ``dispatch``
(cross_validate). Writes evidence under
``_bmad-output/implementation-artifacts/evidence/research-r2-<stamp>/``.

Usage (repo root, Scite + Consensus creds in ``.env``)::

    python scripts/utilities/run_research_r2_live_evidence.py
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


def _summarize_provider_results(result: object) -> dict:
    results = result if isinstance(result, list) else [result]
    providers: list[dict] = []
    for provider_result in results:
        rows = []
        for row in getattr(provider_result, "rows", []) or []:
            signal = getattr(row, "convergence_signal", None)
            rows.append(
                {
                    "provider": getattr(row, "provider", None),
                    "source_id": getattr(row, "source_id", None),
                    "title": getattr(row, "title", None),
                    "convergence": (
                        signal.model_dump()
                        if signal is not None and hasattr(signal, "model_dump")
                        else None
                    ),
                }
            )
        providers.append(
            {
                "provider": getattr(provider_result, "provider", None),
                "acceptance_met": getattr(provider_result, "acceptance_met", None),
                "row_count": len(rows),
                "rows": rows[:3],
            }
        )
    return {
        "provider_result_count": len(providers),
        "providers_seen": sorted(
            {p["provider"] for p in providers if p.get("provider")}
        ),
        "total_rows": sum(p["row_count"] for p in providers),
        "results": providers,
    }


def main() -> int:
    oauth_loaded = ensure_consensus_bearer_from_mcp_auth()
    os.environ.setdefault("CONSENSUS_MCP_URL", "https://mcp.consensus.app/mcp")

    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r2-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    if not _scite_creds_present():
        missing.append("SCITE_USER_NAME/SCITE_PASSWORD")
    if not consensus_creds_present():
        missing.append("CONSENSUS_API_KEY or mcp-remote OAuth token (~/.mcp-auth)")
    if missing:
        verdict = {
            "story": "research-r2",
            "pass": False,
            "fence": "creds-absent",
            "missing": missing,
            "oauth_cache_loaded": oauth_loaded,
        }
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8"
        )
        (out_dir / "PROOF.md").write_text(
            "# PROOF R2 — FENCED\n\n"
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
        "research_goal_id": "r2-live-corroborate-bolster",
    }
    intent = selector.select_posture(brief)
    named = [h.provider for h in intent.provider_hints]
    shape_ok = named == ["scite", "consensus"] and intent.cross_validate is True

    error = None
    summary: dict = {}
    try:
        result = dispatch_intent(intent)
        summary = _summarize_provider_results(result)
    except Exception as exc:  # noqa: BLE001 — evidence capture
        error = f"{type(exc).__name__}: {exc}"

    providers_seen = set(summary.get("providers_seen") or [])
    dual_dispatch = summary.get("provider_result_count", 0) >= 2
    dual_live = {"scite", "consensus"} <= providers_seen
    overall = shape_ok and error is None and dual_dispatch

    verdict = {
        "story": "research-r2",
        "flag_detective": "MARCUS_RESEARCH_DETECTIVE_LIVE=1",
        "evidence_bolster": True,
        "oauth_cache_loaded": oauth_loaded,
        "intent_providers": named,
        "cross_validate": intent.cross_validate,
        "intent_text": intent.intent,
        "shape_ok": shape_ok,
        "dual_dispatch": dual_dispatch,
        "dual_live_rows": dual_live,
        "error": error,
        "summary": summary,
        "pass": overall,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    (out_dir / "command-transcript.md").write_text(
        "\n".join(
            [
                "# R2 live command transcript",
                "",
                "```",
                "python scripts/utilities/run_research_r2_live_evidence.py",
                "```",
                "",
                f"Overall PASS={overall}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    lines = [
        "# PROOF R2 — Consensus evidence-bolster live",
        "",
        "- detective ON + `evidence_bolster=True`",
        f"- intent providers: `{named}` cross_validate={intent.cross_validate}",
        f"- dual_dispatch={dual_dispatch} total_rows={summary.get('total_rows')}",
        f"- overall PASS={overall}",
        "",
    ]
    if error:
        lines.append(f"- error: `{error}`")
    for block in summary.get("results") or []:
        lines.append(
            f"- provider `{block.get('provider')}`: rows={block.get('row_count')} "
            f"acceptance_met={block.get('acceptance_met')}"
        )
        for row in block.get("rows") or []:
            lines.append(f"  - `{row.get('source_id')}` — {row.get('title')}")
    lines.append("")
    (out_dir / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {out_dir}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())

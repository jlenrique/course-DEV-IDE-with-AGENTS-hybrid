#!/usr/bin/env python3
"""R1 live evidence — Scite corroborate + gap_fill via production posture seam.

Authentic live-test binding for Agentic Research Foundations story R1.
Shapes intents through ``DeterministicPostureSelector`` with
``MARCUS_RESEARCH_DETECTIVE_LIVE=1``, then dispatches via Texas ``dispatch``
(Scite MCP). Writes an evidence pack under
``_bmad-output/implementation-artifacts/evidence/research-r1-<stamp>/``.

Usage (repo root, with Scite creds in ``.env``)::

    python scripts/utilities/run_research_r1_live_evidence.py
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

from retrieval.dispatcher import dispatch as dispatch_intent  # noqa: E402

from app.marcus.orchestrator.research_wiring import (  # noqa: E402
    DeterministicPostureSelector,
    resolve_research_posture,
)


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _scite_creds_present() -> bool:
    return bool(
        os.environ.get("SCITE_USER_NAME", "").strip()
        and os.environ.get("SCITE_PASSWORD", "").strip()
    )


def _rows_from_dispatch(result: object) -> list[dict]:
    results = result if isinstance(result, list) else [result]
    rows: list[dict] = []
    for provider_result in results:
        for row in getattr(provider_result, "rows", []) or []:
            rows.append(
                {
                    "provider": getattr(row, "provider", None),
                    "source_id": getattr(row, "source_id", None),
                    "title": getattr(row, "title", None),
                    "url": getattr(row, "url", None),
                    "acceptance_met": getattr(
                        provider_result, "acceptance_met", None
                    ),
                }
            )
    return rows


def _run_case(
    *,
    case_id: str,
    brief: dict,
    selector: DeterministicPostureSelector,
) -> dict:
    posture = resolve_research_posture(brief)
    intent = selector.select_posture(brief)
    hint_params = dict(intent.provider_hints[0].params)
    try:
        result = dispatch_intent(intent)
        rows = _rows_from_dispatch(result)
        error = None
    except Exception as exc:  # noqa: BLE001 — evidence capture
        rows = []
        error = f"{type(exc).__name__}: {exc}"
    return {
        "case_id": case_id,
        "resolved_posture": posture,
        "intent_text": intent.intent,
        "hint_params": hint_params,
        "providers": [h.provider for h in intent.provider_hints],
        "row_count": len(rows),
        "rows": rows[:5],
        "error": error,
        "pass": error is None and len(rows) >= 1,
    }


def main() -> int:
    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r1-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if not _scite_creds_present():
        verdict = {
            "story": "research-r1",
            "pass": False,
            "reason": "SCITE_USER_NAME / SCITE_PASSWORD absent",
        }
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8"
        )
        (out_dir / "PROOF.md").write_text(
            "# PROOF R1 — FAIL\n\nScite credentials absent.\n",
            encoding="utf-8",
        )
        print(json.dumps(verdict, indent=2))
        return 2

    selector = DeterministicPostureSelector()

    # Corroborate — tracy_smoke claim (Tejal-adjacent pedagogy claim).
    corroborate_brief = {
        "gap_type": "evidence",
        "claim": (
            "Worked examples improve novice transfer in introductory instruction."
        ),
        "source_context": (
            "Need a supporting citation for the worked-example rationale."
        ),
        "scope_decision": "in-scope",
        "research_goal_id": "r1-live-corroborate",
    }
    # Gap-fill — research_goals-shaped brief (Irene Pass-1 mechanical carry).
    gap_fill_brief = {
        "gap_description": (
            "Learners need prerequisite background on cognitive apprenticeship "
            "before applying modeling and coaching moves."
        ),
        "target_element": "LO-cognitive-apprenticeship",
        "research_goal_id": "r1-live-gap-fill",
        "scope_decision": "in-scope",
        "content_type": "background",
    }

    cases = [
        _run_case(
            case_id="corroborate",
            brief=corroborate_brief,
            selector=selector,
        ),
        _run_case(
            case_id="gap_fill",
            brief=gap_fill_brief,
            selector=selector,
        ),
    ]

    overall = all(c["pass"] for c in cases)
    verdict = {
        "story": "research-r1",
        "flag": "MARCUS_RESEARCH_DETECTIVE_LIVE=1",
        "seam": "DeterministicPostureSelector + Texas dispatch",
        "pass": overall,
        "cases": cases,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    (out_dir / "command-transcript.md").write_text(
        "\n".join(
            [
                "# R1 live command transcript",
                "",
                "```",
                "python scripts/utilities/run_research_r1_live_evidence.py",
                "```",
                "",
                f"Overall PASS={overall}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    lines = [
        "# PROOF R1 — Posture runtime live Scite",
        "",
        "- detective flag ON: `MARCUS_RESEARCH_DETECTIVE_LIVE=1`",
        "- seam: DeterministicPostureSelector → Texas `dispatch` → Scite",
        f"- overall PASS={overall}",
        "",
    ]
    for case in cases:
        lines.append(
            f"- **{case['case_id']}**: posture={case['resolved_posture']} "
            f"rows={case['row_count']} pass={case['pass']}"
        )
        if case["error"]:
            lines.append(f"  - error: `{case['error']}`")
        elif case["rows"]:
            first = case["rows"][0]
            lines.append(
                f"  - sample: `{first.get('source_id')}` — {first.get('title')}"
            )
    lines.append("")
    (out_dir / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {out_dir}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())

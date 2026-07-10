"""Mine 1 liveproof: lesson_plan.collateral → ComponentSelection (Option A).

Banks under runs/<uuid>/ + evidence stamp. No Gamma spend.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.collateral_selection import (  # noqa: E402
    CollateralSelectionError,
    derive_selection_from_lesson_plan,
    load_selection_from_lesson_plan_json,
)
from app.marcus.lesson_plan.composition import compose_and_digest  # noqa: E402
from app.marcus.lesson_plan.collateral_spec import (  # noqa: E402
    CollateralSpec,
    DepthDeltaContract,
    WorkbookSection,
    WorkbookSpec,
)
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.specialists.irene_pass1._act import write_lesson_plan  # noqa: E402


def _workbook_plan() -> dict:
    collateral = CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(
            sections=[
                WorkbookSection(
                    section_id="sec-1",
                    learning_objective_id="obj-1",
                    title="Read in depth",
                    depth_delta=DepthDeltaContract(
                        deferred_from_slide="slide-1",
                        deferred_depth="the supporting method",
                    ),
                )
            ]
        ),
    )
    return {
        "lesson_summary": "Mine-1 auto-selection liveproof plan",
        "plan_units": [
            {
                "unit_id": "u1",
                "title": "Bridge",
                "learning_objective": "Map radar to leadership",
                "scope_decision": "in-scope",
                "rationale": "core",
            }
        ],
        "collateral": collateral.model_dump(mode="json"),
    }


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    runs_root = REPO / "runs"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine1-auto-selection-{stamp}"
    )
    evidence.mkdir(parents=True)
    item_ev = evidence / "automatic-lesson-plan"
    item_ev.mkdir()

    plan = _workbook_plan()
    md_path = write_lesson_plan(plan, run_id=run_id, runs_root=runs_root)
    json_path = run_dir / "irene-pass1.lesson-plan.json"
    assert json_path.is_file(), "machine-readable plan JSON missing"

    derived = load_selection_from_lesson_plan_json(json_path)
    assert derived.source == "plan_collateral"
    assert derived.bundle_id == "narrated-deck-with-workbook"
    assert derived.selection == ComponentSelection(
        deck=True, motion=True, workbook=True
    )

    # Consumer: compose_and_digest reads the derived selection (not baseline).
    baseline = ComponentSelection.production_default()
    assert derived.selection != baseline
    digest = compose_and_digest(derived.selection)

    # Negative: absent collateral fails loud
    neg_ok = False
    try:
        derive_selection_from_lesson_plan({"plan_units": []})
    except CollateralSelectionError:
        neg_ok = True

    selection_receipt = {
        "lesson_plan_ref": str(json_path.as_posix()),
        "bundle_id": derived.bundle_id,
        "selection": derived.selection.as_map(),
        "source": derived.source,
        "composed_graph_digest": digest.composed_graph_digest,
        "baseline_differs": derived.selection != baseline,
    }
    (run_dir / "component_selection.json").write_text(
        json.dumps(selection_receipt, indent=2), encoding="utf-8"
    )

    verdict = {
        "item": "automatic-lesson-plan",
        "predicate": "plan_collateral_derives_selection_and_compose_consumes",
        "pass": bool(
            json_path.is_file()
            and md_path.is_file()
            and derived.source == "plan_collateral"
            and derived.selection.workbook is True
            and digest.composed_graph_digest
            and neg_ok
        ),
        "actual": selection_receipt,
        "negative_absent_collateral_fail_loud": neg_ok,
        "run_dir": str(run_dir.as_posix()),
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8"
    )
    (evidence / "PROOF.md").write_text(
        f"# Mine 1 PROOF — Automatic Lesson_plan\n\n"
        f"**Stamp:** {stamp}\n"
        f"**RUN:** `runs/{run_id}/`\n"
        f"**Pass:** {verdict['pass']}\n"
        f"**Bundle:** {derived.bundle_id}\n"
        f"**Source:** {derived.source}\n"
        f"**Compose digest:** {digest.composed_graph_digest[:16]}…\n"
        f"**Negative fail-loud:** {neg_ok}\n"
        f"**Non-claims:** Gamma not invoked; SPOC REPL not claimed.\n",
        encoding="utf-8",
    )
    print(json.dumps({"pass": verdict["pass"], "run_id": run_id, "evidence": str(evidence)}, indent=2))
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

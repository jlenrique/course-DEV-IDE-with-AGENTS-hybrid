"""Mine 2A liveproof: interactive plan-dialogue → ratification + LO companions.

Scripted REPL (confirm-before-write) under runs/<uuid>/; evidence stamp.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.cli.plan_dialogue_cli import main as plan_dialogue_main  # noqa: E402
from app.marcus.lesson_plan.planning_context import load_planning_context  # noqa: E402

TEJAL = (
    REPO
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine2a-interactive-planning-{stamp}"
    )
    item_ev = evidence / "interactive-spoc"
    item_ev.mkdir(parents=True)

    script = run_dir / "plan-dialogue-script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "Bridge assessments to Module 2 via interactive SPOC planning",
                "audience": "APC C1 learners",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait,ask_operator",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "Rich Tejal leaf; synthesize framing for Mine 2A",
                "learning_objectives": [
                    "Map radar trends to clinical leadership decisions",
                    "Apply assessment-bridge framing to Module 2 handoff",
                ],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )

    # Negative: malformed workflow must fail before write
    bad_script = run_dir / "bad-script.yaml"
    bad_script.write_text(
        yaml.safe_dump(
            {
                "purpose": "p",
                "audience": "a",
                "workflow": "bogus-workflow",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "learning_objectives": ["x"],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    bad_code = plan_dialogue_main(
        [
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(run_dir / "negative-malformed"),
            "--script",
            str(bad_script),
        ]
    )
    negative_malformed_ok = bad_code == 2

    code = plan_dialogue_main(
        [
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(run_dir),
            "--script",
            str(script),
        ]
    )
    ctx = load_planning_context(run_dir)
    transcript = run_dir / "marcus-planning-dialogue.md"
    companion = run_dir / "planning-ratification.json"
    intent = run_dir / "ratified-collateral-intent.yaml"
    los = run_dir / "ratified-los.json"

    turn_count = 0
    if transcript.is_file():
        turn_count = transcript.read_text(encoding="utf-8").count("## Turn ")

    predicates = {
        "cli_exit_0": code == 0,
        "companion_present": companion.is_file(),
        "intent_present": intent.is_file(),
        "ratified_los_present": los.is_file(),
        "transcript_present": transcript.is_file(),
        "transcript_turns_ge_2": turn_count >= 2,
        "planning_context_has_framing": bool(ctx and ctx.has_framing()),
        "planning_context_lo_count_ge_1": bool(
            ctx and len(ctx.learning_objectives) >= 1
        ),
        "negative_malformed_fail_loud": negative_malformed_ok,
        "run_id": run_id,
        "turn_count": turn_count,
    }
    passed = all(
        predicates[k]
        for k in predicates
        if k not in {"run_id", "turn_count"}
    )
    verdict = {
        "item": "interactive-spoc",
        "mine": "2A",
        "pass": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "stamp": stamp,
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    # Mirror key artifacts into evidence
    for name in (
        "planning-ratification.json",
        "ratified-collateral-intent.yaml",
        "ratified-los.json",
        "marcus-planning-dialogue.md",
    ):
        src = run_dir / name
        if src.is_file():
            (item_ev / name).write_bytes(src.read_bytes())

    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

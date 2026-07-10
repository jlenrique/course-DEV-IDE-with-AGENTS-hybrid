"""Mine-next N2-lite liveproof: SPOC --plan-dialogue writes companions."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.cli.marcus_spoc import main as spoc_main  # noqa: E402
from app.marcus.cli.plan_dialogue_cli import PlanDialogueError  # noqa: E402
from app.marcus.cli.marcus_spoc import run_plan_dialogue_preflight  # noqa: E402
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
        / f"mine-next-n2-spoc-plan-dialogue-{stamp}"
    )
    item_ev = evidence / "spoc-plan-dialogue"
    item_ev.mkdir(parents=True)

    script = run_dir / "plan-dialogue-script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "SPOC-owned LO + workflow ratification (N2-lite)",
                "audience": "APC C1 learners",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait,ask_operator",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "Tejal leaf; SPOC surface not CLI-only",
                "learning_objectives": [
                    "Map radar trends to clinical leadership decisions",
                    "Apply assessment-bridge framing to Module 2 handoff",
                ],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )

    # Negative: confirm decline via SPOC preflight
    decline = run_dir / "decline.yaml"
    decline.write_text(
        yaml.safe_dump(
            {
                "purpose": "p",
                "audience": "a",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "learning_objectives": ["x"],
                "confirm": "no",
            }
        ),
        encoding="utf-8",
    )
    decline_ok = False
    try:
        run_plan_dialogue_preflight(
            corpus_dir=TEJAL,
            output_dir=run_dir / "negative-decline",
            script=decline,
        )
    except PlanDialogueError:
        decline_ok = True

    code = spoc_main(
        [
            "--plan-dialogue",
            "--corpus-dir",
            str(TEJAL),
            "--plan-output-dir",
            str(run_dir),
            "--plan-script",
            str(script),
        ]
    )
    ctx = load_planning_context(run_dir)
    los_path = run_dir / "ratified-los.json"
    los = json.loads(los_path.read_text(encoding="utf-8")) if los_path.is_file() else {}

    predicates = {
        "spoc_exit_0": code == 0,
        "companion_written": (run_dir / "planning-ratification.json").is_file(),
        "intent_written": (run_dir / "ratified-collateral-intent.yaml").is_file(),
        "los_written": los_path.is_file(),
        "los_count_2": len(los.get("ratified_los") or []) == 2,
        "planning_context_framing": ctx is not None and ctx.has_framing(),
        "confirm_decline_fail_loud": decline_ok,
        "run_id": run_id,
    }
    passed = all(
        predicates[k]
        for k in (
            "spoc_exit_0",
            "companion_written",
            "intent_written",
            "los_written",
            "los_count_2",
            "planning_context_framing",
            "confirm_decline_fail_loud",
        )
    )

    verdict = {
        "lane": "N2",
        "name": "spoc-plan-dialogue-wire",
        "passed": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item_ev / "command-transcript.md").write_text(
        f"# N2 SPOC plan-dialogue liveproof\n\n"
        f"python -m app.marcus.cli.marcus_spoc --plan-dialogue "
        f"--corpus-dir <tejal> --plan-output-dir {run_dir} --plan-script …\n\n"
        f"passed={passed}\n",
        encoding="utf-8",
    )
    (item_ev / "PROOF.md").write_text(
        "# PROOF N2\n\n- SPOC surface owns LO + workflow ratification\n"
        f"- companions under runs/{run_id}/\n"
        f"- decline fail-loud={decline_ok}\n- PASS={passed}\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Mine-next trust T4b + T4c liveproof.

T4b: positive-carry (source∩deck must appear in narration), flag-gated.
T4c: flag-ON activation over REAL offline Pass-2 artifacts (no fresh Gamma):
  clean twin sails; confab halt; positive-carry miss halt; flag-OFF inert.

Uses Leg-3 c-u03 Pass-2 + perception artifacts (real gpt-5.5 production output).
"""

from __future__ import annotations

import copy
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.specialists._shared.figure_tokens import _figures  # noqa: E402
from app.specialists.irene.graph import (  # noqa: E402
    FIGURE_FIDELITY_ACTIVE_ENV,
    Pass2GroundingError,
    _assert_figure_citations_within_perceived,
    _assert_narration_figures_sourced,
    _assert_source_figures_positively_carried,
    _slide_roster,
    narration_figure_fidelity_active,
)

LEG3 = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence"
    / "leg3-cu03-subslide-invariant-20260701T021037Z"
)
# Source corpus matching the Leg-3 probe (digit-form figures the deck carries).
SOURCE = (
    "Medical knowledge that once took 50 years to double now doubles in just "
    "73 days. Adoption is already here — 66% of physicians report using some "
    "form of AI — while formal oversight training remains limited."
)


def _bank(slug: str, lane: str, name: str, predicates: dict, transcript: str) -> bool:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)
    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"{slug}-{stamp}"
    )
    item = evidence / name
    item.mkdir(parents=True)
    bool_keys = [k for k, v in predicates.items() if isinstance(v, bool)]
    passed = all(predicates[k] for k in bool_keys)
    verdict = {
        "lane": lane,
        "name": name,
        "passed": passed,
        "predicates": {**predicates, "run_id": run_id},
        "run_dir": str(run_dir),
        "artifact_source": str(LEG3),
    }
    (item / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item / "command-transcript.md").write_text(transcript, encoding="utf-8")
    (item / "PROOF.md").write_text(
        f"# PROOF {lane}\n\n{json.dumps(predicates, indent=2)}\n\nPASS={passed}\n",
        encoding="utf-8",
    )
    # Fresh asset copies under the run dir for Murat stampability.
    (run_dir / "source.md").write_text(SOURCE, encoding="utf-8")
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return passed


def _payload_from_leg3() -> tuple[dict, dict]:
    parsed = json.loads((LEG3 / "pass2-output.json").read_text(encoding="utf-8"))
    artifacts = json.loads(
        (LEG3 / "perception-artifacts.json").read_text(encoding="utf-8")
    )
    envelope = {
        "bundle_reference": str(LEG3),
        "lesson_plan": {"title": "c-u03 per-subslide (real Pass-2)"},
        "gary_slide_output": [
            {
                "slide_id": a["slide_id"],
                "visual_description": a.get("slide_title") or a.get("extracted_text", "")[:80],
            }
            for a in artifacts
        ],
        "slide_briefs": [
            {"slide_id": a["slide_id"], "prompt": "stat"} for a in artifacts
        ],
        "perception_artifacts": artifacts,
    }
    return envelope, parsed


def main() -> int:
    lines: list[str] = ["# T4b/T4c liveproof transcript\n"]
    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    default_off = not narration_figure_fidelity_active()
    lines.append(f"default_flag_off={default_off}")

    envelope, parsed = _payload_from_leg3()
    roster = _slide_roster(envelope)
    source_figs = sorted(_figures(SOURCE))
    lines.append(f"source_figures={source_figs}")
    for entry in roster:
        lines.append(
            f"  deck[{entry['slide_id']}]="
            f"{sorted(entry.get('perceived_figures') or [])}"
        )

    # ---- T4b synthetic RED/GREEN (unit-level liveproof) ----
    os.environ[FIGURE_FIDELITY_ACTIVE_ENV] = "1"
    head = roster[0]
    head_id = head["slide_id"]
    # Build a minimal single-slide roster that requires percent:66 carry.
    mini_env = {
        "bundle_reference": "mini",
        "lesson_plan": {"title": "t"},
        "gary_slide_output": [{"slide_id": head_id, "visual_description": "x"}],
        "slide_briefs": [{"slide_id": head_id, "prompt": "x"}],
        "perception_artifacts": [
            a for a in envelope["perception_artifacts"] if a["slide_id"] == head_id
        ],
    }
    mini_roster = _slide_roster(mini_env)
    miss = {
        "narration_script": [
            {
                "id": "seg-miss",
                "slide_id": head_id,
                "narration_text": "Adoption is climbing across many teams.",
            }
        ],
        "segment_manifest_deltas": [],
    }
    carry_miss_raised = False
    try:
        _assert_source_figures_positively_carried(
            miss, mini_roster, source_text=SOURCE
        )
    except Pass2GroundingError as exc:
        carry_miss_raised = exc.tag == "irene.pass2.figure-positive-carry-miss"

    happy = {
        "narration_script": [
            {
                "id": "seg-ok",
                "slide_id": head_id,
                "narration_text": (
                    "Adoption is already here — 66% of physicians report using AI."
                ),
            }
        ],
        "segment_manifest_deltas": [],
    }
    _assert_figure_citations_within_perceived(happy, mini_roster)
    _assert_narration_figures_sourced(happy, mini_roster, source_text=SOURCE)
    _assert_source_figures_positively_carried(happy, mini_roster, source_text=SOURCE)

    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    _assert_source_figures_positively_carried(miss, mini_roster, source_text=SOURCE)
    flag_off_inert = True

    t4b = {
        "default_flag_off": default_off,
        "carry_miss_raises": carry_miss_raised,
        "happy_path_no_raise": True,
        "flag_off_inert": flag_off_inert,
        "source_has_percent_66": "percent:66" in source_figs,
    }
    p4b = _bank(
        "mine-next-trust-t4b-positive-carry",
        "T4b",
        "positive-carry",
        t4b,
        "\n".join(lines) + "\n",
    )

    # ---- T4c: flag-ON over REAL Pass-2 artifacts ----
    lines2 = ["# T4c flag-ON activation over real Pass-2 artifacts\n"]
    os.environ[FIGURE_FIDELITY_ACTIVE_ENV] = "1"
    assert narration_figure_fidelity_active()

    # (i) real narration sails deck + source + positive-carry
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=SOURCE)
    _assert_source_figures_positively_carried(parsed, roster, source_text=SOURCE)
    lines2.append("(i) REAL narration SAILS deck + source + positive-carry")

    # (ii-a) confab halt
    defect_a = copy.deepcopy(parsed)
    defect_a["narration_script"][0]["narration_text"] += (
        " The addressable market is $4.6B this year."
    )
    confab_tag = ""
    try:
        _assert_narration_figures_sourced(defect_a, roster, source_text=SOURCE)
        lines2.append("(ii-a) FAILED TO RAISE on $4.6B confab")
    except Pass2GroundingError as exc:
        confab_tag = exc.tag
        lines2.append(f"(ii-a) confab RAISED tag={exc.tag}")

    # (ii-b) positive-carry miss on real roster: strip 66% from head narration
    defect_b = copy.deepcopy(parsed)
    defect_b["narration_script"][0]["narration_text"] = (
        "Medical knowledge is accelerating. Stewardship becomes part of your role."
    )
    # Source-direction may still pass (no unsourced digit figures); carry must raise.
    _assert_narration_figures_sourced(defect_b, roster, source_text=SOURCE)
    carry_tag = ""
    try:
        _assert_source_figures_positively_carried(
            defect_b, roster, source_text=SOURCE
        )
        lines2.append("(ii-b) FAILED TO RAISE on positive-carry miss")
    except Pass2GroundingError as exc:
        carry_tag = exc.tag
        lines2.append(f"(ii-b) carry-miss RAISED tag={exc.tag}")

    # (iii) flag-OFF firewall
    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    _assert_narration_figures_sourced(defect_a, roster, source_text=SOURCE)
    _assert_source_figures_positively_carried(defect_b, roster, source_text=SOURCE)
    lines2.append("(iii) flag-OFF firewall: defects INERT")

    t4c = {
        "flag_on_active": True,  # was True during (i)/(ii)
        "real_narration_sails": True,
        "confab_halt": confab_tag == "irene.pass2.figure-unsourced",
        "positive_carry_halt": carry_tag == "irene.pass2.figure-positive-carry-miss",
        "flag_off_firewall": True,
        "default_remains_off_after": not narration_figure_fidelity_active(),
        "note_no_default_on": True,  # activation proven; default stays OFF
    }
    # Reset the transient flag_on_active truth for the bank (we popped env).
    t4c["flag_on_active"] = confab_tag != "" and carry_tag != ""
    p4c = _bank(
        "mine-next-trust-t4c-flag-on-activation",
        "T4c",
        "flag-on-activation",
        t4c,
        "\n".join(lines2) + "\n",
    )

    return 0 if (p4b and p4c) else 1


if __name__ == "__main__":
    raise SystemExit(main())

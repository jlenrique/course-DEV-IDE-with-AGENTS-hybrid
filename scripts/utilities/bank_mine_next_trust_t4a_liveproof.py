"""Mine-next trust T4a liveproof: fidelity precision (flag stays OFF by default)."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.specialists._shared.figure_tokens import (  # noqa: E402
    PERCENT_TOLERANCE_PP,
    _figure_near_match,
    _figures,
)
from app.specialists.irene.graph import (  # noqa: E402
    FIGURE_FIDELITY_ACTIVE_ENV,
    Pass2GroundingError,
    _assert_narration_figures_sourced,
    _slide_roster,
    narration_figure_fidelity_active,
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)
    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine-next-trust-t4a-fidelity-precision-{stamp}"
    )
    item = evidence / "fidelity-precision"
    item.mkdir(parents=True)

    # Default OFF
    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    default_off = not narration_figure_fidelity_active()

    os.environ[FIGURE_FIDELITY_ACTIVE_ENV] = "1"
    source_figs = _figures("Adoption rose to 67% while 18.4% still lag.")
    near = _figure_near_match("percent:18", source_figs)
    far = _figure_near_match("percent:60", source_figs)
    comma = "money-trillion:1.2" in _figures("$1,200 billion")
    plain = "money-trillion:1.2" in _figures("$1200 billion")

    payload = {
        "bundle_reference": "bundle",
        "lesson_plan": {"title": "t"},
        "gary_slide_output": [{"slide_id": "s1", "visual_description": "x"}],
        "slide_briefs": [{"slide_id": "s1", "prompt": "x"}],
        "perception_artifacts": [
            {
                "slide_id": "s1",
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": "18% still lag",
                "layout_description": "x",
                "slide_title": "x",
                "text_blocks": [{"text": "18% still lag", "role": "callout"}],
                "visual_elements": [{"kind": "stat_callout", "text": "18% still lag"}],
                "source_png_path": "bundle/s1.png",
            }
        ],
    }
    roster = _slide_roster(payload)
    parsed = {
        "narration_script": [
            {"id": "seg-1", "slide_id": "s1", "narration_text": "About 18% still lag."}
        ],
        "segment_manifest_deltas": [],
    }
    _assert_narration_figures_sourced(
        parsed, roster, source_text="Adoption rose while 18.4% still lag."
    )
    conflict_raised = False
    try:
        _assert_narration_figures_sourced(
            {
                "narration_script": [
                    {
                        "id": "seg-1",
                        "slide_id": "s1",
                        "narration_text": "Adoption climbed to 60%.",
                    }
                ],
                "segment_manifest_deltas": [],
            },
            _slide_roster(
                {
                    **payload,
                    "perception_artifacts": [
                        {
                            **payload["perception_artifacts"][0],
                            "extracted_text": "60% adoption",
                            "text_blocks": [{"text": "60% adoption", "role": "callout"}],
                            "visual_elements": [
                                {"kind": "stat_callout", "text": "60% adoption"}
                            ],
                        }
                    ],
                }
            ),
            source_text="Adoption reached 67% this year.",
        )
    except Pass2GroundingError:
        conflict_raised = True

    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)

    predicates = {
        "default_flag_off": default_off,
        "percent_tolerance_band": PERCENT_TOLERANCE_PP == 0.6,
        "near_match_18_4_to_18": near,
        "far_match_67_to_60_rejected": not far,
        "comma_money_parses": comma,
        "plain_money_parses": plain,
        "tolerant_gate_no_raise": True,
        "real_conflict_still_raises": conflict_raised,
        "run_id": run_id,
    }
    passed = all(v for k, v in predicates.items() if k != "run_id")
    verdict = {
        "lane": "T4a",
        "name": "fidelity-precision-before-flag-on",
        "passed": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "note": "Flag remains default-OFF; positive-carry + live activation still OPEN",
    }
    (item / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item / "command-transcript.md").write_text(
        f"# T4a fidelity precision\n\npassed={passed}\nflag default OFF\n",
        encoding="utf-8",
    )
    (item / "PROOF.md").write_text(
        "# PROOF T4a\n\n- percent tolerance 18.4→18\n- comma money surfaces\n"
        f"- conflict 67 vs 60 still raises\n- PASS={passed}\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

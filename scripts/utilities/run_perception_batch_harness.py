#!/usr/bin/env python3
"""A2 perception harness CLI — offline scaffolding + optional --run-live.

Hermetic done-bar is pytest. Live arm never gates CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime.llm_batch.perception_harness import (  # noqa: E402
    HARNESS_BASELINE_BATCH_ID,
    assert_frozen_fixtures_present,
    compare_arm_scores,
    run_live_compare,
    score_perception,
    write_compare_report,
)
from app.specialists.vision.payload_contract import VisionProviderResponse  # noqa: E402


def _offline_demo_report(out: Path) -> Path:
    """Write a scaffolding compare report from synthetic scores (no network)."""

    slides = assert_frozen_fixtures_present()
    rt = []
    bt = []
    for slide_id, _ in slides:
        synth = VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",  # type: ignore[arg-type]
            slide_title=f"offline-{slide_id}",
            extracted_text="offline scaffolding text",
            layout_description="offline layout",
            visual_elements=[{"kind": "title", "role_tier": "2"}],
            provider_model_id="gpt-5.5",
        )
        rt.append(score_perception(synth, arm="realtime"))
        bt.append(score_perception(synth, arm="batch"))
    report = compare_arm_scores(rt, bt)
    report.notes.append("offline scaffolding demo — not live quality evidence")
    return write_compare_report(out, report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "A2 perception eval harness (LiteLLM). "
            "Default: offline scaffolding. Optional --run-live for API compare."
        )
    )
    parser.add_argument(
        "--run-live",
        action="store_true",
        help="Call realtime + batch arms (requires API keys). Never gates CI.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=REPO_ROOT / "_artifacts" / "current-trial" / "runs",
        help="Runs root for batch receipts when --run-live",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run id for live batch (default: harness-<utc>)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Compare report JSON path",
    )
    args = parser.parse_args(argv)

    slides = assert_frozen_fixtures_present()
    print(f"frozen_slides={len(slides)}")
    print(f"narrative_baseline_batch_id={HARNESS_BASELINE_BATCH_ID}")

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = args.output or (
        REPO_ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"a2-perception-harness-{stamp}"
        / "compare-report.json"
    )

    if not args.run_live:
        path = _offline_demo_report(out)
        print(f"offline_report={path}")
        print(json.dumps({"mode": "offline", "path": str(path)}, indent=2))
        return 0

    run_id = args.run_id or f"a2-harness-{stamp}"
    report = run_live_compare(
        runs_root=args.runs_root,
        run_id=run_id,
        output_path=out,
    )
    print(f"live_report={out}")
    print(
        json.dumps(
            {
                "mode": "live",
                "path": str(out),
                "both_arms_non_vacuous": report.both_arms_non_vacuous,
                "delta_count": len(report.deltas),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Mine 6 liveproof: before/after learner-ready prose uplift with SME voice."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.prose_uplift import (  # noqa: E402
    measure_prose_delta,
    sme_aware_prose_revoicer,
)
from app.marcus.lesson_plan.workbook_producer import (  # noqa: E402
    REVOICE_REQUIRED_MARKER,
    default_prose_revoicer,
)

# Real-ish workbook segment language (deixis-laden transcript scaffold)
_SEGMENTS = (
    (
        "seg-01",
        "Here you see the 70% clinician burnout figure on the slide. "
        "As you can see, this chart frames why leadership must act.",
    ),
    (
        "seg-02",
        "Look at this figure: on the slide, the radar trend sits beside "
        "the assessment bridge. Click next when ready.",
    ),
    (
        "seg-03",
        "In this slide, as shown above, the Module 2 handoff depends on "
        "this chart of opportunity signals.",
    ),
)


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine6-prose-uplift-{stamp}"
    )
    item_ev = evidence / "workbook-learner-ready-prose-uplift"
    item_ev.mkdir(parents=True)

    revoicer = sme_aware_prose_revoicer("tejal")
    before_parts: list[str] = []
    after_parts: list[str] = []
    per_seg: list[dict] = []
    for seg_id, text in _SEGMENTS:
        before = default_prose_revoicer(seg_id, text)
        after = revoicer(seg_id, text)
        delta = measure_prose_delta(before, after)
        before_parts.append(f"## {seg_id}\n\n{before}\n")
        after_parts.append(f"## {seg_id}\n\n{after}\n")
        per_seg.append({"segment_id": seg_id, **delta.to_dict()})

    before_doc = "# BEFORE (default scaffold)\n\n" + "\n".join(before_parts)
    after_doc = "# AFTER (Tejal SME uplift)\n\n" + "\n".join(after_parts)
    (run_dir / "workbook-prose-before.md").write_text(before_doc, encoding="utf-8")
    (run_dir / "workbook-prose-after.md").write_text(after_doc, encoding="utf-8")

    # Idempotency: second uplift on after_doc segments
    second_pass = revoicer("seg-01", after_parts[0])
    idempotent = (
        REVOICE_REQUIRED_MARKER not in second_pass
        and second_pass.count("Voice profile:") == 1
    )

    total_before_markers = before_doc.count(REVOICE_REQUIRED_MARKER)
    total_after_markers = after_doc.count(REVOICE_REQUIRED_MARKER)
    deixis_before = sum(d["deixis_hits_before"] for d in per_seg)
    deixis_after = sum(d["deixis_hits_after"] for d in per_seg)

    predicates = {
        "markers_cleared": total_before_markers >= 3 and total_after_markers == 0,
        "deixis_reduced": deixis_after < deixis_before,
        "sme_attribution_present": "Tejal" in after_doc or "tejal" in after_doc.lower(),
        "idempotent_second_pass": idempotent,
        "per_segment_deltas": len(per_seg) == 3,
        "run_id": run_id,
        "total_before_markers": total_before_markers,
        "total_after_markers": total_after_markers,
        "deixis_before": deixis_before,
        "deixis_after": deixis_after,
        "per_seg": per_seg,
    }
    passed = all(
        predicates[k]
        for k in (
            "markers_cleared",
            "deixis_reduced",
            "sme_attribution_present",
            "idempotent_second_pass",
            "per_segment_deltas",
        )
    )
    verdict = {
        "item": "workbook-learner-ready-prose-uplift",
        "mine": "6",
        "pass": passed,
        "predicates": predicates,
        "run_dir": str(run_dir),
        "stamp": stamp,
    }
    (item_ev / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (item_ev / "workbook-prose-before.md").write_bytes(
        (run_dir / "workbook-prose-before.md").read_bytes()
    )
    (item_ev / "workbook-prose-after.md").write_bytes(
        (run_dir / "workbook-prose-after.md").read_bytes()
    )
    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

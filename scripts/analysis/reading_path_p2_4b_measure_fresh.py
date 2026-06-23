"""Measure LLM-primary reading-path tuples over frozen fresh perceptions.

The fresh role_tier-aware perceptions were already captured on 2026-06-23.
This script does not re-perceive and does not relabel gold. It runs the live
LLM-primary tuple producer over those frozen perception artifacts, scores the
emitted tuples against the operator-confirmed gold, and counts safe-degraded
rows separately.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUT_DIR = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-holdout-rescan-2026-06-23"
)
PERCEPTIONS_DIR = OUT_DIR / "perceptions"
REPORT = OUT_DIR / "llm-primary-reading-path-measurement.json"
MODEL_ID = "gpt-5.5"


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    _load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("FATAL: OPENAI_API_KEY not set")

    from app.models.perception.perception_artifact import PerceptionArtifact
    from scripts.analysis.reading_path_p2_4b_run import load_gold
    from scripts.analysis.reading_path_p2_4b_score import ReadingPathTuple, score
    from scripts.utilities.reading_path_classifier import with_llm_primary_reading_path

    gold = load_gold()
    captured_at = datetime.now(UTC).isoformat()
    load_errors: list[dict[str, str]] = []
    perception_provenance: dict[str, str] = {}
    emitted_by_slide: dict[str, ReadingPathTuple] = {}
    sources_by_slide: dict[str, str | None] = {}
    degraded_by_slide: dict[str, bool] = {}

    for slide_id in gold:
        pjson = PERCEPTIONS_DIR / f"{slide_id}.json"
        if not pjson.is_file():
            load_errors.append({"slide_id": slide_id, "error": "fresh-perception-missing"})
            continue
        payload = json.loads(pjson.read_text(encoding="utf-8"))
        perception_provenance[slide_id] = payload.get("provenance", {}).get(
            "captured_at",
            "?",
        )
        artifact = PerceptionArtifact.model_validate(payload["perception_artifact"])
        classified = with_llm_primary_reading_path(artifact)
        dump = classified.model_dump()
        emitted_by_slide[slide_id] = ReadingPathTuple(
            macro_layout=dump.get("macro_layout"),
            image_role=dump.get("dominant_image_role"),
            text_substructure=dump.get("text_substructure"),
            narration_cadence=dump.get("narration_cadence"),
            callout_intent=dump.get("callout_intent"),
            derived_primary=dump.get("reading_path"),
        )
        sources_by_slide[slide_id] = dump.get("reading_path_source")
        degraded_by_slide[slide_id] = bool(dump.get("reading_path_degraded"))

    rows = [(sid, emitted_by_slide[sid], gold[sid]) for sid in gold if sid in emitted_by_slide]
    rep = score(rows)
    degraded_rows = sum(degraded_by_slide.values())

    summary = {
        "captured_at": captured_at,
        "model_id": MODEL_ID,
        "subject": "llm-primary reading-path classifier",
        "substrate": "frozen fresh@2026-06-23 role_tier-aware perceptions",
        "perception_provenance_sample": dict(list(perception_provenance.items())[:3]),
        "classified_ok": len(emitted_by_slide),
        "load_errors": load_errors,
        "scored_slides": len(rows),
        "primary_key_top1": rep.primary_key_top1,
        "full_tuple_rate": rep.full_tuple_rate,
        "per_axis": {
            axis: rep.per_axis_rate(axis)
            for axis in ("macro_layout", "image_role", "text_substructure", "narration_cadence")
        },
        "passes_primary_key_0_85": rep.passes_primary_key,
        "passes_full_tuple_0_80": getattr(rep, "passes_full_tuple", None),
        "degraded_rows": degraded_rows,
        "hard_blocks": 0,
        "sources_by_slide": sources_by_slide,
        "degraded_by_slide": degraded_by_slide,
    }
    REPORT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== LLM-PRIMARY READING-PATH MEASUREMENT ===")
    print("subject=llm-primary reading-path classifier  substrate=frozen fresh@2026-06-23")
    print(f"classified OK: {len(emitted_by_slide)}/14  (load errors: {len(load_errors)})")
    print(f"scored slides: {len(rows)}/14")
    print(f"primary-key top-1 = {rep.primary_key_top1:.3f}  (>=0.85? {rep.passes_primary_key})")
    print(f"full-tuple = {rep.full_tuple_rate:.3f}")
    print(
        f"per-axis: macro={summary['per_axis']['macro_layout']:.3f} "
        f"image_role={summary['per_axis']['image_role']:.3f} "
        f"text={summary['per_axis']['text_substructure']:.3f} "
        f"cadence={summary['per_axis']['narration_cadence']:.3f}"
    )
    print(f"degraded rows = {degraded_rows}  hard blocks = 0")
    for line in rep.confusion_lines():
        print(line)
    print(f"\nreport: {REPORT}")


if __name__ == "__main__":
    main()

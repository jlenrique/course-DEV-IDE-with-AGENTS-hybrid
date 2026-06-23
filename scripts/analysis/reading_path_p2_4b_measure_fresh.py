"""P2-4b leg 3 — HONEST built-classifier measurement on the ALREADY-CAPTURED
fresh role_tier perceptions (leg 1a output), WITHOUT re-perceiving.

Rationale: leg 1a (re-perceive the 14 held-out under S2 role_tier) already ran
(2026-06-23 00:03-00:07, gpt-5.5, role_tier-aware) and its perceptions stand as
the first-run-stands substrate. The companion `reading_path_holdout_rescan.py`
re-perceives every invocation; re-running it would RE-ROLL leg 1a. This script
reuses those frozen fresh perceptions and runs ONLY leg 3:

    S1/S2 classify (with_classified_reading_path) + live S3 escalation
    (run_s3_escalation) -> emitted ReadingPathTuple per slide -> score vs the
    operator-confirmed frozen gold.

First-run-stands; no retry-to-green. The single live leg is the S3 escalation
call (>= gpt-5.5). Reads OPENAI_API_KEY from .env. Writes a subject/substrate-
tagged report next to the fresh perceptions.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUT_DIR = (
    REPO_ROOT / "_bmad-output" / "implementation-artifacts"
    / "reading-path-holdout-rescan-2026-06-23"
)
PERCEPTIONS_DIR = OUT_DIR / "perceptions"
REPORT = OUT_DIR / "honest-built-classifier-measurement.json"
MODEL_ID = "gpt-5.5"


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def main() -> None:
    _load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("FATAL: OPENAI_API_KEY not set")

    from app.models.perception.perception_artifact import PerceptionArtifact
    from scripts.analysis.reading_path_p2_4b_run import _dominant_image_role, load_gold
    from scripts.analysis.reading_path_p2_4b_score import ReadingPathTuple, score
    from scripts.utilities.reading_path_classifier import with_classified_reading_path
    from scripts.utilities.reading_path_escalation import run_s3_escalation

    gold = load_gold()
    captured_at = datetime.now(UTC).isoformat()

    # Load the FROZEN fresh perceptions (leg 1a) + S1/S2 classify. No re-perception.
    classified: dict[str, object] = {}
    load_errors: list[dict] = []
    perception_provenance: dict[str, str] = {}
    for sid in gold:
        pjson = PERCEPTIONS_DIR / f"{sid}.json"
        if not pjson.is_file():
            load_errors.append({"slide_id": sid, "error": "fresh-perception-missing"})
            continue
        payload = json.loads(pjson.read_text(encoding="utf-8"))
        perception_provenance[sid] = payload.get("provenance", {}).get("captured_at", "?")
        art = PerceptionArtifact.model_validate(payload["perception_artifact"])
        classified[sid] = with_classified_reading_path(art)

    arts = [classified[sid] for sid in gold if sid in classified]

    # LEG 3 — live S3 escalation (the one live leg) + score emitted-vs-gold.
    res = run_s3_escalation(arts)
    post = {a.slide_id: a for a in res.artifacts}

    def emit(a):
        d = a.model_dump()
        return ReadingPathTuple(
            d.get("macro_layout"),
            _dominant_image_role(d.get("image_roles")),
            d.get("text_substructure"),
            d.get("narration_cadence"),
            d.get("callout_intent"),
            d.get("reading_path"),
        )

    rows = [(sid, emit(post[sid]), gold[sid]) for sid in gold if sid in post]
    rep = score(rows)

    led = res.ledger
    fired: Counter = Counter()
    for s in led["slides"]:
        for f in s.get("fired", []):
            fired[f] += 1

    summary = {
        "captured_at": captured_at,
        "model_id": MODEL_ID,
        "subject": "built-classifier (S1/S2/S3)",
        "substrate": "fresh@2026-06-23 (re-perceived under S2 role_tier; leg-3-only, no re-perception)",
        "perception_provenance_sample": dict(list(perception_provenance.items())[:3]),
        "classified_ok": len(classified),
        "load_errors": load_errors,
        "scored_slides": len(rows),
        "primary_key_top1": rep.primary_key_top1,
        "full_tuple_rate": rep.full_tuple_rate,
        "per_axis": {
            ax: rep.per_axis_rate(ax)
            for ax in ("macro_layout", "image_role", "text_substructure", "narration_cadence")
        },
        "passes_primary_key_0_85": rep.passes_primary_key,
        "passes_full_tuple_0_80": getattr(rep, "passes_full_tuple", None),
        "escalation_rate": led.get("escalation_rate"),
        "escalation_fired": dict(fired),
        "degraded_rows": sum(1 for s in led["slides"] if s.get("degraded")),
    }
    REPORT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== HONEST BUILT-CLASSIFIER MEASUREMENT (leg-3 over frozen fresh perceptions) ===")
    print(f"subject=built-classifier(S1/S2/S3)  substrate=fresh@2026-06-23")
    print(f"classified OK: {len(classified)}/14  (load errors: {len(load_errors)})")
    print(f"scored slides: {len(rows)}/14")
    print(f"primary-key top-1 = {rep.primary_key_top1:.3f}  (>=0.85? {rep.passes_primary_key})")
    print(f"full-tuple = {rep.full_tuple_rate:.3f}")
    print(
        f"per-axis: macro={summary['per_axis']['macro_layout']:.3f} "
        f"image_role={summary['per_axis']['image_role']:.3f} "
        f"text={summary['per_axis']['text_substructure']:.3f} "
        f"cadence={summary['per_axis']['narration_cadence']:.3f}"
    )
    print(f"escalation rate = {led.get('escalation_rate')}  fired={dict(fired)}  degraded={summary['degraded_rows']}")
    for line in rep.confusion_lines():
        print(line)
    print(f"\nreport: {REPORT}")


if __name__ == "__main__":
    main()

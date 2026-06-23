"""P2-4b calibration legs 1+3 — re-perceive the held-out 14 under S2's role_tier
perceiver, run the FULL built classifier (S1/S2/S3-live), and score vs the
operator-confirmed gold. This is the HONEST built-classifier measurement that the
S3-T11 live dry-run showed the catalog-approach 0.93 did NOT represent.

- LEG 1: fresh perception (live gpt-5.5, role_tier-aware) → a NEW dir (does NOT
  overwrite the stale 2026-06-22 held-out-scan provenance).
- LEG 3: S1/S2 classify + live S3 escalation → emitted tuples → score vs gold.

First-run-stands; no retry-to-green. Reads OPENAI_API_KEY from .env.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CORPUS_DIR = Path(r"C:\Users\juanl\OneDrive\Desktop\z-2026-06-21")
OUT_DIR = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-holdout-rescan-2026-06-23"
)
PERCEPTIONS_DIR = OUT_DIR / "perceptions"
REPORT = OUT_DIR / "honest-built-classifier-measurement.json"
MODEL_ID = "gpt-5.5"
CAPTURED_AT = datetime.now(UTC).isoformat()


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def main() -> None:
    _load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("FATAL: OPENAI_API_KEY not set")
    from app.models.perception.perception_artifact import PerceptionArtifact
    from app.specialists.vision.provider import VisionProviderError, perceive_png
    from scripts.analysis.reading_path_p2_4b_run import load_gold
    from scripts.analysis.reading_path_p2_4b_score import ReadingPathTuple, score
    from scripts.utilities.reading_path_classifier import with_classified_reading_path
    from scripts.utilities.reading_path_escalation import run_s3_escalation

    PERCEPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    gold = load_gold()

    # LEG 1 — fresh perception (role_tier-aware) + S1/S2 classify
    classified: dict[str, object] = {}
    perceive_errors: list[dict] = []
    for idx, sid in enumerate(gold, start=1):
        png = CORPUS_DIR / f"{sid}.png"
        if not png.is_file():
            perceive_errors.append({"slide_id": sid, "error": "png-missing"})
            continue
        print(f"[{idx:2d}/14] re-perceiving {sid} ...", flush=True)
        try:
            resp = perceive_png(png, slide_id=sid, model_id=MODEL_ID)
            art = PerceptionArtifact.model_validate(resp.model_dump())
            (PERCEPTIONS_DIR / f"{sid}.json").write_text(
                json.dumps(
                    {
                        "provenance": {
                            "captured_at": CAPTURED_AT,
                            "model_id": MODEL_ID,
                            "source_png": str(png),
                            "tool": "reading_path_holdout_rescan.py",
                        },
                        "perception_artifact": art.model_dump(),
                    },
                    indent=2, ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            classified[sid] = with_classified_reading_path(art)
            roles = classified[sid].model_dump().get("image_roles")
            print(f"    -> macro={classified[sid].macro_layout} roles={roles}", flush=True)
        except VisionProviderError as exc:
            perceive_errors.append(
                {"slide_id": sid, "tag": getattr(exc, "tag", "?"), "error": str(exc)}
            )
            print(f"    ! perceive error: {exc}", flush=True)
        except Exception as exc:  # noqa: BLE001
            perceive_errors.append({"slide_id": sid, "error": f"{exc}\n{traceback.format_exc()}"})
            print(f"    ! unexpected: {exc}", flush=True)

    arts = [classified[sid] for sid in gold if sid in classified]

    # LEG 3 — live S3 escalation + score emitted-vs-gold
    res = run_s3_escalation(arts)
    post = {a.slide_id: a for a in res.artifacts}

    def emit(a):
        d = a.model_dump()
        return ReadingPathTuple(
            d.get("macro_layout"), d.get("dominant_image_role"),
            d.get("text_substructure"), d.get("narration_cadence"),
            d.get("callout_intent"), d.get("reading_path"),
        )

    rows = [(sid, emit(post[sid]), gold[sid]) for sid in gold if sid in post]
    rep = score(rows)
    led = res.ledger
    fired = Counter()
    for s in led["slides"]:
        for f in s.get("fired", []):
            fired[f] += 1

    summary = {
        "captured_at": CAPTURED_AT,
        "model_id": MODEL_ID,
        "subject": "built-classifier (S1/S2/S3)",
        "substrate": "fresh@2026-06-23 (re-perceived under S2 role_tier)",
        "perceived_ok": len(classified),
        "perceive_errors": perceive_errors,
        "scored_slides": len(rows),
        "primary_key_top1": rep.primary_key_top1,
        "full_tuple_rate": rep.full_tuple_rate,
        "per_axis": {ax: rep.per_axis_rate(ax) for ax in
                     ("macro_layout", "image_role", "text_substructure", "narration_cadence")},
        "passes_primary_key_0_85": rep.passes_primary_key,
        "escalation_rate": led.get("escalation_rate"),
        "escalation_fired": dict(fired),
        "degraded_rows": sum(1 for s in led["slides"] if s.get("degraded")),
    }
    REPORT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== HONEST BUILT-CLASSIFIER MEASUREMENT (fresh re-perception) ===")
    print(f"perceived OK: {len(classified)}/14  (errors: {len(perceive_errors)})")
    print(f"primary-key top-1 = {rep.primary_key_top1:.3f}  (>=0.85? {rep.passes_primary_key})")
    print(f"full-tuple = {rep.full_tuple_rate:.3f}")
    print(f"per-axis: macro={summary['per_axis']['macro_layout']:.3f} "
          f"image_role={summary['per_axis']['image_role']:.3f} "
          f"text={summary['per_axis']['text_substructure']:.3f} "
          f"cadence={summary['per_axis']['narration_cadence']:.3f}")
    print(
        f"escalation rate = {led.get('escalation_rate')}  "
        f"fired={dict(fired)}  degraded={summary['degraded_rows']}"
    )
    print(f"report: {REPORT}")
    for line in rep.confusion_lines():
        print(line)


if __name__ == "__main__":
    main()

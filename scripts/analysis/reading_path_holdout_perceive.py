"""Reading-path HELD-OUT perception — P2-4b confirm/deny kit input (EVIDENCE tool).

Operator-authorized PLAN CHANGE (2026-06-22): the held-out 14 are no longer kept
naive. Claude now LABELS them with the newly-synthesized catalog v1 approach and
the operator CONFIRMS/DENIES. This script does the LIVE-PERCEPTION half only:

1. Enumerates the 14 HELD-OUT slides (the inverse of the corpus scan's working
   set) from `reading-path-holdout-split-2026-06-21.md`. Asserts exactly the 14
   are present in the corpus (fails loud otherwise).
2. LIVE-perceives each via the real gpt-5.5 perceiver
   (`app.specialists.vision.provider.perceive_png`). NO mocks. First-run-stands;
   per-slide error recorded + tagged, scan CONTINUES.
3. Captures each raw PerceptionArtifact to JSON with provenance.
4. Computes the content-blind feature vector (reused from the corpus-scan tool,
   two-source rule) AND records what the CURRENT (pre-P2-4c) 7-enum geometry
   classifier returns + its position-order scan — for reference only. The tuple
   LABELING itself is the orchestrator's catalog-guided judgment downstream, NOT
   decided here.
5. Emits a machine-readable summary the orchestrator turns into the confirm/deny
   kit.

Run:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe \
        scripts/analysis/reading_path_holdout_perceive.py

Reads OPENAI_API_KEY from .env.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CORPUS_DIR = Path(r"C:\Users\juanl\OneDrive\Desktop\z-2026-06-21")
OUT_DIR = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "reading-path-holdout-scan"
PERCEPTIONS_DIR = OUT_DIR / "perceptions"
SUMMARY_JSON = OUT_DIR / "holdout-perception-summary.json"

CAPTURED_AT = datetime.now(UTC).isoformat()
MODEL_ID = "gpt-5.5"

# The 14 HELD-OUT slides (reading-path-holdout-split-2026-06-21.md). These are
# now perceived for the Claude-labels -> operator-confirm/deny validation.
HELD_OUT: tuple[str, ...] = (
    "1_Diagnosis-Innovation.png",
    "3_Achieving-the-Ideal-State.png",
    "5_Check-Your-Understanding.png",
    "6_All-of-them-belong-to-BOTH.png",
    "8_Decision-Making-Foundations.png",
    "9_Comparing-Expected-Value-and-Expected-Utility.png",
    "11_Value-Creation-in-Innovation.png",
    "13_Effective-Problem-Solving-Approach.png",
    "15_Types-of-Motivation.png",
    "17_Examples-of-Effective-Leadership-in-Public-Health.png",
    "18_The-Future-of-Public-Health-Leadership.png",
    "20_Resources-for-Entrepreneurship-and-Innovation.png",
    "21_Key-Takeaways.png",
    "22_Next-Steps-Your-Path-Forward.png",
)
EXPECTED_HELDOUT_COUNT = 14


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def enumerate_heldout_slides() -> list[Path]:
    if not CORPUS_DIR.is_dir():
        raise SystemExit(f"FATAL: corpus dir not found: {CORPUS_DIR}")
    all_pngs = {p.name: p for p in CORPUS_DIR.glob("*.png")}
    missing = [n for n in HELD_OUT if n not in all_pngs]
    if missing:
        raise SystemExit(f"FATAL: held-out slides missing from corpus: {missing}")
    paths = [all_pngs[n] for n in HELD_OUT]
    if len(paths) != EXPECTED_HELDOUT_COUNT:
        raise SystemExit(f"FATAL: expected {EXPECTED_HELDOUT_COUNT} held-out, got {len(paths)}")
    return paths


def scan() -> dict[str, Any]:
    from app.models.perception.perception_artifact import PerceptionArtifact
    from app.specialists.vision.provider import VisionProviderError, perceive_png
    from scripts.analysis.reading_path_corpus_scan import compute_feature_vector
    from scripts.utilities.reading_path_classifier import (
        ReadingPathClassificationError,
        classify_reading_path,
        ordered_element_keys_for_reading_path,
    )

    slides = enumerate_heldout_slides()
    PERCEPTIONS_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for idx, png in enumerate(slides, start=1):
        slide_id = png.stem
        print(f"[{idx:2d}/{len(slides)}] perceiving {slide_id} ...", flush=True)
        try:
            response = perceive_png(png, slide_id=slide_id, model_id=MODEL_ID)
        except VisionProviderError as exc:
            tag = getattr(exc, "tag", "vision.provider.error")
            print(f"    ! ERROR ({tag}): {exc}", flush=True)
            errors.append({"slide_id": slide_id, "tag": tag, "error": str(exc)})
            rows.append({"slide_id": slide_id, "error": {"tag": tag, "message": str(exc)}})
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"    ! UNEXPECTED ERROR: {exc}", flush=True)
            errors.append(
                {
                    "slide_id": slide_id,
                    "tag": "unexpected",
                    "error": f"{exc}\n{traceback.format_exc()}",
                }
            )
            rows.append({"slide_id": slide_id, "error": {"tag": "unexpected", "message": str(exc)}})
            continue

        artifact = PerceptionArtifact.model_validate(response.model_dump())
        artifact_dump = artifact.model_dump()
        capture = {
            "provenance": {
                "captured_at": CAPTURED_AT,
                "model_id": MODEL_ID,
                "source_png": str(png),
                "scan_tool": "scripts/analysis/reading_path_holdout_perceive.py",
            },
            "perception_artifact": artifact_dump,
        }
        (PERCEPTIONS_DIR / f"{slide_id}.json").write_text(
            json.dumps(capture, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        fv = compute_feature_vector(artifact_dump)

        try:
            current_fit = classify_reading_path(artifact)
        except ReadingPathClassificationError:
            current_fit = "UNCLASSIFIABLE"
        try:
            scan_order = ordered_element_keys_for_reading_path(artifact)
        except ReadingPathClassificationError:
            scan_order = []

        rows.append(
            {
                "slide_id": slide_id,
                "source_png": str(png),
                "perceived_title": artifact_dump.get("slide_title", ""),
                "layout_description": artifact_dump.get("layout_description", ""),
                "element_count": fv["anchor_count"],
                "elements": [
                    {
                        "id": e.get("id"),
                        "kind": e.get("kind") or e.get("type"),
                        "text": (e.get("text") or "")[:90],
                        "bbox": e.get("bbox") or e.get("bounds") or e.get("position"),
                    }
                    for e in (artifact_dump.get("visual_elements") or [])
                ],
                "feature_vector": fv,
                "current_classifier_fit": current_fit,
                "current_scan_order": scan_order,
                "confidence_proxy": artifact_dump.get("confidence_score")
                or artifact_dump.get("confidence", "n/a"),
            }
        )
        print(
            f"    -> current_fit={current_fit} elems={fv['anchor_count']} "
            f"vec={fv['reading_vector']} dens={fv['text_density_band']}",
            flush=True,
        )

    return {
        "rows": rows,
        "errors": errors,
        "perceived_count": sum(1 for r in rows if "error" not in r),
        "heldout_count": len(slides),
    }


def main() -> None:
    _load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("FATAL: OPENAI_API_KEY not set (and not found in .env)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = scan()
    summary = {
        "captured_at": CAPTURED_AT,
        "model_id": MODEL_ID,
        "heldout_count": result["heldout_count"],
        "perceived_count": result["perceived_count"],
        "errors": result["errors"],
        "rows": result["rows"],
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== HELD-OUT PERCEPTION COMPLETE ===")
    print(f"perceived: {result['perceived_count']}/{result['heldout_count']}")
    print(f"errors: {len(result['errors'])}")
    print(f"summary: {SUMMARY_JSON}")


if __name__ == "__main__":
    main()

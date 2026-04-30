# /// script
# requires-python = ">=3.10"
# ///
"""Offline comparative evaluator for C1-M1 template-selection iterations.

This scaffold compares a baseline bundle and a candidate bundle to provide
deterministic metrics and a simple pass/warn/fail decision before live HIL runs.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_bundle_snapshot(bundle_dir: str | Path) -> dict[str, Any]:
    bundle = Path(bundle_dir).resolve()
    if not bundle.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle}")

    authorized = _load_json_object(bundle / "authorized-storyboard.json")
    storyboard = _load_json_object(bundle / "storyboard" / "storyboard.json")
    envelope_path = bundle / "pass2-envelope.json"
    envelope = _load_json_object(envelope_path) if envelope_path.is_file() else {}

    return {
        "bundle_path": str(bundle),
        "authorized": authorized,
        "storyboard": storyboard,
        "pass2_envelope": envelope,
    }


def _extract_metrics(snapshot: dict[str, Any]) -> dict[str, Any]:
    authorized = snapshot["authorized"]
    storyboard = snapshot["storyboard"]
    envelope = snapshot["pass2_envelope"]

    authorized_slides = authorized.get("authorized_slides", [])
    storyboard_slides = storyboard.get("slides", [])
    review_meta = storyboard.get("review_meta", {})
    cluster_groups = storyboard.get("cluster_groups", []) if isinstance(storyboard.get("cluster_groups"), list) else []
    template_plan = envelope.get("cluster_template_plan") if isinstance(envelope.get("cluster_template_plan"), dict) else {}
    template_clusters = template_plan.get("clusters", []) if isinstance(template_plan.get("clusters"), list) else []

    interstitial_count = 0
    narrated_count = 0
    selected_template_ids: set[str] = set()
    for slide in storyboard_slides:
        if not isinstance(slide, dict):
            continue
        if str(slide.get("cluster_role") or "").strip().lower() == "interstitial":
            interstitial_count += 1
        if str(slide.get("narration_status") or "").strip().lower() == "present":
            narrated_count += 1
        selected_template = str(slide.get("selected_template_id") or "").strip()
        if selected_template:
            selected_template_ids.add(selected_template)

    return {
        "authorized_slide_count": len([s for s in authorized_slides if isinstance(s, dict)]),
        "storyboard_slide_count": len([s for s in storyboard_slides if isinstance(s, dict)]),
        "cluster_group_count": len(cluster_groups),
        "template_cluster_count": len([c for c in template_clusters if isinstance(c, dict)]),
        "interstitial_slide_count": interstitial_count,
        "narrated_slide_count": narrated_count,
        "missing_asset_count": _safe_int(review_meta.get("missing_assets", 0)),
        "double_dispatch_enabled": bool(review_meta.get("double_dispatch_enabled", False)),
        "unique_selected_template_count": len(selected_template_ids),
    }


def compare_c1_m1_runs(
    *,
    lesson_id: str,
    baseline_bundle: str | Path,
    candidate_bundle: str | Path,
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
) -> dict[str, Any]:
    baseline_snapshot = load_bundle_snapshot(baseline_bundle)
    candidate_snapshot = load_bundle_snapshot(candidate_bundle)

    baseline_metrics = _extract_metrics(baseline_snapshot)
    candidate_metrics = _extract_metrics(candidate_snapshot)

    delta = {
        key: candidate_metrics[key] - baseline_metrics[key]
        for key in (
            "authorized_slide_count",
            "storyboard_slide_count",
            "cluster_group_count",
            "template_cluster_count",
            "interstitial_slide_count",
            "narrated_slide_count",
            "missing_asset_count",
            "unique_selected_template_count",
        )
    }

    status = "pass"
    reasons: list[str] = []
    if candidate_metrics["missing_asset_count"] > baseline_metrics["missing_asset_count"]:
        status = "fail"
        reasons.append("candidate_missing_assets_exceed_baseline")
    if candidate_metrics["template_cluster_count"] == 0 and candidate_metrics["cluster_group_count"] > 0:
        status = "fail"
        reasons.append("cluster_groups_present_without_template_cluster_plan")
    if candidate_metrics["unique_selected_template_count"] == 0 and candidate_metrics["cluster_group_count"] > 0:
        status = "fail"
        reasons.append("clustered_candidate_missing_selected_template_ids")
    if candidate_metrics["narrated_slide_count"] < baseline_metrics["narrated_slide_count"] and status != "fail":
        status = "warn"
        reasons.append("candidate_narrated_slide_count_below_baseline")
    if not reasons:
        reasons.append("no_regression_detected_on_minimal_metrics")

    return {
        "artifact_version": 1,
        "artifact_type": "c1-m1-comparative-evaluation",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "lesson_id": lesson_id,
        "baseline": {
            "label": baseline_label,
            "bundle_path": baseline_snapshot["bundle_path"],
            "metrics": baseline_metrics,
        },
        "candidate": {
            "label": candidate_label,
            "bundle_path": candidate_snapshot["bundle_path"],
            "metrics": candidate_metrics,
        },
        "delta": delta,
        "decision": {"status": status, "reasons": reasons},
    }


def write_artifact(report: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="C1-M1 baseline vs candidate comparative evaluation")
    parser.add_argument("--lesson-id", default="C1-M1")
    parser.add_argument("--baseline-bundle", type=Path, required=True)
    parser.add_argument("--candidate-bundle", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("_bmad-output/test-artifacts/20c-2-eval/c1-m1-comparative-eval.json"),
    )
    args = parser.parse_args()

    try:
        report = compare_c1_m1_runs(
            lesson_id=args.lesson_id,
            baseline_bundle=args.baseline_bundle,
            candidate_bundle=args.candidate_bundle,
        )
        output_path = write_artifact(report, args.output)
        print(json.dumps({"status": "ok", "output_path": str(output_path), "decision": report["decision"]}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


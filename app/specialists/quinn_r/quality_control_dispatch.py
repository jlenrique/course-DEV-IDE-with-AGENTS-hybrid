"""Importlib dispatch wrapper for Quinn-R quality-control checks."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
QC_SCRIPTS = REPO_ROOT / "skills" / "quality-control" / "scripts"


def _content_error(name: str, tag: str) -> type:
    """G5 content errors are dual-based (audio-arc taxonomy re-base
    2026-06-12): SpecialistDispatchError so the runner error-pauses
    recoverably (the bare ValueError form CRASHED cycle-5 at node 13 and
    lost walk progress), and ValueError so existing handlers/tests keep
    their semantics."""

    def _init(
        self,
        message: str,
        *,
        tag: str = tag,
        scope: str = "content",
    ) -> None:  # noqa: ANN001
        SpecialistDispatchError.__init__(self, message, tag=tag)
        self.scope = scope

    return type(name, (SpecialistDispatchError, ValueError), {"__init__": _init})


WpmThresholdError = _content_error("WpmThresholdError", "quinn_r.g5.wpm-threshold")
VttMonotonicityError = _content_error("VttMonotonicityError", "quinn_r.g5.vtt-monotonicity")
CoverageGapError = _content_error("CoverageGapError", "quinn_r.g5.coverage-gap")
DurationCoherenceError = _content_error(
    "DurationCoherenceError", "quinn_r.g5.duration-coherence"
)
FidelityError = _content_error("FidelityError", "quinn_r.g5.fidelity-orphan-reference")


class StoryboardBInputError(SpecialistDispatchError):
    """G3B reached without its Pass-2/Gary inputs — data-plane starvation.

    dp-v1.1 (Trial-3 cycle-4 defect 2): the old "post" body demanded a §14
    composed artifact that cannot exist at 08B. The storyboard-b body reviews
    Pass-2 narration against Gary's REAL slide roster; missing either input
    is a recoverable dispatch error, not a review verdict.
    """


def run_g5_grounding(payload: dict[str, Any]) -> dict[str, Any]:
    """Ground the G5 payload: construct narration_segments from Pass-2 keys.

    Audio-arc consensus 2026-06-12: node 13 projects narration_script +
    segment_manifest_deltas (irene), narration_outputs (enrique durations),
    slides (gary). When narration_segments is already present (legacy/test
    payloads) pass through. Starvation raises (the fabricated slide-1
    roster is retired); estimated durations flag the WPM check advisory
    (Winston: WPM against a chars/14 estimate is self-referential).
    """
    if payload.get("narration_segments"):
        return payload
    narration = payload.get("narration_script")
    deltas = payload.get("segment_manifest_deltas")
    if not narration or not deltas:
        raise StoryboardBInputError(
            "G5 requires narration_segments or Pass-2 narration keys "
            "(narration_script + segment_manifest_deltas projections)",
            tag="quinn_r.g5.input-missing",
        )
    from app.specialists.narration_join import (
        collapsed_segment_ids,
        join_narration_segments,
        phantom_segment_ids,
    )

    rows = join_narration_segments(narration, deltas)
    # Mine-next trust T3: non-bijective collapse is fail-loud at G5 (observability
    # path); Enrique refuses the same shape pre-spend.
    collapsed = collapsed_segment_ids(rows)
    if collapsed:
        raise StoryboardBInputError(
            f"narration join collapsed segment id(s) {collapsed} onto multiple "
            "slides (non-bijective); refusing G5 coverage on a flooded join",
            tag="quinn_r.g5.join-collapsed",
        )
    # dp-v1.2 rider (Amelia R1): a delta with no matching narration joins
    # with empty text — drop it BEFORE coverage counting so its slide
    # reports uncovered (CoverageGapError) instead of silently passing
    # while enrique skipped its audio.
    phantom = phantom_segment_ids(rows)
    if phantom:
        rows = [
            row
            for row in rows
            if str(row.get("segment_id") or row.get("id") or "") not in phantom
        ]
    if not rows:
        detail = f" (all joined rows were phantom deltas: {phantom})" if phantom else ""
        raise StoryboardBInputError(
            f"G5 narration join produced zero segments{detail}",
            tag="quinn_r.g5.input-missing",
        )
    durations: dict[str, float] = {}
    measured: dict[str, bool] = {}
    for out_row in payload.get("narration_outputs") or []:
        if isinstance(out_row, dict):
            sid = str(out_row.get("segment_id") or "")
            durations[sid] = float(out_row.get("duration_seconds") or 0)
            measured[sid] = str(out_row.get("duration_source") or "") == "measured"
            caption = str(out_row.get("caption_path") or "")
            # Winston MUST-FIX 1 (dp-v1.2 review): a synthesized segment
            # WITHOUT a caption is a coverage failure, not a silent pass —
            # the check exists precisely for the producer that doesn't write one.
            if str(out_row.get("audio_path") or "") and (
                not caption or not Path(caption).is_file()
            ):
                raise StoryboardBInputError(
                    f"narration output for {sid} lacks a readable caption: "
                    f"{caption or '<none>'}",
                    tag="quinn_r.g5.caption-missing",
                )
    segments: list[dict[str, Any]] = []
    any_estimated = False
    for row in rows:
        sid = row["segment_id"]
        duration = durations.get(sid) or max(1.0, len(row["narration_text"]) / 14.0)
        if not measured.get(sid, False):
            any_estimated = True
        segments.append(
            {
                "slide_id": row["slide_id"],
                "text": row["narration_text"],
                "duration_seconds": duration,
            }
        )
    grounded = dict(payload)
    grounded["narration_segments"] = segments
    if phantom:
        # Witness record (review patch): the drop must leave an audit trail
        # even when another segment covers the same slide.
        grounded["phantom_segment_ids_dropped"] = phantom
    if any_estimated:
        grounded["wpm_durations_estimated"] = True
    return grounded


def run_storyboard_b_review(payload: dict[str, Any]) -> dict[str, Any]:
    """Deterministic Storyboard-B review: narration vs the real slide roster.

    Checks (party consensus 2026-06-12, Winston/Amelia/Murat):
    - narration_script is a non-empty list of segments with id + text;
    - every roster slide id is referenced by at least one visual_reference
      (per-slide coverage);
    - no narration reference names a slide outside the roster (orphans).
    Content findings yield a "blocked" verdict for the HIL gate — quinn_r
    reports; the operator decides. Input starvation raises instead.
    """
    slide_rows = payload.get("gary_slide_output")
    if not isinstance(slide_rows, list) or not slide_rows:
        raise StoryboardBInputError(
            "storyboard-b review requires gary_slide_output (real slide "
            "roster) in the payload",
            tag="quinn_r.storyboard_b.input-missing",
        )
    narration = payload.get("narration_script")
    deltas = payload.get("segment_manifest_deltas")
    if not isinstance(narration, list) or not narration:
        raise StoryboardBInputError(
            "storyboard-b review requires narration_script from Irene Pass 2",
            tag="quinn_r.storyboard_b.input-missing",
        )
    roster = {
        str(row.get("slide_id") or "").strip()
        for row in slide_rows
        if isinstance(row, dict) and str(row.get("slide_id") or "").strip()
    }
    blocking: list[dict[str, Any]] = []
    for index, segment in enumerate(narration, start=1):
        if not isinstance(segment, dict) or not str(
            segment.get("narration_text") or ""
        ).strip():
            blocking.append(
                {"check": "segment-text", "reason": f"segment {index} has no text"}
            )
    referenced: set[str] = set()
    for delta in deltas if isinstance(deltas, list) else []:
        if not isinstance(delta, dict):
            continue
        for ref in delta.get("visual_references") or []:
            if isinstance(ref, dict):
                source = str(ref.get("perception_source") or "").strip()
                if source:
                    referenced.add(source)
    uncovered = sorted(roster - referenced)
    orphans = sorted(referenced - roster)
    if uncovered:
        blocking.append(
            {"check": "coverage", "reason": f"slides without narration: {uncovered}"}
        )
    if orphans:
        blocking.append(
            {"check": "roster-join", "reason": f"references outside roster: {orphans}"}
        )
    return {
        "mode": "storyboard-b-review",
        "status": "blocked" if blocking else "reviewed",
        "blocking": blocking,
        "coverage": {
            "roster_size": len(roster),
            "covered": len(roster) - len(uncovered),
            "segments": len(narration),
        },
        "checks": ["segment-text", "coverage", "roster-join"],
    }


def _ensure_module_stub(name: str) -> None:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _ensure_package_stubs() -> None:
    _ensure_module_stub("skills")
    _ensure_module_stub("skills.quality_control")
    _ensure_module_stub("skills.quality_control.scripts")


def _load_module(module_name: str, file_name: str) -> Any:
    _ensure_package_stubs()
    path = QC_SCRIPTS / file_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load quality-control module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_precomposition_validators(*, artifact_paths: list[str]) -> dict[str, Any]:
    if not artifact_paths:
        return {
            "status": "skipped",
            "findings": [],
            "dimension_scores": {"composition": "SKIPPED"},
        }
    precomp = _load_module(
        "skills.quality_control.scripts.precomposition_validator",
        "precomposition_validator.py",
    )
    accessibility = _load_module(
        "skills.quality_control.scripts.accessibility_checker",
        "accessibility_checker.py",
    )
    target = artifact_paths[0]
    if not Path(target).is_file():
        return {
            "status": "degraded",
            "findings": [{"dimension": "composition", "reason": "artifact missing"}],
            "dimension_scores": {"composition": "LOW"},
        }
    result = precomp.validate_precomposition(target)
    if not isinstance(result, dict):
        raise RuntimeError("validate_precomposition must return a mapping")
    content = []
    for path in artifact_paths:
        candidate = Path(path)
        if candidate.is_file():
            content.append(candidate.read_text(encoding="utf-8", errors="ignore"))
    accessibility_result = accessibility.run_accessibility_check("\n\n".join(content))
    findings = result.get("findings", [])
    if isinstance(accessibility_result, dict):
        findings = [
            *findings,
            *accessibility_result.get("findings", []),
        ]
    result["findings"] = findings
    dimension_scores = result.get("dimension_scores", {})
    if isinstance(dimension_scores, dict):
        accessibility_status = str(accessibility_result.get("status", "pass")).lower()
        dimension_scores["accessibility"] = (
            "PASS" if accessibility_status == "pass" else "FAIL"
        )
    result["dimension_scores"] = dimension_scores
    return result


def run_postcomposition_validators(*, artifact_path: str | None) -> dict[str, Any]:
    if not artifact_path:
        return {
            "status": "skipped",
            "findings": [],
            "dimension_scores": {"accessibility": "SKIPPED", "brand": "SKIPPED"},
        }
    artifact = Path(artifact_path)
    if not artifact.is_file():
        return {
            "status": "degraded",
            "findings": [{"dimension": "content", "reason": "artifact missing"}],
            "dimension_scores": {
                "accessibility": "SKIPPED",
                "brand": "SKIPPED",
                "composition": "SKIPPED",
            },
        }
    artifact_text = artifact.read_text(encoding="utf-8", errors="ignore")
    accessibility = _load_module(
        "skills.quality_control.scripts.accessibility_checker",
        "accessibility_checker.py",
    )
    brand = _load_module(
        "skills.quality_control.scripts.brand_validator",
        "brand_validator.py",
    )
    visual = _load_module(
        "skills.quality_control.scripts.visual_fill_validator",
        "visual_fill_validator.py",
    )
    accessibility_result = accessibility.run_accessibility_check(artifact_text)
    brand_result = brand.run_brand_validation(artifact_text)
    visual_result = visual.validate_visual_fill(str(artifact))
    accessibility_status = str(accessibility_result.get("status", "pass")).lower()
    brand_status = str(brand_result.get("status", "pass")).lower()
    return {
        "status": "ok",
        "accessibility": accessibility_result,
        "brand": brand_result,
        "visual_fill": visual_result,
        "dimension_scores": {
            "accessibility": "PASS" if accessibility_status == "pass" else "FAIL",
            "brand": "PASS" if brand_status == "pass" else "FAIL",
            "composition": "PASS" if visual_result.get("passed", True) else "WARN",
        },
    }


__all__ = [
    "CoverageGapError",
    "DurationCoherenceError",
    "FidelityError",
    "StoryboardBInputError",
    "VttMonotonicityError",
    "WpmThresholdError",
    "run_g5_grounding",
    "run_postcomposition_validators",
    "run_precomposition_validators",
    "run_storyboard_b_review",
]

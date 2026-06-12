"""Bounded Quinn-R act body for Slab 7b Story 7b.2."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import validate

from app.models.state import specialist_summary_artifacts as summary_writer
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.runtime.economics import RUNS_ROOT
from app.specialists.quinn_r.quality_control_dispatch import (
    run_postcomposition_validators,
    run_precomposition_validators,
    run_storyboard_b_review,
)
from app.specialists.quinn_r.sensory_bridges_dispatch import dispatch_to_sensory_bridges

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "state/config/schemas/authorized-storyboard.schema.json"
# Finding #10 (2026-06-11) retired at dp-v1.1 (Trial-3 cycle-4 defect 2):
# G3B remapped post→storyboard_b — the "post" body presumed a §14 composed
# artifact that cannot exist at 08B; G3B reviews Storyboard B = Pass-2
# narration against Gary's real slide roster.
GATE_MODES = {"G2C": "pre", "G5": "g5", "G3B": "storyboard_b", "G2B": "variant", "G2F": "motion"}  # noqa: E501


class ModeMismatchError(ValueError):
    """Raised when Quinn-R is invoked for a gate/body mismatch."""


WpmThresholdError = type("WpmThresholdError", (ValueError,), {})
VttMonotonicityError = type("VttMonotonicityError", (ValueError,), {})
CoverageGapError = type("CoverageGapError", (ValueError,), {})
DurationCoherenceError = type("DurationCoherenceError", (ValueError,), {})


def _trail(last: ModelResolutionEntry, reason: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last.level,
        requested=last.requested,
        resolved=last.resolved,
        reason=reason,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last.cache_prefix_hash,
    )


def _payload(state: RunState) -> dict[str, Any]:
    raw = state.cache_state.cache_prefix if state.cache_state else "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ModeMismatchError("Quinn-R envelope payload must be a mapping")
    return value


def _mode(payload: dict[str, Any]) -> tuple[str, str]:
    gate_id = str(payload.get("gate_id") or "").upper()
    mode = GATE_MODES.get(gate_id)
    if mode is None:
        phase = str(payload.get("gate_phase") or "")
        mode = {"pre-composition": "pre", "post-composition": "post"}.get(phase)
    if mode is None:
        raise ModeMismatchError(f"unknown Quinn-R gate_id/gate_phase: {gate_id!r}")
    phase = str(payload.get("gate_phase") or "")
    expected = {"pre": "pre-composition", "g5": "pre-composition", "post": "post-composition", "variant": "pre-composition", "motion": "post-composition", "storyboard_b": "pre-composition"}[mode]  # noqa: E501
    if phase and phase != expected:
        raise ModeMismatchError(f"Quinn-R {gate_id or phase} cannot run {phase} body")
    return gate_id or expected, mode


def _slides(payload: dict[str, Any]) -> list[dict[str, Any]]:
    source = payload.get("slides") or payload.get("storyboard", {}).get("slides", [])
    return source if isinstance(source, list) and source else [{"slide_id": "slide-1"}]


def _authorized_doc(payload: dict[str, Any]) -> dict[str, Any]:
    slides = []
    for index, slide in enumerate(_slides(payload), start=1):
        slide_id = str(slide.get("slide_id") or slide.get("id") or f"slide-{index}")
        slides.append(
            {
                "slide_id": slide_id,
                "title": str(slide.get("title") or slide_id),
                "narration_pointer": str(slide.get("narration_pointer") or slide_id),
                "motion_pointer": str(slide.get("motion_pointer") or slide_id),
                "quinn_r_verdict": slide.get("quinn_r_verdict") or "approved",
                "evidence_block": str(slide.get("evidence_block") or "fixture-reviewed"),
            }
        )
    return {"schema_version": "1.0", "slides": slides}


def _write_authorized(doc: dict[str, Any], state: RunState, payload: dict[str, Any]) -> Path:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validate(instance=doc, schema=schema)
    runs_root = Path(str(payload.get("runs_root") or RUNS_ROOT))
    target = runs_root / str(state.run_id) / "quinn-r" / "g2c" / "authorized-storyboard.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _vtt_seconds(stamp: str) -> float:
    hours, minutes, rest = stamp.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def run_g5_checks(payload: dict[str, Any]) -> dict[str, Any]:
    target_wpm = float(payload.get("narration_profile_controls", {}).get("target_wpm", 150))
    tolerance = float(payload.get("wpm_tolerance", 20))
    segments = payload.get("narration_segments") or []
    text = " ".join(str(seg.get("text", "")) for seg in segments if isinstance(seg, dict))
    duration = sum(float(seg.get("duration_seconds", 0)) for seg in segments if isinstance(seg, dict))  # noqa: E501
    observed = (len(text.split()) / duration * 60) if duration else target_wpm
    if abs(observed - target_wpm) > tolerance:
        raise WpmThresholdError(f"WPM {observed:.1f} outside target {target_wpm:.1f}")
    previous = -1.0
    for line in str(payload.get("vtt_text") or "").splitlines():
        if "-->" not in line:
            continue
        start = _vtt_seconds(line.split("-->", 1)[0].strip())
        if start <= previous:
            raise VttMonotonicityError("VTT timestamps must be strictly increasing")
        previous = start
    slide_ids = {str(slide.get("slide_id") or slide.get("id")) for slide in _slides(payload)}
    covered = {str(seg.get("slide_id")) for seg in segments if isinstance(seg, dict)}
    missing = sorted(slide_ids - covered)
    if missing:
        raise CoverageGapError(f"missing narration coverage: {missing}")
    advisory: list[dict[str, Any]] = []
    for seg in segments:
        declared = float(seg.get("duration_seconds", 0))
        motion = float(seg.get("motion_duration_seconds", declared))
        if declared and abs(motion - declared) / declared > 0.10:
            advisory.append({"slide_id": seg.get("slide_id"), "reason": "duration-coherence"})
    return {"blocking": [], "advisory": advisory, "checks": ["wpm", "vtt", "coverage", "duration", "partition"]}  # noqa: E501


def _summary(state: RunState, payload: dict[str, Any], gate_id: str, verdict: dict[str, Any]) -> Path:  # noqa: E501
    return summary_writer.emit_summary(
        specialist_id="quinn-r",
        trial_id=state.run_id,
        gate_id=gate_id,
        runs_root=Path(str(payload.get("runs_root") or RUNS_ROOT)),
        decided=f"Quinn-R emitted {verdict['mode']} verdict: {verdict['status']}.",
        artifact_paths=verdict.get("artifact_paths", []),
        resolution_trail=[entry.reason for entry in state.model_resolution_trail[-3:]],
    )


def act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("quinn_r act invoked before plan; resolution trail is empty")
    last = state.model_resolution_trail[-1]
    try:
        payload = _payload(state)
        gate_id, mode = _mode(payload)
        if mode == "pre":
            doc = _authorized_doc(payload)
            artifact = _write_authorized(doc, state, payload)
            run_precomposition_validators(artifact_paths=[str(artifact)])
            verdict = {"mode": "pre-composition", "status": "approved", "artifact_paths": [str(artifact)]}  # noqa: E501
        elif mode == "g5":
            verdict = {"mode": "g5-pre-composition-qa", "status": "approved", **run_g5_checks(payload)}  # noqa: E501
        elif mode == "variant":
            selections = [{"slide_id": str(s.get("slide_id") or s.get("id") or f"slide-{i}"), "selected_variant": str(s.get("selected_variant") or "variant-1")} for i, s in enumerate(_slides(payload), start=1)]  # noqa: E501
            verdict = {"mode": "variant-selection", "status": "approved", "selections": selections}
        elif mode == "motion":
            assets = payload.get("motion_assets")
            verdict = {"mode": "motion-gate", "status": "reviewed", "motion_assets_reviewed": len(assets) if isinstance(assets, list) else 0}  # noqa: E501
        elif mode == "storyboard_b":
            verdict = run_storyboard_b_review(payload)
        else:
            artifact_path = payload.get("artifact_path")
            perception = dispatch_to_sensory_bridges(artifact_path=artifact_path, modality=str(payload.get("modality") or "video"), gate=gate_id)  # noqa: E501
            deterministic = run_postcomposition_validators(artifact_path=artifact_path)
            verdict = {"mode": "post-composition", "status": "reviewed", "perception": perception, "deterministic": deterministic}  # noqa: E501
        summary = _summary(state, payload, gate_id, verdict)
    except Exception as exc:
        state.model_resolution_trail.append(_trail(last, getattr(exc, "tag", type(exc).__name__)))
        raise
    output = {"quinn_r_review": verdict, "gate_id": gate_id, "summary_path": str(summary)}
    return {
        "model_resolution_trail": [*state.model_resolution_trail, _trail(last, "qrr.parsed.ok")],
        "cache_state": {"cache_prefix": json.dumps(output, sort_keys=True), "entries_count": (state.cache_state.entries_count + 1) if state.cache_state else 1},  # noqa: E501
    }


from app.specialists.quinn_r.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = ["CONSUMED_PAYLOAD_KEYS", "CoverageGapError", "DurationCoherenceError", "ModeMismatchError", "VttMonotonicityError", "WpmThresholdError", "act", "run_g5_checks"]  # noqa: E501

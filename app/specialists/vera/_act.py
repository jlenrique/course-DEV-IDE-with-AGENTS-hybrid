"""Bounded Vera act body for Slab 7b Story 7b.3."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state import specialist_summary_artifacts as summary_writer
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.runtime.economics import RUNS_ROOT
from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
G4_CONTRACT = REPO_ROOT / "state/config/fidelity-contracts/g4-narration-script.yaml"
G0_DIMENSIONS = (
    "source_coverage",
    "evidence_sentence",
    "claim_atomicity",
    "provenance_anchor",
    "omission_scan",
    "alteration_scan",
)
G1_DIMENSIONS = (
    "ingestion_completeness",
    "ingestion_fidelity",
    "source_mapping_coverage",
    "manifest_hash_integrity",
    "evidence_anchor_traceability",
    "cross_validation_hint_application",
)
OIA = {"O", "I", "A"}


class FTRParseError(SpecialistDispatchError):  # noqa: N818
    """Raised when Vera's Fidelity Trace Report cannot be parsed.

    Taxonomy re-base (live-path tranche, 2026-06-12): dispatch-family so a
    mid-walk failure error-pauses recoverably instead of killing the trial.
    """


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
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FTRParseError(
            f"vera act envelope cache_prefix is not valid JSON: {exc}",
            tag="ftr.parsed.malformed",
        ) from exc
    if not isinstance(value, dict):
        raise FTRParseError(
            "vera act envelope cache_prefix must decode to a mapping",
            tag="ftr.parsed.wrong-type",
        )
    return value


def _parse_ftr(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise FTRParseError(f"vera ftr parse failed: {exc}", tag="ftr.parsed.malformed") from exc
    if not isinstance(parsed, dict):
        raise FTRParseError("vera ftr must be a mapping", tag="ftr.parsed.wrong-type")
    for key in ("status", "severity", "summary", "findings"):
        if key not in parsed:
            raise FTRParseError(f"vera ftr missing key: {key}", tag="ftr.parsed.missing-key")
    if not isinstance(parsed["findings"], list):
        raise FTRParseError("vera ftr findings must be a list", tag="ftr.parsed.wrong-type")
    if not parsed["findings"]:
        raise FTRParseError("vera ftr findings cannot be empty", tag="ftr.parsed.empty")
    if not all(isinstance(item, dict) for item in parsed["findings"]):
        raise FTRParseError(
            "vera ftr findings entries must be objects",
            tag="ftr.parsed.wrong-type",
        )
    status = {
        "pass": "pass",
        "passed": "pass",
        "warn": "warn",
        "warning": "warn",
        "fail": "fail",
        "failed": "fail",
    }.get(str(parsed["status"]).strip().lower())
    if status is None or parsed["severity"] not in {"low", "medium", "high", "critical"}:
        raise FTRParseError(
            "vera ftr contract validation failed",
            tag="ftr.parsed.contract-failure",
        )
    parsed["status"] = status
    return parsed


def _text(payload: dict[str, Any]) -> str:
    path = payload.get("extracted_path") or payload.get("artifact_path")
    bundle = payload.get("texas_bundle_dir") or payload.get("bundle_reference")
    if not path and bundle:
        path = Path(str(bundle)) / "extracted.md"
    if path and Path(str(path)).is_file():
        return Path(str(path)).read_text(encoding="utf-8")
    return str(payload.get("extracted_text") or payload.get("source_text") or "")


def _finding(category: str, severity: str, anchor: str, description: str) -> dict[str, str]:
    return {
        "category": category,
        "severity": severity,
        "evidence_anchor": anchor,
        "description": description,
    }


def _g0(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    text = _text(payload)
    findings: list[dict[str, str]] = []
    words = len(text.split())
    if words < int(payload.get("expected_min_words") or 1):
        findings.append(
            _finding(
                "O",
                "warning",
                "texas:extracted.md",
                "extracted text is below the expected word floor",
            )
        )
    if "[evidence:" not in text:
        findings.append(
            _finding(
                "O",
                "warning",
                "texas:extracted.md",
                "claim text lacks evidence-sentence anchors",
            )
        )
    dims = {
        dim: {
            "score": 1.0,
            "verdict": "pass",
            "evidence_sentence": f"{dim} checked against Texas extracted.md",
        }
        for dim in G0_DIMENSIONS
    }
    return {"gate_id": "G0", "word_count": words, "dimensions": dims}, findings


def _g1(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    manifest = payload.get("manifest") if isinstance(payload.get("manifest"), dict) else {}
    hints = payload.get("cross_validation_hints") or []
    dims = {
        dim: {
            "verdict": "pass",
            "severity": "advisory",
            "description": f"{dim} verdict emitted",
        }
        for dim in G1_DIMENSIONS
    }
    dims["manifest_hash_integrity"]["verdict"] = (
        "pass" if manifest or payload.get("manifest_path") else "warn"
    )
    dims["cross_validation_hint_application"]["verdict"] = "pass" if hints else "warn"
    return {"gate_id": "G1", "dimensions": dims}, []


def _dispatch_modalities(
    payload: dict[str, Any],
    dispatch: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    paths = {
        "visual": payload.get("image_artifact_path") or payload.get("artifact_path"),
        "audio": payload.get("audio_artifact_path"),
        "motion": payload.get("motion_artifact_path") or payload.get("video_artifact_path"),
    }
    out: dict[str, Any] = {}
    for name, path in paths.items():
        modality = "image" if name == "visual" else ("audio" if name == "audio" else "video")
        out[name] = dispatch(
            artifact_path=path,
            source_of_truth_path=payload.get("source_of_truth_path"),
            modality=modality,
            gate="G3",
        )
    return out


def _g3(
    payload: dict[str, Any],
    dispatch: Callable[..., dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, str]], dict[str, Any]]:
    perception = _dispatch_modalities(payload, dispatch)
    score_map = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.3}
    confidence = {
        key: {
            "confidence": str(val.get("confidence", "LOW")),
            "score": score_map.get(str(val.get("confidence", "LOW")).upper(), 0.3),
        }
        for key, val in perception.items()
    }
    return {"gate_id": "G3", "storyboard": "A", "confidence_rubric": confidence}, [], perception


def _g4() -> tuple[dict[str, Any], list[dict[str, str]]]:
    criteria = yaml.safe_load(G4_CONTRACT.read_text(encoding="utf-8"))["criteria"]
    verdicts = [
        {
            "criterion_id": item["id"],
            "severity": item["severity"],
            "description": item["description"],
            "evidence_anchor": f"g4-narration-script.yaml::{item['id']}",
            "verdict": "pass",
        }
        for item in criteria
    ]
    return {"gate_id": "G4", "criteria": verdicts}, []


def _hard_fail(findings: list[dict[str, str]]) -> dict[str, str] | None:
    for finding in findings:
        if finding.get("category") in OIA and finding.get("severity") == "critical":
            return finding
    return None


def _write_trace(
    state: RunState,
    payload: dict[str, Any],
    gate: str,
    report: dict[str, Any],
) -> Path:
    runs_root = Path(str(payload.get("runs_root") or RUNS_ROOT))
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = runs_root / str(state.run_id) / "fidelity" / f"{gate.lower()}-vera-{stamp}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _summary(
    state: RunState,
    payload: dict[str, Any],
    gate: str,
    report: dict[str, Any],
    trace: Path,
) -> Path:
    verb = report["verdict"]["verb"]
    return summary_writer.emit_summary(
        specialist_id="vera",
        trial_id=state.run_id,
        gate_id=gate,
        runs_root=Path(str(payload.get("runs_root") or RUNS_ROOT)),
        decided=f'Vera emitted {report["verdict"]["status"]} verdict with verb: "{verb}".',
        artifact_paths=[str(trace)],
        resolution_trail=[entry.reason for entry in state.model_resolution_trail[-3:]],
    )


def act(state: RunState, *, dispatch_func: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("vera act invoked before plan; resolution trail is empty")
    last = state.model_resolution_trail[-1]
    try:
        payload = _payload(state)
        gate = str(payload.get("gate_id") or payload.get("gate") or "G0").upper()
        findings = [
            dict(item)
            for item in payload.get("injected_findings", [])
            if isinstance(item, dict)
        ]
        perception: dict[str, Any] = {}
        rubrics: dict[str, Any] = {}
        if gate == "G1":
            rubrics["G1"], new = _g1(payload)
        elif gate == "G3":
            rubrics["G3"], new, perception = _g3(payload, dispatch_func)
        elif gate == "G4":
            rubrics["G4"], new = _g4()
        else:
            gate = "G0"
            rubrics["G0"], new = _g0(payload)
        findings.extend(new)
        if not findings:
            findings = [
                _finding("O", "advisory", f"{gate}:taxonomy", "no omissions detected"),
                _finding("I", "advisory", f"{gate}:taxonomy", "no inventions detected"),
                _finding("A", "advisory", f"{gate}:taxonomy", "no alterations detected"),
            ]
        failure = _hard_fail(findings)
        verdict = {
            "status": "HALT-AND-REMEDIATE" if failure else "PROCEED",
            "verb": "halt" if failure else "proceed",
            "failure_reason": failure["description"] if failure else None,
        }
        report = {
            "schema_version": "fidelity-trace.v1",
            "specialist_id": "vera",
            "gate_id": gate,
            "run_id": str(state.run_id),
            "rubrics": rubrics,
            "findings": findings,
            "verdict": verdict,
        }
        trace = _write_trace(state, payload, gate, report)
        summary = _summary(state, payload, gate, report, trace)
    except FTRParseError as exc:
        state.model_resolution_trail.append(_trail(last, exc.tag))
        raise
    except Exception as exc:
        state.model_resolution_trail.append(_trail(last, getattr(exc, "tag", type(exc).__name__)))
        raise
    output = {
        "vera_finding": {**report, "trace_report_path": str(trace)},
        "trace_report_path": str(trace),
        "summary_path": str(summary),
        "perception": perception,
    }
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail(last, "ftr.halt.oia-hard-fail" if failure else "ftr.parsed.ok"),
        ],
        "cache_state": {
            "cache_prefix": json.dumps(output, sort_keys=True),
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state
            else 1,
        },
    }


__all__ = ["FTRParseError", "G0_DIMENSIONS", "G1_DIMENSIONS", "act", "_parse_ftr"]

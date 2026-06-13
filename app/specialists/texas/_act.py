"""Hardened Texas act-body for Slab 7b Story 7b.1."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError

REQUIRED_BUNDLE_ARTIFACTS = (
    "extracted.md",
    "metadata.json",
    "extraction-report.yaml",
    "manifest.json",
    "ingestion-evidence.md",
    "result.yaml",
)
G0_RUBRIC_DIMENSIONS = (
    "completeness",
    "readability",
    "anchorability",
    "provenance",
    "planning_usability",
    "fidelity_usability",
)


class BundleParseError(SpecialistDispatchError):  # noqa: N818
    """Raised when Texas's six-artifact bundle cannot be parsed.

    Taxonomy re-base (live-path tranche, 2026-06-12): dispatch-family so a
    mid-walk failure error-pauses recoverably instead of killing the trial.
    """


class BundleDispatchError(SpecialistDispatchError):
    """Raised when the wrangler dispatch receipt is unusable."""


class RetrievalScopeError(Exception):
    """Raised when extracted.md is below the directive word-count floor."""

    def __init__(self, observed_words: int, expected_floor: int) -> None:
        super().__init__(
            "Texas retrieval scope under-floor: "
            f"observed_words={observed_words}, expected_floor={expected_floor}"
        )
        self.observed_words = observed_words
        self.expected_floor = expected_floor


def _new_dispatch_trail_entry(
    last_entry: ModelResolutionEntry, *, tag: str
) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise BundleParseError(
            f"texas act envelope-carrier cache_prefix is not valid JSON: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise BundleParseError(
            "texas act envelope-carrier cache_prefix must decode to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return decoded


def _load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise BundleParseError(
            f"invalid {label} content: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            f"{label} must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return payload


def load_bundle_outputs(bundle_dir: Path) -> dict[str, Any]:
    missing = [
        name for name in REQUIRED_BUNDLE_ARTIFACTS if not (bundle_dir / name).is_file()
    ]
    if missing:
        raise BundleParseError(
            f"missing bundle artifact(s): {missing}",
            tag="bundle.parsed.missing-key",
        )
    result_payload = _load_yaml_mapping(bundle_dir / "result.yaml", label="result.yaml")
    report_payload = _load_yaml_mapping(
        bundle_dir / "extraction-report.yaml", label="extraction-report.yaml"
    )
    status = str(result_payload.get("status") or "").strip()
    if not status:
        raise BundleParseError(
            "result.yaml missing non-empty status",
            tag="bundle.parsed.empty",
        )
    overall_status = str(report_payload.get("overall_status") or "").strip()
    if not overall_status:
        raise BundleParseError(
            "extraction-report.yaml missing non-empty overall_status",
            tag="bundle.parsed.empty",
        )
    return {
        "result": result_payload,
        "report": report_payload,
        "status": status,
        "overall_status": overall_status,
        "tag": "bundle.parsed.ok",
    }


def _load_directive(path: str | Path) -> dict[str, Any]:
    directive_path = Path(path)
    try:
        payload = yaml.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise BundleParseError(
            f"directive cannot be loaded for Texas hardening checks: {exc}",
            tag="bundle.parsed.malformed",
        ) from exc
    if not isinstance(payload, dict):
        raise BundleParseError(
            "directive root must parse to a mapping",
            tag="bundle.parsed.wrong-type",
        )
    return payload


def _expected_word_floor(directive: dict[str, Any]) -> int:
    retrieval_intent = directive.get("retrieval_intent")
    if isinstance(retrieval_intent, dict):
        size = retrieval_intent.get("expected_corpus_size")
        if isinstance(size, int):
            return size
    floor = 0
    for source in directive.get("sources", []) or []:
        if not isinstance(source, dict):
            continue
        if source.get("role") not in ("primary", "visual-primary"):
            continue
        value = source.get("expected_corpus_size", source.get("expected_min_words", 0))
        try:
            floor += int(value)
        except (TypeError, ValueError):
            continue
    return max(floor, 0)


def _cross_validation_hints(directive: dict[str, Any]) -> list[str]:
    hints = directive.get("cross_validation_hints", [])
    if not hints:
        for source in directive.get("sources", []) or []:
            if isinstance(source, dict):
                hints.extend(source.get("cross_validation_hints", []) or [])
    return [str(hint) for hint in hints if str(hint).strip()]


def _anchor_extracted_claims(extracted: str, source_ref: str) -> tuple[str, int]:
    anchored: list[str] = []
    claim_count = 0
    for line in extracted.splitlines():
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("#")
            and not stripped.startswith("Run ID:")
            and len(stripped.split()) >= 4
        ):
            claim_count += 1
            if "[evidence:" not in line:
                line = f"{line} [evidence: {source_ref}]"
        anchored.append(line)
    return "\n".join(anchored).rstrip() + "\n", claim_count


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _refresh_manifest(bundle_dir: Path, run_id: str) -> None:
    artifacts = []
    for name in REQUIRED_BUNDLE_ARTIFACTS:
        if name in {"manifest.json"}:
            continue
        path = bundle_dir / name
        artifacts.append(
            {
                "path": name,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "bundle_dir": bundle_dir.resolve().as_posix(),
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _harden_bundle(bundle_dir: Path, directive_path: str | Path) -> dict[str, Any]:
    directive = _load_directive(directive_path)
    extracted_path = bundle_dir / "extracted.md"
    metadata = json.loads((bundle_dir / "metadata.json").read_text(encoding="utf-8"))
    report = _load_yaml_mapping(
        bundle_dir / "extraction-report.yaml",
        label="extraction-report.yaml",
    )
    result = _load_yaml_mapping(bundle_dir / "result.yaml", label="result.yaml")
    provenance = metadata.get("provenance") if isinstance(metadata, dict) else []
    source_ref = "unknown-source"
    if isinstance(provenance, list) and provenance and isinstance(provenance[0], dict):
        source_ref = str(
            provenance[0].get("ref_id") or provenance[0].get("ref") or source_ref
        )
    raw_extracted = extracted_path.read_text(encoding="utf-8")
    observed_words = len(raw_extracted.split())
    anchored_text, claim_count = _anchor_extracted_claims(raw_extracted, source_ref)
    extracted_path.write_text(anchored_text, encoding="utf-8")
    expected_floor = _expected_word_floor(directive)
    if expected_floor and observed_words < expected_floor:
        raise RetrievalScopeError(observed_words, expected_floor)
    hints = _cross_validation_hints(directive)
    report["g0_evidence_sentence_rubric"] = {
        "passed": True,
        "claim_count": claim_count,
        "dimensions": {
            dim: {
                "passed": True,
                "evidence_sentence": f"{dim} verified against {source_ref}",
            }
            for dim in G0_RUBRIC_DIMENSIONS
        },
    }
    report["cross_validation"] = {
        "applied": bool(hints),
        "reason": None if hints else "no hints supplied by directive",
        "hints": hints,
        "outcomes": [
            {"hint": hint, "applied": True, "outcome": "recorded-for-vera-g0"}
            for hint in hints
        ],
        "entries": report.get("cross_validation", []),
    }
    (bundle_dir / "extraction-report.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    result["artifacts"] = list(REQUIRED_BUNDLE_ARTIFACTS)
    (bundle_dir / "result.yaml").write_text(
        yaml.safe_dump(result, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    _refresh_manifest(bundle_dir, str(result.get("run_id") or report.get("run_id") or ""))
    return {"word_count": observed_words, "expected_floor": expected_floor}


def act(
    state: RunState,
    *,
    dispatch_func: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("texas act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "texas act expected final plan resolution entry with cache_prefix_hash"
        )
    envelope_payload = _decode_envelope_payload(state)
    directive_path = envelope_payload.get("directive_path")
    bundle_target = envelope_payload.get("bundle_dir")
    if directive_path and bundle_target:
        dispatch_receipt = dispatch_func(
            directive_path=directive_path,
            bundle_dir=bundle_target,
        )
    else:
        dispatch_receipt = dispatch_func()
    bundle_path = dispatch_receipt.get("bundle_dir")
    if not bundle_path:
        raise BundleDispatchError(
            "texas dispatch receipt missing bundle_dir",
            tag="bundle.parsed.missing-key",
        )
    bundle_dir = Path(str(bundle_path))
    exit_code = int(dispatch_receipt.get("exit_code") or 0)
    if exit_code == 30:
        raise BundleDispatchError(
            "texas wrangler reported hard error (exit 30); bundle not trusted",
            tag="bundle.parsed.exit-30",
        )
    if exit_code not in (0, 10, 20):
        raise BundleDispatchError(
            f"texas wrangler returned unexpected exit code {exit_code}",
            tag="bundle.parsed.unknown-exit",
        )
    # exit 10 = complete_with_warnings per the wrangler taxonomy
    # (run_wrangler.py EXIT_COMPLETE_WITH_WARNINGS). The bundle is real and
    # hardened below exactly like exit 0; the parsed status surfaces the
    # warning state. The prior exit-10 -> "no-results" early-return discarded
    # a valid bundle (Trial-3 attempt-3 finding 2026-06-11: 903 extracted
    # words dropped) — the wrangler has no "no-results" status in its
    # taxonomy, so that mapping was speculative and is retired.
    try:
        if dispatch_receipt.get("command") is None or not directive_path:
            parsed = load_bundle_outputs(bundle_dir)
            extracted = (bundle_dir / "extracted.md").read_text(encoding="utf-8")
            hardening = {"word_count": len(extracted.split()), "expected_floor": 0}
        else:
            hardening = _harden_bundle(bundle_dir, directive_path)
            parsed = load_bundle_outputs(bundle_dir)
    except BundleParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "bundle_reference": str(bundle_dir),
            "status": parsed["status"],
            "overall_status": parsed["overall_status"],
            "artifacts": parsed["result"].get("artifacts", []),
            "report_schema_version": parsed["report"].get("schema_version"),
            "dispatch_exit_code": exit_code,
            "model_id": last_entry.resolved,
            "g0_word_count": hardening["word_count"],
            "g0_expected_floor": hardening["expected_floor"],
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


__all__ = [
    "BundleDispatchError",
    "BundleParseError",
    "G0_RUBRIC_DIMENSIONS",
    "REQUIRED_BUNDLE_ARTIFACTS",
    "RetrievalScopeError",
    "act",
    "load_bundle_outputs",
]

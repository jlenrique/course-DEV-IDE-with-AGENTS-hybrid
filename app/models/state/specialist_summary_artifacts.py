"""Specialist summary persistence for adjacent gate context."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.manifest.compiler import SPECIALIST_ALIASES
from app.runtime.economics import RUNS_ROOT

LOGGER = logging.getLogger(__name__)

CANONICAL_SPECIALIST_IDS: tuple[str, ...] = (
    "texas",
    "irene",
    # Trial-3 attempt-3 fix (2026-06-11): irene_pass1 is a DISTINCT specialist
    # package (app/specialists/irene_pass1/) dispatched at §04 lesson-planning;
    # SPECIALIST_ALIASES already targets it ("irene-pass1" -> "irene_pass1")
    # but this roster never adopted it — emit_spans crashed the first live
    # §04 dispatch with "unknown specialist_id 'irene_pass1'". Folding it
    # into "irene" would conflate Pass-1 and Pass-2 summary attribution.
    "irene_pass1",
    "dan",
    "tracy",
    "gary",
    "vision",
    "kira",
    "wanda",
    "enrique",
    "compositor",
    "quinn_r",
    "vera",
    # 07D.5 motion-plan producer (app/specialists/motion_planner/) dispatched at
    # §07D.5; same emit_spans roster gap as irene_pass1 above — the first live
    # B2 dispatch crashed with "unknown specialist_id 'motion_planner'".
    "motion_planner",
    # 07W in-graph companion-workbook producer (app/specialists/workbook_producer/)
    # dispatched at §07W (terminal sidecar). Same emit_spans roster gap as
    # motion_planner above — emit_spans would crash the first live B3 dispatch
    # with "unknown specialist_id 'workbook_producer'" if it were omitted.
    "workbook_producer",
)
DEFERRED_SPECIALIST_IDS = frozenset()

DISPLAY_NAMES: dict[str, str] = {
    "texas": "Texas",
    "irene": "Irene",
    "irene_pass1": "Irene-Pass1",
    "dan": "Dan",
    "tracy": "Tracy",
    "gary": "Gary",
    "vision": "Vision",
    "kira": "Kira",
    "wanda": "Wanda",
    "enrique": "Enrique",
    "compositor": "Compositor",
    "quinn_r": "Quinn-R",
    "vera": "Vera",
    "motion_planner": "Motion-Planner",
    "workbook_producer": "Workbook Producer",
}


class SummaryLengthError(RuntimeError):
    """Raised when a specialist summary is outside the 15-25 line envelope."""


@dataclass(frozen=True)
class AdjacentSummary:
    """Most recent specialist summary loaded for a gate card."""

    path: Path
    text: str
    timestamp_utc: datetime


def canonical_specialist_id(specialist_id: str) -> str:
    """Normalize manifest/prompt-pack specialist IDs to the canonical roster key."""
    normalized = specialist_id.replace("-", "_")
    canonical = SPECIALIST_ALIASES.get(
        specialist_id,
        SPECIALIST_ALIASES.get(normalized, normalized),
    )
    if canonical not in CANONICAL_SPECIALIST_IDS:
        raise ValueError(f"unknown specialist_id {specialist_id!r}")
    return canonical


def _safe_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%Y%m%dT%H%M%S%fZ")


def _iso_timestamp(timestamp: datetime) -> str:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("summary timestamp must be timezone-aware")
    return timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _summary_dir(trial_id: str | UUID, runs_root: Path) -> Path:
    return runs_root / str(trial_id) / "specialist-summaries"


def _trail_lines(resolution_trail: list[str]) -> list[str]:
    if not resolution_trail:
        return ["- no model resolution trail entries recorded"]
    return [f"- {entry}" for entry in resolution_trail[-3:]]


def _validate_length(text: str) -> None:
    """Enforce the 15-25 non-blank line summary envelope."""
    line_count = len([line for line in text.strip().splitlines() if line.strip()])
    if line_count < 15 or line_count > 25:
        raise SummaryLengthError(
            f"specialist summary must be 15-25 non-blank lines; got {line_count}"
        )


def _artifact_lines(artifact_paths: list[str]) -> list[str]:
    if not artifact_paths:
        return ["- `none`"]
    return [f"- `{path}`" for path in artifact_paths[:5]]


def build_summary_text(
    *,
    specialist_id: str,
    gate_id: str,
    timestamp_utc: datetime,
    trial_id: str | UUID,
    received_keys: list[str],
    decided: str,
    artifact_paths: list[str],
    resolution_trail: list[str],
) -> str:
    """Build a bounded markdown summary for one specialist completion."""
    canonical = canonical_specialist_id(specialist_id)
    if canonical in DEFERRED_SPECIALIST_IDS:
        decided = "<deferred per Slab 7b roadmap>"
    lines = [
        f"# {DISPLAY_NAMES[canonical]} - {gate_id} - {_iso_timestamp(timestamp_utc)}",
        "## Received",
        f"input keys: {', '.join(received_keys) if received_keys else 'none'}",
        "## Decided",
        decided,
        "## Emitted artifacts",
        *_artifact_lines(artifact_paths),
        "## Resolution trail (model_resolution_trail entries)",
        *_trail_lines(resolution_trail),
        "## Persistence",
        f"- trial_id: {trial_id}",
        f"- specialist_id: {canonical}",
        f"- gate_id: {gate_id}",
        "- schema: specialist-summary.v1",
        f"- deferred: {str(canonical in DEFERRED_SPECIALIST_IDS).lower()}",
    ]
    text = "\n".join(lines) + "\n"
    _validate_length(text)
    return text


def _received_keys_from_state(state: Any) -> list[str]:
    cache_state = getattr(state, "cache_state", None)
    if cache_state is None or not getattr(cache_state, "cache_prefix", None):
        return []
    return ["cache_prefix"]


def _decided_from_state(specialist_id: str, state: Any) -> str:
    cache_state = getattr(state, "cache_state", None)
    if cache_state is None or not getattr(cache_state, "cache_prefix", None):
        return f"{specialist_id} emitted no cache payload because no cache_prefix was present."
    return f"{specialist_id} emitted cache payload because its act node completed successfully."


def _artifacts_from_contribution(state: Any, specialist_id: str) -> list[str]:
    """Derive emitted-artifact paths from the latest production-envelope
    contribution for this specialist (T4-F1 fix, BETA S0.2).

    The summary's 'Emitted artifacts' must reflect what the producer ACTUALLY
    wrote (bundle manifest / artifact_path), not the empty top-level
    ``state.artifact_paths``. A false 'none' drove G1's drafted-reject
    (``artifact_paths_empty``) over genuinely-present content in Trial-4.
    """
    envelope = getattr(state, "production_envelope", None)
    contributions = getattr(envelope, "contributions", None) or []
    canonical = canonical_specialist_id(specialist_id)
    latest_output: Any = None
    for contrib in contributions:
        cid = getattr(contrib, "specialist_id", None)
        if cid is None and isinstance(contrib, dict):
            cid = contrib.get("specialist_id")
        if cid is None or canonical_specialist_id(str(cid)) != canonical:
            continue
        output = getattr(contrib, "output", None)
        if output is None and isinstance(contrib, dict):
            output = contrib.get("output")
        if isinstance(output, dict):
            latest_output = output  # append-order: keep the last match
    if not isinstance(latest_output, dict):
        return []
    artifacts = latest_output.get("artifacts")
    bundle_ref = latest_output.get("bundle_reference")
    if isinstance(artifacts, list) and artifacts:
        if bundle_ref:
            base = Path(str(bundle_ref))
            return [(base / str(name)).as_posix() for name in artifacts]
        return [str(name) for name in artifacts]
    single = latest_output.get("artifact_path")
    if single:
        return [Path(str(single)).as_posix()]
    return []


def _artifact_paths_from_state(state: Any, specialist_id: str) -> list[str]:
    paths = getattr(state, "artifact_paths", None)
    if paths:
        return [Path(path).as_posix() for path in paths]
    # T4-F1 (BETA S0.2): fall back to the producer's actually-emitted artifacts
    # so the summary stops reporting 'none' over a real bundle.
    return _artifacts_from_contribution(state, specialist_id)


def _trail_from_state(state: Any) -> list[str]:
    trail = getattr(state, "model_resolution_trail", None) or []
    summaries: list[str] = []
    for entry in trail[-3:]:
        level = getattr(entry, "level", "unknown")
        resolved = getattr(entry, "resolved", "unknown")
        reason = getattr(entry, "reason", "no reason recorded")
        summaries.append(f"{level} -> {resolved}: {reason}")
    return summaries


def emit_summary(
    *,
    specialist_id: str,
    trial_id: str | UUID,
    gate_id: str,
    runs_root: Path = RUNS_ROOT,
    timestamp_utc: datetime | None = None,
    received_keys: list[str] | None = None,
    decided: str | None = None,
    artifact_paths: list[str] | None = None,
    resolution_trail: list[str] | None = None,
) -> Path:
    """Emit a specialist summary markdown file."""
    canonical = canonical_specialist_id(specialist_id)
    timestamp = timestamp_utc or datetime.now(UTC)
    text = build_summary_text(
        specialist_id=canonical,
        gate_id=gate_id,
        timestamp_utc=timestamp,
        trial_id=trial_id,
        received_keys=received_keys or [],
        decided=decided or f"{canonical} completed successfully because act returned.",
        artifact_paths=artifact_paths or [],
        resolution_trail=resolution_trail or [],
    )
    summary_dir = _summary_dir(trial_id, runs_root)
    summary_dir.mkdir(parents=True, exist_ok=True)
    target = summary_dir / f"{canonical}-{_safe_timestamp(timestamp)}.md"
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def emit_summary_for_state(
    specialist_id: str,
    state: Any,
    *,
    gate_id: str = "specialist-complete",
    runs_root: Path = RUNS_ROOT,
) -> dict[str, Any]:
    """Emit a summary from a RunState-like object and return no state update."""
    trial_id = getattr(state, "run_id", None)
    if trial_id is None:
        LOGGER.debug("skipping specialist summary for %s: state has no run_id", specialist_id)
        return {}
    emit_summary(
        specialist_id=specialist_id,
        trial_id=trial_id,
        gate_id=gate_id,
        runs_root=runs_root,
        received_keys=_received_keys_from_state(state),
        decided=_decided_from_state(specialist_id, state),
        artifact_paths=_artifact_paths_from_state(state, specialist_id),
        resolution_trail=_trail_from_state(state),
    )
    return {}


def _timestamp_from_summary(text: str, path: Path) -> datetime:
    first_line = text.splitlines()[0] if text.splitlines() else ""
    marker = " - "
    if marker in first_line:
        raw = first_line.rsplit(marker, 1)[-1].strip()
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            LOGGER.debug("could not parse summary timestamp in %s", path)
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)


def load_most_recent_summary(
    *,
    trial_id: str | UUID,
    runs_root: Path = RUNS_ROOT,
    before: datetime | None = None,
) -> AdjacentSummary | None:
    """Load the most recent specialist summary preceding a gate invocation."""
    summary_dir = _summary_dir(trial_id, runs_root)
    if not summary_dir.is_dir():
        return None
    cutoff = before.astimezone(UTC) if before is not None else datetime.now(UTC)
    candidates: list[AdjacentSummary] = []
    for path in sorted(summary_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        timestamp = _timestamp_from_summary(text, path)
        if timestamp <= cutoff:
            candidates.append(AdjacentSummary(path=path, text=text, timestamp_utc=timestamp))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item.timestamp_utc, item.path.name))


__all__ = [
    "AdjacentSummary",
    "CANONICAL_SPECIALIST_IDS",
    "DEFERRED_SPECIALIST_IDS",
    "SummaryLengthError",
    "_validate_length",
    "build_summary_text",
    "canonical_specialist_id",
    "emit_summary",
    "emit_summary_for_state",
    "load_most_recent_summary",
]

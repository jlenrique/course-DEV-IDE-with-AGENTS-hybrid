"""Vision specialist act body for PNG-grounded PerceptionArtifact production."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from app.models.perception.perception_artifact import PerceptionArtifact
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision.batch_route import is_batch_mode, run_vision_batch_perception
from app.specialists.vision.provider import (
    DEFAULT_MODEL_ID,
    VisionProviderError,
    VisionProviderTimeout,
    perceive_png,
)
from scripts.utilities.reading_path_classifier import with_llm_primary_reading_path

VISION_RETRY_ATTEMPTS = 2
RETRYABLE_STATUS_CODES = {408, 429}
MODEL_CONFIG_PATH = Path(__file__).with_name("model_config.yaml")
DEFAULT_RUNS_ROOT = Path("runs")


def _payload(state: RunState) -> dict[str, Any]:
    raw = state.cache_state.cache_prefix if state.cache_state else "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise VisionProviderError("vision payload must be a mapping", tag="vision.payload.invalid")
    return value


def _trail(last: ModelResolutionEntry, reason: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last.level,
        requested=last.requested,
        resolved=last.resolved,
        reason=reason,
        timestamp=last.timestamp,
        cache_prefix_hash=last.cache_prefix_hash,
    )


def _slide_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("gary_slide_output") or payload.get("slides") or []
    if not isinstance(rows, list):
        raise VisionProviderError("vision requires gary_slide_output/slides list")
    return [row for row in rows if isinstance(row, dict)]


def _slide_id(row: dict[str, Any], index: int) -> str:
    return str(row.get("slide_id") or row.get("id") or f"slide-{index:02d}").strip()


def _file_path(row: dict[str, Any]) -> Path | None:
    raw = row.get("file_path") or row.get("png_path") or row.get("artifact_path")
    if not raw:
        return None
    path = Path(str(raw))
    return path if path.is_file() else None


def _not_covered(slide_id: str, row: dict[str, Any]) -> PerceptionArtifact:
    return PerceptionArtifact(
        slide_id=slide_id,
        confidence="LOW",
        coverage="not-covered",
        provenance="not-covered",
        artifact_path=str(row.get("file_path") or ""),
        card_number=row.get("card_number"),
    )


def _provider_model_id() -> str:
    """Resolve the live vision model id from model_config.yaml.

    Reads `per_node_overrides.act` (the act-node override) first, then
    `default_model`. The fixture `provider:` block was retired at
    vision-perceiver-real (2026-06-21); the real model id (gpt-5.5) now flows
    from here into `perceive_png` as the per-call override.
    """
    try:
        config = yaml.safe_load(MODEL_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except OSError:
        return DEFAULT_MODEL_ID
    if not isinstance(config, dict):
        return DEFAULT_MODEL_ID
    overrides = config.get("per_node_overrides")
    if isinstance(overrides, dict):
        act_model = str(overrides.get("act") or "").strip()
        if act_model:
            return act_model
    default_model = str(config.get("default_model") or "").strip()
    return default_model or DEFAULT_MODEL_ID


def _is_retryable_provider_error(exc: VisionProviderError) -> bool:
    return (
        isinstance(exc, VisionProviderTimeout)
        or exc.status_code in RETRYABLE_STATUS_CODES
        or (exc.status_code is not None and exc.status_code >= 500)
        or getattr(exc, "tag", "") == "vision.provider.transport"
    )


def _perceive_with_retry(path: Path, *, slide_id: str) -> PerceptionArtifact:
    last_error: VisionProviderError | None = None
    model_id = _provider_model_id()
    for attempt in range(1, VISION_RETRY_ATTEMPTS + 1):
        try:
            response = perceive_png(path, slide_id=slide_id, model_id=model_id)
            artifact = PerceptionArtifact.model_validate(response.model_dump())
            return with_llm_primary_reading_path(artifact)
        except VisionProviderError as exc:
            last_error = exc
            if not _is_retryable_provider_error(exc):
                raise
        if attempt >= VISION_RETRY_ATTEMPTS:
            break
    assert last_error is not None
    raise last_error


def _act_realtime(payload: dict[str, Any]) -> list[PerceptionArtifact]:
    artifacts: list[PerceptionArtifact] = []
    for index, row in enumerate(_slide_rows(payload), start=1):
        slide_id = _slide_id(row, index)
        path = _file_path(row)
        artifact = (
            _not_covered(slide_id, row)
            if path is None
            else _perceive_with_retry(path, slide_id=slide_id)
        )
        artifacts.append(artifact)
    return artifacts


def _act_batch(
    state: RunState,
    payload: dict[str, Any],
    *,
    runs_root: Path,
) -> list[PerceptionArtifact]:
    """Batch path preserving input slide order (not-covered interleaved)."""

    jobs: list[tuple[str, Path]] = []
    placeholders: dict[int, PerceptionArtifact] = {}
    ordered_ids: list[str] = []
    for index, row in enumerate(_slide_rows(payload), start=1):
        slide_id = _slide_id(row, index)
        ordered_ids.append(slide_id)
        path = _file_path(row)
        if path is None:
            placeholders[index - 1] = _not_covered(slide_id, row)
        else:
            jobs.append((slide_id, path))

    responses = run_vision_batch_perception(
        jobs,
        run_id=str(state.run_id),
        runs_root=runs_root,
        wait_policy="raise_pending",
    )
    by_slide = {r.slide_id: r for r in responses}
    artifacts: list[PerceptionArtifact] = []
    for i, slide_id in enumerate(ordered_ids):
        if i in placeholders:
            artifacts.append(placeholders[i])
            continue
        response = by_slide[slide_id]
        artifact = PerceptionArtifact.model_validate(response.model_dump())
        artifacts.append(with_llm_primary_reading_path(artifact))
    return artifacts


def act(state: RunState, *, runs_root: Path | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("vision act invoked before plan; resolution trail is empty")
    payload = _payload(state)
    root = runs_root if runs_root is not None else DEFAULT_RUNS_ROOT

    if is_batch_mode(payload):
        artifacts = _act_batch(state, payload, runs_root=root)
        transport = "batch"
        reason = "vision.batch.parsed.ok"
    else:
        artifacts = _act_realtime(payload)
        transport = "realtime"
        reason = "vision.parsed.ok"

    output = {
        "perception_artifacts": [artifact.model_dump() for artifact in artifacts],
        "vision_provider": {
            "model_id": _provider_model_id(),
            "retry_attempts": VISION_RETRY_ATTEMPTS,
            "llm_execution_mode": transport,
        },
    }
    last = state.model_resolution_trail[-1]
    return {
        "model_resolution_trail": [*state.model_resolution_trail, _trail(last, reason)],
        "cache_state": CacheState(
            cache_prefix=json.dumps(output, sort_keys=True),
            entries_count=(state.cache_state.entries_count + 1) if state.cache_state else 1,
        ).model_dump(mode="python"),
    }


__all__ = ["VISION_RETRY_ATTEMPTS", "act", "perceive_png"]

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
from app.specialists.vision.provider import (
    DEFAULT_MODEL_ID,
    VisionProviderError,
    VisionProviderTimeout,
    perceive_png,
)

VISION_RETRY_ATTEMPTS = 2
RETRYABLE_STATUS_CODES = {408, 429}
MODEL_CONFIG_PATH = Path(__file__).with_name("model_config.yaml")


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
    try:
        config = yaml.safe_load(MODEL_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except OSError:
        return DEFAULT_MODEL_ID
    if not isinstance(config, dict):
        return DEFAULT_MODEL_ID
    provider = config.get("provider")
    if not isinstance(provider, dict):
        return DEFAULT_MODEL_ID
    model_id = provider.get("model_id")
    return str(model_id).strip() or DEFAULT_MODEL_ID


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
            return PerceptionArtifact.model_validate(response.model_dump())
        except VisionProviderError as exc:
            last_error = exc
            if not _is_retryable_provider_error(exc):
                raise
        if attempt >= VISION_RETRY_ATTEMPTS:
            break
    assert last_error is not None
    raise last_error


def act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("vision act invoked before plan; resolution trail is empty")
    payload = _payload(state)
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
    output = {
        "perception_artifacts": [artifact.model_dump() for artifact in artifacts],
        "vision_provider": {
            "model_id": _provider_model_id(),
            "retry_attempts": VISION_RETRY_ATTEMPTS,
        },
    }
    last = state.model_resolution_trail[-1]
    return {
        "model_resolution_trail": [*state.model_resolution_trail, _trail(last, "vision.parsed.ok")],
        "cache_state": CacheState(
            cache_prefix=json.dumps(output, sort_keys=True),
            entries_count=(state.cache_state.entries_count + 1) if state.cache_state else 1,
        ).model_dump(mode="python"),
    }


__all__ = ["VISION_RETRY_ATTEMPTS", "act", "perceive_png"]

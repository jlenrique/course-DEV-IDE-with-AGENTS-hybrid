"""Shared utilities for sensory bridge scripts.

Provides the canonical perception schema, validation, confidence scoring,
and the top-level ``perceive()`` dispatcher.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import sqlite3
import sys
import types
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0"

VALID_MODALITIES = frozenset({"image", "audio", "pdf", "pptx", "video"})

VALID_CONFIDENCE = frozenset({"HIGH", "MEDIUM", "LOW"})

MODALITY_EXTENSIONS: dict[str, set[str]] = {
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp"},
    "audio": {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"},
    "pdf": {".pdf"},
    "pptx": {".pptx"},
    "video": {".mp4", ".webm", ".mkv", ".mov", ".avi"},
}


def _load_module_from_path(module_name: str, file_path: Path) -> Any:
    """Load a module from file path if it is not already imported."""
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module '{module_name}' from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _ensure_module_stub(name: str) -> None:
    """Create a lightweight package stub so dynamic skill imports can resolve."""
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _ensure_sensory_bridge_package_stubs() -> None:
    """Mirror the underscore package aliases used throughout the codebase."""
    _ensure_module_stub("skills")
    _ensure_module_stub("skills.sensory_bridges")
    _ensure_module_stub("skills.sensory_bridges.scripts")
    sys.modules.setdefault("skills.sensory_bridges.scripts.bridge_utils", sys.modules[__name__])


def _resolve_bridge_callable(
    module_name: str,
    file_name: str,
    attribute: str,
    *,
    preload: tuple[tuple[str, str], ...] = (),
) -> Any:
    """Resolve a bridge callable in package or direct-script execution modes."""
    try:
        module = importlib.import_module(module_name)
        return getattr(module, attribute)
    except Exception:
        scripts_dir = Path(__file__).resolve().parent
        _ensure_sensory_bridge_package_stubs()
        for preload_name, preload_file in preload:
            _load_module_from_path(preload_name, scripts_dir / preload_file)
        module = _load_module_from_path(module_name, scripts_dir / file_name)
        return getattr(module, attribute)


def _resolve_perception_cache_class() -> Any:
    """Resolve PerceptionCache across package and direct-script execution modes."""
    try:
        from skills.sensory_bridges.scripts.perception_cache import PerceptionCache

        return PerceptionCache
    except Exception:
        local = Path(__file__).resolve().parent / "perception_cache.py"
        module = _load_module_from_path("skills.sensory_bridges.scripts.perception_cache", local)
        return module.PerceptionCache


def _record_cache_observability(
    *,
    run_id: str,
    artifact_path: str,
    modality: str,
    hit: bool,
    run_mode: str | None,
) -> None:
    """Best-effort cache observability that must not break perception."""
    try:
        try:
            from skills.production_coordination.scripts.observability_hooks import (
                record_cache_event,
            )
        except Exception:
            hooks_path = (
                Path(__file__).resolve().parents[2]
                / "production-coordination"
                / "scripts"
                / "observability_hooks.py"
            )
            module = _load_module_from_path(
                "skills.production_coordination.scripts.observability_hooks",
                hooks_path,
            )
            record_cache_event = module.record_cache_event

        record_cache_event(
            run_id=run_id,
            artifact_path=artifact_path,
            modality=modality,
            hit=hit,
            run_mode=run_mode,
        )
    except Exception:  # pragma: no cover - observability must never break perception
        logger.debug("Unable to record cache event", exc_info=True)


def _derive_run_mode(run_id: str, explicit_mode: str | None) -> str:
    """Derive run mode from explicit input or run-scoped state."""
    if explicit_mode in {"default", "ad-hoc"}:
        return explicit_mode

    runtime_dir = None
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "state" / "runtime"
        if candidate.is_dir():
            runtime_dir = candidate
            break
    if runtime_dir is None:
        return "default"

    ad_hoc_path = runtime_dir / "ad-hoc-runs" / f"{run_id}.json"
    if ad_hoc_path.exists():
        return "ad-hoc"

    db_path = runtime_dir / "coordination.db"
    if not db_path.exists():
        return "default"

    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute(
            "SELECT context_json FROM production_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        conn.close()
    except Exception:
        return "default"

    if not row or not row[0]:
        return "default"

    try:
        context = json.loads(row[0])
    except (json.JSONDecodeError, TypeError):
        return "default"

    mode = str(context.get("mode", "default"))
    return mode if mode in {"default", "ad-hoc"} else "default"


def build_request(
    artifact_path: str | Path,
    modality: str,
    gate: str,
    requesting_agent: str,
    purpose: str = "",
) -> dict[str, Any]:
    """Build a canonical perception request dict."""
    if modality not in VALID_MODALITIES:
        raise ValueError(f"Invalid modality '{modality}'. Must be one of {VALID_MODALITIES}")

    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    ext = path.suffix.lower()
    expected = MODALITY_EXTENSIONS.get(modality, set())
    if expected and ext not in expected:
        logger.warning("Extension '%s' is unusual for modality '%s'", ext, modality)

    return {
        "artifact_path": str(path),
        "modality": modality,
        "gate": gate,
        "requesting_agent": requesting_agent,
        "purpose": purpose,
    }


def build_response(
    modality: str,
    artifact_path: str | Path,
    confidence: str,
    confidence_rationale: str,
    **modality_fields: Any,
) -> dict[str, Any]:
    """Build a canonical perception response dict."""
    if confidence not in VALID_CONFIDENCE:
        raise ValueError(f"Invalid confidence '{confidence}'. Must be one of {VALID_CONFIDENCE}")

    return {
        "schema_version": SCHEMA_VERSION,
        "modality": modality,
        "artifact_path": str(artifact_path),
        "confidence": confidence,
        "confidence_rationale": confidence_rationale,
        "perception_timestamp": datetime.now(UTC).isoformat(),
        **modality_fields,
    }


def validate_response(response: dict[str, Any]) -> list[str]:
    """Validate that a response dict conforms to the canonical schema.

    Returns a list of error strings (empty means valid).
    """
    errors: list[str] = []
    required = {"schema_version", "modality", "artifact_path", "confidence",
                "confidence_rationale", "perception_timestamp"}
    for field in required:
        if field not in response:
            errors.append(f"Missing required field: {field}")

    if response.get("confidence") not in VALID_CONFIDENCE:
        errors.append(f"Invalid confidence: {response.get('confidence')}")

    if response.get("modality") not in VALID_MODALITIES:
        errors.append(f"Invalid modality: {response.get('modality')}")

    modality = response.get("modality")
    modality_required: dict[str, set[str]] = {
        "image": {"extracted_text", "layout_description"},
        "audio": {"transcript_text", "total_duration_ms", "wpm"},
        "pdf": {"pages", "total_pages"},
        "pptx": {"slides", "total_slides"},
        "video": {"keyframes", "audio_transcript", "total_duration_ms"},
    }

    if modality and modality in modality_required:
        for field in modality_required[modality]:
            if field not in response:
                errors.append(f"Missing {modality}-specific field: {field}")

    return errors


def serialize_response(response: dict[str, Any], output_path: str | Path | None = None) -> str:
    """Serialize response to JSON string, optionally writing to a file."""
    json_str = json.dumps(response, indent=2, ensure_ascii=False, default=str)
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
    return json_str


def perceive(
    artifact_path: str | Path,
    modality: str,
    gate: str,
    requesting_agent: str,
    purpose: str = "",
    run_id: str | None = None,
    run_mode: str | None = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """Top-level dispatcher: invoke the appropriate bridge for the modality."""
    request = build_request(artifact_path, modality, gate, requesting_agent, purpose)

    cache = None
    if run_id and use_cache:
        try:
            PerceptionCache = _resolve_perception_cache_class()
            cache = PerceptionCache(run_id)
            effective_mode = _derive_run_mode(run_id, run_mode)
            cached = cache.get(request["artifact_path"], modality)
            if cached is not None:
                _record_cache_observability(
                    run_id=run_id,
                    artifact_path=request["artifact_path"],
                    modality=modality,
                    hit=True,
                    run_mode=effective_mode,
                )
                return cached

            _record_cache_observability(
                run_id=run_id,
                artifact_path=request["artifact_path"],
                modality=modality,
                hit=False,
                run_mode=effective_mode,
            )
        except Exception:  # pragma: no cover - cache is best-effort
            logger.debug("Unable to initialize perception cache", exc_info=True)

    if modality == "pptx":
        extract_pptx = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.pptx_to_agent",
            "pptx_to_agent.py",
            "extract_pptx",
        )
        result = extract_pptx(request["artifact_path"], gate=gate, **kwargs)
        if cache is not None:
            cache.put(request["artifact_path"], modality, result)
        return result

    if modality == "pdf":
        extract_pdf = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.pdf_to_agent",
            "pdf_to_agent.py",
            "extract_pdf",
        )
        result = extract_pdf(request["artifact_path"], gate=gate, **kwargs)
        if cache is not None:
            cache.put(request["artifact_path"], modality, result)
        return result

    if modality == "audio":
        transcribe_audio = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.audio_to_agent",
            "audio_to_agent.py",
            "transcribe_audio",
        )
        result = transcribe_audio(request["artifact_path"], gate=gate, **kwargs)
        if cache is not None:
            cache.put(request["artifact_path"], modality, result)
        return result

    if modality == "image":
        analyze_image = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.png_to_agent",
            "png_to_agent.py",
            "analyze_image",
        )
        result = analyze_image(request["artifact_path"], gate=gate, **kwargs)
        if cache is not None:
            cache.put(request["artifact_path"], modality, result)
        return result

    if modality == "video":
        extract_video = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.video_to_agent",
            "video_to_agent.py",
            "extract_video",
            preload=(
                ("skills.sensory_bridges.scripts.audio_to_agent", "audio_to_agent.py"),
            ),
        )
        result = extract_video(request["artifact_path"], gate=gate, **kwargs)
        if cache is not None:
            cache.put(request["artifact_path"], modality, result)
        return result

    raise ValueError(f"No bridge implemented for modality '{modality}'")

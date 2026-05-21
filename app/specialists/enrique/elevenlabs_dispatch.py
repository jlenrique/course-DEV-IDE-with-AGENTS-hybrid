"""Importlib dispatch seam for Enrique ElevenLabs operations."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
OPERATIONS_PATH = REPO_ROOT / "skills" / "elevenlabs-audio" / "scripts" / "elevenlabs_operations.py"

ALLOWED_ENRIQUE_MODES: frozenset[str] = frozenset(
    {
        "voice-preview",
        "narration",
        "sfx",
        "music",
    }
)


class ElevenlabsDispatchError(RuntimeError):  # noqa: N818
    """Raised when ElevenLabs dispatch cannot execute the requested mode."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _ensure_module_stub(name: str) -> None:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def _ensure_package_stubs() -> None:
    _ensure_module_stub("skills")
    _ensure_module_stub("skills.elevenlabs_audio")
    _ensure_module_stub("skills.elevenlabs_audio.scripts")


def _load_operations_module() -> Any:
    _ensure_package_stubs()
    module_name = "skills.elevenlabs_audio.scripts.elevenlabs_operations"
    spec = importlib.util.spec_from_file_location(module_name, OPERATIONS_PATH)
    if spec is None or spec.loader is None:
        raise ElevenlabsDispatchError(
            f"unable to load elevenlabs operations at {OPERATIONS_PATH}",
            tag="enrique_audio.parsed.missing-key",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _coerce_api_error_tag(exc: Exception) -> str:
    text = str(exc).lower()
    if "api" in text or "http" in text or "401" in text or "403" in text:
        return "enrique_audio.parsed.api-error"
    return "enrique_audio.parsed.dispatch-failed"


def dispatch_to_elevenlabs(
    *,
    mode: str,
    operation_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch an Enrique mode decision to the ElevenLabs operations module."""
    normalized_mode = str(mode).strip()
    if normalized_mode not in ALLOWED_ENRIQUE_MODES:
        raise ElevenlabsDispatchError(
            f"unsupported enrique mode: {normalized_mode!r}",
            tag="enrique_audio.parsed.missing-key",
        )

    payload = dict(operation_payload or {})
    module = _load_operations_module()

    try:
        if normalized_mode == "voice-preview":
            result = module.preview_voice_options(**payload)
        elif normalized_mode == "narration":
            text = payload.pop("text", "")
            if not str(text).strip():
                raise ElevenlabsDispatchError(
                    "narration mode requires non-empty text",
                    tag="enrique_audio.parsed.missing-key",
                )
            result = module.generate_narration(text=str(text), **payload)
        elif normalized_mode == "sfx":
            text = payload.pop("text", "")
            if not str(text).strip():
                raise ElevenlabsDispatchError(
                    "sfx mode requires non-empty text",
                    tag="enrique_audio.parsed.missing-key",
                )
            result = module.generate_sound_effect(text=str(text), **payload)
        else:
            result = module.generate_music(**payload)
    except ElevenlabsDispatchError:
        raise
    except Exception as exc:
        raise ElevenlabsDispatchError(
            "elevenlabs dispatch failed",
            tag=_coerce_api_error_tag(exc),
        ) from exc

    if not isinstance(result, dict):
        raise ElevenlabsDispatchError(
            "elevenlabs dispatch result must be a mapping",
            tag="enrique_audio.parsed.wrong-type",
        )
    return {
        "mode": normalized_mode,
        "receipt": result,
    }


__all__ = [
    "ALLOWED_ENRIQUE_MODES",
    "ElevenlabsDispatchError",
    "dispatch_to_elevenlabs",
]

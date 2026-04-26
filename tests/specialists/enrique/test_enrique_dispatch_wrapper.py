from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from app.specialists.enrique.elevenlabs_dispatch import (
    ALLOWED_ENRIQUE_MODES,
    ElevenlabsDispatchError,
    dispatch_to_elevenlabs,
)


def test_enrique_wrapper_uses_importlib_loader_pattern() -> None:
    source = Path("app/specialists/enrique/elevenlabs_dispatch.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "importlib.util" in imports


def test_enrique_modes_contract() -> None:
    assert {"voice-preview", "narration", "sfx", "music"} == ALLOWED_ENRIQUE_MODES


def test_enrique_wrapper_rejects_unknown_mode() -> None:
    with pytest.raises(ElevenlabsDispatchError) as exc_info:
        dispatch_to_elevenlabs(mode="unknown", operation_payload={})
    assert exc_info.value.tag == "enrique_audio.parsed.missing-key"


def test_enrique_wrapper_dispatches_to_preview(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Ops:
        @staticmethod
        def preview_voice_options(**_: Any) -> dict[str, Any]:
            return {"status": "success", "candidate_voices": []}

    monkeypatch.setattr(
        "app.specialists.enrique.elevenlabs_dispatch._load_operations_module",
        lambda: _Ops(),
    )
    out = dispatch_to_elevenlabs(mode="voice-preview", operation_payload={})
    assert out["mode"] == "voice-preview"
    assert out["receipt"]["status"] == "success"


def test_enrique_wrapper_marks_api_error_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Ops:
        @staticmethod
        def generate_music(**_: Any) -> dict[str, Any]:
            raise RuntimeError("API 401 unauthorized")

    monkeypatch.setattr(
        "app.specialists.enrique.elevenlabs_dispatch._load_operations_module",
        lambda: _Ops(),
    )
    with pytest.raises(ElevenlabsDispatchError) as exc_info:
        dispatch_to_elevenlabs(mode="music", operation_payload={})
    assert exc_info.value.tag == "enrique_audio.parsed.api-error"

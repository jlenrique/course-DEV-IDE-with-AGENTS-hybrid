"""Tests for bridge_utils shared utilities."""

import json
import threading
import types
from unittest.mock import patch

import pytest

import skills.sensory_bridges.scripts.bridge_utils as bridge_utils_module
from skills.sensory_bridges.scripts.bridge_utils import (
    SCHEMA_VERSION,
    VALID_MODALITIES,
    _resolve_bridge_callable,
    build_request,
    build_response,
    perceive,
    validate_response,
)
from skills.sensory_bridges.scripts.perception_cache import PerceptionCache


class TestBuildRequest:
    def test_valid_request(self, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_text("dummy")
        req = build_request(f, "pptx", "G3", "fidelity-assessor")
        assert req["modality"] == "pptx"
        assert req["gate"] == "G3"
        assert req["requesting_agent"] == "fidelity-assessor"

    def test_invalid_modality(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("dummy")
        with pytest.raises(ValueError, match="Invalid modality"):
            build_request(f, "spreadsheet", "G3", "test")

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            build_request("/nonexistent/file.pptx", "pptx", "G3", "test")


class TestBuildResponse:
    def test_valid_response(self):
        resp = build_response(
            modality="pptx",
            artifact_path="/test.pptx",
            confidence="HIGH",
            confidence_rationale="All good",
            slides=[],
            total_slides=0,
        )
        assert resp["schema_version"] == SCHEMA_VERSION
        assert resp["confidence"] == "HIGH"
        assert resp["modality"] == "pptx"
        assert "perception_timestamp" in resp

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="Invalid confidence"):
            build_response("pptx", "/test.pptx", "MAYBE", "unsure")


class TestValidateResponse:
    def test_valid_pptx_response(self):
        resp = build_response(
            modality="pptx",
            artifact_path="/test.pptx",
            confidence="HIGH",
            confidence_rationale="OK",
            slides=[{"slide_number": 1, "text_frames": ["Hello"]}],
            total_slides=1,
        )
        errors = validate_response(resp)
        assert errors == []

    def test_valid_audio_response(self):
        resp = build_response(
            modality="audio",
            artifact_path="/test.mp3",
            confidence="HIGH",
            confidence_rationale="OK",
            transcript_text="Hello world",
            timestamped_words=[],
            total_duration_ms=5000,
            wpm=120.0,
        )
        errors = validate_response(resp)
        assert errors == []

    def test_missing_modality_fields(self):
        resp = {
            "schema_version": "1.0",
            "modality": "pptx",
            "artifact_path": "/test.pptx",
            "confidence": "HIGH",
            "confidence_rationale": "OK",
            "perception_timestamp": "2026-03-28T00:00:00Z",
        }
        errors = validate_response(resp)
        assert any("slides" in e for e in errors)
        assert any("total_slides" in e for e in errors)

    def test_missing_common_fields(self):
        resp = {"modality": "pptx"}
        errors = validate_response(resp)
        assert len(errors) >= 4  # missing schema_version, artifact_path, confidence, etc.

    def test_all_modalities_have_required_fields(self):
        for modality in VALID_MODALITIES:
            resp = {"modality": modality}
            errors = validate_response(resp)
            modality_errors = [e for e in errors if f"{modality}-specific" in e]
            assert len(modality_errors) > 0, f"No modality-specific validation for {modality}"


class TestPerceptionCache:
    @patch("skills.sensory_bridges.scripts.png_to_agent.analyze_image")
    def test_perceive_uses_run_cache(self, mock_analyze, tmp_path):
        artifact = tmp_path / "test.png"
        artifact.write_bytes(b"fake-png-bytes")

        mock_analyze.return_value = {
            "schema_version": SCHEMA_VERSION,
            "modality": "image",
            "artifact_path": str(artifact),
            "confidence": "HIGH",
            "confidence_rationale": "synthetic",
            "perception_timestamp": "2026-01-01T00:00:00Z",
            "extracted_text": "",
            "layout_description": "test",
        }

        first = perceive(
            artifact_path=artifact,
            modality="image",
            gate="G2",
            requesting_agent="tester",
            run_id="CACHE-RUN-1",
            use_cache=True,
        )
        second = perceive(
            artifact_path=artifact,
            modality="image",
            gate="G2",
            requesting_agent="tester",
            run_id="CACHE-RUN-1",
            use_cache=True,
        )

        assert first["modality"] == "image"
        assert second["modality"] == "image"
        assert mock_analyze.call_count == 1

    def test_cache_concurrent_puts_keep_all_entries(self, tmp_path):
        cache = PerceptionCache("CACHE-CONCURRENT", runtime_dir=tmp_path)

        def worker(idx: int) -> None:
            artifact = tmp_path / f"asset-{idx}.png"
            cache.put(
                artifact_path=artifact,
                modality="image",
                result={"id": idx, "modality": "image"},
            )

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        raw = json.loads(cache.cache_path.read_text(encoding="utf-8"))
        assert len(raw.get("entries", {})) == 20


class TestDynamicBridgeLoading:
    def test_resolve_bridge_callable_falls_back_to_local_loader(self, monkeypatch):
        loaded: list[str] = []

        def fake_import_module(name):
            if name == "skills.sensory_bridges.scripts.video_to_agent":
                raise ModuleNotFoundError("simulated direct-script import failure")
            raise AssertionError(f"unexpected import attempt: {name}")

        def fake_load_module(name, file_path):
            loaded.append(name)
            if name == "skills.sensory_bridges.scripts.audio_to_agent":
                return types.SimpleNamespace(transcribe_audio=lambda *args, **kwargs: {})
            if name == "skills.sensory_bridges.scripts.video_to_agent":
                return types.SimpleNamespace(extract_video=lambda *args, **kwargs: {"status": "ok"})
            raise AssertionError(f"unexpected loader target: {name}")

        monkeypatch.setattr(bridge_utils_module.importlib, "import_module", fake_import_module)
        monkeypatch.setattr(bridge_utils_module, "_load_module_from_path", fake_load_module)

        func = _resolve_bridge_callable(
            "skills.sensory_bridges.scripts.video_to_agent",
            "video_to_agent.py",
            "extract_video",
            preload=(
                ("skills.sensory_bridges.scripts.audio_to_agent", "audio_to_agent.py"),
            ),
        )

        assert func() == {"status": "ok"}
        assert loaded == [
            "skills.sensory_bridges.scripts.audio_to_agent",
            "skills.sensory_bridges.scripts.video_to_agent",
        ]

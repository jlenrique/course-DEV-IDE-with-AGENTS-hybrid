from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from scripts.api_clients.base_client import APIError

MODULE_PATH = Path(__file__).resolve().parents[1] / "kling_validation_runner.py"
SPEC = importlib.util.spec_from_file_location("kling_validation_runner", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _case_file(tmp_path: Path, cases: list[dict[str, object]]) -> Path:
    path = tmp_path / "validation-cases.yaml"
    path.write_text(yaml.safe_dump({"cases": cases}, sort_keys=False), encoding="utf-8")
    return path


def test_find_cases_returns_requested_case_ids(tmp_path: Path) -> None:
    case_file = _case_file(
        tmp_path,
        [
            {"case_id": "T1", "operation": "text2video"},
            {"case_id": "I1", "operation": "image2video"},
        ],
    )

    cases = MODULE.find_cases(["I1"], case_file=case_file)

    assert len(cases) == 1
    assert cases[0]["case_id"] == "I1"


def test_execute_text_case_silent_omits_native_audio(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run_text_to_video(prompt: str, **kwargs: object) -> dict[str, object]:
        captured["prompt"] = prompt
        captured.update(kwargs)
        output_path = Path(kwargs["output_dir"]) / str(kwargs["filename"])
        output_path.write_bytes(b"mp4-bytes")
        return {
            "task_id": "task-123",
            "video_url": "https://cdn.example.com/video.mp4",
            "video_duration": "5.0",
            "output_path": str(output_path),
            "generation_choices": {"mode": "std"},
            "task_data": {"data": {"task_status": "succeed"}},
        }

    monkeypatch.setattr(MODULE, "run_text_to_video", fake_run_text_to_video)

    receipt = MODULE.execute_validation_case(
        {
            "case_id": "T1",
            "operation": "text2video",
            "model_name": "kling-v2-6",
            "mode": "std",
            "duration": "5",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "silent",
            "prompt": "Hospital corridor.",
        },
        output_dir=tmp_path,
    )

    assert receipt["status"] == "success"
    assert receipt["request"]["api_audio_field"] == "omitted"
    assert receipt["policy"]["lane"] == "validation-only"
    assert receipt["policy"]["production_safe"] is False
    assert captured["sound"] is None


def test_execute_text_case_native_audio_sets_sound_true(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run_text_to_video(prompt: str, **kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        output_path = Path(kwargs["output_dir"]) / str(kwargs["filename"])
        output_path.write_bytes(b"mp4-bytes")
        return {
            "task_id": "task-456",
            "video_url": "https://cdn.example.com/audio.mp4",
            "video_duration": "5.0",
            "output_path": str(output_path),
            "generation_choices": {"mode": "pro"},
            "task_data": {"data": {"task_status": "succeed"}},
        }

    monkeypatch.setattr(MODULE, "run_text_to_video", fake_run_text_to_video)

    receipt = MODULE.execute_validation_case(
        {
            "case_id": "T2",
            "operation": "text2video",
            "model_name": "kling-v2-6",
            "mode": "pro",
            "duration": "5",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "native",
            "prompt": "Ambient clinical audio.",
        },
        output_dir=tmp_path,
    )

    assert receipt["status"] == "success"
    assert receipt["request"]["api_audio_field"] == "sound=true"
    assert captured["sound"] is True


def test_native_sfx_alias_maps_to_sound_true(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run_text_to_video(prompt: str, **kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        output_path = Path(kwargs["output_dir"]) / str(kwargs["filename"])
        output_path.write_bytes(b"mp4-bytes")
        return {
            "task_id": "task-sfx",
            "video_url": "https://cdn.example.com/sfx.mp4",
            "video_duration": "5.0",
            "output_path": str(output_path),
            "generation_choices": {"mode": "pro"},
            "task_data": {"data": {"task_status": "succeed"}},
        }

    monkeypatch.setattr(MODULE, "run_text_to_video", fake_run_text_to_video)

    receipt = MODULE.execute_validation_case(
        {
            "case_id": "T2b",
            "operation": "text2video",
            "model_name": "kling-v2-6",
            "mode": "pro",
            "duration": "5",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "native-sfx",
            "prompt": "ambient sfx probe",
        },
        output_dir=tmp_path,
    )

    assert receipt["status"] == "success"
    assert receipt["request"]["api_audio_field"] == "sound=true"
    assert captured["sound"] is True


def test_build_client_supports_public_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeCurrent:
        pass

    class FakePublic:
        pass

    monkeypatch.setattr(MODULE, "KlingClient", FakeCurrent)
    monkeypatch.setattr(MODULE, "KlingPublicClient", FakePublic)

    assert isinstance(MODULE._build_client("current_repo_client"), FakeCurrent)
    assert isinstance(MODULE._build_client("newer_public_surface"), FakePublic)


def test_execute_case_uses_public_surface_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakePublicClient:
        pass

    def fake_run_text_to_video(prompt: str, **kwargs: object) -> dict[str, object]:
        captured["client"] = kwargs["client"]
        output_path = Path(kwargs["output_dir"]) / str(kwargs["filename"])
        output_path.write_bytes(b"mp4-bytes")
        return {
            "task_id": "task-public",
            "video_url": "https://cdn.example.com/public.mp4",
            "video_duration": "10.0",
            "output_path": str(output_path),
            "generation_choices": {"mode": "pro"},
            "task_data": {"data": {"task_status": "succeed"}},
        }

    monkeypatch.setattr(MODULE, "KlingPublicClient", FakePublicClient)
    monkeypatch.setattr(MODULE, "run_text_to_video", fake_run_text_to_video)

    receipt = MODULE.execute_validation_case(
        {
            "case_id": "V3-public",
            "api_surface": "newer_public_surface",
            "operation": "text2video",
            "model_name": "kling-v3.0",
            "mode": "pro",
            "duration": "10",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "silent",
            "prompt": "public probe",
        },
        output_dir=tmp_path,
        client=None,
    )

    assert receipt["status"] == "success"
    assert receipt["request"]["api_surface"] == "newer_public_surface"
    assert receipt["policy"]["promotion_status"] == "non-promoting"
    assert isinstance(captured["client"], FakePublicClient)


def test_execute_image_case_requires_image_url(tmp_path: Path) -> None:
    receipt = MODULE.execute_validation_case(
        {
            "case_id": "I1",
            "operation": "image2video",
            "model_name": "kling-v2-6",
            "mode": "std",
            "duration": "5",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "silent",
            "prompt": "Preserve the slide.",
        },
        output_dir=tmp_path,
    )

    assert receipt["status"] == "error"
    assert "requires image_url" in receipt["error"]


def test_run_validation_cases_writes_summary_and_receipts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    case_file = _case_file(
        tmp_path,
        [
            {
                "case_id": "T1",
                "operation": "text2video",
                "model_name": "kling-v2-6",
                "mode": "std",
                "duration": "5",
                "aspect_ratio": "16:9",
                "requested_audio_mode": "silent",
                "prompt": "Hospital corridor.",
            }
        ],
    )

    def fake_execute(case: dict[str, object], **_: object) -> dict[str, object]:
        return {
            "case_id": case["case_id"],
            "status": "success",
            "task_id": "task-123",
            "output_path": str(tmp_path / "result.mp4"),
        }

    monkeypatch.setattr(MODULE, "execute_validation_case", fake_execute)

    summary = MODULE.run_validation_cases(
        ["T1"],
        output_root=tmp_path / "reports",
        run_label="run-1",
        case_file=case_file,
    )

    assert summary["success_count"] == 1
    assert summary["error_count"] == 0
    assert (tmp_path / "reports" / "run-1" / "summary.json").exists()
    receipt_path = tmp_path / "reports" / "run-1" / "receipts" / "t1.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "success"


def test_execute_case_captures_structured_api_error_details(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run_text_to_video(prompt: str, **kwargs: object) -> dict[str, object]:
        raise APIError("HTTP 400: Bad Request", status_code=400, response_body={"code": 1201})

    monkeypatch.setattr(MODULE, "run_text_to_video", fake_run_text_to_video)

    receipt = MODULE.execute_validation_case(
        {
            "case_id": "T3",
            "operation": "text2video",
            "model_name": "kling-v2-6",
            "mode": "std",
            "duration": "5",
            "aspect_ratio": "16:9",
            "requested_audio_mode": "silent",
            "prompt": "probe",
        },
        output_dir=tmp_path,
    )

    assert receipt["status"] == "error"
    assert receipt["status_code"] == 400
    assert receipt["response_body"] == {"code": 1201}

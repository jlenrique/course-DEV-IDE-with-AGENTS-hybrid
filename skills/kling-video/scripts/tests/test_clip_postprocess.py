"""Tests for clip_postprocess.py."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "clip_postprocess.py"
SPEC = importlib.util.spec_from_file_location("clip_postprocess", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_build_slow_tail_filter_for_8s_delivery() -> None:
    result = MODULE.build_slow_tail_filter(
        normal_seconds=5.0,
        slow_tail_output_seconds=3.0,
        tail_source_seconds=1.5,
    )

    assert "trim=start=0:end=5.000" in result
    assert "trim=start=3.500:end=5.000" in result
    assert "setpts=2.000000*(PTS-STARTPTS)" in result
    assert "concat=n=2:v=1:a=0[outv]" in result


def test_build_slow_tail_filter_rejects_invalid_tail_window() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        MODULE.build_slow_tail_filter(
            normal_seconds=2.0,
            slow_tail_output_seconds=3.0,
            tail_source_seconds=2.5,
        )


def test_build_slow_tail_command_includes_filter_and_output() -> None:
    command = MODULE.build_slow_tail_command(
        ffmpeg_binary="ffmpeg",
        input_path="input.mp4",
        output_path="output.mp4",
        normal_seconds=5.0,
        slow_tail_output_seconds=3.0,
        tail_source_seconds=1.5,
    )

    assert command[0] == "ffmpeg"
    assert "input.mp4" in command
    assert "output.mp4" in command
    assert "-filter_complex" in command


def test_derive_slow_tail_clip_runs_ffmpeg_and_returns_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"mp4")
    output = tmp_path / "derived.mp4"

    seen: dict[str, object] = {}

    def _fake_run(command: list[str], check: bool, capture_output: bool, text: bool) -> subprocess.CompletedProcess[str]:
        seen["command"] = command
        output.write_bytes(b"derived")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(MODULE, "resolve_ffmpeg_binary", lambda explicit_path=None: "ffmpeg-bin")
    monkeypatch.setattr(MODULE.subprocess, "run", _fake_run)

    result = MODULE.derive_slow_tail_clip(
        input_path=source,
        output_path=output,
        normal_seconds=5.0,
        slow_tail_output_seconds=3.0,
        tail_source_seconds=1.5,
    )

    assert result["target_duration_seconds"] == 8.0
    assert result["ffmpeg_binary"] == "ffmpeg-bin"
    assert output.exists()
    assert seen["command"][0] == "ffmpeg-bin"

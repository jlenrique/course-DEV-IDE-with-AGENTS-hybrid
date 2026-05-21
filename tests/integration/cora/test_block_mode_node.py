from __future__ import annotations

import importlib

import pytest

from app.gates.errors import GateError
from app.models.state.story_state import StoryState

block_mode_module = importlib.import_module("app.cora.block_mode_node")
PreClosureResult = block_mode_module.PreClosureResult


def _state() -> StoryState:
    return StoryState(story_id="4.2")


def test_block_mode_node_allows_clean_diff(monkeypatch: pytest.MonkeyPatch) -> None:
    def _allow(story_id: str, diff_paths: list[str], *, skip_l1: bool = False) -> PreClosureResult:
        assert story_id == "4.2"
        assert diff_paths == ["README.md"]
        assert skip_l1 is False
        return PreClosureResult(
            story_id=story_id,
            classification="warn",
            l1_exit_code=None,
            l1_trace_path=None,
            permit_closure=True,
            operator_message="ok",
        )

    monkeypatch.setattr(block_mode_module, "run_preclosure_check", _allow)

    result = block_mode_module.block_mode_node(_state(), diff_paths=["README.md"])

    assert "updated_at" in result


def test_block_mode_node_raises_gate_error_on_block(monkeypatch: pytest.MonkeyPatch) -> None:
    def _block(story_id: str, diff_paths: list[str], *, skip_l1: bool = False) -> PreClosureResult:
        del diff_paths, skip_l1
        return PreClosureResult(
            story_id=story_id,
            classification="block",
            l1_exit_code=1,
            l1_trace_path="reports/dev-coherence/trace.json",
            permit_closure=False,
            operator_message="closure blocked",
        )

    monkeypatch.setattr(block_mode_module, "run_preclosure_check", _block)

    with pytest.raises(GateError, match="closure blocked"):
        block_mode_module.block_mode_node(
            _state(),
            diff_paths=["state/config/pipeline-manifest.yaml"],
        )


def test_block_mode_node_logs_classification(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def _allow(story_id: str, diff_paths: list[str], *, skip_l1: bool = False) -> PreClosureResult:
        del diff_paths, skip_l1
        return PreClosureResult(
            story_id=story_id,
            classification="warn",
            l1_exit_code=0,
            l1_trace_path=None,
            permit_closure=True,
            operator_message="ok",
        )

    monkeypatch.setattr(block_mode_module, "run_preclosure_check", _allow)

    with caplog.at_level("INFO"):
        block_mode_module.block_mode_node(_state(), diff_paths=["README.md"])

    assert "classification=warn" in caplog.text

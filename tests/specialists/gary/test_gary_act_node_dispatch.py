from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.gary.gamma_dispatch import GammaDispatchError
from app.specialists.gary.graph import ReceiptParseError, _act, _parse_dispatch_receipt

FIXTURE_ROOT = Path("tests/fixtures/specialists/gary")
FIXTURE_RECEIPT = json.loads((FIXTURE_ROOT / "fixture_receipt.json").read_text(encoding="utf-8"))


def _build_state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="a" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
    )


def _envelope_cache_prefix() -> str:
    return json.dumps(
        {
            "directive_path": str(FIXTURE_ROOT / "fixture_directive.md"),
            "export_dir": str(FIXTURE_ROOT / "exports"),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


@pytest.mark.parametrize(
    "receipt,expected_message,expected_tag",
    [
        (
            dict(FIXTURE_RECEIPT, generation_id=None),
            "generation_id",
            "receipt.parsed.missing-key",
        ),
        ("{bad json", "decode failed", "receipt.parsed.malformed"),
        (
            dict(FIXTURE_RECEIPT, gary_slide_output="oops"),
            "must be a list",
            "receipt.parsed.wrong-type",
        ),
        (dict(FIXTURE_RECEIPT, gary_slide_output=[]), "is empty", "receipt.parsed.empty"),
        (
            dict(FIXTURE_RECEIPT, status="export-failure"),
            "export failure",
            "receipt.parsed.export-failure",
        ),
    ],
)
def test_gary_receipt_parser_branches(
    receipt: Any, expected_message: str, expected_tag: str
) -> None:
    with pytest.raises(ReceiptParseError, match=expected_message) as exc_info:
        _parse_dispatch_receipt(receipt)
    assert exc_info.value.tag == expected_tag


def test_gary_receipt_parser_happy_path_has_ok_tag() -> None:
    parsed = _parse_dispatch_receipt(FIXTURE_RECEIPT)
    assert parsed["tag"] == "receipt.parsed.ok"
    assert parsed["generation_id"] == "gen-fixture-001"


def test_gary_act_records_timeout_dispatch_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _timeout_dispatch(**_: Any) -> dict[str, Any]:
        raise GammaDispatchError("timeout", tag="receipt.parsed.timeout")

    monkeypatch.setattr("app.specialists.gary.graph.dispatch_to_gamma", _timeout_dispatch)
    state = _build_state(_envelope_cache_prefix())
    with pytest.raises(GammaDispatchError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "receipt.parsed.timeout"
    assert state.model_resolution_trail[-1].reason == "receipt.parsed.timeout"


def test_gary_act_records_api_error_dispatch_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _api_error_dispatch(**_: Any) -> dict[str, Any]:
        raise GammaDispatchError("api", tag="receipt.parsed.api-error")

    monkeypatch.setattr("app.specialists.gary.graph.dispatch_to_gamma", _api_error_dispatch)
    state = _build_state(_envelope_cache_prefix())
    with pytest.raises(GammaDispatchError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "receipt.parsed.api-error"
    assert state.model_resolution_trail[-1].reason == "receipt.parsed.api-error"


def test_gary_act_dispatches_and_emits_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def _fake_dispatch(*, directive_path: Any = None, export_dir: Any = None) -> dict[str, Any]:
        captured["directive_path"] = directive_path
        captured["export_dir"] = export_dir
        return FIXTURE_RECEIPT

    monkeypatch.setattr("app.specialists.gary.graph.dispatch_to_gamma", _fake_dispatch)
    state = _build_state(_envelope_cache_prefix())
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["generation_id"] == "gen-fixture-001"
    assert output["status"] == "complete"
    assert len(output["gary_slide_output"]) == 2
    assert update["model_resolution_trail"][-1].reason == "receipt.parsed.ok"
    assert captured["directive_path"] == str(FIXTURE_ROOT / "fixture_directive.md")
    assert captured["export_dir"] == str(FIXTURE_ROOT / "exports")

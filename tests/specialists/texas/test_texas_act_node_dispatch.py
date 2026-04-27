from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.texas.graph import (
    BundleDispatchError,
    BundleParseError,
    _act,
    _load_bundle_outputs,
)
from app.specialists.texas.retrieval_dispatch import dispatch_retrieval

FIXTURE_ROOT = Path("tests/fixtures/specialists/texas")
FIXTURE_BUNDLE = FIXTURE_ROOT / "fixture_bundle"


def _build_state(
    *,
    cache_prefix: str | None,
    trail: list[ModelResolutionEntry] | None = None,
) -> RunState:
    if trail is None:
        trail = [
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="b" * 64,
            )
        ]
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=trail,
        cache_state=CacheState(
            cache_prefix=cache_prefix or "",
            entries_count=0,
        ),
    )


def _envelope_cache_prefix() -> str:
    return json.dumps(
        {
            "directive_path": str(FIXTURE_ROOT / "fixture_directive.yaml"),
            "bundle_dir": str(FIXTURE_BUNDLE),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


# ---------------------------------------------------------------------------
# AC-B parse-branch coverage (Murat M1 + M5 — 7 cases, two-sided assertions).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mutation,expected_message,expected_tag",
    [
        ("missing_result", "missing bundle artifact", "bundle.parsed.missing-key"),
        ("missing_report", "missing bundle artifact", "bundle.parsed.missing-key"),
        ("bad_result_yaml", "invalid result.yaml content", "bundle.parsed.malformed"),
        (
            "bad_report_yaml",
            "invalid extraction-report.yaml content",
            "bundle.parsed.malformed",
        ),
        (
            "missing_result_status",
            "result.yaml missing non-empty status",
            "bundle.parsed.empty",
        ),
        ("missing_report_status", "overall_status", "bundle.parsed.empty"),
        ("non_mapping_yaml", "must parse to a mapping", "bundle.parsed.wrong-type"),
    ],
)
def test_texas_bundle_parser_branches(
    tmp_path: Path,
    mutation: str,
    expected_message: str,
    expected_tag: str,
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for name in (
        "extracted.md",
        "metadata.json",
        "manifest.json",
        "extraction-report.yaml",
        "ingestion-evidence.md",
        "result.yaml",
    ):
        source = FIXTURE_BUNDLE / name
        (bundle / name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    if mutation == "missing_result":
        (bundle / "result.yaml").unlink()
    elif mutation == "missing_report":
        (bundle / "extraction-report.yaml").unlink()
    elif mutation == "bad_result_yaml":
        (bundle / "result.yaml").write_text(":\n -", encoding="utf-8")
    elif mutation == "bad_report_yaml":
        (bundle / "extraction-report.yaml").write_text(":\n -", encoding="utf-8")
    elif mutation == "missing_result_status":
        (bundle / "result.yaml").write_text("status: ''\n", encoding="utf-8")
    elif mutation == "missing_report_status":
        (bundle / "extraction-report.yaml").write_text(
            "schema_version: '1.1'\noverall_status: ''\n",
            encoding="utf-8",
        )
    elif mutation == "non_mapping_yaml":
        (bundle / "result.yaml").write_text("- one\n- two\n", encoding="utf-8")

    # Two-sided assertion: parser shape (raises) AND tag attribute matches the
    # expected `bundle.parsed.*` classification (Murat M5 rider).
    with pytest.raises(BundleParseError, match=expected_message) as exc_info:
        _load_bundle_outputs(bundle)
    assert exc_info.value.tag == expected_tag


def test_texas_bundle_parser_happy_path_returns_ok_tag(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for name in (
        "extracted.md",
        "metadata.json",
        "manifest.json",
        "extraction-report.yaml",
        "ingestion-evidence.md",
        "result.yaml",
    ):
        source = FIXTURE_BUNDLE / name
        (bundle / name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    parsed = _load_bundle_outputs(bundle)
    assert parsed["tag"] == "bundle.parsed.ok"
    assert parsed["status"] == "complete"
    assert parsed["overall_status"] == "complete"


# ---------------------------------------------------------------------------
# AC-B dispatch-exit-code coverage (Murat M1 cases #6 / #7 + unknown-exit).
# ---------------------------------------------------------------------------


def test_texas_act_exit_30_raises_dispatch_error_with_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "dispatched",
            "bundle_dir": str(FIXTURE_BUNDLE.resolve()),
            "exit_code": 30,
            "stdout": "",
            "stderr": "fatal",
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="hard error") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.exit-30"


def test_texas_act_exit_unknown_raises_dispatch_error_with_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "dispatched",
            "bundle_dir": str(FIXTURE_BUNDLE.resolve()),
            "exit_code": 42,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="unexpected exit code 42") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.unknown-exit"


def test_texas_act_exit_10_returns_no_results_with_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "dispatched",
            "bundle_dir": str(FIXTURE_BUNDLE.resolve()),
            "exit_code": 10,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["bundle_reference"] is None
    assert output["status"] == "no-results"
    assert output["dispatch_exit_code"] == 10
    trail = update["model_resolution_trail"]
    assert trail[-1].reason == "bundle.parsed.exit-10"


def test_texas_act_records_bundle_parse_tag_on_partial_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When dispatch exits 0 but bundle is incomplete, _act mutates the trail
    in-place with the parse-failure tag and re-raises — proving the
    two-sided contract: exception attribute AND state-side trail entry."""
    partial_bundle = tmp_path / "partial"
    partial_bundle.mkdir()
    # Result is fine but extraction-report is missing — should classify as
    # missing-key.
    (partial_bundle / "result.yaml").write_text(
        "status: complete\n", encoding="utf-8"
    )

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "dispatched",
            "bundle_dir": str(partial_bundle),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.missing-key"
    # State-side: the trail entry was appended in-place before the raise.
    assert state.model_resolution_trail[-1].reason == "bundle.parsed.missing-key"


# ---------------------------------------------------------------------------
# Production-mode fail-loud guards (Blind Hunter HIGH findings).
# ---------------------------------------------------------------------------


def test_texas_act_rejects_malformed_cache_prefix_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed JSON in cache_prefix must fail loudly rather than silently
    falling back to the dev-mode fixture bundle short-circuit."""

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        # Should never be called — guard fires first.
        raise AssertionError("dispatch_retrieval should not be invoked")

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix="{not json")
    with pytest.raises(BundleParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.malformed"


def test_texas_act_rejects_non_dict_cache_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        raise AssertionError("dispatch_retrieval should not be invoked")

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix='["not", "a", "mapping"]')
    with pytest.raises(BundleParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.wrong-type"


def test_texas_act_rejects_dispatch_receipt_missing_bundle_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When dispatch_retrieval returns a receipt without bundle_dir, _act
    must fail loudly — historically Path("") resolved to CWD and cascaded into
    a misleading 'missing artifact' error pointing at the wrong path."""

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {"status": "dispatched", "bundle_dir": None, "exit_code": 0}

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="missing bundle_dir") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.missing-key"


# ---------------------------------------------------------------------------
# Happy-path integration — non-vacuous: asserts envelope payload threaded
# through to dispatch_retrieval.
# ---------------------------------------------------------------------------


def test_texas_act_dispatches_and_emits_bundle_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def _fake_dispatch(
        *,
        directive_path: Any = None,
        bundle_dir: Any = None,
        **_: Any,
    ) -> dict[str, Any]:
        # Non-vacuous: pin that envelope payload threaded through to the
        # dispatch wrapper. Vacuous (**_) acceptance allowed _act to drop the
        # envelope payload silently.
        captured["directive_path"] = directive_path
        captured["bundle_dir"] = bundle_dir
        return {
            "status": "mocked",
            "bundle_dir": str(FIXTURE_BUNDLE.resolve()),
            "exit_code": 0,
            "command": None,
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["bundle_reference"]
    assert output["status"] == "complete"
    assert output["overall_status"] == "complete"
    assert output["dispatch_exit_code"] == 0
    assert output["model_id"] == "gpt-5-nano"
    # Two-sided: trail entry records the success tag.
    trail = update["model_resolution_trail"]
    assert trail[-1].reason == "bundle.parsed.ok"
    # Pin envelope thread-through.
    assert captured["directive_path"] == str(
        FIXTURE_ROOT / "fixture_directive.yaml"
    )
    assert captured["bundle_dir"] == str(FIXTURE_BUNDLE)


# ---------------------------------------------------------------------------
# AC-B Amelia A1 rider — subprocess kwargs FULLY pinned (extended to cover
# text / capture_output / cwd in addition to shell / timeout).
# ---------------------------------------------------------------------------


def test_dispatch_wrapper_pins_subprocess_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class _Completed:
        def __init__(self) -> None:
            self.returncode = 0
            self.stdout = "{}"
            self.stderr = ""

    def _fake_run(*args: Any, **kwargs: Any) -> _Completed:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return _Completed()

    monkeypatch.setattr(
        "app.specialists.texas.retrieval_dispatch.subprocess.run", _fake_run
    )
    receipt = dispatch_retrieval(
        directive_path=FIXTURE_ROOT / "fixture_directive.yaml",
        bundle_dir=FIXTURE_BUNDLE,
    )
    kwargs = captured["kwargs"]
    # Hard-pinned per AC-B Amelia A1 contract: no regression that flips
    # shell=True or drops timeout/text/capture_output/cwd silently.
    assert kwargs["shell"] is False
    assert kwargs["timeout"] == 30
    assert kwargs["text"] is True
    assert kwargs["capture_output"] is True
    assert kwargs["cwd"]
    assert receipt["exit_code"] == 0

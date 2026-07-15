from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

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


def _reseal_manifest(bundle: Path) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["artifacts"]:
        artifact = bundle / row["path"]
        if artifact.is_file():
            raw = artifact.read_bytes()
            row["sha256"] = hashlib.sha256(raw).hexdigest()
            row["size_bytes"] = len(raw)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


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


def _envelope_cache_prefix(bundle_dir: Path = FIXTURE_BUNDLE) -> str:
    return json.dumps(
        {
            "directive_path": str(FIXTURE_ROOT / "fixture_directive.yaml"),
            "bundle_dir": str(bundle_dir),
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

    _reseal_manifest(bundle)

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
    _reseal_manifest(bundle)
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


def test_texas_act_exit_10_parses_bundle_as_complete_with_warnings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Exit 10 = complete_with_warnings (wrangler taxonomy) — bundle is KEPT.

    Trial-3 attempt-3 fix (2026-06-11): the prior exit-10 -> "no-results"
    early-return discarded a valid 903-word bundle. The wrangler taxonomy has
    no "no-results" status; exit 10 bundles parse exactly like exit 0.
    """

    bundle = tmp_path / "fixture-bundle"
    shutil.copytree(FIXTURE_BUNDLE, bundle)
    result = yaml.safe_load((bundle / "result.yaml").read_text(encoding="utf-8"))
    report = yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )
    result["status"] = "complete_with_warnings"
    report["overall_status"] = "complete_with_warnings"
    (bundle / "result.yaml").write_text(
        yaml.safe_dump(result, sort_keys=False), encoding="utf-8"
    )
    (bundle / "extraction-report.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False), encoding="utf-8"
    )
    _reseal_manifest(bundle)

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "dispatched",
            "bundle_dir": str(bundle.resolve()),
            "exit_code": 10,
            "stdout": "",
            "stderr": "",
            "command": None,
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix(bundle))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    # Bundle is parsed and referenced, NOT discarded. Pin the ACTUAL parsed
    # status from the bundle's result.yaml (a negative `!= "no-results"`
    # assertion would pass for any garbage status).
    assert output["bundle_reference"]
    assert output["status"] == "complete_with_warnings"
    assert output["overall_status"] == "complete_with_warnings"
    assert output["dispatch_exit_code"] == 10
    trail = update["model_resolution_trail"]
    assert trail[-1].reason == "bundle.parsed.ok"


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
    state = _build_state(cache_prefix=_envelope_cache_prefix(partial_bundle))
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


@pytest.mark.parametrize("receipt", [None, [], "not-a-receipt"])
def test_texas_act_rejects_non_mapping_dispatch_receipt(
    monkeypatch: pytest.MonkeyPatch, receipt: Any
) -> None:
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", lambda **_: receipt
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="must be a mapping") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.wrong-type"


def test_texas_act_rejects_nonnumeric_dispatch_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(FIXTURE_BUNDLE), "exit_code": "not-a-number"},
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="must be an integer") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.wrong-type"


def test_texas_act_rejects_dispatch_bundle_substitution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    substituted = tmp_path / "substituted"
    shutil.copytree(FIXTURE_BUNDLE, substituted)
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(substituted), "exit_code": 0},
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix())
    with pytest.raises(BundleDispatchError, match="substituted") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.provenance-mismatch"


def test_texas_act_rejects_missing_dispatch_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(FIXTURE_BUNDLE)},
    )
    state = _build_state(cache_prefix="{}")
    with pytest.raises(BundleDispatchError, match="missing exit_code") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.missing-key"


def test_texas_act_rejects_exit_code_status_contradiction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(FIXTURE_BUNDLE), "exit_code": 20},
    )
    state = _build_state(cache_prefix="{}")
    with pytest.raises(BundleDispatchError, match="contradicts") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.provenance-mismatch"


def test_texas_act_translates_non_utf8_authenticated_extraction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    shutil.copytree(FIXTURE_BUNDLE, bundle)
    (bundle / "extracted.md").write_bytes(b"\xff\xfe")
    _reseal_manifest(bundle)
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(bundle), "exit_code": 0},
    )
    state = _build_state(cache_prefix="{}")
    with pytest.raises(BundleParseError, match="not UTF-8") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.malformed"


def test_texas_act_rejects_oversized_numeric_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(FIXTURE_BUNDLE), "exit_code": "9" * 5000},
    )
    state = _build_state(cache_prefix="{}")
    with pytest.raises(BundleDispatchError, match="must be an integer") as exc_info:
        _act(state)
    assert exc_info.value.tag == "bundle.parsed.wrong-type"


def test_exit_status_contradiction_does_not_harden_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    shutil.copytree(FIXTURE_BUNDLE, bundle)
    before = {path.name: path.read_bytes() for path in bundle.iterdir()}
    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval",
        lambda **_: {"bundle_dir": str(bundle), "exit_code": 20},
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix(bundle))
    with pytest.raises(BundleDispatchError, match="contradicts"):
        _act(state)
    after = {name: (bundle / name).read_bytes() for name in before}
    assert after == before


# ---------------------------------------------------------------------------
# Happy-path integration — non-vacuous: asserts envelope payload threaded
# through to dispatch_retrieval.
# ---------------------------------------------------------------------------


def test_texas_act_dispatches_and_emits_bundle_reference(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, Any] = {}
    bundle = tmp_path / "fixture-bundle"
    shutil.copytree(FIXTURE_BUNDLE, bundle)

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
            "bundle_dir": str(bundle.resolve()),
            "exit_code": 0,
            "command": None,
        }

    monkeypatch.setattr(
        "app.specialists.texas.graph.dispatch_retrieval", _fake_dispatch
    )
    state = _build_state(cache_prefix=_envelope_cache_prefix(bundle))
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
    assert captured["bundle_dir"] == str(bundle)


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


# ---------------------------------------------------------------------------
# Trial-3 attempt-3 crash fix (2026-06-11) — subprocess cwd MUST be the
# directive's corpus_dir so corpus-relative local_file locators resolve.
# Mirrors the Story 34-1 ratchet's invocation contract (cwd=corpus_dir);
# the prior cwd=REPO_ROOT caused File-not-found on all 11 sources →
# empty bundle → RetrievalScopeError at Texas hardening.
# ---------------------------------------------------------------------------


def _capture_subprocess_run(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
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
    return captured


def test_dispatch_cwd_is_directive_corpus_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """cwd resolves to the directive's corpus_dir when present + existing."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        f"run_id: 00000000-0000-4000-8000-000000000000\n"
        f"corpus_dir: {corpus.as_posix()}\n"
        f"sources: []\n",
        encoding="utf-8",
    )
    captured = _capture_subprocess_run(monkeypatch)
    dispatch_retrieval(directive_path=directive, bundle_dir=tmp_path / "bundle")
    assert captured["kwargs"]["cwd"] == str(corpus)


def test_dispatch_cwd_falls_back_to_repo_root_when_corpus_dir_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Directives with NO corpus_dir keep the legacy REPO_ROOT fallback."""
    from app.specialists.texas.retrieval_dispatch import REPO_ROOT

    no_corpus_field = tmp_path / "no-corpus-field.yaml"
    no_corpus_field.write_text("run_id: x\nsources: []\n", encoding="utf-8")
    captured = _capture_subprocess_run(monkeypatch)
    dispatch_retrieval(directive_path=no_corpus_field, bundle_dir=tmp_path / "bundle")
    assert captured["kwargs"]["cwd"] == str(REPO_ROOT)


def test_dispatch_invalid_corpus_dir_fails_loud(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A present-but-nonexistent corpus_dir raises instead of silently
    reverting to REPO_ROOT (the attempt-3 wrong-cwd crash signature)."""
    from app.specialists.texas._act import BundleDispatchError

    nonexistent_corpus = tmp_path / "bad-corpus.yaml"
    nonexistent_corpus.write_text(
        f"corpus_dir: {(tmp_path / 'does-not-exist').as_posix()}\nsources: []\n",
        encoding="utf-8",
    )
    _capture_subprocess_run(monkeypatch)
    with pytest.raises(BundleDispatchError) as excinfo:
        dispatch_retrieval(
            directive_path=nonexistent_corpus, bundle_dir=tmp_path / "bundle"
        )
    assert excinfo.value.tag == "bundle.dispatch.corpus-dir-invalid"
    assert "does-not-exist" in str(excinfo.value)


def test_dispatch_relative_corpus_dir_is_anchored_to_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Relative corpus_dir resolves against REPO_ROOT, not the process cwd."""
    from app.specialists.texas.retrieval_dispatch import REPO_ROOT

    relative_corpus = "tests/fixtures/specialists/texas/fixture_bundle"
    directive = tmp_path / "relative-corpus.yaml"
    directive.write_text(
        f"corpus_dir: {relative_corpus}\nsources: []\n", encoding="utf-8"
    )
    captured = _capture_subprocess_run(monkeypatch)
    monkeypatch.chdir(tmp_path)  # process cwd must NOT influence resolution
    dispatch_retrieval(directive_path=directive, bundle_dir=tmp_path / "bundle")
    assert captured["kwargs"]["cwd"] == str(REPO_ROOT / relative_corpus)


def test_dispatch_timeout_raises_tagged_dispatch_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """subprocess.TimeoutExpired surfaces as a tagged BundleDispatchError."""
    import subprocess as _subprocess

    from app.specialists.texas._act import BundleDispatchError

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        f"corpus_dir: {corpus.as_posix()}\nsources: []\n", encoding="utf-8"
    )

    def _raise_timeout(*args: Any, **kwargs: Any) -> None:
        raise _subprocess.TimeoutExpired(cmd="run_wrangler.py", timeout=30)

    monkeypatch.setattr(
        "app.specialists.texas.retrieval_dispatch.subprocess.run", _raise_timeout
    )
    with pytest.raises(BundleDispatchError) as excinfo:
        dispatch_retrieval(directive_path=directive, bundle_dir=tmp_path / "bundle")
    assert excinfo.value.tag == "bundle.dispatch.timeout"

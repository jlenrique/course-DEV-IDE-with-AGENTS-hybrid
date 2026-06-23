"""Wiring-contract tests for the §02A CLI adapter (Murat M-A1, 2026-05-21 SCP §7).

Closes the gate-blind-spot Trial-3 G0 exposed: the §02A composer module had its
own unit tests (cache, classification, directive-model shape, Trial-2 regression,
UTF-8 write) but no test exercised the trial-CLI's call path through the adapter.
"Tested module, untested wiring" was exactly the defect class.

These tests mock both ``make_chat_model`` and ``compose`` so they are pure unit
tests of the adapter's contract: they prove the wiring threads correctly without
exercising LangChain or the actual LLM.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import yaml

from app.composers.section_02a import cli_adapter
from app.composers.section_02a.composer import write_directive_yaml
from app.composers.section_02a.directive_model import Directive, DirectiveRole, DirectiveSource
from app.marcus.orchestrator.production_runner import (
    _gamma_settings_from_directive,
    _runner_payload_for_specialist,
)


def _entry_stub() -> SimpleNamespace:
    return SimpleNamespace(
        model_dump=lambda mode="json": {
            "level": "registry_default",
            "requested": None,
            "resolved": "gpt-5.4",
            "reason": "test stub",
            "timestamp": "2026-05-22T00:00:00+00:00",
            "cache_prefix_hash": None,
        }
    )


def _stub_directive(corpus_dir: Path) -> SimpleNamespace:
    """Return a Directive-shaped stub that ``write_directive_yaml`` will accept."""

    return SimpleNamespace(
        model_dump=lambda mode="json": {
            "run_id": "stub-run-id",
            "corpus_dir": corpus_dir.resolve().as_posix(),
            "sources": [],
            "composed_at": "2026-05-21T00:00:00+00:00",
        }
    )


def test_adapter_calls_make_chat_model_marcus_when_llm_is_none(tmp_path: Path) -> None:
    """When llm=None, the adapter must resolve via make_chat_model("marcus") exactly once."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    run_id = uuid4()

    chat_stub = MagicMock(name="chat_stub")
    handle = SimpleNamespace(chat=chat_stub, entry=_entry_stub())

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model", return_value=handle
    ) as mock_make:
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(b"stub")
            cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
                run_id=run_id,
            )

    mock_make.assert_called_once_with("marcus")
    assert mock_compose.call_args.kwargs["run_id"] == run_id


def test_adapter_threads_chat_attribute_as_llm_kwarg(tmp_path: Path) -> None:
    """The .chat attribute of the ChatModelHandle must be what's passed as llm= to compose()."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    run_id = uuid4()

    chat_stub = MagicMock(name="chat_stub")
    handle = SimpleNamespace(chat=chat_stub, entry=_entry_stub())

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model", return_value=handle
    ):
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(b"stub")
            cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
                run_id=run_id,
            )

    kwargs = mock_compose.call_args.kwargs
    assert kwargs["llm"] is chat_stub, (
        f"compose() must receive ChatModelHandle.chat as llm kwarg, "
        f"got {type(kwargs.get('llm'))}"
    )
    assert kwargs["run_id"] == run_id


def test_adapter_returns_path_and_sha256_digest_tuple(tmp_path: Path) -> None:
    """Return value must be (directive_path, sha256_hex_digest) per legacy contract."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    written_bytes = b"directive-yaml-payload\n"
    run_id = uuid4()

    chat_stub = MagicMock(name="chat_stub")

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model",
        return_value=SimpleNamespace(chat=chat_stub, entry=_entry_stub()),
    ):
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(written_bytes)
            result = cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
                run_id=run_id,
            )

    assert isinstance(result, tuple) and len(result) == 2
    directive_path, digest = result
    assert directive_path == run_dir / "directive.yaml"
    assert digest == hashlib.sha256(written_bytes).hexdigest()


def test_adapter_accepts_injected_llm_and_skips_make_chat_model(tmp_path: Path) -> None:
    """When llm is passed explicitly, the adapter must NOT call make_chat_model."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    run_id = uuid4()

    injected_llm = MagicMock(name="injected_llm")

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model"
    ) as mock_make:
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(b"stub")
            cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
                run_id=run_id,
                llm=injected_llm,
            )

    mock_make.assert_not_called()
    assert mock_compose.call_args.kwargs["llm"] is injected_llm
    assert mock_compose.call_args.kwargs["run_id"] == run_id
    assert not (run_dir / "model_resolution_trail.json").exists()


def _deterministic_directive(run_id: UUID, corpus_dir: str = "C:/tmp/corpus") -> Directive:
    return Directive(
        run_id=run_id,
        corpus_dir=corpus_dir,
        sources=[
            DirectiveSource(
                ref_id="src-001",
                locator="lesson.md",
                role=DirectiveRole.PRIMARY,
                expected_min_words=500,
                description="Primary lesson source.",
            )
        ],
        composed_at=datetime(2026, 6, 23, 12, 0, tzinfo=UTC),
    )


def test_write_directive_yaml_legacy_no_gamma_settings_bytes_stable(tmp_path: Path) -> None:
    run_id = UUID("11111111-1111-4111-8111-111111111111")
    directive = _deterministic_directive(run_id)
    directive_path = tmp_path / "directive.yaml"

    write_directive_yaml(directive, directive_path)

    expected = (
        "run_id: 11111111-1111-4111-8111-111111111111\n"
        "corpus_dir: C:/tmp/corpus\n"
        "sources:\n"
        "- ref_id: src-001\n"
        "  locator: lesson.md\n"
        "  provider: local_file\n"
        "  role: primary\n"
        "  description: Primary lesson source.\n"
        "  expected_min_words: 500\n"
        "  excluded_reason: null\n"
        "composed_at: '2026-06-23T12:00:00Z'\n"
        "schema_version: 1\n"
    )
    actual = directive_path.read_text(encoding="utf-8")
    assert actual == expected
    assert "gamma_settings" not in actual
    assert hashlib.sha256(directive_path.read_bytes()).hexdigest() == (
        "06b587cc99b654967409b5170c5c532c6c7cb3d16d2ebb6b7e463afe173b5b57"
    )


def test_compose_and_write_injects_gamma_settings_before_digest_and_gary_payload(
    tmp_path: Path,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_id = uuid4()
    gamma_settings = [{"variant_id": "A"}, {"variant_id": "B"}]

    with patch.object(cli_adapter, "compose") as mock_compose:
        mock_compose.return_value = _deterministic_directive(
            run_id,
            corpus_dir.resolve().as_posix(),
        )
        directive_path, digest = cli_adapter.compose_and_write(
            corpus_dir=corpus_dir,
            run_dir=run_dir,
            run_id=run_id,
            llm=MagicMock(name="llm"),
            gamma_settings=gamma_settings,
        )

    payload = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    assert payload["gamma_settings"] == gamma_settings
    assert hashlib.sha256(directive_path.read_bytes()).hexdigest() == digest
    assert _gamma_settings_from_directive(directive_path) == gamma_settings
    gary_payload = _runner_payload_for_specialist(
        specialist_id="gary",
        directive_path=directive_path,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=run_id,
    )
    assert gary_payload is not None
    assert gary_payload["gamma_settings"] == gamma_settings

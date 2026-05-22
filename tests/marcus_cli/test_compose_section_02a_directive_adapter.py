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
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.composers.section_02a import cli_adapter


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

    chat_stub = MagicMock(name="chat_stub")
    handle = SimpleNamespace(chat=chat_stub, entry=MagicMock())

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model", return_value=handle
    ) as mock_make:
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(b"stub")
            cli_adapter.compose_and_write(corpus_dir=corpus_dir, run_dir=run_dir)

    mock_make.assert_called_once_with("marcus")


def test_adapter_threads_chat_attribute_as_llm_kwarg(tmp_path: Path) -> None:
    """The .chat attribute of the ChatModelHandle must be what's passed as llm= to compose()."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    chat_stub = MagicMock(name="chat_stub")
    handle = SimpleNamespace(chat=chat_stub, entry=MagicMock(name="entry_discarded"))

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model", return_value=handle
    ):
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(b"stub")
            cli_adapter.compose_and_write(corpus_dir=corpus_dir, run_dir=run_dir)

    kwargs = mock_compose.call_args.kwargs
    assert kwargs["llm"] is chat_stub, (
        f"compose() must receive ChatModelHandle.chat as llm kwarg, "
        f"got {type(kwargs.get('llm'))}"
    )


def test_adapter_returns_path_and_sha256_digest_tuple(tmp_path: Path) -> None:
    """Return value must be (directive_path, sha256_hex_digest) per legacy contract."""

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    written_bytes = b"directive-yaml-payload\n"

    chat_stub = MagicMock(name="chat_stub")

    with patch.object(cli_adapter, "compose") as mock_compose, patch(
        "app.models.adapter.make_chat_model",
        return_value=SimpleNamespace(chat=chat_stub, entry=MagicMock()),
    ):
        mock_compose.return_value = _stub_directive(corpus_dir)
        with patch.object(cli_adapter, "write_directive_yaml") as mock_write:
            mock_write.side_effect = lambda directive, path: path.write_bytes(written_bytes)
            result = cli_adapter.compose_and_write(
                corpus_dir=corpus_dir,
                run_dir=run_dir,
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
                llm=injected_llm,
            )

    mock_make.assert_not_called()
    assert mock_compose.call_args.kwargs["llm"] is injected_llm

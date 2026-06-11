"""G0 confirm-or-edit prompt harness tests (Story 7a.1, AC-7.1-C, J)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.marcus.cli.trial import (
    DirectiveConfirmationRequiredError,
    DirectiveDeclinedError,
    EditorUnavailableError,
    _confirm_or_edit_directive,
    _resolve_editor,
    start_trial,
)


@pytest.fixture
def composed_directive_path(tmp_path: Path) -> Path:
    target = tmp_path / "directive.yaml"
    target.write_text("run_id: TEST\nsources: []\n", encoding="utf-8")
    return target


@pytest.fixture
def stub_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    return corpus


def _start_args(stub_corpus: Path, runs_root: Path, **overrides: Any) -> dict:
    base = {
        "preset": "production",
        "input_path": stub_corpus,
        "operator_id": "operator_test",
        "trial_id": uuid4(),
        "allow_offline_cost_report": True,
        "runs_root": runs_root,
    }
    base.update(overrides)
    return base


def test_confirm_choice_returns_confirmed(composed_directive_path: Path) -> None:
    """Operator types 'c' → returns 'confirmed' without invoking editor."""
    edit_fn = MagicMock()
    verdict = _confirm_or_edit_directive(
        directive_path=composed_directive_path,
        auto_confirm_directive=False,
        input_fn=lambda _prompt: "c",
        edit_fn=edit_fn,
        isatty_fn=lambda: True,
        print_fn=lambda _msg: None,
    )
    assert verdict == "confirmed"
    edit_fn.assert_not_called()


def test_edit_then_confirm_returns_confirmed(composed_directive_path: Path) -> None:
    """Operator types 'e' then 'c' → editor invoked once, returns 'confirmed'."""
    inputs = iter(["e", "c"])
    edit_fn = MagicMock()
    verdict = _confirm_or_edit_directive(
        directive_path=composed_directive_path,
        auto_confirm_directive=False,
        input_fn=lambda _prompt: next(inputs),
        edit_fn=edit_fn,
        isatty_fn=lambda: True,
        print_fn=lambda _msg: None,
    )
    assert verdict == "confirmed"
    edit_fn.assert_called_once_with(composed_directive_path)


def test_save_only_returns_saved_only(composed_directive_path: Path) -> None:
    """Operator types 's' → returns 'saved-only' (no specialist dispatch)."""
    verdict = _confirm_or_edit_directive(
        directive_path=composed_directive_path,
        auto_confirm_directive=False,
        input_fn=lambda _prompt: "s",
        edit_fn=MagicMock(),
        isatty_fn=lambda: True,
        print_fn=lambda _msg: None,
    )
    assert verdict == "saved-only"


def test_cancel_choice_raises(composed_directive_path: Path) -> None:
    """Operator types 'x' → raises DirectiveDeclinedError with explicit message."""
    with pytest.raises(
        DirectiveDeclinedError, match="directive composition declined"
    ):
        _confirm_or_edit_directive(
            directive_path=composed_directive_path,
            auto_confirm_directive=False,
            input_fn=lambda _prompt: "x",
            edit_fn=MagicMock(),
            isatty_fn=lambda: True,
            print_fn=lambda _msg: None,
        )


def test_invalid_choice_re_prompts_until_valid(
    composed_directive_path: Path,
) -> None:
    """Bogus inputs re-prompt without progressing."""
    inputs = iter(["q", "yes", "", "c"])
    verdict = _confirm_or_edit_directive(
        directive_path=composed_directive_path,
        auto_confirm_directive=False,
        input_fn=lambda _prompt: next(inputs),
        edit_fn=MagicMock(),
        isatty_fn=lambda: True,
        print_fn=lambda _msg: None,
    )
    assert verdict == "confirmed"


def test_non_interactive_without_auto_confirm_raises(
    composed_directive_path: Path,
) -> None:
    """Non-TTY + no --auto-confirm-directive → raise (no silent auto-accept)."""
    with pytest.raises(
        DirectiveConfirmationRequiredError, match="non-interactive stdin"
    ):
        _confirm_or_edit_directive(
            directive_path=composed_directive_path,
            auto_confirm_directive=False,
            input_fn=lambda _prompt: "c",
            edit_fn=MagicMock(),
            isatty_fn=lambda: False,
            print_fn=lambda _msg: None,
        )


def test_non_interactive_with_auto_confirm_returns_confirmed(
    composed_directive_path: Path,
) -> None:
    """Non-TTY + --auto-confirm-directive → return 'confirmed' silently."""
    verdict = _confirm_or_edit_directive(
        directive_path=composed_directive_path,
        auto_confirm_directive=True,
        input_fn=lambda _prompt: "should-not-call",
        edit_fn=MagicMock(),
        isatty_fn=lambda: False,
        print_fn=lambda _msg: None,
    )
    assert verdict == "confirmed"


def test_resolve_editor_prefers_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EDITOR", "emacs")
    assert _resolve_editor() == "emacs"


def test_resolve_editor_windows_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("sys.platform", "win32")
    assert _resolve_editor() == "notepad"


def test_resolve_editor_posix_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("sys.platform", "linux")
    # vi is not on PATH on a Windows dev box; the test pins fallback
    # RESOLUTION, not PATH presence (same idiom as the sibling P6 tests).
    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/vi")
    assert _resolve_editor() == "vi"


def test_editor_unavailable_raises_when_subprocess_missing(
    monkeypatch: pytest.MonkeyPatch,
    composed_directive_path: Path,
) -> None:
    """If subprocess.call raises OSError, raise EditorUnavailableError (P6)."""
    from app.marcus.cli import trial as trial_module

    monkeypatch.setenv("EDITOR", "vi")  # bypass _resolve_editor's shutil.which check

    def _boom(_args: list[str]) -> int:
        raise FileNotFoundError("vi: command not found")

    monkeypatch.setattr(trial_module.subprocess, "call", _boom)
    with pytest.raises(EditorUnavailableError, match="could not be launched"):
        trial_module._edit_directive_in_editor(composed_directive_path)


def test_resolve_editor_strips_whitespace_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6: whitespace-only $EDITOR is treated as empty (falls through to fallback)."""
    from app.marcus.cli.trial import _resolve_editor

    monkeypatch.setenv("EDITOR", "   ")
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/vi")
    assert _resolve_editor() == "vi"


def test_resolve_editor_raises_when_fallback_missing_from_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6: platform fallback that's absent from PATH raises EditorUnavailableError."""
    from app.marcus.cli.trial import _resolve_editor

    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("shutil.which", lambda _name: None)
    with pytest.raises(EditorUnavailableError, match="not found on PATH"):
        _resolve_editor()


def test_editor_non_zero_exit_raises(
    monkeypatch: pytest.MonkeyPatch,
    composed_directive_path: Path,
) -> None:
    """P6: editor exiting with non-zero code raises EditorUnavailableError."""
    from app.marcus.cli import trial as trial_module

    monkeypatch.setenv("EDITOR", "vi")
    monkeypatch.setattr(trial_module.subprocess, "call", lambda _args: 1)
    with pytest.raises(EditorUnavailableError, match="exited with non-zero code 1"):
        trial_module._edit_directive_in_editor(composed_directive_path)


def test_edit_directive_succeeds_on_zero_exit(
    monkeypatch: pytest.MonkeyPatch,
    composed_directive_path: Path,
) -> None:
    """P6: editor exiting 0 returns cleanly (no exception)."""
    from app.marcus.cli import trial as trial_module

    monkeypatch.setenv("EDITOR", "vi")
    monkeypatch.setattr(trial_module.subprocess, "call", lambda _args: 0)
    trial_module._edit_directive_in_editor(composed_directive_path)  # no raise


def test_cancel_path_writes_cancellation_record_and_exits_2(
    stub_corpus: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC-7.1-J: cancel writes trial-cancelled-at-g0.json + status=cancelled-at-g0."""
    runs_root = tmp_path / "runs"
    monkeypatch.setattr("os.environ", {"OPENAI_API_KEY": "sk-fake",
                                        "LANGSMITH_API_KEY": "lsv2",
                                        "LANGSMITH_PROJECT": "test"})

    # The §02A composer is LLM-driven (post-7c §02A); a real call with the
    # sk-fake sentinel 401s. This test pins the G0 CANCELLATION contract,
    # not composition — stub the composer at the trial-CLI seam.
    def _stub_compose_and_write(
        corpus_dir: Path, run_dir: Path, *, run_id: Any, llm: Any = None
    ) -> tuple[Path, str]:
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "directive.yaml"
        path.write_text(
            f"run_id: {run_id}\ncorpus_dir: {corpus_dir.as_posix()}\nsources: []\n",
            encoding="utf-8",
        )
        return path, "stub-digest"

    monkeypatch.setattr(
        "app.marcus.cli.trial.compose_and_write", _stub_compose_and_write
    )

    def _confirm(*, directive_path: Path, auto_confirm_directive: bool) -> str:
        raise DirectiveDeclinedError(
            "directive composition declined; trial halted at G0 with no "
            "specialist dispatch"
        )

    payload = start_trial(
        **_start_args(stub_corpus, runs_root, confirm_fn=_confirm)
    )
    assert payload["status"] == "cancelled-at-g0"
    record_path = Path(payload["cancellation_record"])
    assert record_path.exists()
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["reason"] == "directive_composition_declined"

"""Fixture tests for ``scripts/utilities/generate_project_context.py``.

Hermetic: builds a synthetic repo root in a tmp dir; git identity injected via
env vars. Exercises steady-state regeneration, bootstrap split, and fail-loud.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "utilities"
    / "generate_project_context.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_project_context", _MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _load_module()


_BASE_DOC = """\
# Project Context: Multi-Agent Course Content Production System

## Purpose

The hand-authored base doc. Every byte below the marker must survive verbatim.

## Key Decisions From Planning

- Decision one.
- Decision two.
"""

_HANDOFF = """\
# Session close 2026-07-17 (NIGHT) — latest

## What is next

Do the next thing.

## Unresolved issues / risks

- A risk.
"""

_SOTA = """\
# STATE OF THE APP

### 11.1 You are here

**(2026-07-17 — CURRENT) The current you-are-here paragraph.**

> **(SUPERSEDED you-are-here — 2026-07-15)** old stuff that must not be lifted.

### 11.2 Next
"""


def _scaffold(root: Path) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "SESSION-HANDOFF.md").write_text(_HANDOFF, encoding="utf-8")
    (root / "docs" / "STATE-OF-THE-APP.md").write_text(_SOTA, encoding="utf-8")


def test_steady_state_preserves_base_byte_for_byte(tmp_path):
    root = tmp_path / "repo"
    _scaffold(root)
    existing = (
        "# Project Context — Current State (GENERATED)\n\nOLD HEADER TO REPLACE\n\n"
        + gen.BASE_DOC_MARKER
        + "\n"
        + _BASE_DOC
    )
    target = root / "docs" / "project-context.md"
    target.write_text(existing, encoding="utf-8")

    rc = gen.main(["--root", str(root)])
    assert rc == 0

    out = target.read_text(encoding="utf-8")
    # Header regenerated (old header gone; current-state card present).
    assert "OLD HEADER TO REPLACE" not in out
    assert "## Current Session State" in out
    # P4d: header is idempotent — no volatile timestamp / branch / HEAD sha;
    # a stable regenerate pointer replaces them.
    assert "GENERATED thin header — regenerate with" in out
    assert "**Generated:**" not in out
    assert "**Branch:**" not in out
    assert "The current you-are-here paragraph." in out
    assert "old stuff that must not be lifted" not in out

    # Marker present exactly once; base doc from the marker on preserved verbatim.
    assert out.count(gen.BASE_DOC_MARKER_PREFIX) == 1
    preserved = out[out.index(gen.BASE_DOC_MARKER_PREFIX):]
    assert preserved == gen.BASE_DOC_MARKER + "\n" + _BASE_DOC
    # No history sibling on a steady-state run.
    assert not (root / "docs" / "project-context.history.md").exists()


def test_header_is_idempotent_across_reruns(tmp_path):
    """P4d: regenerating twice yields byte-identical output (no volatile fields)."""
    root = tmp_path / "repo"
    _scaffold(root)
    target = root / "docs" / "project-context.md"
    target.write_text(gen.BASE_DOC_MARKER + "\n" + _BASE_DOC, encoding="utf-8")

    assert gen.main(["--root", str(root)]) == 0
    first = target.read_text(encoding="utf-8")
    assert gen.main(["--root", str(root)]) == 0
    second = target.read_text(encoding="utf-8")
    assert first == second


def test_writes_lf_line_endings_byte_for_byte(tmp_path):
    """P4c: target is written with newline='' so no LF→CRLF translation occurs."""
    root = tmp_path / "repo"
    _scaffold(root)
    target = root / "docs" / "project-context.md"
    target.write_text(gen.BASE_DOC_MARKER + "\n" + _BASE_DOC, encoding="utf-8")

    assert gen.main(["--root", str(root)]) == 0
    raw = target.read_bytes()
    assert b"\r\n" not in raw  # pure LF preserved even on win32


def test_you_are_here_missing_emits_explicit_note(tmp_path):
    """P4a: absent §11.1 → explicit unavailable note, not a silent empty block."""
    root = tmp_path / "repo"
    _scaffold(root)
    # Overwrite SOTA with a file that has no §11.1 heading.
    (root / "docs" / "STATE-OF-THE-APP.md").write_text(
        "# STATE OF THE APP\n\n## 12 Something else\n\nNo you-are-here here.\n",
        encoding="utf-8",
    )
    target = root / "docs" / "project-context.md"
    target.write_text(gen.BASE_DOC_MARKER + "\n" + _BASE_DOC, encoding="utf-8")

    assert gen.main(["--root", str(root)]) == 0
    out = target.read_text(encoding="utf-8")
    assert "<!-- STATE-OF-THE-APP §11.1 unavailable at generation -->" in out
    assert "## You Are Here" not in out


def test_fail_loud_missing_target_file(tmp_path, capsys):
    """T-failloud (2): docs/project-context.md missing entirely → rc=1."""
    root = tmp_path / "repo"
    _scaffold(root)  # no project-context.md created
    rc = gen.main(["--root", str(root)])
    assert rc == 1
    assert "not found" in capsys.readouterr().err
    assert not (root / "docs" / "project-context.md").exists()


def test_fail_loud_missing_session_handoff(tmp_path, capsys):
    """T-failloud (3): P4a SESSION-HANDOFF missing → rc=1, target untouched."""
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "STATE-OF-THE-APP.md").write_text(_SOTA, encoding="utf-8")
    # NOTE: no SESSION-HANDOFF.md written.
    target = root / "docs" / "project-context.md"
    original = gen.BASE_DOC_MARKER + "\n" + _BASE_DOC
    target.write_text(original, encoding="utf-8")

    rc = gen.main(["--root", str(root)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "SESSION-HANDOFF.md" in err
    assert target.read_text(encoding="utf-8") == original


def test_fail_loud_multiple_base_headings(tmp_path, capsys):
    """P4b: >1 '# Project Context:' heading in bootstrap → rc=1, no overwrite."""
    root = tmp_path / "repo"
    _scaffold(root)
    target = root / "docs" / "project-context.md"
    # An addendum that spuriously restates the base heading, then the real base.
    original = (
        "# Current Context Addendum\n\n"
        "# Project Context: spurious restatement\n\n"
        + _BASE_DOC
    )
    target.write_text(original, encoding="utf-8")

    rc = gen.main(["--root", str(root)])
    assert rc == 1
    assert "Project Context:" in capsys.readouterr().err
    assert target.read_text(encoding="utf-8") == original


def test_bootstrap_run_twice_does_not_duplicate_addenda(tmp_path):
    """T-failloud (4): a second run (now steady-state) leaves history unchanged."""
    root = tmp_path / "repo"
    _scaffold(root)
    addenda = "# Current Context Addendum\n\nRegenerable dup history.\n\n---\n\n"
    target = root / "docs" / "project-context.md"
    target.write_text(addenda + _BASE_DOC, encoding="utf-8")

    assert gen.main(["--root", str(root)]) == 0  # bootstrap
    history = root / "docs" / "project-context.history.md"
    first_history = history.read_text(encoding="utf-8")
    assert first_history.count("Regenerable dup history.") == 1

    assert gen.main(["--root", str(root)]) == 0  # steady-state re-run
    # History sibling untouched (no second archived copy of the addenda).
    assert history.read_text(encoding="utf-8") == first_history
    assert history.read_text(encoding="utf-8").count("Regenerable dup history.") == 1


def test_bootstrap_splits_addenda_and_inserts_marker(tmp_path):
    root = tmp_path / "repo"
    _scaffold(root)
    addenda = (
        "# Current Context Addendum - 2026-07-17\n\nRegenerable dup history.\n\n---\n\n"
    )
    target = root / "docs" / "project-context.md"
    target.write_text(addenda + _BASE_DOC, encoding="utf-8")

    rc = gen.main(["--root", str(root)])
    assert rc == 0

    out = target.read_text(encoding="utf-8")
    # Addendum stack removed from the hot file; marker + base doc verbatim below.
    assert "Regenerable dup history." not in out
    assert gen.BASE_DOC_MARKER in out
    preserved = out[out.index(gen.BASE_DOC_MARKER_PREFIX):]
    assert preserved == gen.BASE_DOC_MARKER + "\n" + _BASE_DOC

    # History sibling created with the addenda, and NOT named project-context.md.
    history = root / "docs" / "project-context.history.md"
    assert history.exists()
    assert "Regenerable dup history." in history.read_text(encoding="utf-8")


def test_fail_loud_no_marker_no_base_heading_does_not_overwrite(tmp_path, capsys):
    root = tmp_path / "repo"
    _scaffold(root)
    target = root / "docs" / "project-context.md"
    original = "# Some unrelated doc\n\nNo marker, no base heading here.\n"
    target.write_text(original, encoding="utf-8")

    rc = gen.main(["--root", str(root)])

    assert rc == 1
    err = capsys.readouterr().err
    assert "generate_project_context" in err
    # Target left untouched (never drop the base doc).
    assert target.read_text(encoding="utf-8") == original


def test_check_flag_does_not_write(tmp_path):
    root = tmp_path / "repo"
    _scaffold(root)
    target = root / "docs" / "project-context.md"
    original = gen.BASE_DOC_MARKER + "\n" + _BASE_DOC
    target.write_text(original, encoding="utf-8")

    rc = gen.main(["--root", str(root), "--check"])
    assert rc == 0
    # Unchanged on --check.
    assert target.read_text(encoding="utf-8") == original

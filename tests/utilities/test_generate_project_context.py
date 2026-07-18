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


@pytest.fixture(autouse=True)
def _inject_git(monkeypatch):
    monkeypatch.setenv(gen._ENV_BRANCH, "trial/test-branch")
    monkeypatch.setenv(gen._ENV_HEAD, "abc1234")


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
    assert "trial/test-branch" in out
    assert "The current you-are-here paragraph." in out
    assert "old stuff that must not be lifted" not in out

    # Marker present exactly once; base doc from the marker on preserved verbatim.
    assert out.count(gen.BASE_DOC_MARKER_PREFIX) == 1
    preserved = out[out.index(gen.BASE_DOC_MARKER_PREFIX):]
    assert preserved == gen.BASE_DOC_MARKER + "\n" + _BASE_DOC
    # No history sibling on a steady-state run.
    assert not (root / "docs" / "project-context.history.md").exists()


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

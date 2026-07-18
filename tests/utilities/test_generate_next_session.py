"""Fixture tests for ``scripts/utilities/generate_next_session.py``.

Hermetic: every test builds a synthetic repo root in a tmp dir and injects git
identity via env vars, so nothing touches the real repo files.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "utilities"
    / "generate_next_session.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("generate_next_session", _MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _load_module()


_HANDOFF_HAPPY = """\
# Session close 2026-07-17 (NIGHT) — latest session

**Final class:** S.

## What was completed

- Did a thing.

## What is next

1. First next action for the fresh session.
2. Second next action.

## Unresolved issues / risks

- A carried risk that must be watched.

---

# Session close 2026-07-16 EVE — older session

## What is next

Stale content that must NOT be lifted (older section).
"""


_HANDOFF_NO_WHATNEXT = """\
# Session close 2026-07-17 (NIGHT) — latest session

## What was completed

- Did a thing.

## Unresolved issues / risks

- A risk.
"""


_DEFERRED = """\
# Deferred Inventory

| Epic | Focus | Stories | Count | Trigger |
|---|---|---|---|---|
| **Epic 15** | Learning | 15-1 | 1 | trigger |
| **Epic 16** | Autonomy | 16-1 | 1 | trigger |
"""


def _make_root(tmp_path: Path, handoff: str) -> Path:
    root = tmp_path / "repo"
    (root / "_bmad-output" / "planning-artifacts").mkdir(parents=True)
    (root / "SESSION-HANDOFF.md").write_text(handoff, encoding="utf-8")
    (root / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md").write_text(
        _DEFERRED, encoding="utf-8"
    )
    return root


@pytest.fixture(autouse=True)
def _inject_git(monkeypatch):
    monkeypatch.setenv(gen._ENV_BRANCH, "trial/test-branch")
    monkeypatch.setenv(gen._ENV_HEAD, "abc1234")


def test_happy_path_writes_all_required_contract_elements(tmp_path):
    root = _make_root(tmp_path, _HANDOFF_HAPPY)

    rc = gen.main(["--root", str(root)])
    assert rc == 0

    target = root / "next-session-start-here.md"
    assert target.exists()
    out = target.read_text(encoding="utf-8")

    # First line + CLAUDE.md-mandated expected-class line.
    assert out.startswith("# Next Session — Start Here")
    assert "**Expected class for next session:**" in out

    # Title-Case parser-contract headings (progress_map.py CASE-SENSITIVE).
    assert "\n## Immediate Next Action\n" in out
    assert "\n## Key Risks / Unresolved Issues\n" in out
    assert "\n## Branch Metadata\n" in out
    assert "\n## Deferred Inventory Status\n" in out

    # Content lifted from the LATEST handoff section (not the older one).
    assert "First next action for the fresh session." in out
    assert "A carried risk that must be watched." in out
    assert "Stale content that must NOT be lifted" not in out

    # Branch + HEAD + deferred count present.
    assert "trial/test-branch" in out
    assert "abc1234" in out
    assert "2 register rows" in out  # two `| **` rows in the synthetic inventory

    # Footer names the generator + fallback SSOT.
    assert "generate_next_session.py" in out


def test_check_flag_does_not_write(tmp_path):
    root = _make_root(tmp_path, _HANDOFF_HAPPY)
    rc = gen.main(["--root", str(root), "--check"])
    assert rc == 0
    assert not (root / "next-session-start-here.md").exists()


def test_fail_loud_missing_what_is_next_does_not_write(tmp_path, capsys):
    root = _make_root(tmp_path, _HANDOFF_NO_WHATNEXT)
    # Pre-existing authored fallback must survive untouched.
    target = root / "next-session-start-here.md"
    target.write_text("AUTHORED FALLBACK — do not clobber\n", encoding="utf-8")

    rc = gen.main(["--root", str(root)])

    assert rc == 1
    err = capsys.readouterr().err
    assert "generate_next_session" in err
    assert "What is next" in err
    # Target unchanged (fail-loud never overwrites).
    assert target.read_text(encoding="utf-8") == "AUTHORED FALLBACK — do not clobber\n"


def test_fail_loud_missing_handoff_file(tmp_path, capsys):
    root = tmp_path / "repo"
    (root / "_bmad-output" / "planning-artifacts").mkdir(parents=True)

    rc = gen.main(["--root", str(root)])

    assert rc == 1
    assert "SESSION-HANDOFF.md not found" in capsys.readouterr().err
    assert not (root / "next-session-start-here.md").exists()

"""Standalone gh-pages prune CLI — dry-run inertness + --yes push (AC8/G5, RA7f).

The primitive ``prune_retention`` is unit-tested in
``tests/marcus/orchestrator/test_gh_pages_publish.py``; THIS suite pins the shipped CLI:
the safety-critical ``--dry-run`` DEFAULT (bare invocation must NEVER push), that dry-run
leaves the origin ref byte-identical, and that ``--yes`` actually commits + pushes the
prune. The publisher config is monkeypatched to a temp bare origin so no real GitHub is hit.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import scripts.utilities.prune_gh_pages_site as prune_mod

DAY = 86400


def _git(args: list[str], cwd: Path, env: dict | None = None) -> str:
    import os

    full_env = {**os.environ, **env} if env else None
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=full_env
    ).stdout


def _origin_with_old_and_recent(tmp_path: Path) -> Path:
    """Bare origin holding one >retention pack and one recent pack under a managed root."""
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(["init", "--bare", "--initial-branch=main", "."], cwd=bare)
    work = tmp_path / "work"
    work.mkdir()
    _git(["init", "--initial-branch=main", "."], cwd=work)
    _git(["config", "user.name", "t"], cwd=work)
    _git(["config", "user.email", "t@x"], cwd=work)
    now = int(__import__("time").time())
    for name, age in (("oldpack", 30 * DAY), ("recentpack", 2 * DAY)):
        d = work / "assets" / "styleguide-picker" / name
        d.mkdir(parents=True)
        (d / "index.html").write_text(name, encoding="utf-8")
        stamp = f"@{now - age} +0000"
        _git(["add", "--", f"assets/styleguide-picker/{name}"], cwd=work)
        _git(
            ["commit", "-m", name],
            cwd=work,
            env={"GIT_COMMITTER_DATE": stamp, "GIT_AUTHOR_DATE": stamp},
        )
    _git(["remote", "add", "origin", str(bare)], cwd=work)
    _git(["push", "origin", "main"], cwd=work)
    return bare


@pytest.fixture
def _wired(tmp_path: Path, monkeypatch):
    bare = _origin_with_old_and_recent(tmp_path)
    monkeypatch.setattr(
        prune_mod,
        "_load_config",
        lambda: {
            "site_repo_url": str(bare),
            "site_branch": "main",
            "retention_days": 10,
            "managed_roots": ["assets/styleguide-picker"],
            "protected_paths": [],
            "token_env_var": "GITHUB_PAGES_TOKEN",
        },
    )
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    monkeypatch.delenv("STORYBOARD_SITE_REPO_URL", raising=False)
    return bare


def _origin_ref(bare: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "refs/heads/main"],
        cwd=bare,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_prune_default_is_dry_run_and_inert(_wired: Path, capsys) -> None:
    """Bare invocation defaults to dry-run: prints the plan, pushes NOTHING (RA7f)."""
    bare = _wired
    before = _origin_ref(bare)
    rc = prune_mod.main([])  # no args → --dry-run default
    assert rc == 0
    out = capsys.readouterr().out
    assert "oldpack" in out and "DRY-RUN" in out
    assert "delete  assets/styleguide-picker/recentpack" not in out  # recent not pruned
    assert _origin_ref(bare) == before  # origin ref byte-identical — no push


def test_prune_yes_pushes_the_deletion(_wired: Path) -> None:
    """--yes actually prunes + pushes: the old pack is gone from origin, recent survives."""
    bare = _wired
    before = _origin_ref(bare)
    rc = prune_mod.main(["--yes"])
    assert rc == 0
    assert _origin_ref(bare) != before  # a prune commit was pushed
    checkout = bare.parent / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=bare.parent)
    assert not (checkout / "assets/styleguide-picker/oldpack").exists()
    assert (checkout / "assets/styleguide-picker/recentpack").exists()


def test_prune_dry_run_and_yes_are_mutually_exclusive(_wired: Path) -> None:
    with pytest.raises(SystemExit):
        prune_mod.main(["--dry-run", "--yes"])


def test_prune_missing_token_fails_before_clone(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        prune_mod,
        "_load_config",
        lambda: {
            "site_repo_url": "https://github.com/owner/repo",
            "managed_roots": ["assets/styleguide-picker"],
            "token_env_var": "GITHUB_PAGES_TOKEN",
        },
    )
    monkeypatch.delenv("GITHUB_PAGES_TOKEN", raising=False)
    monkeypatch.delenv("STORYBOARD_SITE_REPO_URL", raising=False)
    with pytest.raises(SystemExit, match="(?i)GITHUB_PAGES_TOKEN"):
        prune_mod.main(["--dry-run"])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))

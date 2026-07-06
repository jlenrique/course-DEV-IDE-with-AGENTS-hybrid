"""Offline hygiene tests for gamma literal-visual publish (Task 1b).

Exercises the gh-pages hygiene primitives now woven around
``publish_preintegration_literal_visuals``'s own git transport: retention prune,
size guard (fail-loud → no push), whole-repo commit gate, and the ``verify`` seam.

NO MOCKING of git and NO live network: every test runs against a temp BARE origin,
points ``site_repo_url`` at that local path (exercising the non-github fallback in
``_github_pages_base_url``), and calls with ``verify=False`` (the offline seam — a temp
bare repo has no live HTTP endpoint). Retention dates are made deterministic by pinning
BOTH ``GIT_COMMITTER_DATE`` and ``GIT_AUTHOR_DATE`` to explicit ``@<epoch> +0000`` stamps
(mirrors ``tests/marcus/orchestrator/test_gh_pages_publish.py``).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import gamma_operations  # noqa: E402
from gamma_operations import publish_preintegration_literal_visuals  # noqa: E402

from app.marcus.orchestrator.gh_pages_publish import (  # noqa: E402
    SizeGuardConfig,
    SizeGuardRefusal,
)

DAY = 86400
NOW = 1_800_000_000

# Tiny 1x1 red-pixel PNG (exact bytes — no PIL required).
_DUMMY_PNG_BYTES = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
    0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82,
])


def _git(args: list[str], cwd: Path, env: dict | None = None) -> str:
    full_env = None
    if env is not None:
        import os

        full_env = {**os.environ, **env}
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=full_env
    ).stdout


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git(["init", "--initial-branch=main", "."], cwd=path)
    _git(["config", "user.name", "t"], cwd=path)
    _git(["config", "user.email", "t@x"], cwd=path)


def _commit_pack(repo: Path, rel: str, *, epoch: int, size_bytes: int = 64) -> None:
    """Create + commit a pack dir at ``rel`` with committer date pinned to ``epoch``."""
    pack = repo / rel
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "index.html").write_text(f"<html>{rel}</html>", encoding="utf-8")
    (pack / "blob.bin").write_bytes(b"x" * size_bytes)
    _git(["add", "--", rel], cwd=repo)
    stamp = f"@{epoch} +0000"
    _git(
        ["commit", "-m", f"publish {rel}"],
        cwd=repo,
        env={"GIT_COMMITTER_DATE": stamp, "GIT_AUTHOR_DATE": stamp},
    )
    got = _git(["log", "-1", "--format=%ct", "--", rel], cwd=repo).strip()
    assert got == str(epoch), f"fixture self-check: %ct={got} expected {epoch}"


def _bare_origin(tmp_path: Path) -> Path:
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(["init", "--bare", "--initial-branch=main", "."], cwd=bare)
    return bare


def _seed(tmp_path: Path, bare: Path, seed_fn=None) -> None:
    """Seed the bare origin with a README and any packs created by ``seed_fn(seed_repo)``."""
    seed = tmp_path / "seed"
    _init_repo(seed)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git(["add", "."], cwd=seed)
    _git(["commit", "-m", "seed"], cwd=seed)
    if seed_fn is not None:
        seed_fn(seed)
    _git(["remote", "add", "origin", str(bare)], cwd=seed)
    _git(["push", "origin", "main"], cwd=seed)


def _reclone(tmp_path: Path, bare: Path, name: str = "verify") -> Path:
    checkout = tmp_path / name
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    return checkout


def _freeze_now(monkeypatch) -> None:
    """Pin retention's clock so backdated packs age deterministically."""
    monkeypatch.setattr(gamma_operations.time, "time", lambda: float(NOW))


def _run_publish(tmp_path: Path, bare: Path, monkeypatch, *, module_part: str, cards):
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    _freeze_now(monkeypatch)
    return publish_preintegration_literal_visuals(
        cards,
        module_part,
        site_repo_url=str(bare),
        verify=False,
    )


def _make_png(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_bytes(_DUMMY_PNG_BYTES)
    return p


# ─────────────────────────────────────────────────────────────── retention
def test_current_run_pack_never_deleted_even_if_backdated(tmp_path, monkeypatch) -> None:
    """RA7a: a pack at THIS run's subdir survives even when its commit date is old."""
    bare = _bare_origin(tmp_path)
    module_part = "c1m1/run1"

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, f"assets/gamma/{module_part}", epoch=NOW - 40 * DAY)

    _seed(tmp_path, bare, seed)
    png = _make_png(tmp_path, "img.png")
    result = _run_publish(tmp_path, bare, monkeypatch, module_part=module_part, cards={1: png})

    assert result["pushed"] is True
    checkout = _reclone(tmp_path, bare)
    # The current-run pack survived AND now carries the newly published PNG.
    assert (checkout / f"assets/gamma/{module_part}").is_dir()
    assert (checkout / f"assets/gamma/{module_part}/img.png").is_file()


def test_retention_boundary_survives_and_past_boundary_deleted(tmp_path, monkeypatch) -> None:
    """RA7b: a pack aged exactly retention_days survives; retention_days+1 is deleted."""
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/gamma/atboundary", epoch=NOW - 10 * DAY)
        _commit_pack(seed_repo, "assets/gamma/pastboundary", epoch=NOW - 11 * DAY)

    _seed(tmp_path, bare, seed)
    png = _make_png(tmp_path, "img.png")
    _run_publish(tmp_path, bare, monkeypatch, module_part="c1m1/run1", cards={1: png})

    checkout = _reclone(tmp_path, bare)
    assert (checkout / "assets/gamma/atboundary").is_dir()  # exactly 10d → kept (> semantics)
    assert not (checkout / "assets/gamma/pastboundary").exists()  # 11d → pruned


def test_retention_allowlisted_old_packs_survive(tmp_path, monkeypatch) -> None:
    """RA7d: protected_paths (assets/gamma/shared, assets/gamma/courses) survive old age."""
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/gamma/shared", epoch=NOW - 90 * DAY)
        _commit_pack(seed_repo, "assets/gamma/courses", epoch=NOW - 90 * DAY)

    _seed(tmp_path, bare, seed)
    png = _make_png(tmp_path, "img.png")
    _run_publish(tmp_path, bare, monkeypatch, module_part="c1m1/run1", cards={1: png})

    checkout = _reclone(tmp_path, bare)
    assert (checkout / "assets/gamma/shared").is_dir()
    assert (checkout / "assets/gamma/courses").is_dir()


def test_old_non_protected_pack_deleted_and_committed(tmp_path, monkeypatch) -> None:
    """An old pack in ANOTHER managed root is pruned AND the delete is committed+pushed."""
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/storyboards/oldstory-uuid", epoch=NOW - 20 * DAY)

    _seed(tmp_path, bare, seed)
    png = _make_png(tmp_path, "img.png")
    result = _run_publish(
        tmp_path, bare, monkeypatch, module_part="c1m1/run1", cards={1: png}
    )

    assert result["pushed"] is True
    assert result["retention"]["deleted"] >= 1
    checkout = _reclone(tmp_path, bare)
    # Old storyboard pack gone; new gamma files present — both in one push.
    assert not (checkout / "assets/storyboards/oldstory-uuid").exists()
    assert (checkout / "assets/gamma/c1m1/run1/img.png").is_file()


# ─────────────────────────────────────────────────────────────── regression
def test_regression_result_keys_preserved(tmp_path, monkeypatch) -> None:
    """url_map / copied_count / substituted_cards preserved on a normal publish."""
    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)
    png1 = _make_png(tmp_path, "a.png")
    png2 = _make_png(tmp_path, "b.png")
    result = _run_publish(
        tmp_path, bare, monkeypatch, module_part="c1m1/run1", cards={1: png1, 2: png2}
    )

    assert result["copied_count"] == 2
    assert result["substituted_cards"] == [1, 2]
    assert set(result["url_map"].keys()) == {1, 2}
    assert result["url_map"][1].endswith("/a.png")
    assert result["preintegration_ready"] is True
    assert result["pushed"] is True


def test_adhoc_mode_still_skips(tmp_path, monkeypatch) -> None:
    """The ad-hoc skip path is preserved (no push, empty url_map)."""
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)
    png = _make_png(tmp_path, "a.png")
    result = publish_preintegration_literal_visuals(
        {1: png},
        "c1m1/run1",
        site_repo_url=str(bare),
        mode="ad-hoc",
        verify=False,
    )
    assert result["pushed"] is False
    assert result["url_map"] == {}


# ─────────────────────────────────────────────────────────────── size guard
def test_size_guard_refuses_and_performs_no_push(tmp_path, monkeypatch) -> None:
    """Over-threshold projected size raises SizeGuardRefusal and pushes NOTHING."""
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        # A protected >1 MB blob that survives prune and pushes the projected tree
        # over a monkeypatched 1 MB fail threshold.
        big = seed_repo / "assets/gamma/shared"
        big.mkdir(parents=True)
        (big / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))
        _git(["add", "."], cwd=seed_repo)
        _git(["commit", "-m", "big"], cwd=seed_repo)

    _seed(tmp_path, bare, seed)

    real = gamma_operations.load_hygiene_config

    def tiny(cfg):
        retention, _size, verify = real(cfg)
        return retention, SizeGuardConfig(warn_at_mb=1, fail_at_mb=1), verify

    monkeypatch.setattr(gamma_operations, "load_hygiene_config", tiny)
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    _freeze_now(monkeypatch)

    png = _make_png(tmp_path, "a.png")
    with pytest.raises(SizeGuardRefusal):
        publish_preintegration_literal_visuals(
            {1: png},
            "c1m1/run1",
            site_repo_url=str(bare),
            verify=False,
        )

    # Origin must be untouched — the new pack never landed.
    checkout = _reclone(tmp_path, bare)
    assert not (checkout / "assets/gamma/c1m1/run1").exists()


# ────────────────────────────────────────────── staged-only commit gate (FIX1/FIX2)
def test_noop_republish_with_worktree_noise_does_not_raise(tmp_path, monkeypatch) -> None:
    """FIX1/FIX2: a no-op re-publish (identical PNG already in origin) must NOT raise even
    when the fresh clone carries untracked worktree noise with NOTHING staged.

    Whole-repo ``git status --porcelain`` reports untracked/unstaged entries, so the old
    commit gate would try to commit with an empty index and abort. The staged-only gate
    (``git diff --cached --name-only``) sees nothing staged and cleanly skips the push.
    Untracked noise is injected via the retention seam (which receives the internal clone
    dir) — git itself is never mocked.
    """
    bare = _bare_origin(tmp_path)
    module_part = "c1m1/run1"

    def seed(seed_repo: Path) -> None:
        # The CURRENT-run pack already holds the exact PNG we will re-publish → `git add`
        # stages nothing (a true no-op re-publish).
        pack = seed_repo / f"assets/gamma/{module_part}"
        pack.mkdir(parents=True)
        (pack / "img.png").write_bytes(_DUMMY_PNG_BYTES)
        _git(["add", "."], cwd=seed_repo)
        _git(["commit", "-m", "seed current pack"], cwd=seed_repo)

    _seed(tmp_path, bare, seed)

    called = {"pruned": False}
    real_prune = gamma_operations.prune_retention

    def prune_and_litter(clone_dir, **kw):
        rep = real_prune(clone_dir, **kw)
        (Path(clone_dir) / "untracked_noise.txt").write_text("noise\n", encoding="utf-8")
        called["pruned"] = True
        return rep

    monkeypatch.setattr(gamma_operations, "prune_retention", prune_and_litter)

    png = _make_png(tmp_path, "img.png")  # identical bytes to the seeded pack's img.png
    result = _run_publish(tmp_path, bare, monkeypatch, module_part=module_part, cards={1: png})

    assert called["pruned"], "retention seam must run to inject worktree noise"
    assert result["pushed"] is False  # nothing staged → no commit, no push, no raise
    assert 1 in result["url_map"]  # url_map still returned for card substitution


# ─────────────────────────────────────── _github_pages_base_url host fallback (FIX4)
def test_github_pages_base_url_host_conditioned_fallback() -> None:
    """FIX4: a malformed *github* URL fails loud; other hosts keep the lenient fallback."""
    from gamma_operations import _github_pages_base_url

    with pytest.raises(ValueError):
        _github_pages_base_url("https://github.com/owner")  # missing repo on github host
    # Non-github host with <2 path parts keeps the offline/local lenient fallback.
    assert _github_pages_base_url("https://example.com/foo") == "https://example.com/foo"
    # A normal user.github.io repo still resolves to its Pages base.
    assert (
        _github_pages_base_url("https://github.com/jlenrique/jlenrique.github.io")
        == "https://jlenrique.github.io"
    )


# ──────────────────────────────────────────── retention-disabled warning (FIX5)
def test_retention_disabled_emits_warning(tmp_path, monkeypatch, caplog) -> None:
    """FIX5: when ``load_hygiene_config`` yields retention=None the publisher WARNS loudly."""
    import logging

    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)

    real = gamma_operations.load_hygiene_config

    def no_retention(cfg):
        _r, size, verify = real(cfg)
        return None, size, verify

    monkeypatch.setattr(gamma_operations, "load_hygiene_config", no_retention)
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    _freeze_now(monkeypatch)

    png = _make_png(tmp_path, "a.png")
    with caplog.at_level(logging.WARNING, logger="gamma_operations"):
        publish_preintegration_literal_visuals(
            {1: png},
            "c1m1/run1",
            site_repo_url=str(bare),
            verify=False,
        )
    assert "retention pruning DISABLED" in caplog.text

"""Shared gh-pages publish helper — retention, size guard, verify, transport.

RED-first per the Task 1 greenlight (RA1-RA10). Retention date fixtures are made
DETERMINISTIC + cross-platform by setting BOTH ``GIT_COMMITTER_DATE`` and
``GIT_AUTHOR_DATE`` to an explicit epoch (``@<epoch> +0000``) in the subprocess env,
with a read-back self-check that ``%ct`` equals the intended epoch (Murat: test the
harness). The size guard is proved against a temp bare origin so a refusal can be
shown to perform NO push (origin unchanged).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.marcus.orchestrator.gh_pages_publish import (
    GhPagesPublishError,
    RetentionConfig,
    SizeGuardConfig,
    SizeGuardRefusal,
    _default_pages_build_checker,
    _map_pages_build_response,
    git_publish_dir,
    project_published_size,
    prune_retention,
)

DAY = 86400


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
    """Create + commit a pack dir at ``rel`` with committer date pinned to ``epoch``.

    Sets BOTH GIT_COMMITTER_DATE and GIT_AUTHOR_DATE (``git commit --date`` alone sets
    only the author date, leaving %ct = wall clock → retention theater). Reads %ct back
    and asserts it equals ``epoch`` — the fixture self-check.
    """
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


# ─────────────────────────────────────────────────────────────── G1 retention
def _cfg(**kw) -> RetentionConfig:
    kw.setdefault("managed_roots", ("assets/styleguide-picker",))
    return RetentionConfig(**kw)


def test_retention_deletes_only_old_non_allowlisted(tmp_path: Path) -> None:
    """AC1: >retention_days packs delete; recent packs survive."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/styleguide-picker/oldpack", epoch=now - 20 * DAY)
    _commit_pack(repo, "assets/styleguide-picker/recentpack", epoch=now - 3 * DAY)
    report = prune_retention(repo, config=_cfg(), now=now)
    deleted = {p.path for p in report.deleted}
    assert deleted == {"assets/styleguide-picker/oldpack"}
    assert not (repo / "assets/styleguide-picker/oldpack").exists()
    assert (repo / "assets/styleguide-picker/recentpack").exists()


def test_retention_allowlist_exact_match_no_false_neighbor(tmp_path: Path) -> None:
    """AC2 + RA7d: protecting 'foo' must NOT protect 'foo-2'."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/gamma/shared", epoch=now - 40 * DAY)
    _commit_pack(repo, "assets/gamma/shared-2", epoch=now - 40 * DAY)
    cfg = RetentionConfig(
        managed_roots=("assets/gamma",),
        protected_paths=frozenset({"assets/gamma/shared"}),
    )
    report = prune_retention(repo, config=cfg, now=now)
    deleted = {p.path for p in report.deleted}
    assert deleted == {"assets/gamma/shared-2"}
    assert "assets/gamma/shared" in report.skipped_protected
    assert (repo / "assets/gamma/shared").exists()


def test_retention_never_deletes_current_run_pack(tmp_path: Path) -> None:
    """RA7a (highest severity): the pack published THIS run is protected by identity."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    # An OLD committer date on the very pack we're publishing this run (e.g. rebased).
    _commit_pack(repo, "assets/styleguide-picker/currentrun", epoch=now - 30 * DAY)
    report = prune_retention(
        repo, config=_cfg(), now=now, current_subdir="assets/styleguide-picker/currentrun"
    )
    assert report.deleted == []
    assert report.skipped_current == ["assets/styleguide-picker/currentrun"]
    assert (repo / "assets/styleguide-picker/currentrun").exists()


def test_retention_protects_ancestor_of_nested_current_subdir(tmp_path: Path) -> None:
    """FIX3: an immediate-child pack that is an ANCESTOR of a deeper ``current_subdir`` is
    identity-protected. Publishing a nested sub-pack ``assets/gamma/mod/part1`` must NOT
    prune the stale parent pack ``assets/gamma/mod`` (which would destroy sibling part2)."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/gamma/mod", epoch=now - 30 * DAY)
    report = prune_retention(
        repo,
        config=RetentionConfig(managed_roots=("assets/gamma",), max_age_days=10),
        now=now,
        current_subdir="assets/gamma/mod/part1",
    )
    assert report.deleted == []
    assert "assets/gamma/mod" in report.skipped_current
    assert (repo / "assets/gamma/mod").exists()


def test_retention_boundary_exactly_at_threshold_survives(tmp_path: Path) -> None:
    """RA7b: age == retention_days survives (> semantics); +1 second deletes."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/styleguide-picker/atboundary", epoch=now - 10 * DAY)
    _commit_pack(repo, "assets/styleguide-picker/pastboundary", epoch=now - 10 * DAY - 1)
    report = prune_retention(repo, config=_cfg(max_age_days=10), now=now)
    deleted = {p.path for p in report.deleted}
    assert deleted == {"assets/styleguide-picker/pastboundary"}
    assert (repo / "assets/styleguide-picker/atboundary").exists()


def test_retention_absent_managed_root_is_benign_noop(tmp_path: Path) -> None:
    """RA7c: a managed root missing from the clone is a WARN skip, never a raise."""
    repo = tmp_path / "r"
    _init_repo(repo)
    (repo / "README").write_text("x", encoding="utf-8")
    _git(["add", "."], cwd=repo)
    _git(["commit", "-m", "seed"], cwd=repo)
    report = prune_retention(
        repo,
        config=RetentionConfig(managed_roots=("assets/does-not-exist", "assets/gamma")),
        now=1_800_000_000,
    )
    assert report.deleted == []  # no crash, nothing deleted


def test_retention_empty_present_managed_root_is_noop(tmp_path: Path) -> None:
    """RA7c: a managed root that EXISTS but holds no packs is a clean no-op."""
    repo = tmp_path / "r"
    _init_repo(repo)
    (repo / "assets/styleguide-picker").mkdir(parents=True)  # present but empty
    (repo / "README").write_text("x", encoding="utf-8")
    _git(["add", "."], cwd=repo)
    _git(["commit", "-m", "seed"], cwd=repo)
    report = prune_retention(repo, config=_cfg(), now=1_800_000_000)
    assert report.deleted == []


def test_retention_ignores_loose_files_and_unknown_age(tmp_path: Path) -> None:
    """RA7e + unknown-age: a loose file in the root and an uncommitted dir are skipped."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/styleguide-picker/oldpack", epoch=now - 20 * DAY)
    root = repo / "assets/styleguide-picker"
    (root / "loose.txt").write_text("not a pack", encoding="utf-8")  # loose file
    (root / "uncommitted").mkdir()  # dir with no commit history
    (root / "uncommitted" / "f").write_text("x", encoding="utf-8")
    report = prune_retention(repo, config=_cfg(), now=now)
    deleted = {p.path for p in report.deleted}
    assert deleted == {"assets/styleguide-picker/oldpack"}
    assert "assets/styleguide-picker/uncommitted" in report.skipped_unknown_age


def test_retention_dry_run_is_inert(tmp_path: Path) -> None:
    """RA7f: dry_run reports the deletion set + reclaim bytes but stages nothing."""
    repo = tmp_path / "r"
    _init_repo(repo)
    now = 1_800_000_000
    _commit_pack(repo, "assets/styleguide-picker/oldpack", epoch=now - 20 * DAY, size_bytes=2048)
    report = prune_retention(repo, config=_cfg(), now=now, dry_run=True)
    assert {p.path for p in report.deleted} == {"assets/styleguide-picker/oldpack"}
    assert report.reclaim_bytes >= 2048
    # still on disk + still clean (nothing staged for deletion)
    assert (repo / "assets/styleguide-picker/oldpack").exists()
    assert _git(["status", "--porcelain"], cwd=repo).strip() == ""


# ─────────────────────────────────────────────────────────────── G2 size guard
def test_size_guard_raises_over_fail_threshold(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    (tree / "assets").mkdir(parents=True)
    (tree / "assets" / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    with pytest.raises(SizeGuardRefusal, match="(?i)size|guard"):
        project_published_size(tree, config=SizeGuardConfig(warn_at_mb=1, fail_at_mb=1))


def test_size_guard_under_threshold_passes(tmp_path: Path) -> None:
    tree = tmp_path / "tree"
    (tree / "assets").mkdir(parents=True)
    (tree / "assets" / "small.bin").write_bytes(b"x" * 1024)
    report = project_published_size(tree, config=SizeGuardConfig())
    assert report.warned is False
    assert report.total_bytes >= 1024


def test_size_guard_excludes_dot_git(tmp_path: Path) -> None:
    """.git object storage must not count toward the published-tree size."""
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    (tree / ".git" / "huge.pack").write_bytes(b"x" * (5 * 1024 * 1024))
    (tree / "index.html").write_text("<html></html>", encoding="utf-8")
    report = project_published_size(tree, config=SizeGuardConfig(warn_at_mb=1, fail_at_mb=1))
    assert report.total_bytes < 1024  # only index.html counted, .git excluded


# ─────────────────────────────────────────────────────── G3 verify adapter (RA6)
def test_map_pages_build_response_200_returns_dict() -> None:
    body = {"status": "built", "error": None}
    assert _map_pages_build_response(200, lambda: body) == body


@pytest.mark.parametrize("code", [401, 403, 404, 500])
def test_map_pages_build_response_non_200_returns_none(code: int) -> None:
    """A non-200 (esp. 403 = token lacks Pages:read) degrades to None → URL poll."""
    assert _map_pages_build_response(code, lambda: {"status": "built"}) is None


def test_map_pages_build_response_non_dict_body_returns_none() -> None:
    assert _map_pages_build_response(200, lambda: ["not", "a", "dict"]) is None


def test_default_pages_build_checker_httpx_200_maps_dict(monkeypatch) -> None:
    """RA6: the ONE httpx-stubbed test — the default checker maps a real httpx 200 body."""
    import httpx

    def fake_get(url, headers=None, timeout=None):
        assert "api.github.com/repos/owner/repo/pages/builds/latest" in url
        return httpx.Response(200, json={"status": "built", "error": None})

    monkeypatch.setattr(httpx, "get", fake_get)
    result = _default_pages_build_checker("https://github.com/owner/repo", "tok")
    assert result == {"status": "built", "error": None}


def test_default_pages_build_checker_httpx_403_degrades_to_none(monkeypatch) -> None:
    """A 403 (token lacks Pages:read) maps to None so the caller falls back to URL poll."""
    import httpx

    monkeypatch.setattr(
        httpx, "get", lambda *a, **k: httpx.Response(403, json={"message": "Forbidden"})
    )
    assert _default_pages_build_checker("https://github.com/owner/repo", "tok") is None


def test_default_pages_build_checker_httpx_raise_never_breaks(monkeypatch) -> None:
    """A network raise inside the checker degrades to None — never breaks publishing."""
    import httpx

    def boom(*a, **k):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(httpx, "get", boom)
    assert _default_pages_build_checker("https://github.com/owner/repo", "tok") is None


# ──────────────────────────────────────────────── transport + integration (bare origin)
def _bare_origin(tmp_path: Path) -> Path:
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(["init", "--bare", "--initial-branch=main", "."], cwd=bare)
    seed = tmp_path / "seed"
    _init_repo(seed)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git(["add", "."], cwd=seed)
    _git(["commit", "-m", "seed"], cwd=seed)
    _git(["remote", "add", "origin", str(bare)], cwd=seed)
    _git(["push", "origin", "main"], cwd=seed)
    return bare


def test_git_publish_dir_scrubs_token_on_failure(tmp_path: Path) -> None:
    """The transport never leaks x-access-token:{token} in a raised message (RA4 basis)."""
    secret = "ghp_SUPERSECRETTOKEN1234567890"
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(GhPagesPublishError) as excinfo:
        git_publish_dir(
            pack,
            site_repo="https://github.com/does-not-exist/nope",
            subdir="assets/x/run1",
            token=secret,
        )
    msg = str(excinfo.value)
    assert secret not in msg
    assert "x-access-token:" not in msg or "***" in msg


def test_git_publish_dir_size_guard_refuses_before_push(tmp_path: Path) -> None:
    """AC3: over-threshold projected size RAISES and performs NO push (origin unchanged)."""
    bare = _bare_origin(tmp_path)
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html></html>", encoding="utf-8")
    (pack / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    with pytest.raises(SizeGuardRefusal):
        git_publish_dir(
            pack,
            site_repo=str(bare),
            subdir="assets/styleguide-picker/run1",
            token="dummy",
            size_guard=SizeGuardConfig(warn_at_mb=1, fail_at_mb=1),
        )
    # origin must be untouched — re-clone and confirm the pack never landed.
    checkout = tmp_path / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    assert not (checkout / "assets" / "styleguide-picker" / "run1").exists()


def test_git_publish_dir_prunes_and_publishes_in_one_push(tmp_path: Path) -> None:
    """Integration: an old managed pack is pruned AND the new pack lands in one publish."""
    bare = _bare_origin(tmp_path)
    now = 1_800_000_000
    # seed an OLD pack into the origin so the clone sees it
    seed = tmp_path / "seed2"
    _git(["clone", "--branch", "main", str(bare), str(seed)], cwd=tmp_path)
    _git(["config", "user.name", "t"], cwd=seed)
    _git(["config", "user.email", "t@x"], cwd=seed)
    _commit_pack(seed, "assets/styleguide-picker/oldpack", epoch=now - 30 * DAY)
    _git(["push", "origin", "main"], cwd=seed)

    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html>new</html>", encoding="utf-8")

    url = git_publish_dir(
        pack,
        site_repo=str(bare),
        subdir="assets/styleguide-picker/newrun",
        token="dummy",
        retention=RetentionConfig(managed_roots=("assets/styleguide-picker",), max_age_days=10),
        size_guard=SizeGuardConfig(),
        now=now,
    )
    assert url.endswith("/assets/styleguide-picker/newrun/index.html")
    checkout = tmp_path / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    assert (checkout / "assets/styleguide-picker/newrun/index.html").is_file()
    assert not (checkout / "assets/styleguide-picker/oldpack").exists()  # pruned same push

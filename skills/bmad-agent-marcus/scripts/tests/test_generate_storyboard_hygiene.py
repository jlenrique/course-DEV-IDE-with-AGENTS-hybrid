"""Offline hygiene tests for the storyboard publish transport (Task 1b).

Exercises the gh-pages hygiene primitives now woven around ``cmd_publish``'s own git
transport: retention prune, size guard (fail-loud → no push), whole-repo commit gate,
and the ``verify`` seam.

NO MOCKING of git and NO live network: every test runs against a temp BARE origin,
points ``--site-repo-url`` at that local path (exercising the non-github fallback in
``_github_pages_base_url``), and calls ``cmd_publish(args, verify=False)`` (the offline
seam — a temp bare repo has no live HTTP endpoint). Retention dates are made
deterministic by pinning BOTH ``GIT_COMMITTER_DATE`` and ``GIT_AUTHOR_DATE`` to explicit
``@<epoch> +0000`` stamps and freezing ``time.time`` (mirrors
``tests/marcus/orchestrator/test_gh_pages_publish.py``).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

import app.marcus.orchestrator.gh_pages_publish as ghp
from app.marcus.orchestrator.gh_pages_publish import SizeGuardConfig, SizeGuardRefusal

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_GENERATE_SCRIPT = _SCRIPTS_DIR / "generate-storyboard.py"

DAY = 86400
NOW = 1_800_000_000


def _load_generate_module():
    spec = importlib.util.spec_from_file_location("generate_storyboard_mod", _GENERATE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def _build_bundle(mod, bundle: Path, run_id: str) -> Path:
    """Build a minimal storyboard bundle and return its storyboard.json path."""
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    Image.new("RGB", (12, 6), color=(10, 90, 160)).save(slides / "s1.png", format="PNG")
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s1.png",
            }
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        run_id=run_id,
    )
    mod.write_bundle(manifest, storyboard_dir)
    return storyboard_dir / "storyboard.json"


def _args(tmp_path: Path, bare: Path, storyboard_json: Path) -> SimpleNamespace:
    return SimpleNamespace(
        manifest=storyboard_json,
        export_root=tmp_path / "exports",
        export_name=None,
        site_repo_url=str(bare),
        publish_subdir="assets/storyboards",
        site_branch="main",
        token_env_var="GITHUB_PAGES_TOKEN",
    )


def _run_publish(mod, tmp_path, bare, monkeypatch, *, run_id: str) -> int:
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    monkeypatch.setattr(time, "time", lambda: float(NOW))
    storyboard_json = _build_bundle(mod, tmp_path / "bundle", run_id)
    return mod.cmd_publish(_args(tmp_path, bare, storyboard_json), verify=False)


# ─────────────────────────────────────────────────────────────── retention
def test_current_run_pack_never_deleted_even_if_backdated(tmp_path, monkeypatch) -> None:
    """RA7a: a pack at THIS run's subdir survives even when its commit date is old."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)
    run_id = "RUN-STORY-1"

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, f"assets/storyboards/{run_id}", epoch=NOW - 40 * DAY)

    _seed(tmp_path, bare, seed)
    rc = _run_publish(mod, tmp_path, bare, monkeypatch, run_id=run_id)
    assert rc == 0
    checkout = _reclone(tmp_path, bare)
    assert (checkout / f"assets/storyboards/{run_id}").is_dir()
    assert (checkout / f"assets/storyboards/{run_id}/index.html").is_file()


def test_retention_boundary_survives_and_past_boundary_deleted(tmp_path, monkeypatch) -> None:
    """RA7b: a pack aged exactly retention_days survives; retention_days+1 is deleted."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/storyboards/atboundary", epoch=NOW - 10 * DAY)
        _commit_pack(seed_repo, "assets/storyboards/pastboundary", epoch=NOW - 11 * DAY)

    _seed(tmp_path, bare, seed)
    _run_publish(mod, tmp_path, bare, monkeypatch, run_id="RUN-STORY-1")
    checkout = _reclone(tmp_path, bare)
    assert (checkout / "assets/storyboards/atboundary").is_dir()
    assert not (checkout / "assets/storyboards/pastboundary").exists()


def test_retention_allowlisted_old_packs_survive(tmp_path, monkeypatch) -> None:
    """RA7d: protected_paths (assets/gamma/shared, assets/gamma/courses) survive old age."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/gamma/shared", epoch=NOW - 90 * DAY)
        _commit_pack(seed_repo, "assets/gamma/courses", epoch=NOW - 90 * DAY)

    _seed(tmp_path, bare, seed)
    _run_publish(mod, tmp_path, bare, monkeypatch, run_id="RUN-STORY-1")
    checkout = _reclone(tmp_path, bare)
    assert (checkout / "assets/gamma/shared").is_dir()
    assert (checkout / "assets/gamma/courses").is_dir()


def test_old_non_protected_pack_deleted_and_committed(tmp_path, monkeypatch) -> None:
    """An old pack in another managed root is pruned AND the delete is committed+pushed."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        _commit_pack(seed_repo, "assets/kling-validation/old-uuid", epoch=NOW - 20 * DAY)

    _seed(tmp_path, bare, seed)
    rc = _run_publish(mod, tmp_path, bare, monkeypatch, run_id="RUN-STORY-1")
    assert rc == 0
    checkout = _reclone(tmp_path, bare)
    assert not (checkout / "assets/kling-validation/old-uuid").exists()
    assert (checkout / "assets/storyboards/RUN-STORY-1/index.html").is_file()


# ─────────────────────────────────────────────────────────────── regression
def test_regression_receipt_and_publish_url_preserved(tmp_path, monkeypatch) -> None:
    """A normal publish returns exit 0 and writes a receipt with the expected fields."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)
    rc = _run_publish(mod, tmp_path, bare, monkeypatch, run_id="RUN-STORY-1")
    assert rc == 0

    # The publish receipt is written under export_root.
    receipts = list((tmp_path / "exports").glob("*-publish-receipt.json"))
    assert receipts, "publish receipt should be written"
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert receipt["status"] == "published"
    assert receipt["run_id"] == "RUN-STORY-1"
    assert receipt["target_subdir"] == "assets/storyboards/RUN-STORY-1"
    assert receipt["publish_url"].endswith("/assets/storyboards/RUN-STORY-1/index.html")
    assert "changed" in receipt and "file_count" in receipt

    checkout = _reclone(tmp_path, bare)
    assert (checkout / "assets/storyboards/RUN-STORY-1/index.html").is_file()


# ─────────────────────────────────────────────────────────────── size guard
def test_size_guard_refuses_and_performs_no_push(tmp_path, monkeypatch) -> None:
    """Over-threshold projected size raises SizeGuardRefusal and pushes NOTHING."""
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)

    def seed(seed_repo: Path) -> None:
        big = seed_repo / "assets/gamma/shared"
        big.mkdir(parents=True)
        (big / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))
        _git(["add", "."], cwd=seed_repo)
        _git(["commit", "-m", "big"], cwd=seed_repo)

    _seed(tmp_path, bare, seed)

    real = ghp.load_hygiene_config

    def tiny(cfg):
        retention, _size, verify = real(cfg)
        return retention, SizeGuardConfig(warn_at_mb=1, fail_at_mb=1), verify

    monkeypatch.setattr(ghp, "load_hygiene_config", tiny)
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    monkeypatch.setattr(time, "time", lambda: float(NOW))

    storyboard_json = _build_bundle(mod, tmp_path / "bundle", "RUN-STORY-1")
    with pytest.raises(SizeGuardRefusal):
        mod.cmd_publish(_args(tmp_path, bare, storyboard_json), verify=False)

    # Origin untouched — the new pack never landed.
    checkout = _reclone(tmp_path, bare)
    assert not (checkout / "assets/storyboards/RUN-STORY-1").exists()


# ────────────────────────────────────────────── staged-only commit gate (FIX1/FIX2)
def test_noop_republish_with_worktree_noise_does_not_raise(tmp_path, monkeypatch) -> None:
    """FIX1/FIX2: a byte-identical re-publish (same manifest → deterministic snapshot) must
    NOT raise even when the fresh clone carries untracked worktree noise with NOTHING staged.

    Whole-repo ``git status --porcelain`` reports the untracked entry, so the old commit
    gate would try to commit with an empty index and abort; the staged-only gate
    (``git diff --cached --name-only``) sees nothing staged and cleanly skips the push.
    Untracked noise is injected via the retention seam (which receives the internal clone
    dir) — git itself is never mocked.
    """
    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    monkeypatch.setattr(time, "time", lambda: float(NOW))

    # Build the bundle ONCE so the manifest (and its embedded generated_at) is fixed —
    # re-exporting the same manifest yields a deterministic, identical snapshot.
    storyboard_json = _build_bundle(mod, tmp_path / "bundle", "RUN-NOOP-1")
    args = _args(tmp_path, bare, storyboard_json)

    # First publish lands the pack.
    assert mod.cmd_publish(args, verify=False) == 0
    checkout = _reclone(tmp_path, bare, name="after-first")
    assert (checkout / "assets/storyboards/RUN-NOOP-1/index.html").is_file()

    # Second publish is a no-op (snapshot == origin pack → publish_snapshot_tree
    # changed=False → nothing staged). Inject untracked worktree noise via the retention seam.
    called = {"pruned": False}
    real_prune = ghp.prune_retention

    def prune_and_litter(clone_dir, **kw):
        rep = real_prune(clone_dir, **kw)
        (Path(clone_dir) / "untracked_noise.txt").write_text("noise\n", encoding="utf-8")
        called["pruned"] = True
        return rep

    monkeypatch.setattr(ghp, "prune_retention", prune_and_litter)
    rc = mod.cmd_publish(args, verify=False)
    assert called["pruned"], "retention seam must run to inject worktree noise"
    assert rc == 0  # nothing staged → no commit, no push, no raise


# ──────────────────────────────────────────── retention-disabled warning (FIX5)
def test_retention_disabled_emits_warning(tmp_path, monkeypatch, caplog) -> None:
    """FIX5: when ``load_hygiene_config`` yields retention=None the publisher WARNS loudly."""
    import logging

    mod = _load_generate_module()
    bare = _bare_origin(tmp_path)
    _seed(tmp_path, bare)

    real = ghp.load_hygiene_config

    def no_retention(cfg):
        _r, size, verify = real(cfg)
        return None, size, verify

    monkeypatch.setattr(ghp, "load_hygiene_config", no_retention)
    monkeypatch.setenv("GITHUB_PAGES_TOKEN", "dummy-token")
    monkeypatch.setattr(time, "time", lambda: float(NOW))

    storyboard_json = _build_bundle(mod, tmp_path / "bundle", "RUN-STORY-1")
    with caplog.at_level(logging.WARNING, logger="generate_storyboard"):
        rc = mod.cmd_publish(_args(tmp_path, bare, storyboard_json), verify=False)
    assert rc == 0
    assert "retention pruning DISABLED" in caplog.text

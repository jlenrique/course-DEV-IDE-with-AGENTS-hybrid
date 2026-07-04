"""Chooser publisher transport — token-scrub (RA4) + temp-bare-repo publish.

The chooser's ``_git_publish_dir`` used to leak the publish token in its error message
(``f"...failed: {exc}"`` where ``exc.cmd`` carries ``x-access-token:{token}@``). Task 1
consolidated it onto the shared ``gh_pages_publish.git_publish_dir``, which scrubs the
token. These tests pin that fix and the landing behavior against a temp bare repo.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.marcus.orchestrator.chooser_publisher import ChooserPublishError, _git_publish_dir


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _bare_origin(tmp_path: Path) -> Path:
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(["init", "--bare", "--initial-branch=main", "."], cwd=bare)
    seed = tmp_path / "seed"
    seed.mkdir()
    _git(["init", "--initial-branch=main", "."], cwd=seed)
    _git(["config", "user.name", "seed"], cwd=seed)
    _git(["config", "user.email", "seed@x"], cwd=seed)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git(["add", "."], cwd=seed)
    _git(["commit", "-m", "seed"], cwd=seed)
    _git(["remote", "add", "origin", str(bare)], cwd=seed)
    _git(["push", "origin", "main"], cwd=seed)
    return bare


def test_chooser_publish_error_scrubs_token(tmp_path: Path) -> None:
    """RA4 (blocking): a forced push/clone failure must never expose the token."""
    secret = "ghp_CHOOSERSECRETTOKEN0987654321"
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(ChooserPublishError) as excinfo:
        _git_publish_dir(
            pack,
            site_repo="https://github.com/does-not-exist/nope",
            subdir="assets/storyboards/trial-chooser",
            token=secret,
        )
    msg = str(excinfo.value)
    assert secret not in msg, "the publish token must never appear in the error message"
    assert "x-access-token:" not in msg or "***" in msg
    assert excinfo.value.tag == "chooser.publish.failed"


def test_chooser_publish_lands_pack_on_bare_origin(tmp_path: Path) -> None:
    bare = _bare_origin(tmp_path)
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html>chooser</html>", encoding="utf-8")
    (pack / "A_slide1.png").write_bytes(b"x")

    url = _git_publish_dir(
        pack,
        site_repo=str(bare),
        subdir="assets/storyboards/trial-chooser",
        token="dummy-token",
    )
    assert url.endswith("/assets/storyboards/trial-chooser/index.html")

    checkout = tmp_path / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    landed = checkout / "assets" / "storyboards" / "trial-chooser"
    assert (landed / "index.html").is_file()
    assert (landed / "A_slide1.png").is_file()

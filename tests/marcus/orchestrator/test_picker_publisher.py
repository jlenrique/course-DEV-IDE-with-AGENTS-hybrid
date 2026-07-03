"""Publisher proof against a TEMP BARE git repo as origin (no real GitHub, RED-first).

Mirrors the ``chooser_publisher`` receipt/pack contract: the pack lands on the
site branch carrying ``index.html`` + a ``thumbnails/`` dir, and a receipt JSON
is written with the same shape family the chooser emits.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.picker_publisher import (
    PickerPublishError,
    _filename_issue,
    _git_publish_dir,
    _sanitize_pack,
    publish_picker,
)


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _bare_origin(tmp_path: Path) -> Path:
    """A bare repo with an initial commit on ``main`` so ``clone --branch main`` works."""
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(["init", "--bare", "--initial-branch=main", "."], cwd=bare)
    seed = tmp_path / "seed"
    seed.mkdir()
    _git(["init", "--initial-branch=main", "."], cwd=seed)
    _git(["config", "user.name", "seed"], cwd=seed)
    _git(["config", "user.email", "seed@example.com"], cwd=seed)
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    _git(["add", "."], cwd=seed)
    _git(["commit", "-m", "seed"], cwd=seed)
    _git(["remote", "add", "origin", str(bare)], cwd=seed)
    _git(["push", "origin", "main"], cwd=seed)
    return bare


def _ssot(tmp_path: Path) -> Path:
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "style_guides": {
                    "alpha-style": {
                        "lifecycle": "permanent",
                        "presentation": {"display_name": "Alpha", "distinguishing": "d"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return ssot


def _roster() -> list[dict]:
    return [
        {
            "name": "alpha-style",
            "display_name": "Alpha",
            "distinguishing": "d",
            "narrative": {},
            "probe": False,
            "lifecycle": "permanent",
            "card_dimensions": "",
            "thumbnail_ref": None,
            "example_url": None,
            "last_used": None,
        }
    ]


def test_publish_missing_token_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_PAGES_TOKEN", raising=False)
    with pytest.raises(PickerPublishError, match="(?i)token"):
        publish_picker(
            run_tag="abc12345",
            out_dir=tmp_path / "out",
            roster=_roster(),
            ssot_path=_ssot(tmp_path),
            site_repo=str(tmp_path / "origin.git"),
            token="",
        )


def test_publish_lands_pack_on_branch_with_receipt(tmp_path: Path) -> None:
    bare = _bare_origin(tmp_path)
    thumb = tmp_path / "thumb.png"
    # a valid tiny PNG (1x1) so the thumbnails/ copy path is exercised
    thumb.write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001080600000"
            "01f15c4890000000d49444154789c6360000002000100"
            "05fe02fea7f35c0000000049454e44ae426082"
        )
    )
    roster = _roster()
    roster[0]["thumbnail_ref"] = "thumb.png"

    record = publish_picker(
        run_tag="abc12345",
        out_dir=tmp_path / "out",
        roster=roster,
        repo_root=tmp_path,
        ssot_path=_ssot(tmp_path),
        site_repo=str(bare),
        token="dummy-token",
        verify=False,  # a bare repo has no live HTTP endpoint to poll
    )

    assert record["run_tag"] == "abc12345"
    assert record["style_count"] == 1
    assert "publish_url" in record

    # receipt on disk mirrors the chooser receipt-file shape
    receipt_path = tmp_path / "out" / "picker-publish-abc12345.json"
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["run_tag"] == "abc12345"

    # verify the pack actually landed on main in the bare origin
    checkout = tmp_path / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    subdir = checkout / "assets" / "styleguide-picker" / "abc12345"
    assert (subdir / "index.html").is_file()
    assert (subdir / "thumbnails" / "alpha-style.png").is_file()
    html = (subdir / "index.html").read_text(encoding="utf-8")
    assert "abc12345" in html


# ------------------------------------------------------------ MUST-1 run_tag guard
@pytest.mark.parametrize("bad_tag", ["apc-c1m1", "../evil", "</script><script>", "run tag"])
def test_publish_rejects_bad_run_tag_before_any_work(tmp_path: Path, bad_tag: str) -> None:
    with pytest.raises(PickerPublishError, match="(?i)run_tag|malformed"):
        publish_picker(
            run_tag=bad_tag,
            out_dir=tmp_path / "out",
            roster=_roster(),
            ssot_path=_ssot(tmp_path),
            site_repo=str(tmp_path / "origin.git"),
            token="dummy-token",
        )
    # rejected at the TOP: no out dir / receipt was created
    assert not (tmp_path / "out").exists()


# ------------------------------------------------------------ MUST-2 token scrub
def test_publish_error_message_scrubs_token(tmp_path: Path) -> None:
    secret = "ghp_SUPERSECRETTOKEN1234567890"
    # a non-github, non-existent site_repo forces `git clone` to fail (CalledProcessError)
    with pytest.raises(PickerPublishError) as excinfo:
        _git_publish_dir(
            tmp_path,  # nothing to publish; clone fails first regardless
            site_repo="https://github.com/does-not-exist/nope",
            subdir="assets/styleguide-picker/abc12345",
            token=secret,
        )
    msg = str(excinfo.value)
    assert secret not in msg, "the publish token must never appear in the error message"
    assert "***" in msg or "failed" in msg.lower()


# ------------------------------------------------------------ NIT-8 non-PNG skip
def test_publish_skips_non_png_thumbnail_refs(tmp_path: Path) -> None:
    bare = _bare_origin(tmp_path)
    # a file with a .png extension whose bytes are NOT a valid PNG (bad magic)
    corrupt = tmp_path / "corrupt.png"
    corrupt.write_bytes(b"this is not a png")
    roster = _roster()
    roster[0]["thumbnail_ref"] = "corrupt.png"

    record = publish_picker(
        run_tag="abc12345",
        out_dir=tmp_path / "out",
        roster=roster,
        repo_root=tmp_path,
        ssot_path=_ssot(tmp_path),
        site_repo=str(bare),
        token="dummy-token",
        verify=False,  # a bare repo has no live HTTP endpoint to poll
    )
    assert record["thumbnail_count"] == 0, "a corrupt/non-PNG ref must not be copied"
    checkout = tmp_path / "verify"
    _git(["clone", "--branch", "main", str(bare), str(checkout)], cwd=tmp_path)
    subdir = checkout / "assets" / "styleguide-picker" / "abc12345"
    assert not (subdir / "thumbnails" / "alpha-style.png").exists()


# ============================================================ FIX-1 verify-after-push
def _seq_clock(values: list[float]):
    """A deterministic monotonic clock that yields ``values`` then keeps advancing."""
    state = {"i": 0, "last": 0.0}

    def clock() -> float:
        if state["i"] < len(values):
            state["last"] = values[state["i"]]
            state["i"] += 1
        else:
            state["last"] += 1000.0
        return state["last"]

    return clock


def _publish_with_verify(tmp_path: Path, **verify_kwargs):
    bare = _bare_origin(tmp_path)
    return publish_picker(
        run_tag="abc12345",
        out_dir=tmp_path / "out",
        roster=_roster(),
        repo_root=tmp_path,
        ssot_path=_ssot(tmp_path),
        site_repo=str(bare),
        token="dummy-token",
        verify=True,
        sleep=lambda _s: None,
        **verify_kwargs,
    )


def test_publish_verifies_live_url_200(tmp_path: Path) -> None:
    """(a) url checker returns 200 → receipt records verified_live/http_status."""
    record = _publish_with_verify(tmp_path, url_checker=lambda _url: 200)
    assert record["verified_live"] is True
    assert record["http_status"] == 200


def test_publish_url_stays_404_raises_not_live(tmp_path: Path) -> None:
    """(b) url checker never reaches 200 within the timeout → RAISES not-live."""
    with pytest.raises(PickerPublishError, match="(?i)not.live") as excinfo:
        _publish_with_verify(
            tmp_path,
            url_checker=lambda _url: 404,
            verify_timeout=10.0,
            verify_interval=1.0,
            clock=_seq_clock([0.0, 100.0]),
        )
    assert excinfo.value.tag == "picker.publish.not-live"
    assert "404" in str(excinfo.value)


def test_publish_built_per_api_but_url_404_raises(tmp_path: Path) -> None:
    """(c) THE INCIDENT: Pages API says built, but the NEW asset path 404s → RAISES."""
    with pytest.raises(PickerPublishError, match="(?i)not.live") as excinfo:
        _publish_with_verify(
            tmp_path,
            url_checker=lambda _url: 404,
            pages_build_checker=lambda: {"status": "built"},
            verify_timeout=10.0,
            verify_interval=1.0,
            clock=_seq_clock([0.0, 100.0]),
        )
    assert excinfo.value.tag == "picker.publish.not-live"


def test_publish_pages_api_errored_raises_fast(tmp_path: Path) -> None:
    """(d) Pages API status==errored → RAISE immediately surfacing error.message."""
    with pytest.raises(PickerPublishError) as excinfo:
        _publish_with_verify(
            tmp_path,
            url_checker=lambda _url: 200,  # would be 200, but errored gate fires first
            pages_build_checker=lambda: {
                "status": "errored",
                "error": {"message": "Repository has exceeded size limits"},
            },
        )
    assert "Repository has exceeded size limits" in str(excinfo.value)
    assert excinfo.value.tag == "picker.publish.build-errored"


def test_publish_pages_api_403_falls_back_to_url_poll(tmp_path: Path) -> None:
    """(e) Pages API unavailable (403 → None) → fall back to URL-200 poll, no crash."""

    def _forbidden_builds():
        return None  # the default checker returns None on 401/403

    record = _publish_with_verify(
        tmp_path,
        url_checker=lambda _url: 200,
        pages_build_checker=_forbidden_builds,
    )
    assert record["verified_live"] is True


def test_publish_pages_api_exception_does_not_break_publish(tmp_path: Path) -> None:
    """A raising builds checker must never break publishing — degrade to URL poll."""

    def _boom():
        raise RuntimeError("network down")

    record = _publish_with_verify(
        tmp_path,
        url_checker=lambda _url: 200,
        pages_build_checker=_boom,
    )
    assert record["verified_live"] is True


# ============================================================ FIX-2 sanitize pack
@pytest.mark.parametrize(
    "bad_name",
    ["bad:name.png", "ctrl\x01name.png"],
)
def test_filename_issue_flags_pages_killers(bad_name: str) -> None:
    """The pure filename predicate flags colon / control-char names (cross-platform)."""
    assert _filename_issue(bad_name) is not None
    assert _filename_issue("alpha-style.png") is None
    assert _filename_issue("index.html") is None


def test_sanitize_pack_rejects_colon_filename(tmp_path: Path) -> None:
    """A pack containing a ':'-named file must raise bad-filename (legacy Pages killer)."""
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "index.html").write_text("<html></html>", encoding="utf-8")
    try:
        (pack / "bad:name.png").write_bytes(b"x")
    except OSError:
        pytest.skip("OS refuses to create a ':' filename — guard still applies (see helper test)")
    # On NTFS, 'bad:name.png' becomes an Alternate Data Stream and never shows up as a
    # discoverable directory entry, so the pack-level walk cannot see it (and Pages on
    # Linux is where the guard bites). Skip when the entry is not materialized on disk.
    if not any(":" in p.name for p in pack.rglob("*")):
        pytest.skip("':' name not a discoverable dir entry on this FS — guard still applies")
    with pytest.raises(PickerPublishError, match="(?i)colon|filename") as excinfo:
        _sanitize_pack(pack)
    assert excinfo.value.tag == "picker.publish.bad-filename"


def test_sanitize_pack_rejects_symlink(tmp_path: Path) -> None:
    """A symlink in the pack must raise symlink (legacy Pages hard-fails on symlinks)."""
    pack = tmp_path / "pack"
    pack.mkdir()
    real = tmp_path / "real.png"
    real.write_bytes(b"x")
    link = pack / "link.png"
    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("cannot create symlinks on this OS/user — guard still applies")
    with pytest.raises(PickerPublishError, match="(?i)symlink") as excinfo:
        _sanitize_pack(pack)
    assert excinfo.value.tag == "picker.publish.symlink"


def test_sanitize_pack_accepts_clean_pack(tmp_path: Path) -> None:
    """A hyphen-style, symlink-free pack passes sanitation unchanged."""
    pack = tmp_path / "pack"
    (pack / "thumbnails").mkdir(parents=True)
    (pack / "index.html").write_text("<html></html>", encoding="utf-8")
    (pack / "thumbnails" / "alpha-style.png").write_bytes(b"x")
    _sanitize_pack(pack)  # must not raise

"""Publish the styleguide Picker to GitHub Pages as a static interactive page.

The RETURN-PATH twin of ``app.marcus.orchestrator.chooser_publisher``: it builds a
self-contained pack (``index.html`` via :func:`render_picker_static_html` + a
``thumbnails/`` dir of each roster PNG) and pushes it to the public gh-pages site,
so a client opens the URL, picks styleguide(s) + 1-or-2 versions, and copies the
SELECTION CODE back to ``marcus_spoc``.

The clone/copy/commit/push transport, token-scrub, pack-sanitation, and verify-after-
push logic now live in the shared ``app.marcus.orchestrator.gh_pages_publish`` module
(Task 1 consolidation, party greenlight 2026-07-03) — this module is a thin caller
that keeps its own ``PickerPublishError`` family + ``picker.publish.*`` tags. Every
publish now also runs the shared RETENTION prune + SIZE guard so the public site can
never silently grow past the GitHub Pages 1 GB cap.

Fail-loud (``PickerPublishError``) when the publish token is missing or the git
publish fails. Unit tests exercise this against a TEMP BARE repo as origin — the
real public publish is a separate operator-present checkpoint.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

# Shared transport + hygiene (consolidated). Re-exported private names below keep the
# existing test imports (``_git_publish_dir`` / ``_sanitize_pack`` / ``_filename_issue``)
# resolving against this module.
from app.marcus.orchestrator import gh_pages_publish as _ghp
from app.marcus.orchestrator.gh_pages_publish import (
    PagesBuildChecker,
    SizeGuardRefusal,
    UrlChecker,
    _default_pages_build_checker,
    _default_url_checker,
    _filename_issue,  # noqa: F401 — re-exported for test_picker_publisher imports
    _verify_page_live,
    load_hygiene_config,
)
from app.marcus.orchestrator.picker_html_emitter import (
    _RUN_TAG_RE,
    render_picker_static_html,
)
from app.marcus.orchestrator.styleguide_picker import (
    REPO_ROOT,
    PickerError,
    _png_dimensions,
    load_picker_roster,
)
from app.specialists.dispatch_errors import SpecialistDispatchError

SITE_REPO_URL_ENV = "STORYBOARD_SITE_REPO_URL"
TOKEN_ENV_VAR = "GITHUB_PAGES_TOKEN"
DEFAULT_SITE_REPO = "https://github.com/jlenrique/jlenrique.github.io"
PUBLISH_SUBDIR_ROOT = "assets/styleguide-picker"
_PUBLISHER_CONFIG_PATH = REPO_ROOT / "state" / "config" / "storyboard-publisher.yaml"

# Verify-after-push defaults (shared module owns the poll; these mirror its constants).
VERIFY_TIMEOUT_S = _ghp.VERIFY_TIMEOUT_S
VERIFY_INTERVAL_S = _ghp.VERIFY_INTERVAL_S

_TAG_PREFIX = "picker.publish"


class PickerPublishError(SpecialistDispatchError):
    """Recoverable failure publishing the styleguide picker (mirrors the chooser family)."""


@lru_cache(maxsize=1)
def _hygiene_config() -> tuple[Any, Any, Any]:
    """(RetentionConfig|None, SizeGuardConfig, VerifyConfig) from the publisher config."""
    loaded: dict[str, Any] = {}
    if _PUBLISHER_CONFIG_PATH.is_file():
        parsed = yaml.safe_load(_PUBLISHER_CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            loaded = parsed
    return load_hygiene_config(loaded)


def publish_picker(
    *,
    run_tag: str,
    out_dir: str | Path,
    roster: list[dict[str, Any]] | None = None,
    repo_root: Path | None = None,
    ssot_path: str | Path | None = None,
    include_probes: bool = False,
    site_repo: str | None = None,
    token: str | None = None,
    verify: bool = True,
    verify_timeout: float | None = None,
    verify_interval: float = VERIFY_INTERVAL_S,
    url_checker: UrlChecker | None = None,
    pages_build_checker: PagesBuildChecker | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Build the picker pack, push it to gh-pages, VERIFY it is live, and write a receipt.

    ``out_dir`` is where the local pack and the ``picker-publish-{run_tag}.json``
    receipt are written. ``roster`` defaults to the production :func:`load_picker_roster`.
    The publish token is read from the ``token`` arg first, then ``GITHUB_PAGES_TOKEN`` —
    a missing token FAILS LOUD. The push now also runs the shared retention prune + size
    guard (site-wide hygiene). A ``git push`` succeeding does NOT mean the page is live,
    so when ``verify`` is True we poll the NEW asset path for HTTP 200 and RAISE on a dead
    URL. ``verify=False`` is for unit tests against a temp bare repo. The verify seams
    (``url_checker`` / ``pages_build_checker`` / ``sleep`` / ``clock``) are injectable so
    the poll is deterministic in tests.
    """
    # Producer-side run_tag guard (mirrors the emitter's A3): a hyphen mis-splits the
    # decoder, and a '/' or '..' would flow into the publish subdir + the receipt path
    # (traversal). Reject at the TOP, before any dir is created or any code is baked.
    if not _RUN_TAG_RE.match(str(run_tag)):
        raise PickerPublishError(
            f"run_tag {run_tag!r} is malformed (allowed: letters, digits, '_'); a "
            f"hyphen, '/', or '..' here would corrupt the publish path or receipt",
            tag="picker.publish.bad-run-tag",
        )
    root = repo_root if repo_root is not None else REPO_ROOT
    if roster is None:
        roster = load_picker_roster(include_probes=include_probes, ssot_path=ssot_path)
    if not roster:
        raise PickerPublishError(
            "empty roster: nothing to publish", tag="picker.publish.empty-roster"
        )
    resolved_token = (token if token is not None else os.getenv(TOKEN_ENV_VAR, "")).strip()
    if not resolved_token:
        raise PickerPublishError(
            f"{TOKEN_ENV_VAR} is not set; cannot publish the styleguide picker",
            tag="picker.publish.token-missing",
        )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pack = out / "picker-pack"
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True, exist_ok=True)

    # Copy each curated thumbnail into the pack as a same-origin relative asset.
    thumbnails = pack / "thumbnails"
    copied = 0
    for entry in roster:
        ref = entry.get("thumbnail_ref")
        if not ref:
            continue
        # NIT-8: only copy refs that are a VALID .png. A wrong extension or a corrupt/
        # non-PNG file is skipped, never copied as an orphaned asset.
        if not str(ref).lower().endswith(".png"):
            continue
        src = root / str(ref)
        if not src.is_file():
            continue
        try:
            _png_dimensions(src)
        except PickerError:
            continue
        thumbnails.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, thumbnails / f"{entry['name']}.png")
        copied += 1

    html = render_picker_static_html(roster, run_tag=run_tag, repo_root=root)
    (pack / "index.html").write_text(html, encoding="utf-8")

    # Reject a pack that would fast-fail a legacy Pages build (symlinks, ':' / control /
    # non-UTF-8 filenames) BEFORE we ever push it.
    _sanitize_pack(pack)

    site = site_repo or os.getenv(SITE_REPO_URL_ENV) or DEFAULT_SITE_REPO
    subdir = f"{PUBLISH_SUBDIR_ROOT}/{run_tag}"
    publish_url = _git_publish_dir(pack, site_repo=site, subdir=subdir, token=resolved_token)

    # A push that succeeded does NOT prove the page is live — verify or fail loud. The
    # poll timeout comes from config (verify_timeout_s, default 600 s) so a slow-but-
    # successful Pages build is not falsely declared dead; verify_build=false disables.
    _r, _s, verify_cfg = _hygiene_config()
    resolved_timeout = verify_timeout if verify_timeout is not None else verify_cfg.timeout_s
    verified_status: int | None = None
    if verify and verify_cfg.enabled:
        checker = url_checker if url_checker is not None else _default_url_checker
        builds = pages_build_checker
        if builds is None and url_checker is None:
            def builds() -> dict[str, Any] | None:  # type: ignore[misc]
                return _default_pages_build_checker(site, resolved_token)

        verified_status = _verify_page_live(
            publish_url,
            timeout=resolved_timeout,
            interval=verify_interval,
            url_checker=checker,
            pages_build_checker=builds,
            sleep=sleep,
            clock=clock,
            error_cls=PickerPublishError,
            tag_prefix=_TAG_PREFIX,
        )

    record = {
        "label": "styleguide-picker",
        "publish_url": publish_url,
        "run_tag": run_tag,
        "style_count": len(roster),
        "thumbnail_count": copied,
        "verified_live": verified_status == 200,
        "http_status": verified_status,
    }
    (out / f"picker-publish-{run_tag}.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def _git_publish_dir(local_dir: Path, *, site_repo: str, subdir: str, token: str) -> str:
    """Clone the site (main), prune + size-guard, drop the pack, commit + push.

    Thin wrapper over the shared :func:`gh_pages_publish.git_publish_dir`, injecting the
    picker error family + ``picker.publish.*`` tags and the site-wide retention/size
    hygiene loaded from ``storyboard-publisher.yaml``. Public name preserved so callers
    and the existing temp-bare-repo tests import it unchanged.
    """
    retention, size_guard, _verify = _hygiene_config()
    return _ghp.git_publish_dir(
        local_dir,
        site_repo=site_repo,
        subdir=subdir,
        token=token,
        retention=retention,
        size_guard=size_guard,
        error_cls=PickerPublishError,
        tag_prefix=_TAG_PREFIX,
    )


def _sanitize_pack(pack: Path) -> None:
    """Reject a pack that would fast-fail a legacy Pages build (picker-tagged)."""
    _ghp._sanitize_pack(pack, error_cls=PickerPublishError, tag_prefix=_TAG_PREFIX)


__all__ = [
    "DEFAULT_SITE_REPO",
    "PickerPublishError",
    "SizeGuardRefusal",
    "publish_picker",
]

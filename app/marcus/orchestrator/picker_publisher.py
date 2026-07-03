"""Publish the styleguide Picker to GitHub Pages as a static interactive page.

The RETURN-PATH twin of ``app.marcus.orchestrator.chooser_publisher``: it builds a
self-contained pack (``index.html`` via :func:`render_picker_static_html` + a
``thumbnails/`` dir of each roster PNG) and pushes it to the public gh-pages site,
so a client opens the URL, picks styleguide(s) + 1-or-2 versions, and copies the
SELECTION CODE back to ``marcus_spoc``. Mirrors the chooser's env contract
(``STORYBOARD_SITE_REPO_URL`` default ``jlenrique.github.io``,
``GITHUB_PAGES_TOKEN``), clone/copy/commit/push shape, and receipt file.

Fail-loud (``PickerPublishError``) when the publish token is missing or the git
publish fails. Unit tests exercise this against a TEMP BARE repo as origin — the
real public publish is a separate operator-present checkpoint.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

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

# Verify-after-push defaults: GitHub Pages has post-push build lag, so we POLL the
# NEW asset path (not the domain root — a stale build can serve 200 at the root while
# the new path 404s) up to ``VERIFY_TIMEOUT_S`` at ``VERIFY_INTERVAL_S`` cadence.
VERIFY_TIMEOUT_S = 120.0
VERIFY_INTERVAL_S = 8.0

# Type aliases for the injectable verify seams (deterministic in tests).
UrlChecker = Callable[[str], int]
PagesBuildChecker = Callable[[], dict[str, Any] | None]


class PickerPublishError(SpecialistDispatchError):
    """Recoverable failure publishing the styleguide picker (mirrors the chooser family)."""


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
    verify_timeout: float = VERIFY_TIMEOUT_S,
    verify_interval: float = VERIFY_INTERVAL_S,
    url_checker: UrlChecker | None = None,
    pages_build_checker: PagesBuildChecker | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Build the picker pack, push it to gh-pages, VERIFY it is live, and write a receipt.

    ``out_dir`` is where the local pack and the ``picker-publish-{run_tag}.json``
    receipt are written (a run dir or a scratch dir — the picker pre-flight runs
    BEFORE a trial is opened, so it is not tied to a trial run dir). ``roster``
    defaults to the production :func:`load_picker_roster`. The publish token is
    read from the ``token`` arg first, then ``GITHUB_PAGES_TOKEN`` — a missing
    token FAILS LOUD (never a silent no-op).

    A ``git push`` succeeding does NOT mean the page is live: GitHub Pages runs a
    build after the push and can ERROR (e.g. site at capacity), leaving the new
    path 404 while a stale build keeps serving. So when ``verify`` is True we never
    hand back a dead URL — we poll the NEW asset path (``publish_url``) for HTTP 200
    up to ``verify_timeout`` (interval ``verify_interval``) and, if a Pages-API-capable
    token is present, fail fast on an ``errored`` build. A non-live result RAISES
    ``PickerPublishError`` (``picker.publish.not-live``). ``verify=False`` is for unit
    tests against a temp bare repo (no live HTTP endpoint). ``url_checker`` /
    ``pages_build_checker`` / ``sleep`` / ``clock`` are injectable so the poll is
    deterministic in tests; the defaults hit the network only when ``url_checker`` is
    left unset.
    """
    # Producer-side run_tag guard (mirrors the emitter's A3): a hyphen mis-splits
    # the decoder, and a '/' or '..' would flow into the publish subdir + the
    # picker-publish-{run_tag}.json receipt path (traversal). Reject at the TOP,
    # before any dir is created or any code is baked.
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
        # NIT-8: only copy refs that are a VALID .png (mirror the emitter's
        # _png_dimensions magic/IHDR check). A wrong extension or a corrupt/
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

    # FIX-2: reject a pack that would fast-fail a legacy Pages build (symlinks,
    # ':' / control / non-UTF-8 filenames) BEFORE we ever push it.
    _sanitize_pack(pack)

    site = site_repo or os.getenv(SITE_REPO_URL_ENV) or DEFAULT_SITE_REPO
    subdir = f"{PUBLISH_SUBDIR_ROOT}/{run_tag}"
    publish_url = _git_publish_dir(pack, site_repo=site, subdir=subdir, token=resolved_token)

    # FIX-1: a push that succeeded does NOT prove the page is live — verify or fail loud.
    verified_status: int | None = None
    if verify:
        checker = url_checker if url_checker is not None else _default_url_checker
        builds = pages_build_checker
        if builds is None and url_checker is None:
            # Production path: best-effort Pages-builds gate (skipped silently on 401/403).
            def builds() -> dict[str, Any] | None:  # type: ignore[misc]
                return _default_pages_build_checker(site, resolved_token)

        verified_status = _verify_page_live(
            publish_url,
            timeout=verify_timeout,
            interval=verify_interval,
            url_checker=checker,
            pages_build_checker=builds,
            sleep=sleep,
            clock=clock,
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
    """Clone the site repo (main), drop the pack under ``subdir``, commit + push.

    Mirrors ``chooser_publisher._git_publish_dir`` with one tolerance: when
    ``site_repo`` is not a github.com URL (e.g. a temp BARE repo in a unit test),
    the token is not injected and the pages base falls back to the repo path.
    """
    if "github.com/" in site_repo:
        user = site_repo.split("github.com/", 1)[1].split("/", 1)[0]
        pages_base = f"https://{user}.github.io"
        auth_repo = site_repo.replace("https://", f"https://x-access-token:{token}@", 1)
    else:
        pages_base = site_repo.rstrip("/")
        auth_repo = site_repo
    temp_repo = Path(tempfile.mkdtemp(prefix="picker-publish-"))
    try:
        _git(["clone", "--depth", "1", "--branch", "main", auth_repo, str(temp_repo)])
        _git(["config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        _git(["config", "user.email", "app-marcus-bot@users.noreply.github.com"], cwd=temp_repo)
        target = temp_repo / subdir
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(local_dir, target)
        _git(["add", subdir], cwd=temp_repo)
        status = _git(["status", "--short", subdir], cwd=temp_repo)
        if status.strip():
            _git(["commit", "-m", f"Publish styleguide picker {subdir}"], cwd=temp_repo)
            _git(["push", auth_repo, "HEAD:main"], cwd=temp_repo)
        return f"{pages_base}/{subdir}/index.html"
    except subprocess.CalledProcessError as exc:
        # SECURITY: exc.cmd carries `auth_repo` = https://x-access-token:{token}@...
        # and str(exc) would leak the token. Build the message from returncode + a
        # token-scrubbed command/stderr, and drop the token-carrying cause (`from
        # None`) so no traceback frame can leak it either.
        raw_cmd = exc.cmd if isinstance(exc.cmd, (list, tuple)) else [str(exc.cmd)]
        safe_cmd = " ".join(_scrub_token(str(part), token) for part in raw_cmd)
        stderr = _scrub_token((exc.stderr or "").strip(), token)
        detail = f" — {stderr}" if stderr else ""
        raise PickerPublishError(
            f"picker gh-pages publish failed (exit {exc.returncode}): {safe_cmd}{detail}",
            tag="picker.publish.failed",
        ) from None
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)


def _scrub_token(text: str, token: str) -> str:
    """Redact the publish token from any string before it can reach a message/log."""
    if not token:
        return text
    return text.replace(f"x-access-token:{token}@", "x-access-token:***@").replace(
        token, "***"
    )


def _filename_issue(name: str) -> str | None:
    """Return a human reason if ``name`` would fast-fail a legacy Pages build, else None.

    Legacy (Jekyll) GitHub Pages builds hard-fail on a colon in a path, on control
    characters, and on non-UTF-8 byte names. Our slugs are hyphen-style so this is a
    guard that should never fire in practice.
    """
    if ":" in name:
        return "contains a colon ':' (illegal in a GitHub Pages path)"
    if any(ord(ch) < 0x20 for ch in name):
        return "contains control characters"
    try:
        name.encode("utf-8")
    except UnicodeEncodeError:
        return "is not valid UTF-8"
    return None


def _sanitize_pack(pack: Path) -> None:
    """Reject a pack that would fast-fail a legacy GitHub Pages build (FIX-2).

    Symlinks (mode 120000) and ``:`` / control / non-UTF-8 filenames are cheap
    pre-flight killers for the Jekyll build. ``shutil.copyfile`` already dereferences
    sources, but we assert symlink-freedom as defense-in-depth. Raises
    ``PickerPublishError`` naming the offending path; never mutates the pack.
    """
    for path in sorted(pack.rglob("*")):
        if path.is_symlink():
            raise PickerPublishError(
                f"pack contains a symlink (legacy GitHub Pages hard-fails on symlinks): {path}",
                tag="picker.publish.symlink",
            )
        issue = _filename_issue(path.name)
        if issue is not None:
            raise PickerPublishError(
                f"pack filename {path.name!r} {issue}; GitHub Pages build would fast-fail",
                tag="picker.publish.bad-filename",
            )


def _verify_page_live(
    publish_url: str,
    *,
    timeout: float,
    interval: float,
    url_checker: UrlChecker,
    pages_build_checker: PagesBuildChecker | None,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
) -> int:
    """Confirm ``publish_url`` is actually serving HTTP 200; else RAISE (FIX-1).

    Optional stronger gate first: if a Pages-API-capable checker is available and the
    latest build ``status == "errored"``, fail fast surfacing ``error.message`` rather
    than waiting out the poll. Any failure of that best-effort gate (403/401/network)
    is swallowed — it must NEVER break publishing. Primary gate always: poll the NEW
    asset path for HTTP 200 up to ``timeout``. A non-200 final result raises
    ``picker.publish.not-live`` naming the URL + last status.
    """
    if pages_build_checker is not None:
        try:
            build = pages_build_checker()
        except Exception:  # noqa: BLE001 — best-effort; never break publishing
            build = None
        if isinstance(build, dict) and build.get("status") == "errored":
            message = (build.get("error") or {}).get("message") or "Page build failed"
            raise PickerPublishError(
                f"GitHub Pages build ERRORED for {publish_url}: {message}",
                tag="picker.publish.build-errored",
            )

    deadline = clock() + timeout
    last_status: int | None = None
    while True:
        last_status = url_checker(publish_url)
        if last_status == 200:
            return last_status
        if clock() >= deadline:
            break
        sleep(interval)

    raise PickerPublishError(
        f"picker page is NOT live: {publish_url} returned HTTP {last_status} after "
        f"~{timeout:.0f}s of polling (push succeeded but the Pages build did not serve "
        f"the new path); refusing to hand back a dead URL",
        tag="picker.publish.not-live",
    )


def _default_url_checker(url: str) -> int:
    """Real HTTP GET of ``url`` returning the status code (0 on a non-HTTP failure)."""
    try:
        req = urllib.request.Request(url, method="GET")  # noqa: S310 — https gh-pages URL
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except Exception:  # noqa: BLE001 — DNS/timeout/connection → treat as not-yet-live
        return 0


def _default_pages_build_checker(site_repo: str, token: str) -> dict[str, Any] | None:
    """Best-effort GET of the latest Pages build; None when unavailable (401/403/non-gh).

    A fine-grained PAT with only ``Contents: write`` (the common publish token) lacks
    ``Pages: read`` and gets 403 here — that is EXPECTED and returns None so the caller
    falls back to the URL-200 poll. Never raises.
    """
    if "github.com/" not in site_repo:
        return None
    tail = site_repo.split("github.com/", 1)[1]
    owner, _, repo = tail.partition("/")
    repo = repo.rstrip("/").removesuffix(".git")
    if not owner or not repo:
        return None
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pages/builds/latest"
    try:
        req = urllib.request.Request(  # noqa: S310 — fixed https api.github.com URL
            api_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 — 401/403/404/network all mean "gate unavailable"
        return None


def _git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, timeout=180
    )
    return result.stdout


__all__ = [
    "DEFAULT_SITE_REPO",
    "PickerPublishError",
    "publish_picker",
]

"""Shared gh-pages publish helper: transport + auto hygiene (retention, size, verify).

Consolidates the clone -> stage -> commit -> push transport that picker/chooser
each carried a near-identical copy of, and — the point of this module — weaves in
three FAIL-LOUD hygiene guards so the public asset-host repo can never again grow
silently past the GitHub Pages 1 GB published-site cap and freeze the last build
while new paths 404 (the 2026-07-03 incident):

* ``prune_retention`` — delete managed packs older than ``max_age_days`` (by their
  git COMMITTER date), honoring a protected allowlist, and NEVER the pack being
  published this run.
* ``project_published_size`` — the size guard: sum the checked-out working tree
  (what the Pages *published-site* cap measures) and RAISE ``SizeGuardRefusal``
  before pushing if it would breach the fail threshold.
* ``verify_build_after_push`` / ``_verify_page_live`` — after push, confirm the new
  path actually serves HTTP 200 (a ``git push`` succeeding does NOT mean the page
  is live); fail loud on a dead URL or an ``errored`` Pages build.

DESIGN (party greenlight 2026-07-03, RA1/RA2):
- The three hygiene primitives are AUTH-AGNOSTIC and COPY-AGNOSTIC: they operate on
  a local clone directory + managed-path descriptors and never touch remote URLs or
  credentials. That is what lets gamma (base64-Basic extraheader auth, per-file copy
  + url_map) and the legacy storyboard generator adopt them (Task 1b) around their
  own transport without a rewrite.
- The high-level ``git_publish_dir`` transport is the copytree-of-a-pack shape used
  by picker + chooser only. It takes ``error_cls`` + ``tag_prefix`` so each caller
  keeps its own error family and tags (behavior-preservation for AC7).
- Size is measured by a FILESYSTEM WALK of the checked-out post-prune tree — NOT
  ``git count-objects``/pack size (empirically does not shrink on a retention prune,
  because history retains deleted blobs) and NOT ``cat-file``/``ls-tree -l`` on blob
  OIDs (on a ``--filter=blob:none`` clone that triggers a promisor lazy-refetch).
- The clone is ``--filter=blob:none`` WITH checkout, full history: retention needs
  per-pack commit dates (``--depth 1`` cannot give them), blobless skips downloading
  old blobs, and the checkout materializes the current tree so the walk is cheap.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Collection
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError

# Verify-after-push defaults: GitHub Pages has post-push build lag, so we POLL the
# NEW asset path (not the domain root — a stale build can serve 200 at the root while
# the new path 404s) up to ``VERIFY_TIMEOUT_S`` at ``VERIFY_INTERVAL_S`` cadence.
VERIFY_TIMEOUT_S = 120.0
VERIFY_INTERVAL_S = 8.0

# Hygiene defaults (mirrors spec §4.6 / config block in storyboard-publisher.yaml).
DEFAULT_RETENTION_DAYS = 10
DEFAULT_SIZE_WARN_MB = 750
DEFAULT_SIZE_FAIL_MB = 900
_MB = 1024 * 1024

# Type aliases for the injectable verify seams (deterministic in tests).
UrlChecker = Callable[[str], int]
PagesBuildChecker = Callable[[], "dict[str, Any] | None"]
GitRunner = Callable[..., str]


class GhPagesPublishError(SpecialistDispatchError):
    """Base recoverable failure publishing to the gh-pages site."""


class SizeGuardRefusal(GhPagesPublishError):  # noqa: N818 — party-ratified name (RA1/RA5); it IS an error (subclasses GhPagesPublishError)
    """The projected published tree would breach the size fail threshold — refuse to push."""


# ─────────────────────────────────────────────────────────── config value objects
@dataclass(frozen=True)
class RetentionConfig:
    """Which roots are managed, how old is too old, and what is never deleted."""

    managed_roots: tuple[str, ...]
    protected_paths: frozenset[str] = frozenset()
    max_age_days: int = DEFAULT_RETENTION_DAYS


@dataclass(frozen=True)
class SizeGuardConfig:
    warn_at_mb: int = DEFAULT_SIZE_WARN_MB
    fail_at_mb: int = DEFAULT_SIZE_FAIL_MB


@dataclass(frozen=True)
class VerifyConfig:
    """Verify-after-push policy (config-driven; the operator set 600s to match the
    legacy 10-min Pages deploy cap so a slow-but-successful build is not falsely
    declared dead)."""

    enabled: bool = True
    timeout_s: float = VERIFY_TIMEOUT_S


@dataclass(frozen=True)
class PrunedPack:
    path: str
    size_bytes: int


@dataclass
class PruneReport:
    """What a retention pass would delete / kept, with reclaimable bytes."""

    deleted: list[PrunedPack] = field(default_factory=list)
    skipped_protected: list[str] = field(default_factory=list)
    skipped_current: list[str] = field(default_factory=list)
    skipped_unknown_age: list[str] = field(default_factory=list)

    @property
    def reclaim_bytes(self) -> int:
        return sum(p.size_bytes for p in self.deleted)


@dataclass(frozen=True)
class SizeReport:
    total_bytes: int
    warned: bool

    @property
    def total_mb(self) -> float:
        return self.total_bytes / _MB


# ──────────────────────────────────────────────────────────────── low-level git
def _git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, timeout=180
    )
    return result.stdout


def _scrub_token(text: str, token: str) -> str:
    """Redact the publish token from any string before it can reach a message/log."""
    if not token:
        return text
    return text.replace(f"x-access-token:{token}@", "x-access-token:***@").replace(
        token, "***"
    )


# ─────────────────────────────────────────────────────── pack sanitation (legacy Pages)
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


def _sanitize_pack(
    pack: Path,
    *,
    error_cls: type[GhPagesPublishError] = GhPagesPublishError,
    tag_prefix: str = "gh-pages.publish",
) -> None:
    """Reject a pack that would fast-fail a legacy GitHub Pages build.

    Symlinks (mode 120000) and ``:`` / control / non-UTF-8 filenames are cheap
    pre-flight killers for the Jekyll build. Raises ``error_cls`` naming the offending
    path; never mutates the pack.
    """
    for path in sorted(pack.rglob("*")):
        if path.is_symlink():
            raise error_cls(
                f"pack contains a symlink (legacy GitHub Pages hard-fails on symlinks): {path}",
                tag=f"{tag_prefix}.symlink",
            )
        issue = _filename_issue(path.name)
        if issue is not None:
            raise error_cls(
                f"pack filename {path.name!r} {issue}; GitHub Pages build would fast-fail",
                tag=f"{tag_prefix}.bad-filename",
            )


# ───────────────────────────────────────────────────────────── G1 retention prune
def _dir_size_bytes(path: Path) -> int:
    """Sum the byte size of every regular file under ``path`` (a filesystem walk)."""
    total = 0
    for child in path.rglob("*"):
        if child.is_file() and not child.is_symlink():
            try:
                total += child.stat().st_size
            except OSError:
                continue
    return total


def _pack_commit_epoch(clone_dir: Path, rel: str, git: GitRunner) -> int | None:
    """Committer epoch (``%ct``) of the last commit touching ``rel``; None if unknown.

    ``%ct`` is timezone-agnostic integer seconds computed from the commit object — it
    works on a blobless clone (no blob access needed) and needs no locale/tz string
    parsing (RA3). A path with no commit history (never committed / untracked) returns
    None so the caller treats its age as UNKNOWN and refuses to delete it.
    """
    out = git(["log", "-1", "--format=%ct", "--", rel], cwd=clone_dir).strip()
    if not out:
        return None
    try:
        return int(out.splitlines()[0])
    except (ValueError, IndexError):
        return None


def _is_protected(rel: str, protected_paths: Collection[str]) -> bool:
    """Exact-path or ancestor-dir match (RA7d): ``foo`` never protects ``foo-2``."""
    rel_norm = rel.strip("/")
    for entry in protected_paths:
        e = str(entry).strip("/")
        if not e:
            continue
        if rel_norm == e or rel_norm.startswith(e + "/") or e.startswith(rel_norm + "/"):
            return True
    return False


def prune_retention(
    clone_dir: Path,
    *,
    config: RetentionConfig,
    now: float | None = None,
    current_subdir: str | None = None,
    dry_run: bool = False,
    git: GitRunner = _git,
    logger: Callable[[str], None] | None = None,
) -> PruneReport:
    """Delete managed packs older than ``max_age_days`` by committer date.

    Operates purely on ``clone_dir`` (a checked-out clone) — auth-agnostic and
    copy-agnostic, so any transport can call it. For each managed root, each IMMEDIATE
    CHILD DIRECTORY is a "pack" (loose files and deeper nesting are ignored, RA7e). A
    pack is skipped when: it is the pack being published this run — OR an ANCESTOR of it
    (``current_subdir``, by IDENTITY not date — highest-severity safety, RA7a; protecting
    ancestors stops a nested publish like ``mod/part1`` from pruning the ``mod`` pack and
    destroying sibling ``mod/part2``); it matches the protected
    allowlist (RA7d); or its age is UNKNOWN (no commit history). Age uses ``%ct`` epoch
    vs ``now`` (UTC ``time.time()``); deletion is STRICTLY ``> max_age_days`` so a pack
    exactly at the boundary survives (RA7b). A missing/empty managed root is a benign
    no-op (RA7c). When ``dry_run`` nothing is staged; otherwise deletes are ``git rm``
    -staged for the caller's single publish commit.
    """
    now = time.time() if now is None else now
    log = logger or (lambda _m: None)
    report = PruneReport()
    max_age_seconds = config.max_age_days * 86400
    current_norm = current_subdir.strip("/") if current_subdir else None

    for root in config.managed_roots:
        root_dir = clone_dir / root
        if not root_dir.is_dir():
            log(f"retention: managed root {root!r} absent from clone — skipping (no-op)")
            continue
        for child in sorted(root_dir.iterdir()):
            if not child.is_dir() or child.is_symlink():
                continue  # loose non-pack file, or a symlink-to-dir (never a real pack; RA7e/S1)
            rel = f"{root}/{child.name}"
            rel_norm = rel.strip("/")
            if current_norm is not None and (
                rel_norm == current_norm or current_norm.startswith(rel_norm + "/")
            ):
                report.skipped_current.append(rel)
                continue
            if _is_protected(rel, config.protected_paths):
                report.skipped_protected.append(rel)
                continue
            epoch = _pack_commit_epoch(clone_dir, rel, git)
            if epoch is None:
                report.skipped_unknown_age.append(rel)
                log(f"retention: {rel!r} has no commit date — refusing to delete (unknown age)")
                continue
            age_seconds = now - epoch
            if age_seconds > max_age_seconds:
                size = _dir_size_bytes(child)
                report.deleted.append(PrunedPack(path=rel, size_bytes=size))
                if not dry_run:
                    git(["rm", "-qr", "--", rel], cwd=clone_dir)
    if report.deleted:
        verb = "would delete" if dry_run else "deleted"
        log(
            f"retention: {verb} {len(report.deleted)} pack(s) "
            f"(~{report.reclaim_bytes / _MB:.1f} MB); "
            f"kept {len(report.skipped_protected)} protected, "
            f"{len(report.skipped_current)} current-run, "
            f"{len(report.skipped_unknown_age)} unknown-age"
        )
    return report


# ─────────────────────────────────────────────────────────────── G2 size guard
def project_published_size(
    tree_dir: Path,
    *,
    config: SizeGuardConfig | None = None,
    logger: Callable[[str], None] | None = None,
) -> SizeReport:
    """Sum the checked-out working tree (excluding ``.git``) and enforce the guard.

    This is the PUBLISHED-SITE size the GitHub Pages 1 GB cap actually measures — a
    filesystem walk of the materialized tree AFTER retention deletes and AFTER the new
    pack is copied in, so it reflects exactly what the next Pages build will serve.
    RAISES ``SizeGuardRefusal`` (fail-loud, no push) above ``fail_at_mb``; a loud WARN
    above ``warn_at_mb``; returns the ``SizeReport`` otherwise. (RA2/RA5.)
    """
    config = config or SizeGuardConfig()
    log = logger or (lambda _m: None)
    total = 0
    # os.walk (not rglob) so we PRUNE .git from the traversal instead of walking every
    # git object and discarding it — on the real ~456 MB clone that halves the walk.
    for dirpath, dirnames, filenames in os.walk(tree_dir):
        dirnames[:] = [d for d in dirnames if d != ".git"]  # .git never served by Pages
        for name in filenames:
            fpath = Path(dirpath) / name
            if fpath.is_symlink():
                continue
            try:
                total += fpath.stat().st_size
            except OSError as exc:
                # S2: fail-loud never silent — an unreadable file could pull an over-cap
                # tree under the threshold. WARN loudly rather than silently undercount.
                log(f"size guard WARN: could not stat {fpath} ({exc}); excluded from total")
    total_mb = total / _MB
    if total > config.fail_at_mb * _MB:
        raise SizeGuardRefusal(
            f"projected published assets ≈{total_mb:.0f} MB — over the {config.fail_at_mb} MB "
            f"guard; prune or migrate before publishing (refusing to push a build that would "
            f"breach the GitHub Pages 1 GB cap)",
            tag="gh-pages.publish.size-guard",
        )
    warned = total > config.warn_at_mb * _MB
    if warned:
        log(
            f"size guard WARN: projected published assets ≈{total_mb:.0f} MB — over the "
            f"{config.warn_at_mb} MB warn line (fail at {config.fail_at_mb} MB)"
        )
    return SizeReport(total_bytes=total, warned=warned)


# ──────────────────────────────────────────────────────────── G3 verify after push
def _verify_page_live(
    publish_url: str,
    *,
    timeout: float,
    interval: float,
    url_checker: UrlChecker,
    pages_build_checker: PagesBuildChecker | None,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
    error_cls: type[GhPagesPublishError] = GhPagesPublishError,
    tag_prefix: str = "gh-pages.publish",
) -> int:
    """Confirm ``publish_url`` is actually serving HTTP 200; else RAISE.

    Optional stronger gate first: if a Pages-API-capable checker is available and the
    latest build ``status == "errored"``, fail fast surfacing ``error.message`` rather
    than waiting out the poll. Any failure of that best-effort gate (403/401/network)
    is swallowed — it must NEVER break publishing. Primary gate always: poll the NEW
    asset path for HTTP 200 up to ``timeout``. A non-200 final result raises.
    """
    if pages_build_checker is not None:
        try:
            build = pages_build_checker()
        except Exception:  # noqa: BLE001 — best-effort; never break publishing
            build = None
        if isinstance(build, dict) and build.get("status") == "errored":
            message = (build.get("error") or {}).get("message") or "Page build failed"
            raise error_cls(
                f"GitHub Pages build ERRORED for {publish_url}: {message}",
                tag=f"{tag_prefix}.build-errored",
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

    raise error_cls(
        f"published page is NOT live: {publish_url} returned HTTP {last_status} after "
        f"~{timeout:.0f}s of polling (push succeeded but the Pages build did not serve "
        f"the new path); refusing to hand back a dead URL",
        tag=f"{tag_prefix}.not-live",
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


def _repo_slug(site_repo: str) -> tuple[str, str] | None:
    """(owner, repo) from a github.com URL; None for a non-github (temp bare) repo."""
    if "github.com/" not in site_repo:
        return None
    tail = site_repo.split("github.com/", 1)[1]
    owner, _, repo = tail.partition("/")
    repo = repo.rstrip("/").removesuffix(".git")
    if not owner or not repo:
        return None
    return owner, repo


def _default_pages_build_checker(site_repo: str, token: str) -> dict[str, Any] | None:
    """Best-effort GET of the latest Pages build via httpx; None when unavailable.

    Migrated to the shipped ``httpx`` dependency (RA6) — no ``curl``, no operator CLI.
    A fine-grained PAT with only ``Contents: write`` (the common publish token) lacks
    ``Pages: read`` and gets 403 here — EXPECTED, returns None so the caller falls back
    to the URL-200 poll. Never raises.
    """
    slug = _repo_slug(site_repo)
    if slug is None:
        return None
    owner, repo = slug
    try:
        import httpx

        resp = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}/pages/builds/latest",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=15,
        )
        return _map_pages_build_response(resp.status_code, resp.json)
    except Exception:  # noqa: BLE001 — 401/403/404/network all mean "gate unavailable"
        return None


def _map_pages_build_response(
    status_code: int, json_body: Callable[[], Any] | Any
) -> dict[str, Any] | None:
    """Map a Pages-builds HTTP response to the small verify contract (adapter seam).

    Extracted so the ONE httpx-transport test (RA6) can assert the mapping in isolation
    without touching the poll loop: 200 -> the parsed build dict; anything else -> None
    (gate unavailable → caller degrades to the URL poll). ``json_body`` may be a
    callable (httpx ``resp.json``) or an already-decoded value.
    """
    if status_code != 200:
        return None
    body = json_body() if callable(json_body) else json_body
    return body if isinstance(body, dict) else None


def verify_build_after_push(
    publish_url: str,
    *,
    site_repo: str,
    token: str | None,
    timeout: float = VERIFY_TIMEOUT_S,
    interval: float = VERIFY_INTERVAL_S,
    url_checker: UrlChecker | None = None,
    pages_build_checker: PagesBuildChecker | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    error_cls: type[GhPagesPublishError] = GhPagesPublishError,
    tag_prefix: str = "gh-pages.publish",
) -> int:
    """Public primitive (Task 1b consumers): verify a pushed URL is live or fail loud.

    Thin wrapper over :func:`_verify_page_live` that wires the production default
    checkers when the injectable seams are left unset.
    """
    checker = url_checker if url_checker is not None else _default_url_checker
    builds = pages_build_checker
    if builds is None and url_checker is None and token:
        def builds() -> dict[str, Any] | None:  # type: ignore[misc]
            return _default_pages_build_checker(site_repo, token)

    return _verify_page_live(
        publish_url,
        timeout=timeout,
        interval=interval,
        url_checker=checker,
        pages_build_checker=builds,
        sleep=sleep,
        clock=clock,
        error_cls=error_cls,
        tag_prefix=tag_prefix,
    )


# ────────────────────────────────────────────────────────── high-level transport
def _pages_base_and_auth(site_repo: str, token: str) -> tuple[str, str]:
    """(pages_base_url, auth_clone_url). Non-github (temp bare) repos: no token inject."""
    if "github.com/" in site_repo:
        user = site_repo.split("github.com/", 1)[1].split("/", 1)[0]
        return f"https://{user}.github.io", site_repo.replace(
            "https://", f"https://x-access-token:{token}@", 1
        )
    return site_repo.rstrip("/"), site_repo


def git_publish_dir(
    local_dir: Path,
    *,
    site_repo: str,
    subdir: str,
    token: str,
    branch: str = "main",
    retention: RetentionConfig | None = None,
    size_guard: SizeGuardConfig | None = None,
    now: float | None = None,
    error_cls: type[GhPagesPublishError] = GhPagesPublishError,
    tag_prefix: str = "gh-pages.publish",
    logger: Callable[[str], None] | None = None,
    git: GitRunner = _git,
) -> str:
    """Clone the site, prune + size-guard, drop the pack under ``subdir``, commit + push.

    The consolidated picker/chooser transport. Clone is ``--filter=blob:none`` with
    checkout + full history (retention needs commit dates; blobless skips old blobs).
    When ``retention``/``size_guard`` are supplied the hygiene guards run inside the
    clone before push — retention deletes are committed TOGETHER with the new pack in
    one push, and the size guard RAISES before any push if the projected tree breaches
    the fail threshold. Returns the public ``.../index.html`` URL. On a non-github
    ``site_repo`` (temp bare repo in tests) the token is not injected and the Pages
    base falls back to the repo path.
    """
    # Defense-in-depth for EVERY caller (the picker validates its run_tag, but the
    # chooser/gamma/storyboard subdirs are built from ids that could carry '..' or '/'):
    # a traversal segment would let copytree escape the clone (Blind-NIT5).
    segments = [s for s in subdir.replace("\\", "/").split("/") if s]
    if not segments or any(s in {".", ".."} for s in segments) or subdir.startswith("/"):
        raise error_cls(
            f"refusing to publish to unsafe subdir {subdir!r} (empty, absolute, or "
            f"contains a traversal segment)",
            tag=f"{tag_prefix}.bad-subdir",
        )
    pages_base, auth_repo = _pages_base_and_auth(site_repo, token)
    temp_repo = Path(tempfile.mkdtemp(prefix="gh-pages-publish-"))
    try:
        git(
            ["clone", "--filter=blob:none", "--branch", branch, auth_repo, str(temp_repo)],
        )
        git(["config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        git(
            ["config", "user.email", "app-marcus-bot@users.noreply.github.com"],
            cwd=temp_repo,
        )

        # G1 — retention prune (staged; the current pack is protected by identity).
        if retention is not None:
            prune_retention(
                temp_repo,
                config=retention,
                now=now,
                current_subdir=subdir,
                git=git,
                logger=logger,
            )

        target = temp_repo / subdir
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(local_dir, target)
        git(["add", "--", subdir], cwd=temp_repo)

        # G2 — size guard on the projected tree (post-prune + new pack). Fail-loud.
        if size_guard is not None:
            project_published_size(temp_repo, config=size_guard, logger=logger)

        status = git(["status", "--short"], cwd=temp_repo)
        if status.strip():
            git(["commit", "-m", f"Publish {subdir}"], cwd=temp_repo)
            git(["push", auth_repo, f"HEAD:{branch}"], cwd=temp_repo)
        return f"{pages_base}/{subdir}/index.html"
    except SizeGuardRefusal:
        raise
    except subprocess.CalledProcessError as exc:
        # SECURITY: exc.cmd carries `auth_repo` = https://x-access-token:{token}@...
        # Build the message from returncode + a token-scrubbed command/stderr, and drop
        # the token-carrying cause (`from None`) so no traceback frame can leak it.
        raw_cmd = exc.cmd if isinstance(exc.cmd, (list, tuple)) else [str(exc.cmd)]
        safe_cmd = " ".join(_scrub_token(str(part), token) for part in raw_cmd)
        stderr = _scrub_token((exc.stderr or "").strip(), token)
        detail = f" — {stderr}" if stderr else ""
        raise error_cls(
            f"gh-pages publish failed (exit {exc.returncode}): {safe_cmd}{detail}",
            tag=f"{tag_prefix}.failed",
        ) from None
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)


def load_hygiene_config(
    publisher_config: dict[str, Any] | None,
) -> tuple[RetentionConfig | None, SizeGuardConfig, VerifyConfig]:
    """Build (RetentionConfig, SizeGuardConfig, VerifyConfig) from a publisher-config dict.

    Retention is None (disabled) when the config declares no ``managed_roots``; the size
    guard always applies with defaults so every consolidated publish is protected. The
    verify config threads the operator's ``verify_build`` / ``verify_timeout_s`` keys (the
    600 s value matches the legacy 10-min Pages deploy cap — a hardcoded 120 s would
    falsely declare a slow-but-successful build dead).
    """
    cfg = publisher_config or {}
    roots = tuple(str(r) for r in (cfg.get("managed_roots") or ()))
    retention = (
        RetentionConfig(
            managed_roots=roots,
            protected_paths=frozenset(str(p) for p in (cfg.get("protected_paths") or ())),
            max_age_days=int(cfg.get("retention_days", DEFAULT_RETENTION_DAYS)),
        )
        if roots
        else None
    )
    size = SizeGuardConfig(
        warn_at_mb=int(cfg.get("size_warn_mb", DEFAULT_SIZE_WARN_MB)),
        fail_at_mb=int(cfg.get("size_fail_mb", DEFAULT_SIZE_FAIL_MB)),
    )
    verify = VerifyConfig(
        enabled=bool(cfg.get("verify_build", True)),
        timeout_s=float(cfg.get("verify_timeout_s", VERIFY_TIMEOUT_S)),
    )
    return retention, size, verify


__all__ = [
    "GhPagesPublishError",
    "SizeGuardRefusal",
    "RetentionConfig",
    "SizeGuardConfig",
    "VerifyConfig",
    "PruneReport",
    "PrunedPack",
    "SizeReport",
    "prune_retention",
    "project_published_size",
    "verify_build_after_push",
    "git_publish_dir",
    "load_hygiene_config",
]

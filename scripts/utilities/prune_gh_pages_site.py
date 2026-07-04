#!/usr/bin/env python
"""Standalone retention prune for the public gh-pages asset-host site (G5).

Decoupled from a publish: clone the site, delete managed packs older than
``--retention-days`` (by git committer date), and — only with ``--yes`` — commit +
push the deletions. Reuses the SAME ``prune_retention`` primitive the publishers run
inline (single source of truth) so a scheduled/manual cleanup and an on-publish prune
can never diverge. ``--dry-run`` (the DEFAULT) prints the deletion set + reclaim MB and
pushes NOTHING, so the operator can rehearse before anything is deleted.

Config (managed_roots, protected_paths, retention_days, site_repo_url, site_branch,
token_env_var) is read from ``state/config/storyboard-publisher.yaml``; the token comes
from the env var named there (default ``GITHUB_PAGES_TOKEN``).

Examples:
    python scripts/utilities/prune_gh_pages_site.py                # dry-run, prints plan
    python scripts/utilities/prune_gh_pages_site.py --yes          # actually prune + push
    python scripts/utilities/prune_gh_pages_site.py --retention-days 30 --dry-run
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.marcus.orchestrator.gh_pages_publish import (  # noqa: E402
    DEFAULT_RETENTION_DAYS,
    RetentionConfig,
    _git,
    _pages_base_and_auth,
    _scrub_token,
    prune_retention,
)

CONFIG_PATH = REPO_ROOT / "state" / "config" / "storyboard-publisher.yaml"
_MB = 1024 * 1024


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise SystemExit(f"publisher config missing at {CONFIG_PATH}")
    parsed = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict) or not parsed.get("site_repo_url"):
        raise SystemExit(f"publisher config at {CONFIG_PATH} lacks site_repo_url")
    return parsed


def main(argv: list[str] | None = None) -> int:
    cfg = _load_config()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--retention-days",
        type=int,
        default=int(cfg.get("retention_days", DEFAULT_RETENTION_DAYS)),
        help="delete managed packs older than this many days (by committer date)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="print the deletion plan + reclaim MB and push nothing (DEFAULT)",
    )
    group.add_argument(
        "--yes",
        dest="dry_run",
        action="store_false",
        help="actually delete, commit, and push the prune",
    )
    args = parser.parse_args(argv)

    managed_roots = tuple(str(r) for r in (cfg.get("managed_roots") or ()))
    if not managed_roots:
        print("no managed_roots configured — nothing to prune")
        return 0
    retention = RetentionConfig(
        managed_roots=managed_roots,
        protected_paths=frozenset(str(p) for p in (cfg.get("protected_paths") or ())),
        max_age_days=args.retention_days,
    )
    site_repo = os.getenv("STORYBOARD_SITE_REPO_URL") or str(cfg["site_repo_url"])
    branch = str(cfg.get("site_branch") or "main")
    token_env = str(cfg.get("token_env_var") or "GITHUB_PAGES_TOKEN")
    token = os.getenv(token_env, "").strip()
    if not token:
        raise SystemExit(f"{token_env} is not set; cannot access the gh-pages site")

    _pages_base, auth_repo = _pages_base_and_auth(site_repo, token)
    temp_repo = Path(tempfile.mkdtemp(prefix="prune-gh-pages-"))
    try:
        _git(["clone", "--filter=blob:none", "--branch", branch, auth_repo, str(temp_repo)])
        _git(["config", "user.name", "app-marcus-bot"], cwd=temp_repo)
        _git(
            ["config", "user.email", "app-marcus-bot@users.noreply.github.com"],
            cwd=temp_repo,
        )
        report = prune_retention(
            temp_repo,
            config=retention,
            now=time.time(),
            dry_run=args.dry_run,
            logger=print,
        )
        mode = "DRY-RUN (no push)" if args.dry_run else "APPLIED"
        print(f"\n=== gh-pages prune {mode} — retention {args.retention_days}d ===")
        if not report.deleted:
            print("nothing to prune — site is within retention.")
            return 0
        for pack in report.deleted:
            print(f"  delete  {pack.path}  (~{pack.size_bytes / _MB:.1f} MB)")
        print(f"  reclaim total ≈ {report.reclaim_bytes / _MB:.1f} MB")
        if report.skipped_protected:
            print(f"  kept (allowlist): {len(report.skipped_protected)}")
        if args.dry_run:
            print("\n(dry-run) re-run with --yes to commit + push these deletions.")
            return 0
        msg = f"Prune gh-pages packs older than {args.retention_days}d"
        _git(["commit", "-m", msg], cwd=temp_repo)
        _git(["push", auth_repo, f"HEAD:{branch}"], cwd=temp_repo)
        print("\npushed prune to origin.")
        return 0
    except subprocess.CalledProcessError as exc:
        safe = _scrub_token(str(exc), token)
        raise SystemExit(f"gh-pages prune git op failed: {safe}") from None
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

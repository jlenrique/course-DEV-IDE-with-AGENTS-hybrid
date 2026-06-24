"""Fetch enabled Descript doc URLs into references/cache/ (stdlib only)."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = "DesmondDocRefresh/1.0 (+local cache; APP pipeline)"


def _slugify(url: str) -> str:
    slug = re.sub(r"[^\w]+", "-", url.lower()).strip("-")
    return slug[:120] if len(slug) > 120 else slug


def load_registry(skill_root: Path) -> dict:
    reg = skill_root / "references" / "descript-doc-registry.json"
    return json.loads(reg.read_text(encoding="utf-8"))


def fetch_url(url: str, timeout: float = 30.0) -> tuple[int, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        code = getattr(resp, "status", 200)
        body = resp.read()
    return int(code), body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh local Descript doc cache.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List enabled sources without fetching.",
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=None,
        help="Override skill root (default: beside this script).",
    )
    args = parser.parse_args(argv)

    skill_root = args.skill_root or Path(__file__).resolve().parents[1]
    cache_dir = skill_root / "references" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    data = load_registry(skill_root)
    sources = data.get("sources", [])
    enabled = [s for s in sources if s.get("enabled")]

    if not enabled:
        print("No enabled sources in descript-doc-registry.json.")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary: list[str] = []
    had_failure = False

    for src in enabled:
        sid = src.get("id") or _slugify(str(src.get("url", "unknown")))
        url = src.get("url")
        if not url:
            print(f"SKIP {sid}: missing url")
            continue
        out_path = cache_dir / f"{sid}.snapshot.txt"
        if args.dry_run:
            print(f"DRY-RUN would fetch {sid} -> {out_path}")
            continue
        try:
            code, body = fetch_url(url)
        except HTTPError as e:
            had_failure = True
            summary.append(f"{sid}: HTTP {e.code} {url}")
            continue
        except URLError as e:
            had_failure = True
            summary.append(f"{sid}: URL error {e.reason} {url}")
            continue

        text = body.decode("utf-8", errors="replace")
        header = (
            f"---\n"
            f"fetched_at: {stamp}\n"
            f"source_id: {sid}\n"
            f"url: {url}\n"
            f"http_status: {code}\n"
            f"---\n\n"
        )
        out_path.write_text(header + text[:2_000_000], encoding="utf-8")
        summary.append(f"{sid}: OK {code} bytes={len(body)} -> {out_path.name}")

    for line in summary:
        print(line)
    return 1 if had_failure else 0


if __name__ == "__main__":
    import sys as _sys

    raise SystemExit(main(_sys.argv[1:]))

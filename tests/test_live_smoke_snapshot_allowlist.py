from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "live_smoke_snapshot.json"
LIVE_TESTS_DIR = REPO_ROOT / "tests" / "live"
URL_PATTERN = re.compile(r"https://[^\"')\s]+")


def test_live_smoke_raw_urls_are_allowlisted() -> None:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    allowlist = set(snapshot["endpoints"])
    findings: list[str] = []

    for path in LIVE_TESTS_DIR.glob("test_*_smoke.py"):
        content = path.read_text(encoding="utf-8")
        for url in sorted(set(URL_PATTERN.findall(content))):
            if url not in allowlist:
                rel = path.relative_to(REPO_ROOT).as_posix()
                findings.append(f"{rel}: {url}")

    assert not findings, (
        "Live smoke tests named endpoint URLs not present in "
        f"{SNAPSHOT_PATH.relative_to(REPO_ROOT).as_posix()}:\n"
        + "\n".join(findings)
    )

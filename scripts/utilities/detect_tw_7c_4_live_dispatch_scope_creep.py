"""Detect TW-7c-4 live-dispatch scope creep."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ALLOWED_LIVE_DISPATCH_FILES = {
    "run_cache_hit_harness.py",
    "run_5_api_smoke.py",
}
SCANNED_PREFIXES = ("app/specialists/", "app/gates/")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines()]


def detect_scope_creep(root: Path) -> list[str]:
    violations: list[str] = []
    for rel_path in _tracked_files(root):
        if "live_dispatch" in rel_path and Path(rel_path).name not in ALLOWED_LIVE_DISPATCH_FILES:
            violations.append(f"live_dispatch keyword in unexpected file path: {rel_path}")
        if not rel_path.endswith(".py") or not rel_path.startswith(SCANNED_PREFIXES):
            continue
        text = (root / rel_path).read_text(encoding="utf-8")
        if re.search(r"^\s*(from|import)\s+app\.live_dispatch\b", text, re.MULTILINE):
            violations.append(f"live-dispatch import in reserved module: {rel_path}")
    return violations


def main() -> int:
    violations = detect_scope_creep(_repo_root())
    payload = {
        "tripwire_id": "TW-7c-4",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())

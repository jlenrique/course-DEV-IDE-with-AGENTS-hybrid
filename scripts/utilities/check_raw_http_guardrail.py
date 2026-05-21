# /// script
# requires-python = ">=3.10"
# ///
"""Guardrail: detect unexpected direct HTTP calls outside approved files.

Scans runtime script scope and fails when raw HTTP call patterns are found
in files not listed in config/raw-http-allowlist.txt.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCOPE_GLOBS = [
    "scripts/**/*.py",
    "tests/**/*.py",
    "skills/*/scripts/**/*.py",
    "state/runtime/**/*.py",
]

EXCLUDED_PREFIXES = (
    "_bmad/",
    ".cursor/",
    ".agents/",
    ".github/",
    ".claude/",
)

HTTP_PATTERNS = [
    re.compile(r"\brequests\.(get|post|put|patch|delete|request|Session)\(", re.IGNORECASE),
    re.compile(r"\breq\.(get|post|put|patch|delete|request|Session)\(", re.IGNORECASE),
    re.compile(r"\bhttpx\.(get|post|put|patch|delete|request|Client)\(", re.IGNORECASE),
    re.compile(r"\burllib\.request\.urlopen\(", re.IGNORECASE),
    re.compile(r"\burlopen\(", re.IGNORECASE),
]


def project_root() -> Path:
    """Resolve repository root from this script location via pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent.parent.parent


def load_allowlist(path: Path) -> set[str]:
    """Load allowlist entries as exact repo-relative paths."""
    if not path.exists():
        return set()
    entries: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.add(line.replace("\\", "/"))
    return entries


def in_scope(rel_path: str) -> bool:
    """Exclude mirrored/internal paths outside runtime guardrail scope."""
    return not any(rel_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def iter_python_files(root: Path) -> list[Path]:
    """Collect candidate Python files in guardrail scope."""
    out: list[Path] = []
    seen: set[Path] = set()
    for pattern in SCOPE_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file() or path in seen:
                continue
            rel = path.relative_to(root).as_posix()
            if not in_scope(rel):
                continue
            seen.add(path)
            out.append(path)
    return sorted(out)


def scan_file(root: Path, path: Path) -> list[dict[str, object]]:
    """Scan a single file and return matching raw HTTP call hits."""
    rel = path.relative_to(root).as_posix()
    hits: list[dict[str, object]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return hits

    for idx, line in enumerate(lines, start=1):
        for pattern in HTTP_PATTERNS:
            if pattern.search(line):
                hits.append(
                    {
                        "path": rel,
                        "line": idx,
                        "snippet": line.strip(),
                    }
                )
                break
    return hits


def run_check(root: Path, allowlist: set[str]) -> dict[str, object]:
    """Run guardrail check and classify allowed vs unexpected hits."""
    files = iter_python_files(root)
    all_hits: list[dict[str, object]] = []
    for file_path in files:
        all_hits.extend(scan_file(root, file_path))

    allowed_hits: list[dict[str, object]] = []
    unexpected_hits: list[dict[str, object]] = []
    for hit in all_hits:
        path = str(hit["path"])
        if path in allowlist:
            allowed_hits.append(hit)
        else:
            unexpected_hits.append(hit)

    return {
        "status": "pass" if not unexpected_hits else "fail",
        "files_scanned": len(files),
        "total_hits": len(all_hits),
        "allowed_hits": allowed_hits,
        "unexpected_hits": unexpected_hits,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Raw HTTP guardrail checker")
    parser.add_argument(
        "--allowlist",
        default="config/raw-http-allowlist.txt",
        help="Repo-relative path to allowlist file",
    )
    args = parser.parse_args(argv)

    root = project_root()
    allowlist_path = (root / args.allowlist).resolve()
    allowlist = load_allowlist(allowlist_path)

    result = run_check(root, allowlist)
    print(json.dumps(result, indent=2))

    if result["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

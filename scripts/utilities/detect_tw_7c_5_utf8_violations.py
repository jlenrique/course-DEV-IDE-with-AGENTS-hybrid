"""Detect TW-7c-5 UTF-8 text-file violations with binary false-positive skips."""

from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path

TEXT_GLOBS = (
    "_bmad-output/**/*.md",
    "app/**/*.py",
    "tests/**/*.py",
    "tests/fixtures/**",
)
BINARY_SUFFIXES = (
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".exe",
    ".dylib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".tif",
    ".tiff",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
    ".mp3",
    ".mp4",
    ".wav",
    ".ogg",
    ".webm",
    ".mov",
    ".avi",
    ".mkv",
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".bin",
    ".dat",
    ".svgz",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _pipeline_manifest_globs(root: Path) -> list[str]:
    manifest = root / "state/config/pipeline-manifest.yaml"
    if not manifest.exists():
        return []
    patterns: list[str] = []
    collecting = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.startswith("block_mode_trigger_paths:"):
            collecting = True
            continue
        if collecting:
            if line and not line.startswith("  - "):
                break
            if line.startswith("  - "):
                patterns.append(line[4:].strip())
    return patterns


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines()]


def _matches_any_glob(path: str, patterns: tuple[str, ...] | list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _is_binary_candidate(root: Path, rel_path: str) -> bool:
    if rel_path.lower().endswith(BINARY_SUFFIXES):
        return True
    with (root / rel_path).open("rb") as handle:
        return b"\x00" in handle.read(8192)


def detect_utf8_violations(root: Path) -> tuple[list[str], int]:
    patterns = [*TEXT_GLOBS, *_pipeline_manifest_globs(root)]
    violations: list[str] = []
    scanned = 0
    for rel_path in _tracked_files(root):
        if not _matches_any_glob(rel_path, patterns):
            continue
        if _is_binary_candidate(root, rel_path):
            continue
        scanned += 1
        try:
            (root / rel_path).read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            violations.append(f"{rel_path}:{exc.start}:{exc.reason}")
    return violations, scanned


def main() -> int:
    violations, scanned = detect_utf8_violations(_repo_root())
    payload = {
        "scanned_text_files": scanned,
        "status": "PASS" if not violations else "FAIL",
        "tripwire_id": "TW-7c-5",
        "violations": violations,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())

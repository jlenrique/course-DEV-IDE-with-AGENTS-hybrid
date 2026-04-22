"""Reject common mojibake signatures in committed text files."""

from __future__ import annotations

import sys
from pathlib import Path

BAD_SEQUENCES: dict[str, str] = {
    "\u00c2\u00a7": "\u00a7",
    "\u00c2\u00a0": " ",
    "\u00c3\u2014": "\u00d7",
    "\u00e2\u20ac\u201c": "\u2013",
    "\u00e2\u20ac\u201d": "\u2014",
    "\u00e2\u20ac\u02dc": "\u2018",
    "\u00e2\u20ac\u2122": "\u2019",
    "\u00e2\u20ac\u0153": "\u201c",
    "\u00e2\u20ac": "\u201d",
    "\u00e2\u20ac\u00a6": "\u2026",
    "\u00e2\u2020\u2019": "\u2192",
    "\u00e2\u2030\u02c6": "\u2248",
    "\u00e2\u2030\u00a4": "\u2264",
    "\u00e2\u2030\u00a5": "\u2265",
    "\u00e2\u0160\u00a5": "\u22a5",
    "\u00ef\u00bf\u00bd": "?",
}

TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def _should_check(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def _find_hits(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for bad, good in BAD_SEQUENCES.items():
        if bad in text:
            hits.append((bad, good))
    return hits


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv[1:] if Path(arg).is_file() and _should_check(Path(arg))]
    if not paths:
        return 0

    failed = False
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failed = True
            print(f"{path}: not valid UTF-8 ({exc})", file=sys.stderr)
            continue

        hits = _find_hits(text)
        if not hits:
            continue

        failed = True
        print(f"{path}: detected mojibake sequences", file=sys.stderr)
        for bad, good in hits:
            print(
                f"  replace {bad.encode('unicode_escape').decode()} -> "
                f"{good.encode('unicode_escape').decode()}",
                file=sys.stderr,
            )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

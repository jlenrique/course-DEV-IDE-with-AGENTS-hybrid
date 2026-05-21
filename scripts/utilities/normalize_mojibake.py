"""
Replace common UTF-8 read-as-CP1252 mojibake in text files (most BMAD markdown/yaml).

Safe for mixed content: only replaces known bad multibyte sequences, not valid UTF-8.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Built from: correct_char.encode('utf-8').decode('cp1252') -> mojibake string
# Order: longest / most specific first.
KNOWN_MOJIBAKE_SEQUENCES: tuple[tuple[str, str], ...] = (
    # UTF-8 punctuation misread as Windows-1252, then stored as UTF-8 again ("double mojibake").
    ("\u00e2\u20ac\u201d", "\u2014"),  # em dash —
    ("\u00e2\u2020\u2019", "\u2192"),  # arrow with right single quote
    ("\u00e2\u2020\u201d", "\u2192"),  # arrow with right double quote
    ("\u00e2\u2030\u00a4", "\u2264"),  # ≤
    ("\u00e2\u2030\u00a5", "\u2265"),  # ≥
    ("\u00e2\u0153\u201c", "\u2713"),  # check mark ✓ (in tables)
    # 2-byte UTF-8 (Latin-1) mojibake for U+00A0–U+00FF range misread as cp1252:
    ("\u00c2\u00a7", "\u00a7"),  # §
    ("\u00c2\u00b1", "\u00b1"),  # ±
)

# Optional: single-strategy full-line fix when line is entirely representable in cp1252
def _try_line_cp1252_utf8(line: str) -> str:
    if "\u00e2" not in line and "\u00c2" not in line:
        return line
    try:
        return line.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return line


def normalize_text(text: str, *, aggressive_line: bool = False) -> str:
    """Apply known replacements, then optional line-wise cp1252->utf8 for stubborn lines."""
    out = text
    for bad, good in KNOWN_MOJIBAKE_SEQUENCES:
        out = out.replace(bad, good)
    if aggressive_line:
        lines = []
        for line in out.splitlines(keepends=True):
            if "\u00e2" in line or "\u00c2" in line:
                fixed = _try_line_cp1252_utf8(line.rstrip("\r\n"))
                if fixed != line.rstrip("\r\n"):
                    eol = ""
                    if line.endswith("\r\n"):
                        eol = "\r\n"
                    elif line.endswith("\n"):
                        eol = "\n"
                    lines.append(fixed + eol)
                    continue
            lines.append(line)
        out = "".join(lines)
    return out


def main() -> int:
    p = argparse.ArgumentParser(
        description="Normalize mojibake in text files (dry-run or in-place).",
    )
    p.add_argument("paths", nargs="+", type=Path, help="Files to fix")
    p.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default: dry-run)",
    )
    p.add_argument(
        "--aggressive-line",
        action="store_true",
        help="Also try line-wise cp1252 round-trip",
    )
    args = p.parse_args()
    changed = 0
    for path in args.paths:
        raw = path.read_text(encoding="utf-8")
        new = normalize_text(raw, aggressive_line=args.aggressive_line)
        if new != raw:
            changed += 1
            print(f"Would update: {path}" if not args.apply else f"Updated: {path}")
            if args.apply:
                path.write_text(new, encoding="utf-8", newline="")
    print(f"--- {changed} file(s) changed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

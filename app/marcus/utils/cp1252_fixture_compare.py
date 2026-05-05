"""Byte-level fixture comparison for Windows cp1252 regression checks."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cp1252FixtureComparisonVerdict:
    """Comparison result with enough context to diagnose encoding drift."""

    equivalent: bool
    byte_count_a: int
    byte_count_b: int
    first_divergence_offset: int | None
    divergence_context: str


def _normalize_newlines(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n")


def _first_divergence_offset(left: bytes, right: bytes) -> int | None:
    for offset, (left_byte, right_byte) in enumerate(zip(left, right, strict=False)):
        if left_byte != right_byte:
            return offset
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def _context(raw: bytes, offset: int | None, *, width: int = 16) -> str:
    if offset is None:
        return ""
    start = max(0, offset - width)
    end = min(len(raw), offset + width)
    window = raw[start:end]
    return window.decode("utf-8", errors="replace")


def compare_fixture_bytes(
    expected_path: str | Path,
    actual_path: str | Path,
) -> Cp1252FixtureComparisonVerdict:
    """Compare two fixture files while ignoring CRLF-vs-LF line-ending drift."""
    expected = Path(expected_path).read_bytes()
    actual = Path(actual_path).read_bytes()
    expected_normalized = _normalize_newlines(expected)
    actual_normalized = _normalize_newlines(actual)
    offset = _first_divergence_offset(expected_normalized, actual_normalized)
    return Cp1252FixtureComparisonVerdict(
        equivalent=offset is None,
        byte_count_a=len(expected),
        byte_count_b=len(actual),
        first_divergence_offset=offset,
        divergence_context=_context(actual_normalized, offset),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare UTF-8 fixtures for cp1252-induced byte drift.",
    )
    parser.add_argument("expected_path", type=Path)
    parser.add_argument("actual_path", type=Path)
    args = parser.parse_args(argv)

    verdict = compare_fixture_bytes(args.expected_path, args.actual_path)
    print(json.dumps(asdict(verdict), sort_keys=True))
    return 0 if verdict.equivalent else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""POSIX-portable substrate-frozen-paths check (FR113 + NFR-I13).

Story 7b.12 T11 PATCH-4 cycle-1 remediation 2026-04-30. Replaces the
gawk-extension `match($0, /.../, arr)` parser in
`.github/workflows/substrate-frozen-paths-check.yml` with Python parsing
that:
- works on any runner (gawk / mawk / BusyBox awk are no longer required);
- parses BOTH `-old_start,old_count` AND `+new_start,new_count` in
  hunk headers, so deletion-only hunks against frozen original lines
  are detected (a deletion-only hunk reports `+new,0`);
- detects a [substrate-ceremony] commit token in any commit between
  base..head as the authorization signal.

Usage:
  python scripts/utilities/check_substrate_frozen_paths.py \
    --base <SHA> --head <SHA>

Exit codes:
- 0: no frozen-line diff OR ceremony commit detected; check PASSES
- 1: frozen-line diff present and NO ceremony commit; check FAILS
- 2: invocation error (missing args; git failed)

Frozen invariant: `app/marcus/orchestrator/dispatch_adapter.py:70-95`
(FR113 + NFR-I13).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass

FROZEN_FILE = "app/marcus/orchestrator/dispatch_adapter.py"
FROZEN_RANGE_START = 70
FROZEN_RANGE_END = 95
CEREMONY_TOKEN = "[substrate-ceremony]"

HUNK_HEADER_RE = re.compile(
    r"^@@\s*-(?P<old_start>\d+)(?:,(?P<old_count>\d+))?"
    r"\s*\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))?\s*@@"
)


@dataclass(frozen=True)
class HunkRange:
    old_start: int
    old_count: int
    new_start: int
    new_count: int

    @property
    def old_end(self) -> int:
        # Empty old range (count 0) means pure addition; old_end < old_start
        return self.old_start + self.old_count - 1 if self.old_count > 0 else self.old_start - 1

    @property
    def new_end(self) -> int:
        return self.new_start + self.new_count - 1 if self.new_count > 0 else self.new_start - 1

    def touches_frozen_old(self, lo: int, hi: int) -> bool:
        if self.old_count == 0:
            return False
        return self.old_start <= hi and self.old_end >= lo

    def touches_frozen_new(self, lo: int, hi: int) -> bool:
        if self.new_count == 0:
            return False
        return self.new_start <= hi and self.new_end >= lo


def parse_hunk_header(line: str) -> HunkRange | None:
    match = HUNK_HEADER_RE.match(line)
    if match is None:
        return None
    return HunkRange(
        old_start=int(match.group("old_start")),
        old_count=int(match.group("old_count") or "1"),
        new_start=int(match.group("new_start")),
        new_count=int(match.group("new_count") or "1"),
    )


def hunk_touches_frozen(hunks: list[HunkRange], lo: int, hi: int) -> bool:
    return any(
        hunk.touches_frozen_new(lo, hi) or hunk.touches_frozen_old(lo, hi)
        for hunk in hunks
    )


def collect_hunks_for_path(diff_text: str) -> list[HunkRange]:
    return [
        hunk
        for line in diff_text.splitlines()
        if line.startswith("@@")
        for hunk in [parse_hunk_header(line)]
        if hunk is not None
    ]


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="base ref/SHA")
    parser.add_argument("--head", required=True, help="head ref/SHA")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    diff_rc, diff_text = _run(
        [
            "git",
            "diff",
            "-U0",
            f"{args.base}",
            f"{args.head}",
            "--",
            FROZEN_FILE,
        ]
    )
    if diff_rc != 0:
        sys.stderr.write(f"git diff failed (rc={diff_rc})\n")
        return 2
    hunks = collect_hunks_for_path(diff_text)
    touched = hunk_touches_frozen(hunks, FROZEN_RANGE_START, FROZEN_RANGE_END)
    if not touched:
        return 0
    log_rc, log_text = _run(
        [
            "git",
            "log",
            "--pretty=format:%H%n%B%n---END---",
            f"{args.base}..{args.head}",
        ]
    )
    if log_rc != 0:
        sys.stderr.write(f"git log failed (rc={log_rc})\n")
        return 2
    if CEREMONY_TOKEN in log_text:
        sys.stdout.write(
            f"Ceremony commit detected ({CEREMONY_TOKEN}); "
            "substrate-frozen-paths edit authorized.\n"
        )
        return 0
    sys.stderr.write(
        f"::error::{FROZEN_FILE}:{FROZEN_RANGE_START}-{FROZEN_RANGE_END} "
        "is FR113-frozen substrate.\n"
        f"::error::Diff touches frozen range without {CEREMONY_TOKEN} commit token.\n"
        "::error::Either revert the frozen-range hunk OR add a ceremony commit:\n"
        f"::error::  - commit message MUST contain '{CEREMONY_TOKEN}'\n"
        "::error::  - commit body MUST link to party-mode consensus record\n"
        "::error::See FR113 + NFR-I13 in the Slab 7b PRD.\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Project quality-scorecard CLI — surface the score during dev work.

The authority is ``docs/quality/project-quality-scorecard.md`` (prose). This tool
reads its machine block and:

  * ``--summary`` (default)  — human-readable DID score + per-criterion breakdown.
  * ``--json``               — the parsed machine block, for tooling.
  * ``--run-summary-line``   — one line, as embedded in run_summary.yaml.
  * ``--check``              — staleness ratchet: non-zero exit if the scorecard is
                               missing/malformed or its ``as_of`` is older than
                               ``--max-age-days`` (default 45). Run it in dev to
                               keep the assessment from rotting into believed-green.

Run: ``.venv/Scripts/python.exe scripts/utilities/quality_scorecard.py [--check]``
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

# Allow standalone `python scripts/utilities/quality_scorecard.py` runs to import app.*
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.quality.scorecard import (  # noqa: E402  (path bootstrap must precede import)
    did_score_ref,
    read_scorecard_block,
    scorecard_path,
)


def _fmt_summary(block: dict) -> str:
    # Mirror the reader's own fail-soft guards: a dict block whose `dimensions` is
    # null/list, or whose DID key maps to a scalar, must format gracefully rather
    # than AttributeError. Fall back to an empty mapping so every .get() below holds.
    dims = block.get("dimensions")
    dim = dims.get("dynamic_intelligence_vs_determinism") if isinstance(dims, dict) else None
    dim = dim if isinstance(dim, dict) else {}
    # v2 (Story Q1.1): dimensions carry rubric_version + as_of/as_verified; criteria
    # carry {level, signal, evidence_ref} alongside the retained score/max. as_of
    # falls back to the block-level value for backward-compat with the v1 shape.
    dim_as_of = dim.get("as_of", block.get("as_of", "?"))
    lines = [
        f"Project Quality Scorecard ({block.get('schema', '?')}) — as of {block.get('as_of', '?')}",
        f"  Source: {scorecard_path()}",
        "",
        f"  Dimension 1 — {dim.get('label', 'DID')}: "
        f"{dim.get('score', '?')}/{dim.get('max', 100)} "
        f"({dim.get('band', '?')} — {dim.get('band_note', '')})",
        f"      rubric v{dim.get('rubric_version', '?')} · "
        f"as_of {dim_as_of} · as_verified {dim.get('as_verified', '?')}",
    ]
    crit = dim.get("criteria", {})
    if isinstance(crit, dict):
        for name, c in crit.items():
            if isinstance(c, dict):
                signal = c.get("signal")
                signal_note = "signal: —" if signal is None else f"signal: {signal}"
                lines.append(
                    f"      - {name}: {c.get('score', '?')}/{c.get('max', 4)} "
                    f"({c.get('level', '?')}) · {signal_note} · "
                    f"{c.get('evidence_ref', '')}"
                )
    lines.append(f"  Open leaks: {dim.get('open_leaks', '?')} · trend: {dim.get('trend', '?')}")
    return "\n".join(lines)


def _check(block: dict | None, max_age_days: int) -> int:
    if block is None:
        print("FAIL: scorecard machine block missing or malformed", file=sys.stderr)
        return 1
    as_of = block.get("as_of")
    try:
        when = _dt.date.fromisoformat(str(as_of))
    except (TypeError, ValueError):
        print(f"FAIL: scorecard 'as_of' not an ISO date: {as_of!r}", file=sys.stderr)
        return 1
    age = (_dt.date.today() - when).days
    if age > max_age_days:
        print(
            f"STALE: scorecard as_of {as_of} is {age}d old (> {max_age_days}d). "
            "Refresh the assessment (docs/quality/project-quality-scorecard.md).",
            file=sys.stderr,
        )
        return 1
    print(f"OK: scorecard as_of {as_of} ({age}d old, <= {max_age_days}d).")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Project quality scorecard (DID dimension).")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--summary", action="store_true", help="human-readable summary (default)")
    g.add_argument("--json", action="store_true", help="parsed machine block as JSON")
    g.add_argument("--run-summary-line", action="store_true", help="one-line run-report form")
    g.add_argument("--check", action="store_true", help="staleness ratchet (non-zero if stale)")
    ap.add_argument("--max-age-days", type=int, default=45, help="staleness threshold for --check")
    args = ap.parse_args(argv)

    block = read_scorecard_block()

    if args.check:
        return _check(block, args.max_age_days)
    if args.json:
        print(json.dumps(block, indent=2, sort_keys=False, default=str))
        return 0 if block is not None else 1
    if args.run_summary_line:
        ref = did_score_ref()
        if ref.get("status") == "unavailable":
            print("quality_scorecard: unavailable")
            return 1
        print(
            f"DID {ref['score']}/{ref['max']} ({ref['band']}) "
            f"as of {ref['as_of']} — {ref['source']}"
        )
        return 0
    # default: summary
    if block is None:
        print("scorecard unavailable (missing/malformed machine block)", file=sys.stderr)
        return 1
    print(_fmt_summary(block))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

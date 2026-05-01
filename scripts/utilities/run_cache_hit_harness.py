"""Cache-hit-rate harness aggregator (AC-G; FR106; 10-LLM-specialist).

Slab 7b 7b.12 T12.5 cycle-1 remediation skeleton authored 2026-04-30.
Operator-gated tool: invoked at next-session-start before Gate-2 ceremony.

Fails closed: by default the harness reports `not_run` and exits non-zero
because real cache-hit-rate measurement requires live LLM invocations
which are outside CI scope (NFR-CG13 strict). Operator runs with
`--live-runs` after live-API credentials are loaded; the harness then
performs N invocations per LLM specialist and computes
`median(rates[2:]) >= threshold`.

Evidence file format (JSON; emitted to --evidence-path):

```
{
  "harness": "cache_hit_rate",
  "threshold": 0.85,
  "median_from_index": 2,
  "specialists": [
    {"name": "<id>", "rates": [...], "median_post_warmup": <float>, "pass": <bool>}
  ],
  "verdict": "PASS" | "FAIL" | "not_run",
  "generated_at": "<iso8601>"
}
```
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

LLM_SPECIALISTS: tuple[str, ...] = (
    "texas",
    "quinn_r",
    "vera",
    "irene_pass1",
    "irene",
    "tracy",
    "dan",
    "marcus",
    "desmond",
    "aria",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-G cache-hit-rate harness (FR106). Operator-gated.",
    )
    parser.add_argument(
        "--all-specialists",
        action="store_true",
        help="Iterate the full 10-LLM-specialist set",
    )
    parser.add_argument(
        "--specialist",
        action="append",
        default=[],
        help="Run a single specialist (repeatable)",
    )
    parser.add_argument(
        "--median-from-index",
        type=int,
        default=2,
        help="Slice rates[N:] for median computation (default 2; warm-up tolerance)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="median post-warm-up cache-hit-rate floor (default 0.85)",
    )
    parser.add_argument(
        "--live-runs",
        type=int,
        default=0,
        help=(
            "Number of live LLM invocations per specialist (>0 enables live mode; "
            "0 = fail-closed not_run skeleton)"
        ),
    )
    parser.add_argument(
        "--evidence-path",
        type=Path,
        default=None,
        help="Where to write the evidence JSON",
    )
    return parser.parse_args(argv)


def _emit(evidence: dict, evidence_path: Path | None) -> None:
    text = json.dumps(evidence, indent=2, sort_keys=True)
    sys.stdout.write(text + "\n")
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    targets = LLM_SPECIALISTS if args.all_specialists else tuple(args.specialist)
    if not targets:
        sys.stderr.write(
            "no specialists selected; pass --all-specialists or --specialist <id>\n"
        )
        return 2
    if args.live_runs <= 0:
        evidence = {
            "harness": "cache_hit_rate",
            "threshold": args.threshold,
            "median_from_index": args.median_from_index,
            "specialists": [{"name": name, "status": "not_run"} for name in targets],
            "verdict": "not_run",
            "reason": (
                "fail-closed skeleton; pass --live-runs N to enable live LLM "
                "invocation. Operator must load API credentials and run with "
                "--live-runs >= median_from_index + 3 to populate post-warmup window."
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }
        _emit(evidence, args.evidence_path)
        return 1
    sys.stderr.write(
        "live cache-hit-rate measurement is operator-gated; the skeleton "
        "harness does not yet exercise live LLM endpoints. To unblock Gate-2:\n"
        "  - author the live-call dispatch in this script, OR\n"
        "  - invoke the per-specialist cache-hit-rate fixtures at "
        "tests/end_to_end/test_*_cache_hit_rate.py with credentials loaded "
        "and aggregate the medians manually.\n"
    )
    evidence = {
        "harness": "cache_hit_rate",
        "threshold": args.threshold,
        "median_from_index": args.median_from_index,
        "specialists": [
            {
                "name": name,
                "status": "live_dispatch_pending_authoring",
            }
            for name in targets
        ],
        "verdict": "FAIL",
        "reason": "skeleton harness; live-runs path not yet authored",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

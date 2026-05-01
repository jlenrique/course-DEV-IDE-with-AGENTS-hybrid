"""5-API live-binding smoke (AC-I; operator-gated; spend-ceilinged).

Slab 7b 7b.12 T12.5 cycle-1 remediation skeleton authored 2026-04-30.
Operator-gated tool: invoked at next-session-start before Gate-2 ceremony.

Per AC-I: ≤3 canaries × 5 APIs × ≤$0.40/canary = $6.00 total spend ceiling.
Per Dan's 7b.10 LLM-only resolution, the "5 APIs" reduce to 4 third-party
APIs (gamma / kling / elevenlabs / wondercraft); Dan's slot is replaced
with a `dan-llm-only` shared-facade smoke (no third-party HTTP call).

Fails closed: by default the harness reports `not_run` and exits non-zero
because real live-binding requires API credentials loaded from the
operator's `.env`. Operator runs with `--live` after credentials are
loaded; the harness then invokes each API client per `scripts/api_clients/`
and verifies 200-OK + valid response shape per the per-specialist contract.

Evidence file format (JSON; emitted to --evidence-path):

```
{
  "smoke": "5_api_live_binding",
  "spend_ceiling_usd": 6.00,
  "max_canaries_per_api": 3,
  "max_cost_per_canary_usd": 0.40,
  "apis": [
    {"name": "gamma", "canaries": [...], "total_cost_usd": <float>, "all_ok": <bool>},
    ...
  ],
  "total_spend_usd": <float>,
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

DEFAULT_APIS: tuple[str, ...] = (
    "gamma",
    "kling",
    "elevenlabs",
    "wondercraft",
    "dan-llm-only",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-I 5-API live-binding smoke (operator-gated; cost ≤$6.00).",
    )
    parser.add_argument(
        "--apis",
        default=",".join(DEFAULT_APIS),
        help="Comma-separated API names to smoke",
    )
    parser.add_argument(
        "--max-canaries-per-api",
        type=int,
        default=3,
        help="Max canary calls per API (default 3)",
    )
    parser.add_argument(
        "--max-cost-per-canary",
        type=float,
        default=0.40,
        help="Max cost per canary in USD (default 0.40)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live API invocation (default: fail-closed not_run skeleton)",
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
    api_list = [name.strip() for name in args.apis.split(",") if name.strip()]
    spend_ceiling = (
        len(api_list) * args.max_canaries_per_api * args.max_cost_per_canary
    )
    if not args.live:
        evidence = {
            "smoke": "5_api_live_binding",
            "spend_ceiling_usd": round(spend_ceiling, 2),
            "max_canaries_per_api": args.max_canaries_per_api,
            "max_cost_per_canary_usd": args.max_cost_per_canary,
            "apis": [{"name": name, "status": "not_run"} for name in api_list],
            "total_spend_usd": 0.0,
            "verdict": "not_run",
            "reason": (
                "fail-closed skeleton; pass --live to enable real API "
                "invocation. Operator must load credentials in .env "
                "(GAMMA_API_KEY, KLING_*, ELEVENLABS_API_KEY, WONDERCRAFT_API_KEY) "
                "before re-running."
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }
        _emit(evidence, args.evidence_path)
        return 1
    sys.stderr.write(
        "live API smoke is operator-gated; the skeleton harness does not "
        "yet exercise live API endpoints. To unblock Gate-2:\n"
        "  - author per-API live-call dispatch in this script (consume "
        "scripts/api_clients/{gamma,kling,elevenlabs,wondercraft}_client.py "
        "modules), OR\n"
        "  - operator runs each of the existing per-specialist "
        "operator-gated AC-N-B canary blocks (e.g., AC-6-B Gary live "
        "canary, AC-7-B Kira, AC-8-B Enrique, AC-9-B Wanda) and aggregates "
        "evidence manually into the evidence-path JSON.\n"
    )
    evidence = {
        "smoke": "5_api_live_binding",
        "spend_ceiling_usd": round(spend_ceiling, 2),
        "max_canaries_per_api": args.max_canaries_per_api,
        "max_cost_per_canary_usd": args.max_cost_per_canary,
        "apis": [
            {"name": name, "status": "live_dispatch_pending_authoring"}
            for name in api_list
        ],
        "total_spend_usd": 0.0,
        "verdict": "FAIL",
        "reason": "skeleton harness; live-call path not yet authored",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

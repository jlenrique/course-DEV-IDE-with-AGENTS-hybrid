"""Trial-2 cost-projection (AC-H; Round-(a) John A1; SR-T6 mitigation).

Slab 7b 7b.12 T12.5 cycle-1 remediation skeleton authored 2026-04-30.
Operator-gated tool: invoked at next-session-start before Gate-2 ceremony.

Projects total Trial-2 cost from per-specialist token rate × volume estimate
(per PRD §Journey 5). If projection > BS-3 ceiling, emits FAIL verdict + the
4 named remediation paths from Round-(a) A1 (scope-cut / budget-exception
/ trial-redesign / Slab-7c precondition deferral).

Default projection inputs are conservative placeholders; operator overrides
via flags or fills in `state/config/trial-2-projection-inputs.yaml` (not yet
authored — operator action). Real per-specialist token volumes derive from
Slab 6 trial 475df528 closed-trial telemetry where available.

Evidence file format (JSON; emitted to --evidence-path):

```
{
  "projection": "trial_2_cost",
  "bs_3_ceiling_usd": <float>,
  "projected_cost_usd": <float>,
  "delta_usd": <float>,
  "per_specialist": [
    {"name": <id>, "tokens_in": ..., "tokens_out": ...,
     "rate_usd_per_1k": ..., "cost_usd": ...}
  ],
  "verdict": "PASS" | "FAIL" | "skeleton",
  "remediation_paths": [...] (only if FAIL),
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


# Conservative placeholder projection inputs; OPERATOR MUST OVERRIDE for real
# Trial-2 evaluation. Sourced from Slab 6 trial 475df528 telemetry +
# PRD §Journey 5 volume estimates (4-module storyboard, ~3K total tokens
# for narration, ~5K storyboard, ~1K beds + visuals).
def _llm(name: str, tokens_in: int, tokens_out: int) -> dict:
    return {
        "name": name,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "rate_usd_per_1k_in": 0.005,
        "rate_usd_per_1k_out": 0.015,
    }


def _api(name: str, per_call_usd: float, calls: int) -> dict:
    return {
        "name": name,
        "tokens_in": 0,
        "tokens_out": 0,
        "rate_usd_per_1k_in": 0.0,
        "rate_usd_per_1k_out": 0.0,
        "per_call_usd": per_call_usd,
        "calls": calls,
    }


DEFAULT_INPUTS: tuple[dict, ...] = (
    _llm("texas", 18000, 6000),
    _llm("irene_pass1", 8000, 4000),
    _llm("tracy", 6000, 2000),
    _llm("irene", 12000, 8000),
    _llm("vera", 10000, 3000),
    _llm("quinn_r", 8000, 2000),
    _llm("dan", 4000, 2000),
    _api("gary", 0.40, 5),
    _api("kira", 0.40, 5),
    _api("enrique", 0.30, 6),
    _api("wanda", 0.40, 3),
    _api("compositor", 0.0, 0),
)

DEFAULT_BS_3_CEILING_USD = 25.00  # placeholder; operator confirms from BS-3 cost table

REMEDIATION_PATHS = (
    "scope-cut: reduce Trial-2 corpus or specialist set",
    "budget-exception: party-mode + governance JSON budget-bump",
    "trial-redesign: rework Trial-2 to a smaller-scope dry-run",
    "slab-7c-precondition-deferral: defer Trial-2 to post-Slab-7c readiness",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-H Trial-2 cost-projection (Round-(a) John A1; SR-T6). Operator-gated.",
    )
    parser.add_argument(
        "--bs-3-ceiling-usd",
        type=float,
        default=DEFAULT_BS_3_CEILING_USD,
        help=f"BS-3 ceiling in USD (default {DEFAULT_BS_3_CEILING_USD:.2f}; placeholder)",
    )
    parser.add_argument(
        "--inputs-file",
        type=Path,
        default=None,
        help=(
            "Optional YAML/JSON file with per-specialist projection inputs "
            "overriding placeholder defaults (operator action)"
        ),
    )
    parser.add_argument(
        "--evidence-path",
        type=Path,
        default=None,
        help="Where to write the evidence JSON",
    )
    return parser.parse_args(argv)


def _project_specialist_cost(entry: dict) -> float:
    tokens_in_cost = (entry.get("tokens_in", 0) / 1000.0) * entry.get("rate_usd_per_1k_in", 0.0)
    tokens_out_cost = (entry.get("tokens_out", 0) / 1000.0) * entry.get("rate_usd_per_1k_out", 0.0)
    per_call_cost = entry.get("per_call_usd", 0.0) * entry.get("calls", 0)
    return tokens_in_cost + tokens_out_cost + per_call_cost


def _emit(evidence: dict, evidence_path: Path | None) -> None:
    text = json.dumps(evidence, indent=2, sort_keys=True)
    sys.stdout.write(text + "\n")
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.inputs_file is not None:
        sys.stderr.write(
            f"--inputs-file {args.inputs_file} not yet supported in skeleton; "
            "using DEFAULT_INPUTS placeholders. Operator: author the inputs "
            "file and uncomment the YAML loader in this script.\n"
        )
    inputs = DEFAULT_INPUTS
    per_specialist: list[dict] = []
    total = 0.0
    for entry in inputs:
        cost = _project_specialist_cost(entry)
        total += cost
        per_specialist.append({**entry, "cost_usd": round(cost, 4)})
    delta = round(total - args.bs_3_ceiling_usd, 4)
    pass_threshold = total <= args.bs_3_ceiling_usd
    verdict = "PASS" if pass_threshold else "FAIL"
    evidence = {
        "projection": "trial_2_cost",
        "bs_3_ceiling_usd": args.bs_3_ceiling_usd,
        "projected_cost_usd": round(total, 4),
        "delta_usd": delta,
        "per_specialist": per_specialist,
        "verdict": verdict,
        "remediation_paths": list(REMEDIATION_PATHS) if not pass_threshold else [],
        "skeleton_warning": (
            "DEFAULT_INPUTS are placeholder; operator MUST override via "
            "--inputs-file with real Trial-2 projection inputs from Slab 6 "
            "trial 475df528 telemetry + PRD §Journey 5 before treating "
            "verdict as authoritative"
        ),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 0 if pass_threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())

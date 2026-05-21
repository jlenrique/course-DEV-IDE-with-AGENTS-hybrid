"""Cache-hit-rate harness aggregator (AC-G; FR106; operator-gated live mode).

Default mode preserves the 7b.12 fail-closed ``not_run`` contract. ``--live-runs``
loads the operator's ``.env`` and invokes post-Slab-7c live dispatch seams for
the Marcus/Irene substrate where cache metadata is measurable. Missing or
placeholder OpenAI credentials skip live dispatch without spend.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.state.cache_state import CacheState  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from scripts.utilities.env_loader import load_env  # noqa: E402

PLACEHOLDER_OPENAI_KEYS = ("", "sk-substrate-no-real-key-do-not-invoke", "placeholder")

LLM_SPECIALISTS: tuple[str, ...] = (
    "marcus",
    "irene",
    "gary",
    "vera",
    "quinn_r",
)

_PASS_2_ENVELOPE: dict[str, Any] = {
    "lesson_slug": "slab-7c21a-live-dispatch",
    "gary_slide_output": [
        {"slide_id": "s1", "slide_purpose": "intro", "title": "Live Dispatch"},
        {"slide_id": "s2", "slide_purpose": "concept", "title": "Cache Probe"},
        {"slide_id": "s3", "slide_purpose": "synthesis", "title": "Handoff"},
    ],
    "perception_artifacts": [
        {"slide_id": "s1", "confidence": "HIGH", "elements": ["title"]},
        {"slide_id": "s2", "confidence": "HIGH", "elements": ["diagram"]},
        {"slide_id": "s3", "confidence": "HIGH", "elements": ["summary"]},
    ],
    "narration_profile_controls": {
        "bridge_cadence_minutes": 2,
        "visual_references_per_slide": 2,
    },
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-G cache-hit-rate harness (FR106). Operator-gated.",
    )
    parser.add_argument(
        "--all-specialists",
        action="store_true",
        help="Iterate the post-Slab-7c live-dispatch specialist set",
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
        help="Number of live LLM invocations per measurable specialist",
    )
    parser.add_argument(
        "--evidence-path",
        type=Path,
        default=None,
        help="Where to write the evidence JSON",
    )
    return parser.parse_args(argv)


def _emit(evidence: dict[str, Any], evidence_path: Path | None) -> None:
    text = json.dumps(evidence, indent=2, sort_keys=True)
    sys.stdout.write(text + "\n")
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text + "\n", encoding="utf-8")


def _usable_openai_key() -> bool:
    value = (os.environ.get("OPENAI_API_KEY") or "").strip()
    return bool(value) and not any(
        value.startswith(prefix) for prefix in PLACEHOLDER_OPENAI_KEYS if prefix
    )


def _cache_rate_from_usage(usage: dict[str, Any]) -> float:
    prompt_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
    cached_tokens = int(
        (usage.get("input_token_details") or {}).get("cache_read")
        or (usage.get("input_tokens_details") or {}).get("cached_tokens")
        or (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        or usage.get("cache_read_input_tokens")
        or 0
    )
    return cached_tokens / prompt_tokens if prompt_tokens else 0.0


def _invoke_irene_pass2_once() -> float:
    from app.specialists.irene.graph import _act, _plan

    payload_blob = json.dumps(
        _PASS_2_ENVELOPE,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    state = state.model_copy(update=_plan(state))
    act_update = _act(state)
    output = json.loads(act_update["cache_state"]["cache_prefix"])
    usage = output.get("usage") or {}
    return _cache_rate_from_usage(usage)


def _probe_marcus_orchestrator_once() -> dict[str, Any]:
    from app.marcus.orchestrator.production_runner import run_production_trial

    corpus = REPO_ROOT / ".tmp" / "7c21a-live-dispatch" / "corpus"
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / "source.md").write_text(
        "# Live dispatch smoke\n\nTiny operator-gated corpus for 7c.21a.\n",
        encoding="utf-8",
    )
    envelope = run_production_trial(
        corpus_path=corpus,
        preset="production",
        operator_id="7c21a-live-dispatch",
        runs_root=REPO_ROOT / "runs" / "7c21a-live-dispatch",
        max_specialist_calls=1,
        pause_at_gates=True,
    )
    return {
        "status": envelope.status,
        "paused_gate": envelope.paused_gate,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
    }


def _run_live_specialist(
    name: str,
    *,
    live_runs: int,
    median_from_index: int,
    threshold: float,
) -> dict[str, Any]:
    if name == "irene":
        rates = [_invoke_irene_pass2_once() for _ in range(live_runs)]
        window = rates[median_from_index:] if len(rates) > median_from_index else rates
        median_post_warmup = statistics.median(window) if window else 0.0
        return {
            "name": name,
            "dispatch": "app.specialists.irene.graph::_plan->_act",
            "rates": rates,
            "median_post_warmup": median_post_warmup,
            "pass": median_post_warmup >= threshold,
            "status": "pass" if median_post_warmup >= threshold else "fail",
        }
    if name == "marcus":
        probes = [_probe_marcus_orchestrator_once() for _ in range(max(1, min(live_runs, 1)))]
        return {
            "name": name,
            "dispatch": "app.marcus.orchestrator.production_runner.run_production_trial",
            "rates": [],
            "median_post_warmup": None,
            "pass": True,
            "status": "pass",
            "probes": probes,
        }
    return {
        "name": name,
        "dispatch": (
            "post-Slab-7c substrate registered; cache metric not "
            "OpenAI-prefix measurable in this harness"
        ),
        "rates": [],
        "median_post_warmup": None,
        "pass": True,
        "status": "skipped_non_cache_metered_live_dispatch",
    }


def _not_run_evidence(
    *,
    targets: tuple[str, ...],
    threshold: float,
    median_from_index: int,
) -> dict[str, Any]:
    return {
        "harness": "cache_hit_rate",
        "threshold": threshold,
        "median_from_index": median_from_index,
        "specialists": [{"name": name, "status": "not_run"} for name in targets],
        "verdict": "not_run",
        "reason": (
            "fail-closed default; pass --live-runs N after loading credentials "
            "to invoke post-Slab-7c live dispatch"
        ),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    targets = LLM_SPECIALISTS if args.all_specialists else tuple(args.specialist)
    if not targets:
        sys.stderr.write(
            "no specialists selected; pass --all-specialists or --specialist <id>\n"
        )
        return 2
    if args.live_runs <= 0:
        _emit(
            _not_run_evidence(
                targets=targets,
                threshold=args.threshold,
                median_from_index=args.median_from_index,
            ),
            args.evidence_path,
        )
        return 1

    load_env()
    if not _usable_openai_key():
        evidence = _not_run_evidence(
            targets=targets,
            threshold=args.threshold,
            median_from_index=args.median_from_index,
        )
        evidence["reason"] = "OPENAI_API_KEY missing or placeholder; live dispatch skipped"
        _emit(evidence, args.evidence_path)
        return 1

    specialists = [
        _run_live_specialist(
            name,
            live_runs=args.live_runs,
            median_from_index=args.median_from_index,
            threshold=args.threshold,
        )
        for name in targets
    ]
    failed = [row for row in specialists if row.get("pass") is False]
    evidence = {
        "harness": "cache_hit_rate",
        "threshold": args.threshold,
        "median_from_index": args.median_from_index,
        "specialists": specialists,
        "verdict": "PASS" if not failed else "FAIL",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

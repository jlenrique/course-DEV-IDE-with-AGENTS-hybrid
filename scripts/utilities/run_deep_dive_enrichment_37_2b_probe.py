#!/usr/bin/env python3
"""One-shot, first-run-stands component probe for Story 37.2b.

Probe id: ``probe-37-2b-deep-dive-enrichment-001`` (registered in the story
spec BEFORE it runs — probe honesty contract, wave-3940 party record D3).

Exact claim licensed: "the live deep-dive enrichment writer produces cited,
bolded, pool-grounded prose on real inputs — the frozen Tejal Part-2 authored
skeleton + the real ``a940c5eb`` Ask-A pool — passing the A2 gate first-run."
It licenses NOTHING else (not "the pipeline works", not render, not the bar).

Deterministic machine judge (amendment M3a — the judge NAMES its gates):
  1. the A2 citation-coverage gate (``deep_dive_enrichment_gate``),
  2. the AC4 bold-parity/term-trace gates (named A2 failure rows),
  3. the numeric-fidelity gate over enriched prose (37.2a witnesses re-run —
     the ``enrichment_numeric_fidelity_failed`` row).

Amendment J2: a degraded-honest outcome (row d′ ``pool_unused`` / row d
``pool_empty`` with a PASSING gate) is a VALID machine-judge PASS licensing
ONLY the thin/empty-honesty path; the enrichment claim stays OPEN pending a
richer pool or batch run A. The success criterion is NEVER "citations
appeared" — first-run-stands must not penalize an honest decline.

Vehicle: clone of ``run_deep_dive_38_3a_live_evidence.py`` (same one-shot,
failed-evidence-preservation-pin, immutable-attempt-dir discipline).

``--dry-run``: preflight only — verify frozen inputs, build the digest-bound
request, and print the input-identity digests (drift-flags amendment). NO
provider call is made in dry-run mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

from app.marcus.lesson_plan.deep_dive_enrichment import (  # noqa: E402
    DeepDiveEnrichedResultV1,
    build_deep_dive_enrichment_request,
    deep_dive_enrichment_gate,
)
from app.marcus.lesson_plan.deep_dive_enrichment_provider_contract import (  # noqa: E402
    DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION,
    provider_payload_digest,
)
from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WorkbookBriefRuntimeContext,
    read_workbook_brief,
)
from app.marcus.orchestrator.deep_dive_enrichment_wiring import (  # noqa: E402
    DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME,
    run_workbook_review,
)

PROBE_ID = "probe-37-2b-deep-dive-enrichment-001"
SCHEMA_VERSION = "deep-dive-enrichment-37-2b-probe-evidence.v1"
# Frozen real inputs: the a940c5eb run carries BOTH the live-authored Tejal
# Part-2 skeleton (workbook-brief.v1.json) and the real Ask-A pool (run.json +
# ask-a-research-call.v1.json).
SOURCE_RUN = ROOT / "runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4"
COURSE_ROOT = ROOT / "course-content/courses/tejal-apc-c1-m1-p2-trends"
EVIDENCE_ROOT = ROOT / "_bmad-output/implementation-artifacts/evidence"
SOURCE_ARTIFACTS = (
    "run.json",
    "workbook-brief.v1.json",
    "ask-a-research-call.v1.json",
)
OPTIONAL_SOURCE_ARTIFACTS = ("g0-enrichment.json",)

# The A2 rows the judge NAMES explicitly (M3a): parity/trace (AC4) + numeric
# fidelity. Any OTHER gate failure also fails the judge (gate PASS required).
NAMED_PARITY_FAILURES = (
    "bold_term_parity_failed",
    "skeleton_bold_terms_not_preserved",
    "untraced_new_bold_term",
)
NAMED_NUMERIC_FAILURE = "enrichment_numeric_fidelity_failed"


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _allocate_attempt_root() -> tuple[str, Path]:
    while True:
        attempt_id = str(uuid4())
        attempt_root = EVIDENCE_ROOT / f"deep-dive-enrichment-37-2b-{attempt_id[:8]}"
        try:
            attempt_root.mkdir(parents=True)
        except FileExistsError:
            continue
        return attempt_id, attempt_root


def _stage_run(run_dir: Path) -> dict[str, str]:
    """Copy the frozen source artifacts and re-mint a fresh nested trial id."""
    from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
        ProductionTrialEnvelope,
    )

    run_dir.mkdir(parents=True)
    digests: dict[str, str] = {}
    for name in SOURCE_ARTIFACTS:
        source = SOURCE_RUN / name
        shutil.copy2(source, run_dir / name)
        digests[name] = _sha256_file(source)
    for name in OPTIONAL_SOURCE_ARTIFACTS:
        source = SOURCE_RUN / name
        if source.is_file():
            shutil.copy2(source, run_dir / name)
            digests[name] = _sha256_file(source)
    trial = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text("utf-8")
    )
    fresh = uuid4()
    trial = trial.model_copy(
        update={
            "trial_id": fresh,
            "production_envelope": trial.production_envelope.model_copy(
                update={"trial_id": fresh}
            ),
        }
    )
    (run_dir / "run.json").write_text(trial.model_dump_json(indent=2) + "\n", "utf-8")
    digests["fresh_trial_id"] = str(fresh)
    return digests


def _machine_judge(result: DeepDiveEnrichedResultV1) -> dict[str, object]:
    """Deterministic judge — no human vibes, no LLM judging itself (AC8)."""
    recomputed = deep_dive_enrichment_gate(result.request, result.candidate_snapshot)
    gate = result.gate
    failures = set(gate.failures)
    a2_gate_pass = gate.status == "pass" and gate == recomputed
    parity_pass = not (failures & set(NAMED_PARITY_FAILURES))
    numeric_pass = NAMED_NUMERIC_FAILURE not in failures
    enriched = result.status == "enriched" and gate.disposition == "enriched"
    honest_decline = result.status == "degraded" and gate.disposition in {
        "degraded_pool_unused",
        "degraded_pool_empty",
    }
    verdict_pass = a2_gate_pass and parity_pass and numeric_pass and (
        enriched or honest_decline
    )
    if enriched:
        claim_licensed = (
            "live deep-dive enrichment writer produced cited, bolded, "
            "pool-grounded prose passing the A2 gate first-run"
        )
    elif honest_decline:
        claim_licensed = (
            "thin/empty-pool honesty path only (J2): the writer declined "
            "honestly; the enrichment claim stays OPEN pending a richer pool "
            "or batch run A"
        )
    else:
        claim_licensed = "none"
    return {
        "judge": {
            "a2_citation_coverage_gate": a2_gate_pass,
            "ac4_bold_parity_and_term_trace": parity_pass,
            "numeric_fidelity_over_enriched_prose": numeric_pass,
            "outcome": (
                "enriched"
                if enriched
                else ("degraded_honest" if honest_decline else "failed")
            ),
        },
        "pass": verdict_pass,
        "claim_licensed": claim_licensed,
        "gate_status": gate.status,
        "gate_disposition": gate.disposition,
        "gate_failures": list(gate.failures),
        "used_citation_ids": list(gate.used_citation_ids),
        "unused_citation_ids": list(gate.unused_citation_ids),
        "available_citation_ids": list(gate.available_citation_ids),
        "prose_association_covered_ability_ids": list(
            gate.prose_association_covered_ability_ids
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preflight only: verify inputs + print identity digests; NO provider call",
    )
    args = parser.parse_args()

    if args.dry_run:
        preflight: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "probe_id": PROBE_ID,
            "mode": "dry-run-preflight",
            "provider_calls": 0,
        }
        missing = [
            name for name in SOURCE_ARTIFACTS if not (SOURCE_RUN / name).is_file()
        ]
        if missing:
            preflight["pass"] = False
            preflight["missing_source_artifacts"] = missing
            print(json.dumps(preflight, indent=2, sort_keys=True))
            return 1
        request = build_deep_dive_enrichment_request(SOURCE_RUN)
        brief = read_workbook_brief(SOURCE_RUN)
        from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: PLC0415
            DeepDiveEnrichedWriterResult as _Schema,
        )

        preflight.update(
            {
                "pass": True,
                "input_digests": {
                    name: _sha256_file(SOURCE_RUN / name) for name in SOURCE_ARTIFACTS
                },
                "request_digest": request.request_digest,
                "pool_packet_digest": request.pool_packet_digest,
                "pool_status": request.pool_status,
                "pool_row_count": len(request.pool_rows),
                "skeleton_authority_digest": request.skeleton.authority_digest,
                "skeleton_candidate_digest": request.skeleton.candidate_payload_digest,
                "brief_payload_digest": brief.payload_digest,
                "provider_schema_digest": provider_payload_digest(
                    _Schema.model_json_schema()
                ),
                "provider_normalizer_version": (
                    DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION
                ),
            }
        )
        print(json.dumps(preflight, indent=2, sort_keys=True))
        return 0

    attempt_id, attempt_root = _allocate_attempt_root()
    run_dir = attempt_root / "run"
    verdict_path = attempt_root / "verdict.json"
    verdict: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "probe_id": PROBE_ID,
        "story": "37.2b",
        "attempt_id": attempt_id,
        "started_at": datetime.now(UTC).isoformat(),
        "first_run_stands": True,
        "provider_call_limit": 1,
        "run_dir": run_dir.relative_to(ROOT).as_posix(),
        "pass": False,
    }
    try:
        from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: PLC0415
            LiveDeepDiveEnrichmentWriter,
        )

        input_digests = _stage_run(run_dir)
        verdict["input_digests"] = input_digests
        request = build_deep_dive_enrichment_request(run_dir)
        verdict.update(
            {
                "request_digest": request.request_digest,
                "pool_packet_digest": request.pool_packet_digest,
                "pool_row_count": len(request.pool_rows),
                "skeleton_authority_digest": request.skeleton.authority_digest,
                "skeleton_candidate_digest": request.skeleton.candidate_payload_digest,
            }
        )
        writer = LiveDeepDiveEnrichmentWriter()
        verdict["model_config_digest"] = writer.model_config_digest
        verdict["provider_schema_digest"] = writer.provider_schema_digest
        prompt_text = writer._system_prompt(request)  # noqa: SLF001 - identity capture
        verdict["prompt_text_digest"] = (
            "sha256:" + hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        )
        verdict["model"] = writer.model_config.default_model
        from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
            ProductionTrialEnvelope,
        )

        trial = ProductionTrialEnvelope.model_validate_json(
            (run_dir / "run.json").read_text("utf-8")
        )
        context = WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=COURSE_ROOT,
            encounter_mode="recorded",
            context_origin="operator_migrated",
            writer_execution_mode="live",
            deep_dive_enrichment_writer=writer,
        )
        output = run_workbook_review(
            run_dir=run_dir, trial_id=trial.trial_id, runtime_context=context
        )
        journal = json.loads(
            (run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME).read_text("utf-8")
        )
        replayed = run_workbook_review(
            run_dir=run_dir, trial_id=trial.trial_id, runtime_context=context
        )
        result_payload = output.get("deep_dive_enrichment")
        if result_payload is None:
            raise ValueError("probe run produced no enrichment result")
        result = DeepDiveEnrichedResultV1.model_validate_json(
            json.dumps(result_payload, separators=(",", ":")), strict=True
        )
        judge = _machine_judge(result)
        checks = {
            "exactly_one_provider_call": writer.calls_made == 1,
            "completed_journal": journal.get("state") == "completed",
            "zero_recall_replay": writer.calls_made == 1 and replayed == output,
            "journal_idempotency_present": bool(journal.get("idempotency_key")),
        }
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "checks": checks,
                "machine_judge": judge,
                "pass": bool(judge["pass"]) and all(checks.values()),
                "result_status": result.status,
                "known_losses": list(result.known_losses),
                "journal": journal,
                "receipt": output.get("deep_dive_enrichment_receipt"),
                "provider_calls": writer.calls_made,
            }
        )
    except Exception as exc:  # first-run-stands: record; never retry
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        journal_path = run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME
        try:
            if journal_path.is_file():
                journal = json.loads(journal_path.read_text("utf-8"))
                verdict["journal"] = journal
                verdict["journal_state"] = journal.get("state")
        except Exception as journal_exc:
            verdict["journal_capture_error"] = (
                f"{type(journal_exc).__name__}: {journal_exc}"
            )
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n", "utf-8")
    print(verdict_path.relative_to(ROOT).as_posix())
    print(json.dumps(verdict, sort_keys=True, default=str))
    return 0 if verdict.get("pass") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())

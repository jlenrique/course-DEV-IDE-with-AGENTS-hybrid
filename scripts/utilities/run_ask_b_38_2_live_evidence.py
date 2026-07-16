#!/usr/bin/env python3
"""One-shot, first-run-stands live component probe for Story 38.2 (Ask-B).

Probe registration (D3 M-D3-2a — registered BEFORE it runs):
  probe id: probe-38-2-ask-b-hot-topics-001
  licensed claim (exact, and nothing broader): "the ask_b_hot_topics@07W.4
  seam, given a real ready beat-③ demand on the frozen Tejal Part-2 corpus,
  completes one dispatcher invocation and mints a strict Ask-B packet whose
  digest reloads stably and replays with zero calls."
  judge: deterministic machine judge below (dispatcher count, journal state,
  entry/association/credibility fields, packet digest reload equality,
  zero-call replay). A probe green licenses ONLY the claim above — never
  "the pipeline works".

Pre-declared verdict-class rule (M-5 + J-2): ``completed_empty`` freezes as a
VALID seam witness (verdict class COMPLETED_EMPTY_SEAM_WITNESS, exit 3) — the
zero-witness rule is satisfied for the call path, but the usable-mint half of
the registered claim stays OPEN (neither passed nor failed). Boarding run B on
an empty probe requires an EXPLICIT governed acknowledgment line in the run-B
authorization — never a silent pass, never retry-to-green. A persistently
empty Ask-B yields an empty-honest Door-Ajar at 39.2: the designed honest
outcome, not a defect.

Seed: the frozen 37-2b closure lineage ``deep-dive-enrichment-37-2b-838524b8``
(real ratified 07W.1 brief with AUTHORED scene + promise, completed band
predecessors, and a persisted ``not_yet_wired`` Ask-B stub at 07W.4 — so the
probe exercises the exact production resume-skip upgrade path through
``run_workbook_band_node``, not a side channel).

First-run-stands: a failed attempt is preserved immutably; no retry-to-green
without a governed correction. On success, the frozen journal becomes the
``ask-b-hot-topics-call.v1`` family's first witness — flip the pending row in
``tests/live_witness_replay/witnesses.yaml`` to ``disposition: enrolled`` and
point it at the frozen attempt journal.
"""

from __future__ import annotations

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

from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WorkbookBriefRuntimeContext,
    read_workbook_brief,
)
from app.marcus.lesson_plan.research_demand import (  # noqa: E402
    resolve_hot_topics_demand,
)
from app.marcus.lesson_plan.research_packet import (  # noqa: E402
    REQUIRED_ENTRY_FIELDS,
    resolve_for_hot_topics,
)
from app.marcus.orchestrator import ask_b_research_wiring, workbook_wiring  # noqa: E402
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)

PROBE_ID = "probe-38-2-ask-b-hot-topics-001"
LICENSED_CLAIM = (
    "the ask_b_hot_topics@07W.4 seam, given a real ready beat-③ demand on the "
    "frozen Tejal Part-2 corpus, completes one dispatcher invocation and mints "
    "a strict Ask-B packet whose digest reloads stably and replays with zero "
    "calls"
)
SOURCE_RUN = ROOT / (
    "_bmad-output/implementation-artifacts/evidence/"
    "deep-dive-enrichment-37-2b-838524b8/run"
)
COURSE_ROOT = ROOT / "course-content/courses/tejal-apc-c1-m1-p2-trends"
EVIDENCE_ROOT = ROOT / "_bmad-output/implementation-artifacts/evidence"


def _allocate_attempt_root() -> tuple[str, Path]:
    """Claim one unique evidence directory without an exists/mkdir race."""
    while True:
        attempt_id = str(uuid4())
        attempt_root = EVIDENCE_ROOT / f"ask-b-38-2-live-{attempt_id[:8]}"
        try:
            attempt_root.mkdir(parents=True)
        except FileExistsError:
            continue
        return attempt_id, attempt_root


def main() -> int:
    attempt_id, attempt_root = _allocate_attempt_root()
    run_dir = attempt_root / "run"
    verdict_path = attempt_root / "verdict.json"
    dispatch_calls = 0
    verdict: dict[str, object] = {
        "schema_version": "ask-b-38-2-live-evidence.v1",
        "story": "38.2",
        "probe_id": PROBE_ID,
        "licensed_claim": LICENSED_CLAIM,
        "attempt_id": attempt_id,
        "started_at": datetime.now(UTC).isoformat(),
        "first_run_stands": True,
        "provider_call_limit": 1,
        "run_dir": run_dir.relative_to(ROOT).as_posix(),
        "verdict_class": "FAIL",
        "pass": False,
    }
    try:
        shutil.copytree(SOURCE_RUN, run_dir)
        trial = ProductionTrialEnvelope.model_validate_json(
            (run_dir / "run.json").read_text("utf-8")
        )
        source_trial_id = trial.trial_id
        fresh_trial_id = uuid4()
        trial = trial.model_copy(
            update={
                "trial_id": fresh_trial_id,
                "production_envelope": trial.production_envelope.model_copy(
                    update={"trial_id": fresh_trial_id}
                ),
            }
        )
        (run_dir / "run.json").write_text(
            trial.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if (run_dir / ask_b_research_wiring.JOURNAL_FILENAME).exists():
            raise ValueError("fresh attempt unexpectedly copied an Ask-B journal")
        stub = trial.production_envelope.get_contribution(
            "ask_b_hot_topics", node_id="07W.4"
        )
        if stub is None or stub.output.get("stub_status") != "not_yet_wired":
            raise ValueError(
                "seed run must carry the persisted not_yet_wired Ask-B stub "
                "(resume-skip upgrade path)"
            )
        brief = read_workbook_brief(run_dir)
        demand = resolve_hot_topics_demand(run_dir)
        if demand.status != "ready":
            raise ValueError(
                f"seed demand is not ready: {demand.status} {demand.known_losses}"
            )
        verdict["demand"] = demand.model_dump(mode="json")
        verdict["scene_bound"] = demand.scene_digest is not None

        # Count dispatcher invocations by wrapping the REAL production
        # dispatch seam (the wrapper only counts; the call is live).
        real_dispatch = ask_b_research_wiring._default_dispatch

        def counting_dispatch(intent: object) -> object:
            nonlocal dispatch_calls
            dispatch_calls += 1
            return real_dispatch(intent)

        ask_b_research_wiring._default_dispatch = counting_dispatch
        context = WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=COURSE_ROOT,
            encounter_mode=brief.payload.encounter_mode,
            context_origin="operator_migrated",
            writer_execution_mode="live",
        )
        original_envelope = trial.production_envelope.model_copy(deep=True)
        updated = workbook_wiring.run_workbook_band_node(
            node_id="07W.4",
            production_envelope=original_envelope,
            runtime_context=context,
            dispatch_live=True,
        )
        trial.production_envelope = updated
        (run_dir / "run.json").write_text(
            trial.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        contribution = updated.get_contribution("ask_b_hot_topics", node_id="07W.4")
        if contribution is None:
            raise ValueError("Ask-B contribution missing after dispatch")
        journal = json.loads(
            (run_dir / ask_b_research_wiring.JOURNAL_FILENAME).read_text("utf-8")
        )
        disposition = contribution.output.get("disposition")

        # Reload equality: every consumer witnesses the same packet digest.
        first_packet = resolve_for_hot_topics(run_dir)
        second_packet = resolve_for_hot_topics(run_dir)
        usable_minted = bool(first_packet.usable)
        if usable_minted:
            resolve_for_hot_topics(run_dir, require_usable=True)

        # Zero-call replay through the SAME production seam.
        replayed = workbook_wiring.run_workbook_band_node(
            node_id="07W.4",
            production_envelope=updated,
            runtime_context=context,
            dispatch_live=True,
        )
        entries = contribution.output.get("research_entries") or []
        vow_ids = {ability.ability_id for ability in demand.abilities}
        entry_checks = bool(entries) and all(
            REQUIRED_ENTRY_FIELDS.issubset(entry.keys())
            and entry.get("provider_provenance")
            and entry.get("supports_ability_ids")
            and set(entry["supports_ability_ids"]) <= vow_ids
            and entry.get("evidence_excerpt")
            and entry.get("evidence_body_sha256")
            for entry in entries
        )
        checks = {
            "exactly_one_dispatcher_invocation": dispatch_calls == 1,
            "completed_journal": journal.get("state") == "completed",
            "completed_disposition": str(disposition).startswith("completed"),
            "execution_receipt_present": bool(
                (contribution.output.get("research_intake") or {}).get(
                    "execution_receipt"
                )
            ),
            "packet_digest_reload_equality": (
                first_packet.packet_digest == second_packet.packet_digest
            ),
            "zero_call_replay": dispatch_calls == 1 and replayed is updated,
            "node_specific_marker": (
                contribution.model_used == "deterministic-ask-b-hot-topics-wiring"
            ),
            "fresh_trial_identity": (
                trial.trial_id == trial.production_envelope.trial_id
                and trial.trial_id != source_trial_id
            ),
            "usable_rows_ability_associated_with_credibility": entry_checks,
        }
        seam_checks_green = all(
            value for name, value in checks.items()
            if name != "usable_rows_ability_associated_with_credibility"
        )
        if seam_checks_green and entry_checks:
            verdict_class = "PASS_USABLE_MINT"
        elif seam_checks_green and disposition == "completed_empty":
            # M-5/J-2: VALID seam witness; usable-mint half of the claim OPEN.
            verdict_class = "COMPLETED_EMPTY_SEAM_WITNESS"
        else:
            verdict_class = "FAIL"
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "verdict_class": verdict_class,
                "pass": verdict_class == "PASS_USABLE_MINT",
                "usable_mint_claim": (
                    "PASS"
                    if verdict_class == "PASS_USABLE_MINT"
                    else (
                        "OPEN — governed acknowledgment REQUIRED before run-B "
                        "boarding (M-5/J-2)"
                        if verdict_class == "COMPLETED_EMPTY_SEAM_WITNESS"
                        else "FAIL"
                    )
                ),
                "checks": checks,
                "dispatcher_invocations": dispatch_calls,
                "disposition": disposition,
                "known_losses": contribution.output.get("known_losses"),
                "entry_count": len(entries),
                "packet_digest": first_packet.packet_digest,
                "packet_status": first_packet.status,
                "journal": journal,
                "trial_id": str(trial.trial_id),
                "witness_enrollment_hint": {
                    "family": "ask-b-hot-topics-call.v1",
                    "id": f"ask-b-38-2-live-{attempt_id[:8]}",
                    "path": (
                        run_dir / ask_b_research_wiring.JOURNAL_FILENAME
                    ).relative_to(ROOT).as_posix(),
                    "state": journal.get("state"),
                    "disposition": "enrolled",
                    "capture": {
                        "idempotency_key": journal.get("idempotency_key"),
                        "provider_config_fingerprint": (
                            (journal.get("scope") or {}).get(
                                "provider_config_fingerprint"
                            )
                        ),
                    },
                },
            }
        )
    except Exception as exc:  # first-run-stands: record; never retry
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "dispatcher_invocations": dispatch_calls,
            }
        )
        journal_path = run_dir / ask_b_research_wiring.JOURNAL_FILENAME
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
    if verdict.get("verdict_class") == "PASS_USABLE_MINT":
        return 0
    if verdict.get("verdict_class") == "COMPLETED_EMPTY_SEAM_WITNESS":
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

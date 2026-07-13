#!/usr/bin/env python3
"""One-shot, first-run-stands live witness for Story 38.3a."""

from __future__ import annotations

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

from app.marcus.lesson_plan.prework_artifact import (  # noqa: E402
    WorkbookBriefRuntimeContext,
    read_workbook_brief,
)
from app.marcus.lesson_plan.research_demand import resolve_enrichment_demand  # noqa: E402
from app.marcus.orchestrator import workbook_wiring  # noqa: E402
from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: E402
    WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS,
    LiveDeepDiveWriter,
)
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from app.specialists.workbook_producer._act import (  # noqa: E402
    _reconcile_workbook_brief_authority,
)

SOURCE_RUN = ROOT / (
    "_bmad-output/implementation-artifacts/evidence/"
    "prework-36-4-fresh-input-380ecd47/run"
)
COURSE_ROOT = ROOT / "course-content/courses/tejal-apc-c1-m1-p2-trends"
EVIDENCE_ROOT = ROOT / "_bmad-output/implementation-artifacts/evidence"
FAILED_PINS = {
    "deep-dive-38-3a-live-7ed48f8a/verdict.json": (
        1872,
        "d46681f0402c8f9d280a933f9584773dade6b5a7d84880ae3fd324c2d10ca5cb",
    ),
    "deep-dive-38-3a-live-7ed48f8a/run/workbook-deep-dive-call.v1.json": (
        7123,
        "1dafe2196a97a2262dd59c3d8d802ea93be6a7ee1ab11f77748ae9a2f857768a",
    ),
    "deep-dive-38-3a-live-b6fc76ea/verdict.json": (
        9408,
        "acb3e3f98f26c3563412f1a49f9c73ca0913594a4b1c3bb52de8059536bd801f",
    ),
    "deep-dive-38-3a-live-b6fc76ea/run/workbook-deep-dive-call.v1.json": (
        7105,
        "212d48f9dfcf0ac9f769d11571036eaa4e0c097cbdd6d917f0f687a602da4dcf",
    ),
}
FAILED_JOURNAL_IDENTITIES = {
    "deep-dive-38-3a-live-7ed48f8a/run/workbook-deep-dive-call.v1.json": (
        "sha256:de31a3f58b4987fbb87e88df8f72acc04de1e564a454ed6c13e584137027f32f"
    ),
    "deep-dive-38-3a-live-b6fc76ea/run/workbook-deep-dive-call.v1.json": (
        "sha256:a0ac1ea3e7340f6650fb29fe499bf09b99f8e3b2d4e120925766470bf0de6fb6"
    ),
}


def _assert_failed_evidence_preserved() -> dict[str, object]:
    observed: dict[str, object] = {}
    for relative, (expected_size, expected_digest) in FAILED_PINS.items():
        path = EVIDENCE_ROOT / relative
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != expected_size or digest != expected_digest:
            raise ValueError(f"failed evidence preservation mismatch: {relative}")
        observed[relative] = {"size": len(data), "sha256": digest}
    for relative, idempotency_key in FAILED_JOURNAL_IDENTITIES.items():
        journal = json.loads((EVIDENCE_ROOT / relative).read_text("utf-8"))
        if (
            journal.get("state") != "call_in_progress"
            or journal.get("idempotency_key") != idempotency_key
        ):
            raise ValueError("failed journal state/idempotency preservation mismatch")
    return observed


def _allocate_attempt_root() -> tuple[str, Path]:
    """Claim one unique evidence directory without an exists/mkdir race."""
    while True:
        attempt_id = str(uuid4())
        attempt_root = EVIDENCE_ROOT / f"deep-dive-38-3a-live-{attempt_id[:8]}"
        try:
            attempt_root.mkdir(parents=True)
        except FileExistsError:
            continue
        return attempt_id, attempt_root


def main() -> int:
    attempt_id, attempt_root = _allocate_attempt_root()
    run_dir = attempt_root / "run"
    verdict_path = attempt_root / "verdict.json"
    verdict: dict[str, object] = {
        "schema_version": "deep-dive-38-3a-live-evidence.v1",
        "story": "38.3a",
        "attempt_id": attempt_id,
        "started_at": datetime.now(UTC).isoformat(),
        "first_run_stands": True,
        "provider_call_limit": 1,
        "run_dir": run_dir.relative_to(ROOT).as_posix(),
        "pass": False,
    }
    try:
        preservation_before = _assert_failed_evidence_preserved()
        verdict["failed_evidence_preservation_before"] = preservation_before
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
        copied_journal = run_dir / workbook_wiring.DEEP_DIVE_JOURNAL_FILENAME
        if copied_journal.exists():
            raise ValueError("fresh post-fix run unexpectedly copied a call journal")
        original_envelope = trial.production_envelope.model_copy(deep=True)
        before = read_workbook_brief(run_dir)
        if before.payload.deep_dive_skeleton is not None:
            raise ValueError("frozen source brief is not a legacy-null substrate")
        writer = LiveDeepDiveWriter()
        context = WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=COURSE_ROOT,
            encounter_mode=before.payload.encounter_mode,
            context_origin="operator_migrated",
            writer_execution_mode="live",
            deep_dive_writer=writer,
        )
        updated = workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=original_envelope,
            runtime_context=context,
        )
        after = read_workbook_brief(run_dir)
        trial.production_envelope = updated
        (run_dir / "run.json").write_text(
            trial.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        demand = resolve_enrichment_demand(run_dir)
        state = RunState(
            graph_version="v42",
            status="running",
            production_envelope=updated,
            component_selection=ComponentSelection(deck=True, workbook=True),
        )
        terminal = _reconcile_workbook_brief_authority(state, run_dir)
        replayed = workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=original_envelope,
            runtime_context=context,
        )
        journal = json.loads(
            (run_dir / workbook_wiring.DEEP_DIVE_JOURNAL_FILENAME).read_text("utf-8")
        )
        skeleton = after.payload.deep_dive_skeleton
        receipt = after.payload.deep_dive_writer_receipt
        checks = {
            "exactly_one_provider_call": writer.calls_made == 1,
            "completed_journal": journal.get("state") == "completed",
            "passing_gate": skeleton is not None and skeleton.gate.status == "pass",
            "authored_skeleton": skeleton is not None and skeleton.status == "authored",
            "nonempty_terms": bool(skeleton and skeleton.bold_terms),
            "ready_demand": demand.status == "ready",
            "terminal_reconciled": terminal == after,
            "zero_recall_replay": (
                writer.calls_made == 1
                and replayed.get_contribution("workbook_brief", node_id="07W.1").output
                == updated.get_contribution("workbook_brief", node_id="07W.1").output
            ),
            "prework_preserved": after.payload.pre_work == before.payload.pre_work,
            "fresh_nested_trial_identity": (
                trial.trial_id == trial.production_envelope.trial_id
                and trial.trial_id != source_trial_id
                and str(trial.trial_id) != attempt_id
            ),
            "deep_dive_32k_bound": (
                writer._handle.chat.max_tokens  # noqa: SLF001
                == WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS
            ),
            "failed_evidence_preserved_after": (
                _assert_failed_evidence_preserved() == preservation_before
            ),
        }
        verdict.update(
            {
                "completed_at": datetime.now(UTC).isoformat(),
                "pass": all(checks.values()),
                "checks": checks,
                "journal": journal,
                "payload_digest": after.payload_digest,
                "prior_payload_digest": before.payload_digest,
                "deep_dive_status": skeleton.status if skeleton else None,
                "gate_status": skeleton.gate.status if skeleton else None,
                "gate_failures": list(skeleton.gate.failures) if skeleton else None,
                "bold_terms": [term.term for term in skeleton.bold_terms] if skeleton else [],
                "demand": demand.model_dump(mode="json"),
                "receipt": receipt.model_dump(mode="json") if receipt else None,
                "provider_calls": writer.calls_made,
                "trial_id": str(trial.trial_id),
                "model_config_digest": writer.model_config_digest,
                "max_completion_tokens": WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS,
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
        journal_path = run_dir / workbook_wiring.DEEP_DIVE_JOURNAL_FILENAME
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
    print(json.dumps(verdict, sort_keys=True))
    return 0 if verdict.get("pass") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())

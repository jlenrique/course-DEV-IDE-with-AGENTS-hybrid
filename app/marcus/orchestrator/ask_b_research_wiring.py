"""Exactly-once Ask-B hot-topics dispatch and crash-safe replay at ``07W.4``.

Mirror of ``ask_a_research_wiring`` at the ``ask-b.*`` coordinates (38.2):
own lock, own journal, own idempotency key, own scope digest — never reads
or mutates the Ask-A journal, the ``04.55`` bridge output, or their locks.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Final

from app.marcus.lesson_plan.ask_b_hot_topics import (
    AskBContributionOutputV1,
    AskBExecutionReceiptV1,
    AskBKnowledgeEntryV1,
    AskBResearchIntakeV1,
    AskBRetrievalScopeV1,
    build_scope,
    canonical_digest,
    evidence_for_body,
    match_ability_associations,
)
from app.marcus.lesson_plan.research_demand import (
    ResearchDemandShapeError,
    resolve_hot_topics_demand,
)
from app.marcus.orchestrator.research_citation import (
    compute_source_hash,
    derive_source_ref,
)
from app.marcus.orchestrator.research_credibility import (
    classify_evidence_hierarchy,
    provider_provenance_for_row,
)
from app.specialists.dispatch_errors import SpecialistDispatchError

JOURNAL_FILENAME: Final[str] = "ask-b-hot-topics-call.v1.json"
LOCK_FILENAME: Final[str] = "ask-b-hot-topics-call.v1.lock"
JOURNAL_SCHEMA_VERSION: Final[str] = "ask-b-hot-topics-call.v1"
_FINGERPRINT = canonical_digest(
    {"provider": "scite", "adapter": "retrieval.dispatcher", "contract": "ask-b.v1"}
)


def _raise(message: str, tag: str, *, cause: Exception | None = None) -> None:
    error = SpecialistDispatchError(message, tag=tag)
    if cause is None:
        raise error
    raise error from cause


def _contained_regular(path: Path, root: Path, *, allow_absent: bool = False) -> bool:
    if path.is_symlink():
        _raise("Ask-B coordinate may not be a symlink", "ask-b.reconciliation-failed")
    if not path.exists():
        return allow_absent
    if not path.is_file():
        _raise("Ask-B coordinate must be a regular file", "ask-b.reconciliation-failed")
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        _raise("Ask-B coordinate escapes its run", "ask-b.reconciliation-failed", cause=exc)
    return True


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.is_symlink() or temporary.is_symlink() or temporary.exists():
        raise OSError("unsafe or colliding Ask-B journal coordinate")
    created = False
    try:
        with temporary.open("x", encoding="utf-8", newline="") as handle:
            created = True
            handle.write(
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if created and temporary.exists() and not temporary.is_symlink():
            temporary.unlink()
        raise


def _read_journal(path: Path, run_dir: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    _contained_regular(path, run_dir)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _raise("Ask-B journal is unreadable", "ask-b.reconciliation-failed", cause=exc)
    if not isinstance(value, dict) or value.get("schema_version") != JOURNAL_SCHEMA_VERSION:
        _raise("Ask-B journal schema mismatch", "ask-b.reconciliation-failed")
    return value


def _build_intent(scope: AskBRetrievalScopeV1) -> Any:
    from app.marcus.orchestrator.research_wiring import _import_retrieval  # noqa: PLC0415

    retrieval_intent, _, _ = _import_retrieval()
    from retrieval import AcceptanceCriteria, ProviderHint  # noqa: PLC0415

    return retrieval_intent(
        intent=scope.query,
        provider_hints=[
            ProviderHint(
                provider="scite",
                params={
                    "mode": "search",
                    "posture": scope.posture,
                    "scope_digest": scope.scope_digest,
                },
            )
        ],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1},
            provider_scored={},
            semantic_deferred="trend-claim audit remains downstream (39.2)",
        ),
        iteration_budget=3,
        convergence_required=True,
        cross_validate=False,
    )


def _default_dispatch(intent: Any) -> Any:
    from app.marcus.orchestrator.research_wiring import _import_retrieval  # noqa: PLC0415

    _, dispatch, _ = _import_retrieval()
    return dispatch(intent)


def _credentials_present() -> bool:
    from app.marcus.orchestrator.research_wiring import _scite_creds_present  # noqa: PLC0415

    return _scite_creds_present()


def _snapshot_row(row: Any) -> dict[str, Any]:
    return {
        "provider": getattr(row, "provider", None),
        "source_id": getattr(row, "source_id", None),
        "title": getattr(row, "title", ""),
        "body": getattr(row, "body", None),
        "provider_metadata": getattr(row, "provider_metadata", {}) or {},
        "authority_tier": getattr(row, "authority_tier", None),
    }


def _normalize_results(
    result: Any,
) -> tuple[
    list[dict[str, Any]],
    tuple[int, ...],
    tuple[dict[str, Any], ...],
    tuple[str, ...],
    tuple[dict[str, Any], ...],
]:
    provider_results = result if isinstance(result, list) else [result]
    rows: list[dict[str, Any]] = []
    iterations: list[int] = []
    logs: list[dict[str, Any]] = []
    outcomes: list[str] = []
    receipts: list[dict[str, Any]] = []
    for item in provider_results:
        provider = str(getattr(item, "provider", "") or "")
        accepted = bool(getattr(item, "acceptance_met", False))
        iteration = int(getattr(item, "iterations_used", 0))
        iterations.append(iteration)
        raw_logs = getattr(item, "refinement_log", ()) or ()
        for raw in raw_logs:
            logs.append(raw.model_dump(mode="json") if hasattr(raw, "model_dump") else dict(raw))
        outcomes.append("accepted" if accepted else "not_accepted")
        receipts.append(
            {
                "provider": provider,
                "acceptance_met": accepted,
                "iterations_used": iteration,
                "row_count": len(getattr(item, "rows", ()) or ()),
            }
        )
        if accepted:
            rows.extend(_snapshot_row(row) for row in (getattr(item, "rows", ()) or ()))
    return rows, tuple(iterations), tuple(logs), tuple(outcomes), tuple(receipts)


def _build_completed(
    scope: AskBRetrievalScopeV1,
    *,
    raw_rows: list[dict[str, Any]],
    provider_iterations: tuple[int, ...],
    refinement_logs: tuple[dict[str, Any], ...],
    provider_outcomes: tuple[str, ...],
    provider_receipts: tuple[dict[str, Any], ...],
) -> tuple[AskBContributionOutputV1, list[dict[str, Any]]]:
    candidates: list[
        tuple[int, Any, tuple[str, ...], dict[str, tuple[str, ...]], str, bool, str]
    ] = []
    # Scope losses (scene_identity_absent) lead the completed loss order so the
    # ready-with-loss demand branch stays visible in the packet known_losses.
    losses: list[str] = list(scope.known_scope_losses)
    records: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_rows):
        row = SimpleNamespace(**raw)
        provider = raw.get("provider")
        source_id = raw.get("source_id")
        body = raw.get("body")
        if (
            not isinstance(provider, str)
            or not provider.strip()
            or not isinstance(source_id, str)
            or not source_id.strip()
        ):
            losses.append(f"ask_b_row_source_invalid:{index}")
            records.append({"index": index, "disposition": "source_invalid"})
            continue
        try:
            excerpt, truncated, body_hash = evidence_for_body(body)
        except ValueError:
            losses.append(f"ask_b_row_evidence_invalid:{index}")
            records.append({"index": index, "disposition": "evidence_invalid"})
            continue
        tier, peer_reviewed = classify_evidence_hierarchy(row)
        provenance = tuple(provider_provenance_for_row(row))
        if tier in {"T7_secondary_media", "T8_unknown"} or not provenance:
            losses.append(f"ask_b_row_credibility_excluded:{index}")
            records.append({"index": index, "disposition": "credibility_excluded", "tier": tier})
            continue
        # Associations are matched over the SAME window that is stored as
        # ``evidence_excerpt`` (mirror of the Ask-A Scout MED #3 discipline).
        abilities, matched_tokens = match_ability_associations(
            scope, title=str(raw.get("title") or ""), body=excerpt
        )
        if not abilities:
            losses.append(f"ask_b_row_ability_unassociated:{index}")
            records.append({"index": index, "disposition": "ability_unassociated"})
            continue
        source_ref = derive_source_ref(provider, source_id)
        candidates.append(
            (index, row, abilities, matched_tokens, excerpt, truncated, body_hash)
        )
        records.append({"index": index, "disposition": "candidate", "source_ref": source_ref})

    seen: set[str] = set()
    entries: list[AskBKnowledgeEntryV1] = []
    for raw_index, row, abilities, matched_tokens, excerpt, truncated, body_hash in candidates:
        source_ref = derive_source_ref(row.provider, row.source_id)
        if source_ref in seen:
            losses.append(f"ask_b_row_duplicate:{raw_index}")
            records[raw_index] = {
                "index": raw_index,
                "disposition": "duplicate",
                "source_ref": source_ref,
            }
            continue
        seen.add(source_ref)
        tier, peer_reviewed = classify_evidence_hierarchy(row)
        entries.append(
            AskBKnowledgeEntryV1(
                citation_id=f"ask-b-cite-{len(entries) + 1:03d}",
                source_ref=source_ref,
                provider=row.provider,
                source_id=row.source_id,
                title=str(row.title or ""),
                source_hash=compute_source_hash(row),
                evidence_hierarchy_tier=tier,
                peer_reviewed=peer_reviewed,
                provider_provenance=tuple(provider_provenance_for_row(row)),
                triangulation_status="single_provider",
                reliability_score=None,
                evidence_excerpt=excerpt,
                evidence_truncated=truncated,
                evidence_body_sha256=body_hash,
                scope_digest=scope.scope_digest,
                supports_ability_ids=abilities,
                association_algorithm="ask-b-association.v1",
                matched_ability_tokens=matched_tokens,
            )
        )
    receipt = AskBExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=provider_iterations,
        refinement_logs=refinement_logs,
        provider_outcomes=provider_outcomes,
        provider_receipts=provider_receipts,
    )
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=tuple(entries)
    )
    disposition = (
        "completed_empty"
        if not entries
        else ("completed_degraded" if losses else "completed_ready")
    )
    output = AskBContributionOutputV1.build_completed(
        disposition=disposition, intake=intake, entries=tuple(entries), known_losses=tuple(losses)
    )
    return output, records


def _idempotency_key(*, trial_id: object, scope: AskBRetrievalScopeV1) -> str:
    return canonical_digest(
        {
            "trial_id": str(trial_id),
            "demand_digest": scope.demand_digest,
            "scope_digest": scope.scope_digest,
            "query_digest": scope.query_digest,
            "provider_config_fingerprint": scope.provider_config_fingerprint,
        }
    )


def _replay_completed(
    journal: dict[str, Any], scope: AskBRetrievalScopeV1, trial_id: object
) -> AskBContributionOutputV1:
    if journal.get("state") == "call_in_progress":
        _raise("Ask-B external-call outcome is ambiguous", "ask-b.call-ambiguous")
    if journal.get("state") != "completed":
        _raise("Ask-B journal state is invalid", "ask-b.reconciliation-failed")
    if journal.get("idempotency_key") != _idempotency_key(
        trial_id=trial_id, scope=scope
    ) or journal.get("scope") != scope.model_dump(mode="json"):
        _raise("Ask-B journal scope/idempotency mismatch", "ask-b.reconciliation-failed")
    try:
        output, records = _build_completed(
            scope,
            raw_rows=journal["raw_rows"],
            provider_iterations=tuple(journal["provider_iterations"]),
            refinement_logs=tuple(journal["refinement_logs"]),
            provider_outcomes=tuple(journal["provider_outcomes"]),
            provider_receipts=tuple(journal["provider_receipts"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        _raise(
            "Ask-B completed journal cannot be replayed", "ask-b.reconciliation-failed", cause=exc
        )
    if (
        journal.get("normalization_records") != records
        or journal.get("output") != output.model_dump(mode="json")
        or journal.get("output_digest") != output.output_digest
    ):
        _raise("Ask-B completed journal output mismatch", "ask-b.reconciliation-failed")
    return output


def run_ask_b_research(
    *,
    run_dir: Path,
    trial_id: object,
    dispatch_live: bool,
    provider_config_fingerprint: str | None = None,
    dispatch: Callable[[Any], Any] | None = None,
) -> AskBContributionOutputV1:
    """Resolve exact Ask-B demand and return a retryable or journal-backed output."""
    run_dir = Path(run_dir)
    try:
        run_dir.resolve(strict=True)
    except OSError as exc:
        _raise("Ask-B run directory is unavailable", "ask-b.reconciliation-failed", cause=exc)
    try:
        demand = resolve_hot_topics_demand(run_dir)
    except (ResearchDemandShapeError, ValueError) as exc:
        _raise("Ask-B demand is invalid", "ask-b.demand-invalid", cause=exc)
    if demand.status != "ready":
        return AskBContributionOutputV1.build_retryable(
            disposition="retryable_demand_not_ready", loss="ask_b_demand_not_ready"
        )
    try:
        limit = int(os.getenv("MARCUS_ASK_B_QUERY_MAX_CHARS", "8192"))
    except ValueError as exc:
        _raise("Ask-B query limit is invalid", "ask-b.scope-overflow", cause=exc)
    fingerprint = canonical_digest(
        {
            "adapter_fingerprint": provider_config_fingerprint or _FINGERPRINT,
            "query_limit": limit,
        }
    )
    scope = build_scope(demand, provider_config_fingerprint=fingerprint)
    if limit < 1 or len(scope.query) > limit:
        _raise("Ask-B complete scope exceeds provider query limit", "ask-b.scope-overflow")
    journal_path = run_dir / JOURNAL_FILENAME
    lock_path = run_dir / LOCK_FILENAME
    journal = _read_journal(journal_path, run_dir)
    if journal is not None:
        return _replay_completed(journal, scope, trial_id)
    if lock_path.exists():
        _contained_regular(lock_path, run_dir)
        _raise("Ask-B call claim exists without a completed journal", "ask-b.call-ambiguous")
    if not dispatch_live:
        return AskBContributionOutputV1.build_retryable(
            disposition="retryable_dispatch_disabled", loss="ask_b_dispatch_disabled"
        )
    if dispatch is None and not _credentials_present():
        return AskBContributionOutputV1.build_retryable(
            disposition="retryable_credentials_unavailable", loss="ask_b_credentials_unavailable"
        )
    try:
        with lock_path.open("x", encoding="utf-8", newline="") as lock:
            lock.write(scope.scope_digest + "\n")
            lock.flush()
            os.fsync(lock.fileno())
    except FileExistsError as exc:
        _raise("Ask-B call claim is already held", "ask-b.call-ambiguous", cause=exc)
    except OSError as exc:
        _raise("Ask-B call claim could not be created", "ask-b.dispatch-init-failed", cause=exc)
    idempotency_key = _idempotency_key(trial_id=trial_id, scope=scope)
    pre_call = {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "state": "call_in_progress",
        "idempotency_key": idempotency_key,
        "scope": scope.model_dump(mode="json"),
    }
    try:
        _atomic_json(journal_path, pre_call)
    except OSError as exc:
        _raise("Ask-B pre-call journal write failed", "ask-b.dispatch-init-failed", cause=exc)
    intent = _build_intent(scope)
    try:
        result = (dispatch or _default_dispatch)(intent)
    except Exception as exc:
        _raise("Ask-B provider execution failed", "ask-b.provider-execution-failed", cause=exc)
    try:
        raw_rows, iterations, logs, outcomes, receipts = _normalize_results(result)
        output, records = _build_completed(
            scope,
            raw_rows=raw_rows,
            provider_iterations=iterations,
            refinement_logs=logs,
            provider_outcomes=outcomes,
            provider_receipts=receipts,
        )
    except (TypeError, ValueError) as exc:
        _raise("Ask-B provider output is invalid", "ask-b.output-invalid", cause=exc)
    completed = {
        **pre_call,
        "state": "completed",
        "raw_rows": raw_rows,
        "provider_iterations": list(iterations),
        "refinement_logs": list(logs),
        "provider_outcomes": list(outcomes),
        "provider_receipts": list(receipts),
        "normalization_records": records,
        "research_intake": output.research_intake.model_dump(mode="json"),
        "output": output.model_dump(mode="json"),
        "output_digest": output.output_digest,
    }
    try:
        _atomic_json(journal_path, completed)
    except OSError as exc:
        _raise("Ask-B completed journal write failed", "ask-b.persistence-failed", cause=exc)
    return output


__all__ = [
    "JOURNAL_FILENAME",
    "JOURNAL_SCHEMA_VERSION",
    "LOCK_FILENAME",
    "run_ask_b_research",
]

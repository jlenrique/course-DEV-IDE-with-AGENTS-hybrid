"""Exactly-once journaled Deep Dive enrichment dispatch at ``07W.3`` (Story 37.2b).

Mirrors the proven 07W.1 deep-dive seam (``workbook_wiring._compose_deep_dive``):
crash-safe exactly-once journal (bare ``call_in_progress`` = ambiguous hard
pause; ``call_in_progress`` WITH a recorded ``provider_failure`` = the distinct
``workbook-review.enrichment-prior-failure`` pause; ``completed`` replays with
ZERO provider calls; ``completed_without_dispatch`` is the zero-call empty-pool
honest decline, also replayed with zero calls), raw provider payload +
normalization records + idempotency key stored in-journal, stable node-scoped
error tags (``workbook-review.enrichment-*``) — never a generic factory failure.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Final, Literal

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER,
    POOL_EMPTY_LOSS,
    DeepDiveEnrichedResultV1,
    DeepDiveEnrichedWriterResult,
    DeepDiveEnrichmentAuthorityError,
    DeepDiveEnrichmentExecutionReceiptV1,
    DeepDiveEnrichmentRequestV1,
    DeepDiveSkeletonMissingError,
    DeepDiveSkeletonNotAuthoredError,
    build_deep_dive_enrichment_request,
    build_workbook_review_contribution,
    compose_deep_dive_enrichment,
    offline_deep_dive_enrichment_writer,
    skeleton_not_authored_loss,
)
from app.marcus.lesson_plan.deep_dive_enrichment_provider_contract import (
    DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_enrichment_provider_payload,
)
from app.marcus.lesson_plan.prework_artifact import (
    WORKBOOK_BRIEF_FILENAME,
    WorkbookBriefRuntimeContext,
)
from app.marcus.orchestrator.workbook_prework_writers import (
    DeepDiveEnrichmentProviderOutputError,
)
from app.specialists.dispatch_errors import SpecialistDispatchError

DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME: Final[str] = (
    "workbook-deep-dive-enrichment-call.v1.json"
)
DEEP_DIVE_ENRICHMENT_JOURNAL_SCHEMA_VERSION: Final[str] = (
    "workbook-deep-dive-enrichment-call.v1"
)
WORKBOOK_REVIEW_NODE_ID: Final[str] = "07W.3"
# R1: an EMPTY pool never dispatches the live writer — the journal records a
# zero-call honest-decline entry under its own replayable state.
JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH: Final[str] = "completed_without_dispatch"
# R10: raw provider text preserved in failure journals is bounded, never {}.
RAW_PROVIDER_TEXT_BOUND: Final[int] = 20_000

_JOURNAL_IDENTITY_KEYS: Final[tuple[str, ...]] = (
    "schema_version",
    "idempotency_key",
    "request_digest",
    "pool_packet_digest",
    "skeleton_authority_digest",
    "skeleton_candidate_digest",
    "model_config_digest",
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _raise(message: str, tag: str, *, cause: Exception | None = None) -> None:
    error = SpecialistDispatchError(message, tag=tag)
    if cause is None:
        raise error
    raise error from cause


def deep_dive_enrichment_idempotency_key(
    *,
    trial_id: object,
    request_digest: str,
    pool_packet_digest: str,
    model_config_digest: str,
) -> str:
    """Bind trial id, node, skeleton/pool digests, and provider/config identity."""
    return _sha256(
        {
            "trial_id": str(trial_id),
            "node_id": WORKBOOK_REVIEW_NODE_ID,
            "request_digest": request_digest,
            "pool_packet_digest": pool_packet_digest,
            "model_config_digest": model_config_digest,
        }
    )


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.is_symlink() or temporary.is_symlink():
        raise ValueError("enrichment journal path may not be a symlink")
    created = False
    try:
        with temporary.open("x", encoding="utf-8", newline="") as handle:
            created = True
            handle.write(_canonical_json(payload) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if created and temporary.exists() and not temporary.is_symlink():
            temporary.unlink()
        raise


def _journal_exists(run_dir: Path, journal_path: Path) -> bool:
    if journal_path.is_symlink():
        _raise(
            "enrichment journal may not be a symlink",
            "workbook-review.enrichment-reconciliation-failed",
        )
    if not journal_path.exists():
        return False
    if not journal_path.is_file():
        _raise(
            "enrichment journal is not a regular file",
            "workbook-review.enrichment-reconciliation-failed",
        )
    try:
        resolved_run = Path(run_dir).resolve(strict=True)
        journal_path.resolve(strict=True).relative_to(resolved_run)
    except (OSError, ValueError) as exc:
        _raise(
            "enrichment journal escapes its run root",
            "workbook-review.enrichment-reconciliation-failed",
            cause=exc,
        )
    return True


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object
    )
    if not isinstance(payload, dict):
        raise ValueError("journal root must be a mapping")
    return payload


def _recover_journal_temporary(run_dir: Path, journal_path: Path) -> None:
    """Recover only crash-identifiable enrichment-journal temporary states."""
    temporary = journal_path.with_suffix(journal_path.suffix + ".tmp")
    if temporary.is_symlink():
        _raise(
            "enrichment journal temporary may not be a symlink",
            "workbook-review.enrichment-reconciliation-failed",
        )
    if not temporary.exists():
        return
    try:
        temporary_payload = _read_json(temporary)
        if not journal_path.exists():
            if temporary_payload.get("state") != "call_in_progress":
                raise ValueError("orphan journal temporary is not pre-dispatch")
            temporary.unlink()
            return
        target_payload = _read_json(journal_path)
        if (
            target_payload.get("state") != "call_in_progress"
            or temporary_payload.get("state")
            not in {
                "call_in_progress",
                "completed",
                JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH,
            }
            or any(
                temporary_payload.get(key) != target_payload.get(key)
                for key in _JOURNAL_IDENTITY_KEYS
            )
        ):
            raise ValueError("journal temporary disagrees with committed call")
        os.replace(temporary, journal_path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        _raise(
            f"enrichment journal temporary recovery failed: {exc}",
            "workbook-review.enrichment-reconciliation-failed",
            cause=exc,
        )


def _live_model_config_digest(writer: object) -> str:
    """R18: the live journal identity digest MUST come from the writer.

    The all-zeros fallback is legal ONLY for offline/test writers (and is
    marked as such in the journal/receipt via ``mode``); a live writer without
    a ``model_config_digest`` attribute fails loud before any identity is
    minted.
    """
    digest = getattr(writer, "model_config_digest", None)
    if not isinstance(digest, str) or not digest:
        _raise(
            "live Deep Dive enrichment writer carries no model_config_digest "
            "(journal identity must come from the writer; the all-zeros "
            "fallback is offline-only)",
            "workbook-review.enrichment-writer-identity-missing",
        )
    return digest


def _execution_receipt(
    writer: object,
    *,
    mode: Literal["offline_stub", "live"],
    calls: Literal[0, 1],
    idempotency_key: str,
    model_config_digest: str,
    request: DeepDiveEnrichmentRequestV1,
) -> DeepDiveEnrichmentExecutionReceiptV1:
    config = getattr(writer, "model_config", None)
    cost_usd = getattr(writer, "last_cost_usd", None)
    cost_unavailable_reason = getattr(writer, "last_cost_unavailable_reason", None)
    if mode == "live" and calls == 1 and cost_usd is None and not cost_unavailable_reason:
        cost_unavailable_reason = "injected_writer_supplied_no_cost_evidence"
    return DeepDiveEnrichmentExecutionReceiptV1(
        mode=mode,
        calls=calls,
        idempotency_key=idempotency_key,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model=getattr(config, "default_model", None),
        model_config_digest=model_config_digest,
        request_id=getattr(writer, "last_request_id", None),
        latency_ms=getattr(writer, "last_latency_ms", None),
        input_tokens=getattr(writer, "last_input_tokens", None),
        output_tokens=getattr(writer, "last_output_tokens", None),
        cost_usd=cost_usd,
        cost_unavailable_reason=cost_unavailable_reason,
    )


def _provider_evidence(
    writer: object, candidate: DeepDiveEnrichedWriterResult | None = None
) -> dict[str, object]:
    raw = getattr(writer, "last_raw_provider_payload", None)
    if raw is None and candidate is not None:
        raw = candidate.model_dump(mode="json")
    if raw is None:
        return {}
    raw = json.loads(_canonical_json(raw))
    provider_schema = DeepDiveEnrichedWriterResult.model_json_schema()
    schema_digest = _sha256(provider_schema)
    observed_schema_digest = getattr(writer, "provider_schema_digest", None)
    if observed_schema_digest is not None and observed_schema_digest != schema_digest:
        raise ValueError("enrichment provider schema digest mismatch")
    evidence: dict[str, object] = {
        "provider_contract_mode": DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE,
        "provider_schema_digest": schema_digest,
        "provider_normalizer_version": DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION,
        "raw_provider_payload": raw,
        "raw_provider_payload_digest": _sha256(raw),
    }
    normalization_error = getattr(writer, "last_provider_normalization_error", None)
    if normalization_error:
        if candidate is not None:
            raise ValueError("successful candidate cannot carry a normalization error")
        evidence["provider_normalizations"] = list(
            getattr(writer, "last_provider_normalizations", ())
        )
        evidence["provider_normalization_error"] = normalization_error
        return evidence
    normalized, records = normalize_deep_dive_enrichment_provider_payload(raw)
    normalized_digest = _sha256(normalized)
    observed_records = getattr(writer, "last_provider_normalizations", None)
    if observed_records is not None and tuple(observed_records) != records:
        raise ValueError("enrichment provider normalization records mismatch")
    observed_digest = getattr(writer, "last_normalized_provider_payload_digest", None)
    if observed_digest is not None and observed_digest != normalized_digest:
        raise ValueError("enrichment provider normalized payload digest mismatch")
    if candidate is not None and normalized != candidate.model_dump(mode="json"):
        raise ValueError("enrichment provider normalized payload/candidate mismatch")
    evidence.update(
        {
            "provider_normalizations": list(records),
            "normalized_provider_payload_digest": normalized_digest,
        }
    )
    return evidence


def _persist_provider_failure(
    path: Path, base: dict[str, object], writer: object, exc: Exception
) -> None:
    failed = dict(base)
    failed.update(_provider_evidence(writer))
    # R10: on a provider parse failure the raw provider TEXT is preserved
    # (bounded) — the failure evidence is never an empty mapping.
    raw_text = getattr(writer, "last_raw_provider_text", None)
    if raw_text is not None:
        failed["raw_provider_text"] = str(raw_text)[:RAW_PROVIDER_TEXT_BOUND]
    elif "raw_provider_payload" not in failed:
        failed["raw_provider_text"] = (
            "<no raw provider payload or text was captured before the failure; "
            f"exception: {type(exc).__name__}: {exc}>"
        )[:RAW_PROVIDER_TEXT_BOUND]
    failed["provider_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    _atomic_json(path, failed)


def _check_journal_identity(
    journal: dict[str, Any],
    *,
    request: DeepDiveEnrichmentRequestV1,
    idempotency_key: str,
    model_config_digest: str,
) -> DeepDiveEnrichmentRequestV1:
    if journal.get("schema_version") != DEEP_DIVE_ENRICHMENT_JOURNAL_SCHEMA_VERSION:
        raise ValueError("journal schema mismatch")
    if journal.get("idempotency_key") != idempotency_key:
        raise ValueError("journal idempotency mismatch")
    if journal.get("model_config_digest") != model_config_digest:
        raise ValueError("journal model config mismatch")
    if journal.get("request_digest") != request.request_digest:
        raise ValueError("journal request digest mismatch")
    if journal.get("pool_packet_digest") != request.pool_packet_digest:
        raise ValueError("journal pool packet digest mismatch")
    if (
        journal.get("skeleton_authority_digest") != request.skeleton.authority_digest
        or journal.get("skeleton_candidate_digest")
        != request.skeleton.candidate_payload_digest
    ):
        raise ValueError("journal skeleton digest mismatch")
    saved_request = DeepDiveEnrichmentRequestV1.model_validate_json(
        _canonical_json(journal["request"]), strict=True
    )
    if saved_request != request:
        raise ValueError("journal request/authority mismatch")
    return saved_request


def _empty_pool_decline_candidate() -> DeepDiveEnrichedWriterResult:
    """The deterministic row-d honest-decline shape (R1: no paid call)."""
    return DeepDiveEnrichedWriterResult(
        status="degraded",
        sections=(),
        bold_terms=(),
        known_losses=(POOL_EMPTY_LOSS,),
        marker=DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER,
    )


def _replay_completed_without_dispatch(
    journal: dict[str, Any],
    *,
    request: DeepDiveEnrichmentRequestV1,
    idempotency_key: str,
    model_config_digest: str,
    writer: object,
) -> tuple[DeepDiveEnrichedResultV1, DeepDiveEnrichmentExecutionReceiptV1]:
    """Replay the R1 zero-call honest-decline journal deterministically."""
    saved_request = _check_journal_identity(
        journal,
        request=request,
        idempotency_key=idempotency_key,
        model_config_digest=model_config_digest,
    )
    if request.pool_rows:
        raise ValueError("zero-dispatch journal requires an empty pool")
    if journal.get("dispatch_declined_reason") != POOL_EMPTY_LOSS:
        raise ValueError("zero-dispatch journal must record the pool-empty decline")
    result = compose_deep_dive_enrichment(
        saved_request, lambda _: _empty_pool_decline_candidate()
    )
    if result.model_dump(mode="json") != journal.get("result"):
        raise ValueError("journal zero-dispatch result mismatch")
    if journal.get("result_digest") != _sha256(result.model_dump(mode="json")):
        raise ValueError("journal result digest mismatch")
    receipt = DeepDiveEnrichmentExecutionReceiptV1.model_validate(
        journal["provider_receipt"]
    )
    expected_model = getattr(getattr(writer, "model_config", None), "default_model", None)
    if (
        receipt.mode != "live"
        or receipt.calls != 0
        or receipt.idempotency_key != idempotency_key
        or receipt.model_config_digest != model_config_digest
        or receipt.request_digest != request.request_digest
        or receipt.pool_packet_digest != request.pool_packet_digest
        or receipt.model != expected_model
    ):
        raise ValueError("journal receipt mismatch")
    return result, receipt


def _replay_completed(
    journal: dict[str, Any],
    *,
    request: DeepDiveEnrichmentRequestV1,
    idempotency_key: str,
    model_config_digest: str,
    writer: object,
) -> tuple[DeepDiveEnrichedResultV1, DeepDiveEnrichmentExecutionReceiptV1]:
    saved_request = _check_journal_identity(
        journal,
        request=request,
        idempotency_key=idempotency_key,
        model_config_digest=model_config_digest,
    )
    raw_provider_payload = journal["raw_provider_payload"]
    if not isinstance(raw_provider_payload, dict):
        raise ValueError("journal raw provider payload must be a mapping")
    if journal.get("raw_provider_payload_digest") != _sha256(raw_provider_payload):
        raise ValueError("journal raw provider payload digest mismatch")
    expected_schema_digest = _sha256(DeepDiveEnrichedWriterResult.model_json_schema())
    observed_schema_digest = getattr(writer, "provider_schema_digest", None)
    if (
        observed_schema_digest is not None
        and observed_schema_digest != expected_schema_digest
    ):
        raise ValueError("writer provider schema digest mismatch")
    if journal.get("provider_schema_digest") != expected_schema_digest:
        raise ValueError("journal provider schema digest mismatch")
    if (
        journal.get("provider_contract_mode") != DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE
        or journal.get("provider_normalizer_version")
        != DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION
    ):
        raise ValueError("journal provider contract identity mismatch")
    normalized, records = normalize_deep_dive_enrichment_provider_payload(
        raw_provider_payload
    )
    if journal.get("provider_normalizations") != list(records):
        raise ValueError("journal provider normalization record mismatch")
    if journal.get("normalized_provider_payload_digest") != _sha256(normalized):
        raise ValueError("journal normalized provider payload digest mismatch")
    candidate = DeepDiveEnrichedWriterResult.model_validate_json(
        _canonical_json(normalized), strict=True
    )
    if candidate.model_dump(mode="json") != journal["candidate"]:
        raise ValueError("journal normalized candidate snapshot mismatch")
    saved_result = DeepDiveEnrichedResultV1.model_validate_json(
        _canonical_json(journal["result"]), strict=True
    )
    replayed = compose_deep_dive_enrichment(saved_request, lambda _: candidate)
    if replayed != saved_result:
        raise ValueError("journal replay mismatch")
    if journal.get("result_digest") != _sha256(saved_result.model_dump(mode="json")):
        raise ValueError("journal result digest mismatch")
    receipt = DeepDiveEnrichmentExecutionReceiptV1.model_validate(
        journal["provider_receipt"]
    )
    expected_model = getattr(getattr(writer, "model_config", None), "default_model", None)
    if (
        receipt.mode != "live"
        or receipt.calls != 1
        or receipt.idempotency_key != idempotency_key
        or receipt.model_config_digest != model_config_digest
        or receipt.request_digest != request.request_digest
        or receipt.pool_packet_digest != request.pool_packet_digest
        or receipt.model != expected_model
    ):
        raise ValueError("journal receipt mismatch")
    return saved_result, receipt


def run_workbook_review(
    *,
    run_dir: Path,
    trial_id: object,
    runtime_context: WorkbookBriefRuntimeContext,
) -> dict[str, object]:
    """Author (or replay) the 07W.3 review contribution — deep-dive enrichment leg only.

    Check/Reflection stay honestly stubbed: the payload carries their typed
    ``known_losses`` (``check_writer_not_yet_wired``,
    ``reflection_writer_not_yet_wired``).
    """
    run_dir = Path(run_dir)
    journal_path = run_dir / DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME
    if runtime_context.writer_execution_mode == "offline_stub" and (
        journal_path.is_symlink() or journal_path.exists()
    ):
        # R4: an offline compose must NEVER shadow paid live evidence — a
        # journal in ANY state routes to fail-loud reconciliation, not to the
        # deterministic stub.
        _raise(
            "offline stub cannot run over an existing enrichment call journal "
            "(paid live evidence must be reconciled, never shadowed)",
            "workbook-review.enrichment-reconciliation-failed",
        )
    brief_path = run_dir / WORKBOOK_BRIEF_FILENAME
    if brief_path.is_symlink():
        _raise(
            "workbook brief coordinate is a symlink",
            "workbook-review.enrichment-authority-invalid",
        )
    if not brief_path.is_file():
        # Nothing to enrich: honest typed degrade, never a silent absence.
        return build_workbook_review_contribution(None, None).model_dump(mode="json")
    try:
        request = build_deep_dive_enrichment_request(run_dir)
    except DeepDiveSkeletonMissingError:
        # R5 typed routing: the brief carries NO skeleton at all.
        return build_workbook_review_contribution(None, None).model_dump(mode="json")
    except DeepDiveSkeletonNotAuthoredError as exc:
        # R5 typed routing: a PRESENT-but-non-authored skeleton names its
        # recorded state honestly — never the "no authored skeleton" note.
        return build_workbook_review_contribution(
            None,
            None,
            skeleton_loss=skeleton_not_authored_loss(exc.skeleton_status),
        ).model_dump(mode="json")
    except DeepDiveEnrichmentAuthorityError as exc:
        _raise(
            f"enrichment request authority is invalid: {exc}",
            "workbook-review.enrichment-authority-invalid",
            cause=exc,
        )
    except ValueError as exc:
        _raise(
            f"enrichment request authority is invalid: {exc}",
            "workbook-review.enrichment-authority-invalid",
            cause=exc,
        )

    if runtime_context.writer_execution_mode == "offline_stub":
        result = compose_deep_dive_enrichment(request, offline_deep_dive_enrichment_writer)
        receipt = DeepDiveEnrichmentExecutionReceiptV1(
            mode="offline_stub",
            calls=0,
            idempotency_key=deep_dive_enrichment_idempotency_key(
                trial_id=trial_id,
                request_digest=request.request_digest,
                pool_packet_digest=request.pool_packet_digest,
                # Offline/test-only identity: the all-zeros digest is marked as
                # such by mode="offline_stub" (R18 — live identity always comes
                # from the writer and never falls back).
                model_config_digest="sha256:" + "0" * 64,
            ),
            request_digest=request.request_digest,
            pool_packet_digest=request.pool_packet_digest,
            model_config_digest="sha256:" + "0" * 64,
        )
        return build_workbook_review_contribution(result, receipt).model_dump(mode="json")

    writer = runtime_context.deep_dive_enrichment_writer
    if writer is None:
        _raise(
            "live Deep Dive enrichment writer is not initialized",
            "workbook-review.enrichment-writer-init-failed",
        )
    model_config_digest = _live_model_config_digest(writer)
    idempotency_key = deep_dive_enrichment_idempotency_key(
        trial_id=trial_id,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model_config_digest=model_config_digest,
    )
    _recover_journal_temporary(run_dir, journal_path)
    if _journal_exists(run_dir, journal_path):
        try:
            journal = _read_json(journal_path)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            _raise(
                f"invalid enrichment journal: {exc}",
                "workbook-review.enrichment-reconciliation-failed",
                cause=exc,
            )
        if journal.get("state") == "call_in_progress":
            if "provider_failure" in journal:
                # R12: a RECORDED provider failure is not an ambiguous
                # outcome — it redispatches to its own fail-loud tag so the
                # operator sees "prior call failed", not "outcome unknown".
                _raise(
                    "prior Deep Dive enrichment call recorded a provider "
                    f"failure: {journal.get('provider_failure')!r}",
                    "workbook-review.enrichment-prior-failure",
                )
            _raise(
                "Deep Dive enrichment call outcome is ambiguous",
                "workbook-review.enrichment-call-ambiguous",
            )
        if journal.get("state") == JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH:
            try:
                result, receipt = _replay_completed_without_dispatch(
                    journal,
                    request=request,
                    idempotency_key=idempotency_key,
                    model_config_digest=model_config_digest,
                    writer=writer,
                )
            except (KeyError, TypeError, ValueError) as exc:
                _raise(
                    f"enrichment journal reconciliation failed: {exc}",
                    "workbook-review.enrichment-reconciliation-failed",
                    cause=exc,
                )
            return build_workbook_review_contribution(result, receipt).model_dump(
                mode="json"
            )
        if journal.get("state") != "completed":
            _raise(
                "enrichment journal state is invalid",
                "workbook-review.enrichment-reconciliation-failed",
            )
        try:
            result, receipt = _replay_completed(
                journal,
                request=request,
                idempotency_key=idempotency_key,
                model_config_digest=model_config_digest,
                writer=writer,
            )
        except (KeyError, TypeError, ValueError) as exc:
            _raise(
                f"enrichment journal reconciliation failed: {exc}",
                "workbook-review.enrichment-reconciliation-failed",
                cause=exc,
            )
        return build_workbook_review_contribution(result, receipt).model_dump(mode="json")

    if not request.pool_rows:
        # R1: EMPTY pool → no paid call. The row-d degraded contribution is
        # built deterministically and the journal records a zero-call
        # honest-decline entry under its own replayable state.
        result = compose_deep_dive_enrichment(
            request, lambda _: _empty_pool_decline_candidate()
        )
        receipt = DeepDiveEnrichmentExecutionReceiptV1(
            mode="live",
            calls=0,
            idempotency_key=idempotency_key,
            request_digest=request.request_digest,
            pool_packet_digest=request.pool_packet_digest,
            model=getattr(getattr(writer, "model_config", None), "default_model", None),
            model_config_digest=model_config_digest,
        )
        declined: dict[str, object] = {
            "schema_version": DEEP_DIVE_ENRICHMENT_JOURNAL_SCHEMA_VERSION,
            "state": JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH,
            "idempotency_key": idempotency_key,
            "request_digest": request.request_digest,
            "pool_packet_digest": request.pool_packet_digest,
            "skeleton_authority_digest": request.skeleton.authority_digest,
            "skeleton_candidate_digest": request.skeleton.candidate_payload_digest,
            "model_config_digest": model_config_digest,
            "request": request.model_dump(mode="json"),
            "dispatch_declined_reason": POOL_EMPTY_LOSS,
            "result": result.model_dump(mode="json"),
            "result_digest": _sha256(result.model_dump(mode="json")),
            "provider_receipt": receipt.model_dump(mode="json"),
        }
        try:
            _atomic_json(journal_path, declined)
        except (OSError, ValueError) as exc:
            _raise(
                f"enrichment journal write failed: {exc}",
                "workbook-review.enrichment-persistence-failed",
                cause=exc,
            )
        return build_workbook_review_contribution(result, receipt).model_dump(mode="json")

    in_progress: dict[str, object] = {
        "schema_version": DEEP_DIVE_ENRICHMENT_JOURNAL_SCHEMA_VERSION,
        "state": "call_in_progress",
        "idempotency_key": idempotency_key,
        "request_digest": request.request_digest,
        "pool_packet_digest": request.pool_packet_digest,
        "skeleton_authority_digest": request.skeleton.authority_digest,
        "skeleton_candidate_digest": request.skeleton.candidate_payload_digest,
        "model_config_digest": model_config_digest,
        "request": request.model_dump(mode="json"),
    }
    try:
        _atomic_json(journal_path, in_progress)
    except (OSError, ValueError) as exc:
        _raise(
            f"enrichment journal write failed: {exc}",
            "workbook-review.enrichment-persistence-failed",
            cause=exc,
        )
    try:
        raw_candidate = writer(request)
    except DeepDiveEnrichmentProviderOutputError as exc:
        try:
            _persist_provider_failure(journal_path, in_progress, writer, exc)
        except (OSError, ValueError) as persistence_exc:
            _raise(
                f"enrichment failure evidence persistence failed: {persistence_exc}",
                "workbook-review.enrichment-persistence-failed",
                cause=persistence_exc,
            )
        _raise(
            f"enrichment writer output invalid: {exc}",
            "workbook-review.enrichment-writer-output-invalid",
            cause=exc,
        )
    except Exception as exc:
        try:
            _persist_provider_failure(journal_path, in_progress, writer, exc)
        except (OSError, ValueError) as persistence_exc:
            _raise(
                f"enrichment failure evidence persistence failed: {persistence_exc}",
                "workbook-review.enrichment-persistence-failed",
                cause=persistence_exc,
            )
        _raise(
            f"enrichment writer execution failed: {exc}",
            "workbook-review.enrichment-writer-execution-failed",
            cause=exc,
        )
    try:
        if not isinstance(raw_candidate, DeepDiveEnrichedWriterResult):
            raise TypeError("writer returned the wrong type")
        candidate = DeepDiveEnrichedWriterResult.model_validate(raw_candidate.model_dump())
    except (TypeError, ValueError) as exc:
        _raise(
            f"enrichment writer output invalid: {exc}",
            "workbook-review.enrichment-writer-output-invalid",
            cause=exc,
        )
    if candidate.status == "unavailable":
        # R2: the provider call SUCCEEDED (we hold a structured candidate), so
        # a writer-unavailable claim is dishonest — fail loud, never persist a
        # completed journal that would replay the dishonest shape forever.
        _raise(
            "enrichment writer output invalid: unavailable_shape_dishonest — a "
            "successful live provider call cannot claim writer-unavailable",
            "workbook-review.enrichment-writer-output-invalid",
        )
    try:
        result = compose_deep_dive_enrichment(request, lambda _: candidate)
    except (TypeError, ValueError) as exc:
        _raise(
            f"enrichment writer output invalid: {exc}",
            "workbook-review.enrichment-writer-output-invalid",
            cause=exc,
        )
    try:
        provider_evidence = _provider_evidence(writer, candidate)
    except (TypeError, ValueError) as exc:
        _raise(
            f"enrichment provider evidence invalid: {exc}",
            "workbook-review.enrichment-writer-output-invalid",
            cause=exc,
        )
    try:
        receipt = _execution_receipt(
            writer,
            mode="live",
            calls=1,
            idempotency_key=idempotency_key,
            model_config_digest=model_config_digest,
            request=request,
        )
    except (TypeError, ValueError) as exc:
        _raise(
            f"enrichment provider receipt invalid: {exc}",
            "workbook-review.enrichment-writer-output-invalid",
            cause=exc,
        )
    completed = {
        **in_progress,
        "state": "completed",
        "candidate": candidate.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
        "result_digest": _sha256(result.model_dump(mode="json")),
        "provider_receipt": receipt.model_dump(mode="json"),
        **provider_evidence,
    }
    try:
        _atomic_json(journal_path, completed)
    except (OSError, ValueError) as exc:
        _raise(
            f"enrichment journal completion failed: {exc}",
            "workbook-review.enrichment-persistence-failed",
            cause=exc,
        )
    return build_workbook_review_contribution(result, receipt).model_dump(mode="json")


__all__ = [
    "DEEP_DIVE_ENRICHMENT_JOURNAL_FILENAME",
    "DEEP_DIVE_ENRICHMENT_JOURNAL_SCHEMA_VERSION",
    "JOURNAL_STATE_COMPLETED_WITHOUT_DISPATCH",
    "RAW_PROVIDER_TEXT_BOUND",
    "deep_dive_enrichment_idempotency_key",
    "run_workbook_review",
]

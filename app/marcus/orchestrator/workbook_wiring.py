"""Deterministic orchestration seam for the four-node workbook band."""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import stat
from collections.abc import Callable, Mapping
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Final, Literal, TypeAlias

if os.name == "nt":
    import msvcrt
else:  # pragma: no cover - exercised by non-Windows CI
    import fcntl

from app.marcus.lesson_plan.deep_dive_from_run import (
    MANIFEST_RELATIVE_PATH,
    DeepDiveAuthorityInvalidError,
    DeepDiveAuthorityUnavailableError,
    build_deep_dive_request,
    load_deep_dive_segments,
)
from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonResult,
    DeepDiveSkeletonWriterResult,
    compose_deep_dive_skeleton,
    deep_dive_authority_digest,
    offline_deep_dive_writer,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    DEEP_DIVE_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_provider_payload,
)
from app.marcus.lesson_plan.lesson_type_classifier import (
    LessonTypeClassification,
    LessonTypeEvidence,
)
from app.marcus.lesson_plan.prework_artifact import (
    DEEP_DIVE_JOURNAL_FILENAME,
    DeepDiveExecutionReceiptV1,
    PromiseAuthoringReceipt,
    SceneAuthoringReceipt,
    WorkbookBriefArtifactV1,
    WorkbookBriefPayloadV1,
    WorkbookBriefRuntimeContext,
    WriterExecutionReceipt,
    canonical_payload_digest,
    deep_dive_idempotency_key,
    read_runtime_context,
    read_workbook_brief,
    write_workbook_brief,
)
from app.marcus.lesson_plan.prework_artifact import (
    workbook_brief_contribution_receipt as lesson_plan_workbook_brief_receipt,
)
from app.marcus.lesson_plan.prework_from_run import load_part2_scene_source
from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    SceneBrief,
    offline_promise_transformer,
    offline_scene_composer,
)
from app.marcus.lesson_plan.promise_projection import (
    PromiseObjectiveResolutionError,
    PromiseProjectionRequest,
    compose_promise_projection,
    resolve_promise_objectives,
)
from app.marcus.lesson_plan.research_packet import (
    ASK_A_ENRICHMENT_NODE_ID,
    ASK_A_ENRICHMENT_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
    ASK_B_HOT_TOPICS_SPECIALIST_ID,
)
from app.marcus.lesson_plan.scene_extraction import (
    SceneGateReceipt,
    SceneProjectionRequest,
    compose_scene_projection,
)
from app.marcus.lesson_plan.slide_authority import (
    SLIDE_AUTHORITY_FILENAME,
    SlideAuthorityInvalidError,
    SlideAuthorityPersistenceError,
    WorkbookSlideAuthorityMapV1,
    build_slide_authority_map,
    read_contained_regular_bytes,
    read_slide_authority_map,
    write_or_validate_slide_authority_map,
)
from app.marcus.lesson_plan.workbook_enrichment import RunEnvelopeCorruptError
from app.marcus.orchestrator.workbook_prework_writers import DeepDiveProviderOutputError
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.pass1_generation_lock import (
    Pass1GenerationLockError,
    pass1_generation_lock,
)
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.source_bundle import (
    SourceBundleError,
    read_extracted_source_sections,
)

WORKBOOK_BRIEF_NODE_ID: Final[str] = "07W.1"
WORKBOOK_REVIEW_NODE_ID: Final[str] = "07W.3"
WORKBOOK_BRIEF_SPECIALIST_ID: Final[str] = "workbook_brief"
LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID: Final[str] = "workbook_brief_stub"
WORKBOOK_REVIEW_SPECIALIST_ID: Final[str] = "workbook_review_stub"
WORKBOOK_BAND_MODEL_MARKER: Final[str] = "deterministic-workbook-band-stub"
WORKBOOK_BAND_NODE_IDS: Final[tuple[str, ...]] = (
    WORKBOOK_BRIEF_NODE_ID,
    ASK_A_ENRICHMENT_NODE_ID,
    WORKBOOK_REVIEW_NODE_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
)
WorkbookBandFactory: TypeAlias = Callable[..., dict[str, object]]

WORKBOOK_BAND_SPECIALIST_IDS: Final[dict[str, str]] = {
    WORKBOOK_BRIEF_NODE_ID: WORKBOOK_BRIEF_SPECIALIST_ID,
    ASK_A_ENRICHMENT_NODE_ID: ASK_A_ENRICHMENT_SPECIALIST_ID,
    WORKBOOK_REVIEW_NODE_ID: WORKBOOK_REVIEW_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID: ASK_B_HOT_TOPICS_SPECIALIST_ID,
}


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


def _bytes_sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _contained_regular_bytes(root: Path, relative: Path, label: str) -> bytes:
    path = Path(root) / relative
    return read_contained_regular_bytes(Path(root), path, label)


def _fsync_directory(path: Path) -> None:
    """Durably order journal and authority directory-entry replacements."""
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateFileW(
            str(path),
            0x40000000,
            0x00000007,
            None,
            3,
            0x02000000,
            None,
        )
        if handle == -1:
            raise OSError(ctypes.get_last_error(), "cannot open run directory")
        try:
            if not kernel32.FlushFileBuffers(handle):
                raise OSError(ctypes.get_last_error(), "cannot flush run directory")
        finally:
            kernel32.CloseHandle(handle)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _slide_authority_dispatch_lock(run_dir: Path):
    """Serialize authority validation through Deep-Dive journal completion."""
    lock_path = Path(run_dir) / f".{SLIDE_AUTHORITY_FILENAME}.dispatch.lock"
    descriptor: int | None = None
    locked = False
    try:
        if lock_path.is_symlink():
            raise OSError("dispatch lock coordinate may not be a symlink")
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        opened = os.fstat(descriptor)
        named = lock_path.stat(follow_symlinks=False)
        if (
            not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(named.st_mode)
            or opened.st_nlink != 1
            or named.st_nlink != 1
            or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
        ):
            raise OSError("dispatch lock coordinate is unsafe or changed during open")
        if opened.st_size == 0:
            os.write(descriptor, b"\0")
            os.fsync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.name == "nt":
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:  # pragma: no cover - exercised by non-Windows CI
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
    except OSError as exc:
        if descriptor is not None:
            with suppress(OSError):
                os.close(descriptor)
        raise SlideAuthorityPersistenceError(
            "slide authority dispatch lock is unavailable"
        ) from exc
    assert descriptor is not None
    try:
        yield
    finally:
        cleanup_errors: list[OSError] = []
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            if locked and os.name == "nt":
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            elif locked:  # pragma: no cover - exercised by non-Windows CI
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        except OSError as exc:
            cleanup_errors.append(exc)
        try:
            os.close(descriptor)
        except OSError as exc:
            cleanup_errors.append(exc)
        if cleanup_errors:
            raise SlideAuthorityPersistenceError(
                "slide authority dispatch lock cleanup failed"
            ) from cleanup_errors[0]


def _selected_contribution(
    envelope: ProductionEnvelope, *, specialist_id: str, node_id: str
) -> SpecialistContribution:
    matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == specialist_id and contribution.node_id == node_id
    )
    if len(matches) != 1:
        raise SlideAuthorityInvalidError(
            f"{specialist_id}@{node_id} authority matched {len(matches)} contributions"
        )
    return matches[0]


def _resolve_slide_authority(
    *,
    envelope: ProductionEnvelope,
    runtime_context: WorkbookBriefRuntimeContext,
    allow_legacy_absence: bool = False,
    require_existing: bool = False,
) -> tuple[WorkbookSlideAuthorityMapV1 | None, bytes | None]:
    """Mint/revalidate the exact final-slide authority before any writer call."""
    if allow_legacy_absence:
        carrier = runtime_context.run_dir / SLIDE_AUTHORITY_FILENAME
        temporary = runtime_context.run_dir / f".{SLIDE_AUTHORITY_FILENAME}.tmp"
        if carrier.is_symlink() or temporary.is_symlink() or carrier.exists() or temporary.exists():
            raise SlideAuthorityInvalidError(
                "pre-map replay conflicts with slide authority carrier state"
            )
        return None, None
    exact_plan = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "irene_pass1" and contribution.node_id == "05B"
    )
    exact_package = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "package_builder" and contribution.node_id == "06"
    )
    if not exact_plan and not exact_package:
        raise SlideAuthorityInvalidError(
            "current execution requires irene_pass1@05B and package_builder@06"
        )
    if runtime_context.course_source_root is None:
        raise SlideAuthorityInvalidError("course source authority is absent")
    carrier = runtime_context.run_dir / SLIDE_AUTHORITY_FILENAME
    if require_existing and (carrier.is_symlink() or not carrier.is_file()):
        raise SlideAuthorityInvalidError(
            "persisted slide authority map is absent or unsafe"
        )
    plan = _selected_contribution(
        envelope, specialist_id="irene_pass1", node_id="05B"
    )
    package = _selected_contribution(
        envelope, specialist_id="package_builder", node_id="06"
    )
    sidecar_bytes = _contained_regular_bytes(
        runtime_context.run_dir,
        Path("irene-pass1.lesson-plan.json"),
        "selected lesson-plan sidecar",
    )
    try:
        sidecar = json.loads(
            sidecar_bytes.decode("utf-8"), object_pairs_hook=_unique_json_object
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SlideAuthorityInvalidError("selected lesson-plan sidecar is invalid") from exc
    selected_plan = plan.output.get("lesson_plan")
    if not isinstance(sidecar, dict) or sidecar != selected_plan:
        raise SlideAuthorityInvalidError(
            "selected lesson-plan sidecar/contribution disagree"
        )
    try:
        from app.marcus.lesson_plan.pass1_authority import (
            Pass1PlanAuthorityError,
            assert_receipt_matches_plan,
            validate_receipt,
        )

        authority_receipt = plan.output.get("plan_authority_receipt")
        receipt_bytes = _contained_regular_bytes(
            runtime_context.run_dir,
            Path("irene-pass1.plan-authority.json"),
            "selected plan-authority sidecar",
        )
        persisted_receipt = json.loads(
            receipt_bytes.decode("utf-8"), object_pairs_hook=_unique_json_object
        )
        if persisted_receipt != authority_receipt:
            raise Pass1PlanAuthorityError(
                "plan-authority sidecar and contribution disagree"
            )
        assert_receipt_matches_plan(sidecar, authority_receipt)
        validated_receipt = validate_receipt(authority_receipt)
        authorized_source_ids = {
            row["unit_id"]: row["source_id"]
            for row in validated_receipt["identities"]
            if row["active"] and row["source_id"] is not None
        }
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SlideAuthorityInvalidError(
            f"Pass-1 source authority is invalid: {exc}"
        ) from exc
    plan_units = sidecar.get("plan_units")
    package_slides = package.output.get("slides")
    manifest_bytes = _contained_regular_bytes(
        runtime_context.run_dir, MANIFEST_RELATIVE_PATH, "segment manifest"
    )
    segments = load_deep_dive_segments(
        runtime_context.run_dir, manifest_bytes=manifest_bytes
    )
    # Anchor resolution must read the SAME Texas-authenticated source bodies that
    # Irene Pass-1's span catalog/authority receipt were built over — the bundle
    # persisted at ``<run_dir>/bundle`` — NOT the raw course slides. The raw
    # slides lack the ``[evidence: src-NNN]`` provenance markers Texas appends,
    # so matching source_refs against them diverges from Pass-1 (07W.1 drift).
    try:
        source_sections = read_extracted_source_sections(
            {"bundle_reference": str(runtime_context.run_dir / "bundle")}
        )
    except SourceBundleError as exc:
        raise SlideAuthorityInvalidError(
            f"authenticated source bundle is unavailable for anchor resolution: {exc}"
        ) from exc
    expected = build_slide_authority_map(
        manifest_segments=segments,
        plan_units=plan_units,
        package_slides=package_slides,
        authorized_source_ids=authorized_source_ids,
        course_source_root=runtime_context.course_source_root,
        source_sections=source_sections,
        manifest_digest=_bytes_sha256(manifest_bytes),
        plan_sidecar_digest=_bytes_sha256(sidecar_bytes),
        plan_contribution_digest="sha256:" + plan.output_digest,
        package_contribution_digest="sha256:" + package.output_digest,
    )
    if require_existing:
        if read_slide_authority_map(runtime_context.run_dir) != expected:
            raise SlideAuthorityInvalidError("persisted slide authority map is stale")
    else:
        write_or_validate_slide_authority_map(runtime_context.run_dir, expected)
    return expected, manifest_bytes


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.is_symlink() or temporary.is_symlink():
        raise ValueError("Deep Dive journal path may not be a symlink")
    created = False
    try:
        with temporary.open("x", encoding="utf-8", newline="") as handle:
            created = True
            handle.write(_canonical_json(payload) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    except Exception:
        if created and temporary.exists() and not temporary.is_symlink():
            temporary.unlink()
            _fsync_directory(path.parent)
        raise


def _journal_exists(run_dir: Path, journal_path: Path) -> bool:
    """Return journal presence only for a regular file contained by its run."""
    if journal_path.is_symlink():
        raise SpecialistDispatchError(
            "Deep Dive journal may not be a symlink",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )
    if not journal_path.exists():
        return False
    if not journal_path.is_file():
        raise SpecialistDispatchError(
            "Deep Dive journal is not a regular file",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )
    try:
        resolved_run = Path(run_dir).resolve(strict=True)
        resolved_journal = journal_path.resolve(strict=True)
        resolved_journal.relative_to(resolved_run)
    except (OSError, ValueError) as exc:
        raise SpecialistDispatchError(
            "Deep Dive journal escapes its run root",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        ) from exc
    return True


def _recover_journal_temporary(run_dir: Path, journal_path: Path) -> None:
    """Recover only crash-identifiable Deep-Dive journal temporary states."""
    temporary = journal_path.with_suffix(journal_path.suffix + ".tmp")
    if temporary.is_symlink():
        raise SpecialistDispatchError(
            "Deep Dive journal temporary may not be a symlink",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )
    if not temporary.exists():
        return
    try:
        temporary_payload = json.loads(
            _contained_regular_bytes(
                run_dir, Path(temporary.name), "Deep Dive journal temporary"
            ).decode("utf-8"),
            object_pairs_hook=_unique_json_object,
        )
        if not isinstance(temporary_payload, dict):
            raise ValueError("journal temporary root must be a mapping")
        if not journal_path.exists():
            if temporary_payload.get("state") != "call_in_progress":
                raise ValueError("orphan journal temporary is not pre-dispatch")
            temporary.unlink()
            _fsync_directory(run_dir)
            return
        target_payload = json.loads(
            _contained_regular_bytes(
                run_dir, Path(journal_path.name), "Deep Dive journal"
            ).decode("utf-8"),
            object_pairs_hook=_unique_json_object,
        )
        identity_keys = (
            "schema_version",
            "idempotency_key",
            "authority_digest",
            "model_config_digest",
            "slide_authority_map_digest",
        )
        if (
            not isinstance(target_payload, dict)
            or target_payload.get("state") != "call_in_progress"
            or temporary_payload.get("state") not in {"call_in_progress", "completed"}
            or any(
                temporary_payload.get(key) != target_payload.get(key)
                for key in identity_keys
            )
        ):
            raise ValueError("journal temporary disagrees with committed call")
        os.replace(temporary, journal_path)
        _fsync_directory(run_dir)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive journal temporary recovery failed: {exc}",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        ) from exc


def _deep_dive_receipt(
    context: WorkbookBriefRuntimeContext,
    *,
    idempotency_key: str,
    calls: Literal[0, 1],
    prior_payload_digest: str | None,
    slide_authority_map_digest: str | None,
) -> DeepDiveExecutionReceiptV1:
    writer = context.deep_dive_writer
    config = getattr(writer, "model_config", None)
    cost_usd = getattr(writer, "last_cost_usd", None)
    cost_unavailable_reason = getattr(writer, "last_cost_unavailable_reason", None)
    if (
        context.writer_execution_mode == "live"
        and calls == 1
        and cost_usd is None
        and not cost_unavailable_reason
    ):
        cost_unavailable_reason = "injected_writer_supplied_no_cost_evidence"
    return DeepDiveExecutionReceiptV1(
        mode=context.writer_execution_mode,
        calls=calls,
        idempotency_key=idempotency_key,
        prior_payload_digest=prior_payload_digest,
        slide_authority_map_digest=slide_authority_map_digest,
        model=getattr(config, "default_model", None),
        model_config_digest=(
            getattr(writer, "model_config_digest", None)
            or "sha256:" + "0" * 64
        ),
        request_id=getattr(writer, "last_request_id", None),
        latency_ms=getattr(writer, "last_latency_ms", None),
        input_tokens=getattr(writer, "last_input_tokens", None),
        output_tokens=getattr(writer, "last_output_tokens", None),
        cost_usd=cost_usd,
        cost_unavailable_reason=cost_unavailable_reason,
    )


def _provider_evidence(
    writer: object, candidate: DeepDiveSkeletonWriterResult | None = None
) -> dict[str, object]:
    raw = getattr(writer, "last_raw_provider_payload", None)
    if raw is None and candidate is not None:
        raw = candidate.model_dump(mode="json")
    if raw is None:
        return {}
    raw = json.loads(_canonical_json(raw))
    provider_schema = DeepDiveSkeletonWriterResult.model_json_schema()
    schema_digest = _sha256(provider_schema)
    observed_schema = getattr(writer, "provider_schema", None)
    if (
        observed_schema is not None
        and json.loads(_canonical_json(observed_schema)) != provider_schema
    ):
        raise ValueError("provider schema is not the canonical Deep Dive candidate schema")
    observed_schema_digest = getattr(writer, "provider_schema_digest", None)
    if observed_schema_digest is not None and observed_schema_digest != schema_digest:
        raise ValueError("provider schema digest mismatch")
    evidence: dict[str, object] = {
        "provider_contract_mode": DEEP_DIVE_PROVIDER_CONTRACT_MODE,
        "provider_schema_digest": schema_digest,
        "provider_normalizer_version": DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
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
    normalized, records = normalize_deep_dive_provider_payload(raw)
    normalized_digest = _sha256(normalized)
    observed_records = getattr(writer, "last_provider_normalizations", None)
    observed_normalized_digest = getattr(
        writer, "last_normalized_provider_payload_digest", None
    )
    if observed_records is not None and tuple(observed_records) != records:
        raise ValueError("provider normalization records mismatch")
    if (
        observed_normalized_digest is not None
        and observed_normalized_digest != normalized_digest
    ):
        raise ValueError("provider normalized payload digest mismatch")
    if candidate is not None and normalized != candidate.model_dump(mode="json"):
        raise ValueError("provider normalized payload/candidate mismatch")
    evidence.update(
        {
            "provider_normalizations": list(records),
            "normalized_provider_payload_digest": normalized_digest,
        }
    )
    return evidence


def _persist_provider_failure(
    path: Path,
    base: dict[str, object],
    writer: object,
    exc: Exception,
) -> None:
    failed = dict(base)
    failed.update(_provider_evidence(writer))
    failed["provider_failure"] = {"type": type(exc).__name__, "message": str(exc)}
    _atomic_json(path, failed)


def _compose_deep_dive(
    *,
    request: DeepDiveSkeletonRequest,
    context: WorkbookBriefRuntimeContext,
    trial_id: object,
    prior_payload_digest: str | None = None,
) -> tuple[DeepDiveSkeletonResult, DeepDiveExecutionReceiptV1]:
    authority_digest = deep_dive_authority_digest(request)
    model_config_digest = (
        getattr(context.deep_dive_writer, "model_config_digest", None)
        or "sha256:" + "0" * 64
    )
    idempotency_key = deep_dive_idempotency_key(
        trial_id=trial_id,
        authority_digest=authority_digest,
        model_config_digest=model_config_digest,
    )
    if context.writer_execution_mode == "offline_stub":
        result = compose_deep_dive_skeleton(request, offline_deep_dive_writer)
        return result, _deep_dive_receipt(
            context,
            idempotency_key=idempotency_key,
            calls=0,
            prior_payload_digest=prior_payload_digest,
            slide_authority_map_digest=request.slide_authority_map_digest,
        )
    if context.deep_dive_writer is None:
        raise SpecialistDispatchError(
            "live Deep Dive writer is not initialized",
            tag="workbook-brief.deep-dive-writer-init-failed",
        )
    journal_path = context.run_dir / DEEP_DIVE_JOURNAL_FILENAME
    _recover_journal_temporary(context.run_dir, journal_path)
    if _journal_exists(context.run_dir, journal_path):
        try:
            journal = json.loads(
                _contained_regular_bytes(
                    context.run_dir,
                    Path(DEEP_DIVE_JOURNAL_FILENAME),
                    "Deep Dive journal",
                ).decode("utf-8"),
                object_pairs_hook=_unique_json_object,
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise SpecialistDispatchError(
                f"invalid Deep Dive journal: {exc}",
                tag="workbook-brief.deep-dive-reconciliation-failed",
            ) from exc
        if not isinstance(journal, dict):
            raise SpecialistDispatchError(
                "Deep Dive journal root must be a mapping",
                tag="workbook-brief.deep-dive-reconciliation-failed",
            )
        if journal.get("state") == "call_in_progress":
            raise SpecialistDispatchError(
                "Deep Dive call outcome is ambiguous",
                tag="workbook-brief.deep-dive-call-ambiguous",
            )
        try:
            if journal.get("state") != "completed":
                raise ValueError("journal state mismatch")
            if journal.get("schema_version") != "workbook-deep-dive-call.v1":
                raise ValueError("journal schema mismatch")
            if journal.get("idempotency_key") != idempotency_key:
                raise ValueError("journal idempotency mismatch")
            if journal.get("model_config_digest") != model_config_digest:
                raise ValueError("journal model config mismatch")
            if (
                journal.get("slide_authority_map_digest")
                != request.slide_authority_map_digest
            ):
                raise ValueError("journal slide authority map mismatch")
            saved_request = DeepDiveSkeletonRequest.model_validate_json(
                _canonical_json(journal["authority"]), strict=True
            )
            raw_provider_payload = journal["raw_provider_payload"]
            if not isinstance(raw_provider_payload, dict):
                raise ValueError("journal raw provider payload must be a mapping")
            if journal.get("raw_provider_payload_digest") != _sha256(raw_provider_payload):
                raise ValueError("journal raw provider payload digest mismatch")
            expected_schema_digest = _sha256(
                DeepDiveSkeletonWriterResult.model_json_schema()
            )
            observed_schema_digest = getattr(
                context.deep_dive_writer, "provider_schema_digest", None
            )
            if (
                observed_schema_digest is not None
                and observed_schema_digest != expected_schema_digest
            ):
                raise ValueError("writer provider schema digest mismatch")
            if journal.get("provider_schema_digest") != expected_schema_digest:
                raise ValueError("journal provider schema digest mismatch")
            if (
                journal.get("provider_contract_mode")
                != DEEP_DIVE_PROVIDER_CONTRACT_MODE
                or journal.get("provider_normalizer_version")
                != DEEP_DIVE_PROVIDER_NORMALIZER_VERSION
            ):
                raise ValueError("journal provider contract identity mismatch")
            normalized, records = normalize_deep_dive_provider_payload(
                raw_provider_payload
            )
            if journal.get("provider_normalizations") != list(records):
                raise ValueError("journal provider normalization record mismatch")
            if journal.get("normalized_provider_payload_digest") != _sha256(normalized):
                raise ValueError("journal normalized provider payload digest mismatch")
            candidate = DeepDiveSkeletonWriterResult.model_validate_json(
                _canonical_json(normalized), strict=True
            )
            if candidate.model_dump(mode="json") != journal["candidate"]:
                raise ValueError("journal normalized candidate snapshot mismatch")
            saved_result = DeepDiveSkeletonResult.model_validate_json(
                _canonical_json(journal["result"]), strict=True
            )
            replayed = compose_deep_dive_skeleton(saved_request, lambda _: candidate)
            if saved_request != request or replayed != saved_result:
                raise ValueError("journal replay mismatch")
            if journal.get("authority_digest") != authority_digest:
                raise ValueError("journal authority digest mismatch")
            if journal.get("candidate_digest") != saved_result.candidate_payload_digest:
                raise ValueError("journal candidate digest mismatch")
            if journal.get("result_digest") != _sha256(saved_result.model_dump(mode="json")):
                raise ValueError("journal result digest mismatch")
            receipt = DeepDiveExecutionReceiptV1.model_validate(journal["provider_receipt"])
            expected_model = getattr(
                getattr(context.deep_dive_writer, "model_config", None),
                "default_model",
                None,
            )
            if (
                receipt.mode != "live"
                or receipt.calls != 1
                or receipt.idempotency_key != idempotency_key
                or receipt.model_config_digest != model_config_digest
                or receipt.prior_payload_digest != prior_payload_digest
                or receipt.slide_authority_map_digest
                != request.slide_authority_map_digest
                or receipt.model != expected_model
            ):
                raise ValueError("journal receipt mismatch")
            return saved_result, receipt
        except (KeyError, TypeError, ValueError) as exc:
            raise SpecialistDispatchError(
                f"Deep Dive journal reconciliation failed: {exc}",
                tag="workbook-brief.deep-dive-reconciliation-failed",
            ) from exc
    in_progress: dict[str, object] = {
        "schema_version": "workbook-deep-dive-call.v1",
        "state": "call_in_progress",
        "idempotency_key": idempotency_key,
        "authority_digest": authority_digest,
        "model_config_digest": model_config_digest,
        "slide_authority_map_digest": request.slide_authority_map_digest,
        "authority": request.model_dump(mode="json"),
    }
    try:
        _atomic_json(journal_path, in_progress)
    except (OSError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive journal write failed: {exc}",
            tag="workbook-brief.deep-dive-persistence-failed",
        ) from exc
    try:
        raw_candidate = context.deep_dive_writer(request)
    except DeepDiveProviderOutputError as exc:
        try:
            _persist_provider_failure(
                journal_path, in_progress, context.deep_dive_writer, exc
            )
        except (OSError, ValueError) as persistence_exc:
            raise SpecialistDispatchError(
                f"Deep Dive failure evidence persistence failed: {persistence_exc}",
                tag="workbook-brief.deep-dive-persistence-failed",
            ) from persistence_exc
        raise SpecialistDispatchError(
            f"Deep Dive writer output invalid: {exc}",
            tag="workbook-brief.deep-dive-writer-output-invalid",
        ) from exc
    except Exception as exc:
        try:
            _persist_provider_failure(
                journal_path, in_progress, context.deep_dive_writer, exc
            )
        except (OSError, ValueError) as persistence_exc:
            raise SpecialistDispatchError(
                f"Deep Dive failure evidence persistence failed: {persistence_exc}",
                tag="workbook-brief.deep-dive-persistence-failed",
            ) from persistence_exc
        raise SpecialistDispatchError(
            f"Deep Dive writer execution failed: {exc}",
            tag="workbook-brief.deep-dive-writer-execution-failed",
        ) from exc
    try:
        if not isinstance(raw_candidate, DeepDiveSkeletonWriterResult):
            raise TypeError("writer returned the wrong type")
        candidate = DeepDiveSkeletonWriterResult.model_validate(raw_candidate.model_dump())
        result = compose_deep_dive_skeleton(request, lambda _: candidate)
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive writer output invalid: {exc}",
            tag="workbook-brief.deep-dive-writer-output-invalid",
        ) from exc
    try:
        provider_evidence = _provider_evidence(context.deep_dive_writer, candidate)
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive provider evidence invalid: {exc}",
            tag="workbook-brief.deep-dive-writer-output-invalid",
        ) from exc
    try:
        receipt = _deep_dive_receipt(
            context,
            idempotency_key=idempotency_key,
            calls=1,
            prior_payload_digest=prior_payload_digest,
            slide_authority_map_digest=request.slide_authority_map_digest,
        )
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive provider receipt invalid: {exc}",
            tag="workbook-brief.deep-dive-writer-output-invalid",
        ) from exc
    completed = {
        "schema_version": "workbook-deep-dive-call.v1",
        "state": "completed",
        "idempotency_key": idempotency_key,
        "authority_digest": authority_digest,
        "candidate_digest": result.candidate_payload_digest,
        "result_digest": _sha256(result.model_dump(mode="json")),
        "model_config_digest": model_config_digest,
        "slide_authority_map_digest": request.slide_authority_map_digest,
        "authority": request.model_dump(mode="json"),
        "candidate": candidate.model_dump(mode="json"),
        "result": result.model_dump(mode="json"),
        "provider_receipt": receipt.model_dump(mode="json"),
        **provider_evidence,
    }
    try:
        _atomic_json(journal_path, completed)
    except (OSError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive journal completion failed: {exc}",
            tag="workbook-brief.deep-dive-persistence-failed",
        ) from exc
    return result, receipt


def _brief_factory(
    _node_id: str,
    _envelope: ProductionEnvelope,
    *,
    runtime_context: WorkbookBriefRuntimeContext,
) -> dict[str, object]:
    """Hold one Pass-1 generation from preflight through all writer effects."""
    try:
        with pass1_generation_lock(runtime_context.run_dir):
            return _brief_factory_locked(
                _node_id, _envelope, runtime_context=runtime_context
            )
    except Pass1GenerationLockError as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-persistence-failed"
        ) from exc


def _brief_factory_locked(
    _node_id: str,
    _envelope: ProductionEnvelope,
    *,
    runtime_context: WorkbookBriefRuntimeContext,
) -> dict[str, object]:
    """Author and atomically persist the real 07W.1 handoff."""
    try:
        _resolve_slide_authority(
            envelope=_envelope,
            runtime_context=runtime_context,
        )
    except SlideAuthorityPersistenceError as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-persistence-failed"
        ) from exc
    except SlideAuthorityInvalidError as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-authority-invalid"
        ) from exc
    source = None
    scene_calls = 0
    promise_calls = 0

    def measured_scene_writer(request):
        nonlocal scene_calls
        scene_calls += 1
        return (runtime_context.scene_writer or offline_scene_composer)(request)

    def measured_promise_writer(request):
        nonlocal promise_calls
        promise_calls += 1
        return (runtime_context.promise_writer or offline_promise_transformer)(request)

    scene_introduced_terms: tuple[str, ...] = ()
    if runtime_context.course_source_root is None:
        scene = SceneBrief(
            status="unavailable",
            text=None,
            source_refs=(),
            known_losses=("scene_course_source_root_absent",),
            marker="scene_source_request_required",
        )
        selected_id = selected_ref = lesson_type = archetype = None
        scene_warnings: tuple[str, ...] = ("encounter_mode_defaulted_recorded",)
        scene_classification = LessonTypeClassification(
            status="insufficient",
            lesson_type=None,
            archetype=None,
            confidence=None,
            evidence_refs=("legacy:missing-course-root",),
        )
        scene_gate = SceneGateReceipt(failures=scene.known_losses)
        scene_extraction_losses: tuple[str, ...] = ()
    else:
        try:
            source = load_part2_scene_source(runtime_context.course_source_root)
        except (FileNotFoundError, ValueError, OSError) as exc:
            scene = SceneBrief(
                status="unavailable",
                text=None,
                source_refs=(),
                known_losses=("scene_source_substrate_unavailable",),
                marker="scene_source_request_required",
            )
            selected_id = selected_ref = lesson_type = archetype = None
            scene_warnings = (f"scene_source_detail:{type(exc).__name__}",)
            scene_classification = LessonTypeClassification(
                status="insufficient",
                lesson_type=None,
                archetype=None,
                confidence=None,
                evidence_refs=("source:unavailable",),
            )
            scene_gate = SceneGateReceipt(failures=scene.known_losses)
            scene_extraction_losses = scene.known_losses
        else:
            ref = str(source.raw_candidates[0]["source_ref"])
            scene_result = compose_scene_projection(
                SceneProjectionRequest.from_raw_candidates(
                    raw_candidates=source.raw_candidates,
                    candidate_ids=("part2-q5",),
                    lesson_type_evidence=LessonTypeEvidence(
                        fresh_pain=True,
                        bridge_identity=False,
                        skill_build=False,
                        evidence_refs=(ref,),
                    ),
                    payoff_slide_inventory=source.payoff_slide_inventory,
                    payoff_slide_keys=source.payoff_slide_keys,
                    requested_coverage="full_deck",
                    required_capabilities=("scene",),
                    available_coverage="full_deck",
                    available_capabilities=("scene",),
                ),
                measured_scene_writer,
            )
            scene = scene_result.scene
            selected_id, selected_ref = (
                scene_result.selected_seed_id,
                scene_result.selected_seed_ref,
            )
            lesson_type = scene_result.classification.lesson_type
            archetype = scene_result.classification.archetype
            scene_warnings = scene_result.operator_warnings
            scene_classification = scene_result.classification
            scene_gate = scene_result.gate_receipt
            scene_extraction_losses = scene_result.extraction_losses
            scene_introduced_terms = scene_result.introduced_terms

    try:
        resolution = resolve_promise_objectives(runtime_context.run_dir)
    except (PromiseObjectiveResolutionError, RunEnvelopeCorruptError) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-authority-invalid"
        ) from exc
    forbidden = ()
    if source is not None:
        forbidden = source.forbidden_resolution_spans
    promise_result = compose_promise_projection(
        PromiseProjectionRequest(
            resolution=resolution,
            scene_context=scene.text,
            friction_context=FRICTION_SCALE.rating_prompt,
            forbidden_resolution_spans=forbidden,
        ),
        measured_promise_writer,
    )
    promise: PromiseProjection = promise_result.projection
    losses = scene.known_losses + promise.known_losses
    brief = PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=losses),
    )
    payload = WorkbookBriefPayloadV1(
        pre_work=brief,
        selected_seed_id=selected_id,
        selected_seed_ref=selected_ref,
        lesson_type=lesson_type,
        archetype=archetype,
        promise_authority_refs=promise_result.authority_refs,
        encounter_mode=runtime_context.encounter_mode,
        writer_execution_mode=runtime_context.writer_execution_mode,
        scene_receipt=SceneAuthoringReceipt(
            classification=scene_classification,
            gate=scene_gate,
            extraction_losses=scene_extraction_losses,
            operator_warnings=scene_warnings,
            introduced_terms=scene_introduced_terms,
        ),
        promise_receipt=PromiseAuthoringReceipt(
            gate=promise_result.gate_receipt,
            authority_refs=promise_result.authority_refs,
            operator_warnings=promise_result.operator_warnings,
        ),
        writer_receipts=(
            _writer_receipt("scene", runtime_context, scene_calls),
            _writer_receipt("promise", runtime_context, promise_calls),
        ),
        warnings=tuple(dict.fromkeys((*scene_warnings, *promise_result.operator_warnings))),
        known_losses=losses,
    )
    try:
        if runtime_context.course_source_root is None:
            raise DeepDiveAuthorityUnavailableError(
                "Deep Dive course source authority is absent"
            )
        with _slide_authority_dispatch_lock(runtime_context.run_dir):
            slide_authority, manifest_bytes = _resolve_slide_authority(
                envelope=_envelope,
                runtime_context=runtime_context,
                require_existing=True,
            )
            deep_dive_request = build_deep_dive_request(
                runtime_context.run_dir,
                runtime_context.course_source_root,
                promise,
                authority_map=slide_authority,
                manifest_bytes=manifest_bytes,
            )
            deep_dive_skeleton, deep_dive_receipt = _compose_deep_dive(
                request=deep_dive_request,
                context=runtime_context,
                trial_id=_envelope.trial_id,
            )
        payload = payload.model_copy(
            update={
                "deep_dive_skeleton": deep_dive_skeleton,
                "deep_dive_writer_receipt": deep_dive_receipt,
            }
        )
        payload = WorkbookBriefPayloadV1.model_validate(payload.model_dump())
    except (SlideAuthorityPersistenceError, Pass1GenerationLockError) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-persistence-failed"
        ) from exc
    except (
        DeepDiveAuthorityUnavailableError,
        DeepDiveAuthorityInvalidError,
        SlideAuthorityInvalidError,
    ) as exc:
        # Story 37.2a cannot truthfully represent total request-authority
        # absence. Current executions fail before persistence; only valid
        # thin authority (for example VO-only/no delta) enters composition.
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-authority-invalid"
        ) from exc
    artifact = WorkbookBriefArtifactV1(
        payload=payload, payload_digest=canonical_payload_digest(payload)
    )
    try:
        path = write_workbook_brief(runtime_context.run_dir, artifact)
    except (OSError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive brief persistence failed: {exc}",
            tag="workbook-brief.deep-dive-persistence-failed",
        ) from exc
    assert path.relative_to(runtime_context.run_dir).as_posix() == "workbook-brief.v1.json"
    return workbook_brief_contribution_receipt(artifact)


def _writer_receipt(
    writer: Literal["scene", "promise"],
    context: WorkbookBriefRuntimeContext,
    calls: int,
) -> WriterExecutionReceipt:
    instance = context.scene_writer if writer == "scene" else context.promise_writer
    config = getattr(instance, "model_config", None)
    return WriterExecutionReceipt(
        writer=writer,
        mode=context.writer_execution_mode,
        calls=1 if calls else 0,
        model=getattr(config, "default_model", None),
        model_config_digest=getattr(instance, "model_config_digest", None),
        request_id=getattr(instance, "last_request_id", None),
        latency_ms=getattr(instance, "last_latency_ms", None),
        input_tokens=getattr(instance, "last_input_tokens", None),
        output_tokens=getattr(instance, "last_output_tokens", None),
        cost_usd=getattr(instance, "last_cost_usd", None),
        cost_unavailable_reason=getattr(instance, "last_cost_unavailable_reason", None),
    )


def workbook_brief_contribution_receipt(
    artifact: WorkbookBriefArtifactV1,
) -> dict[str, object]:
    return lesson_plan_workbook_brief_receipt(artifact)


def _ask_a_factory(
    _node_id: str,
    envelope: ProductionEnvelope,
    *,
    runtime_context: WorkbookBriefRuntimeContext,
    dispatch_live: bool,
) -> dict[str, object]:
    from app.marcus.orchestrator.ask_a_research_wiring import (  # noqa: PLC0415
        run_ask_a_research,
    )

    return run_ask_a_research(
        run_dir=runtime_context.run_dir,
        trial_id=envelope.trial_id,
        dispatch_live=dispatch_live,
    ).model_dump(mode="json")


def _review_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }


def _ask_b_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_b_not_yet_wired"],
    }


DEFAULT_WORKBOOK_BAND_FACTORIES: Final[dict[str, WorkbookBandFactory]] = {
    WORKBOOK_BRIEF_NODE_ID: _brief_factory,
    ASK_A_ENRICHMENT_NODE_ID: _ask_a_factory,
    WORKBOOK_REVIEW_NODE_ID: _review_stub,
    ASK_B_HOT_TOPICS_NODE_ID: _ask_b_stub,
}


def runtime_context_for_run(
    run_dir: Path, *, node_id: str | None = None
) -> WorkbookBriefRuntimeContext:
    """Reconstruct persisted context, or identify an honest pre-36.4 run."""
    context_path = Path(run_dir) / "workbook-runtime-context.v1.json"
    if context_path.is_symlink() or (
        context_path.exists() and not context_path.is_file()
    ):
        raise SpecialistDispatchError(
            "workbook runtime context coordinate is not a regular file",
            tag="workbook-brief.context-corrupt",
        )
    if context_path.is_file():
        try:
            context = read_runtime_context(run_dir)
        except ValueError as exc:
            raise SpecialistDispatchError(str(exc), tag="workbook-brief.context-corrupt") from exc
        if context.writer_execution_mode == "live" and node_id == WORKBOOK_BRIEF_NODE_ID:
            from app.marcus.orchestrator.workbook_prework_writers import (  # noqa: PLC0415
                LiveDeepDiveWriter,
                LivePromiseTransformer,
                LiveSceneComposer,
            )

            try:
                context = context.model_copy(
                    update={
                        "scene_writer": LiveSceneComposer(),
                        "promise_writer": LivePromiseTransformer(),
                    }
                )
            except Exception as exc:
                raise SpecialistDispatchError(
                    f"workbook writer initialization failed: {exc}",
                    tag="workbook-brief.writer-init-failed",
                ) from exc
            try:
                return context.model_copy(update={"deep_dive_writer": LiveDeepDiveWriter()})
            except Exception as exc:
                raise SpecialistDispatchError(
                    f"Deep Dive writer initialization failed: {exc}",
                    tag="workbook-brief.deep-dive-writer-init-failed",
                ) from exc
        return context
    return WorkbookBriefRuntimeContext(
        run_dir=Path(run_dir),
        course_source_root=None,
        encounter_mode="recorded",
        context_origin="legacy_default",
        writer_execution_mode="offline_stub",
    )


def _activated_artifact(
    *,
    artifact: WorkbookBriefArtifactV1,
    production_envelope: ProductionEnvelope,
    runtime_context: WorkbookBriefRuntimeContext,
) -> WorkbookBriefArtifactV1:
    if artifact.payload.deep_dive_skeleton is not None:
        return artifact
    if runtime_context.course_source_root is None:
        raise SpecialistDispatchError(
            "Deep Dive upgrade requires course source authority",
            tag="workbook-brief.deep-dive-authority-invalid",
        )
    try:
        with pass1_generation_lock(
            runtime_context.run_dir
        ), _slide_authority_dispatch_lock(runtime_context.run_dir):
            slide_authority, manifest_bytes = _resolve_slide_authority(
                envelope=production_envelope,
                runtime_context=runtime_context,
            )
            request = build_deep_dive_request(
                runtime_context.run_dir,
                runtime_context.course_source_root,
                artifact.payload.pre_work.promise,
                authority_map=slide_authority,
                manifest_bytes=manifest_bytes,
            )
            skeleton, receipt = _compose_deep_dive(
                request=request,
                context=runtime_context,
                trial_id=production_envelope.trial_id,
                prior_payload_digest=artifact.payload_digest,
            )
        payload = WorkbookBriefPayloadV1.model_validate(
            artifact.payload.model_copy(
                update={
                    "deep_dive_skeleton": skeleton,
                    "deep_dive_writer_receipt": receipt,
                }
            ).model_dump()
        )
        upgraded = WorkbookBriefArtifactV1(
            payload=payload, payload_digest=canonical_payload_digest(payload)
        )
        write_workbook_brief(runtime_context.run_dir, upgraded)
        return upgraded
    except (SlideAuthorityPersistenceError, Pass1GenerationLockError) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-persistence-failed"
        ) from exc
    except (DeepDiveAuthorityUnavailableError, SlideAuthorityInvalidError) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-authority-invalid"
        ) from exc
    except DeepDiveAuthorityInvalidError as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-authority-invalid"
        ) from exc
    except SpecialistDispatchError:
        raise
    except (OSError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"Deep Dive brief persistence failed: {exc}",
            tag="workbook-brief.deep-dive-persistence-failed",
        ) from exc


def _replace_brief_contribution(
    envelope: ProductionEnvelope,
    artifact: WorkbookBriefArtifactV1,
    runtime_context: WorkbookBriefRuntimeContext,
) -> ProductionEnvelope:
    updated = envelope.model_copy(deep=True)
    updated = updated.model_copy(
        update={
            "contributions": tuple(
                contribution
                for contribution in updated.contributions
                if not (
                    contribution.specialist_id == LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID
                    and contribution.node_id == WORKBOOK_BRIEF_NODE_ID
                )
            )
        }
    )
    writer = runtime_context.deep_dive_writer
    config = getattr(writer, "model_config", None)
    model_used = (
        getattr(config, "default_model", None)
        if runtime_context.writer_execution_mode == "live"
        else "workbook-brief-offline"
    ) or "workbook-writer-live"
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=WORKBOOK_BRIEF_SPECIALIST_ID,
            node_id=WORKBOOK_BRIEF_NODE_ID,
            output=workbook_brief_contribution_receipt(artifact),
            model_used=model_used,
        )
    )
    return updated


def _reconcile_activated_artifact(
    *,
    artifact: WorkbookBriefArtifactV1,
    production_envelope: ProductionEnvelope,
    runtime_context: WorkbookBriefRuntimeContext,
) -> None:
    if artifact.payload.deep_dive_skeleton is None:
        raise SpecialistDispatchError(
            "activated Deep Dive reconciliation requires a skeleton",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )
    if runtime_context.course_source_root is None:
        raise SpecialistDispatchError(
            "activated Deep Dive reconciliation requires course source authority",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )
    try:
        with pass1_generation_lock(
            runtime_context.run_dir
        ), _slide_authority_dispatch_lock(runtime_context.run_dir):
            slide_authority, manifest_bytes = _resolve_slide_authority(
                envelope=production_envelope,
                runtime_context=runtime_context,
                allow_legacy_absence=(
                    artifact.payload.deep_dive_skeleton.authority.slide_authority_map_digest
                    is None
                ),
                require_existing=(
                    artifact.payload.deep_dive_skeleton.authority.slide_authority_map_digest
                    is not None
                ),
            )
            request = build_deep_dive_request(
                runtime_context.run_dir,
                runtime_context.course_source_root,
                artifact.payload.pre_work.promise,
                authority_map=slide_authority,
                manifest_bytes=manifest_bytes,
            )
            replayed, replayed_receipt = _compose_deep_dive(
                request=request,
                context=runtime_context,
                trial_id=production_envelope.trial_id,
                prior_payload_digest=(
                    artifact.payload.deep_dive_writer_receipt.prior_payload_digest
                ),
            )
    except (SlideAuthorityPersistenceError, Pass1GenerationLockError) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-persistence-failed"
        ) from exc
    except (
        DeepDiveAuthorityInvalidError,
        DeepDiveAuthorityUnavailableError,
        SlideAuthorityInvalidError,
    ) as exc:
        raise SpecialistDispatchError(
            str(exc), tag="workbook-brief.deep-dive-reconciliation-failed"
        ) from exc
    if (
        replayed != artifact.payload.deep_dive_skeleton
        or replayed_receipt != artifact.payload.deep_dive_writer_receipt
    ):
        raise SpecialistDispatchError(
            "Deep Dive sidecar/journal result or receipt mismatch",
            tag="workbook-brief.deep-dive-reconciliation-failed",
        )


def run_workbook_band_node(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    factories: Mapping[str, WorkbookBandFactory] | None = None,
    runtime_context: WorkbookBriefRuntimeContext | None = None,
    dispatch_live: bool | None = None,
) -> ProductionEnvelope:
    """Run one node, skipping an exact persisted coordinate before its factory."""
    if not isinstance(production_envelope, ProductionEnvelope):
        raise SpecialistDispatchError(
            "workbook band requires a ProductionEnvelope context",
            tag="workbook.band.invalid-context",
        )
    specialist_id = WORKBOOK_BAND_SPECIALIST_IDS.get(node_id)
    if specialist_id is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    if node_id == WORKBOOK_BRIEF_NODE_ID:
        real_matches = tuple(
            contribution
            for contribution in production_envelope.contributions
            if contribution.specialist_id == WORKBOOK_BRIEF_SPECIALIST_ID
            and contribution.node_id == WORKBOOK_BRIEF_NODE_ID
        )
        legacy_matches = tuple(
            contribution
            for contribution in production_envelope.contributions
            if contribution.specialist_id == "workbook_brief_stub"
            and contribution.node_id == WORKBOOK_BRIEF_NODE_ID
        )
        allowed = {WORKBOOK_BRIEF_SPECIALIST_ID, "workbook_brief_stub"}
        collisions = tuple(
            contribution
            for contribution in production_envelope.contributions
            if (
                contribution.node_id == WORKBOOK_BRIEF_NODE_ID
                and contribution.specialist_id not in allowed
            )
            or (
                contribution.specialist_id in allowed
                and contribution.node_id != WORKBOOK_BRIEF_NODE_ID
            )
        )
        if (
            collisions
            or len(real_matches) > 1
            or len(legacy_matches) > 1
            or (real_matches and legacy_matches)
        ):
            raise SpecialistDispatchError(
                "workbook brief coordinate collision",
                tag="workbook-brief.sidecar-mismatch",
            )
        existing = real_matches[0] if real_matches else None
    else:
        existing = production_envelope.get_contribution(specialist_id, node_id=node_id)
    if existing is not None and not (
        node_id == ASK_A_ENRICHMENT_NODE_ID and factories is None
    ):
        if node_id == WORKBOOK_BRIEF_NODE_ID:
            if runtime_context is None:
                raise SpecialistDispatchError(
                    "07W.1 resume requires runtime context", tag="workbook-brief.context-missing"
                )
            try:
                artifact = read_workbook_brief(runtime_context.run_dir)
            except ValueError as exc:
                raise SpecialistDispatchError(
                    str(exc), tag="workbook-brief.sidecar-invalid"
                ) from exc
            expected_receipt = workbook_brief_contribution_receipt(artifact)
            if existing.output != expected_receipt:
                if artifact.payload.deep_dive_skeleton is None:
                    if "deep_dive_summary" not in existing.output:
                        raise SpecialistDispatchError(
                            "07W.1 contribution/sidecar mismatch",
                            tag="workbook-brief.sidecar-mismatch",
                        )
                    raise SpecialistDispatchError(
                        "new workbook contribution/old sidecar digest mismatch",
                        tag="workbook-brief.deep-dive-split-brain",
                    )
                if "deep_dive_summary" in existing.output:
                    raise SpecialistDispatchError(
                        "activated Deep Dive contribution/sidecar mismatch",
                        tag="workbook-brief.deep-dive-reconciliation-failed",
                    )
                prior = artifact.payload.deep_dive_writer_receipt.prior_payload_digest
                if prior != existing.output.get("payload_digest"):
                    raise SpecialistDispatchError(
                        "unlinked Deep Dive sidecar/contribution generation",
                        tag="workbook-brief.deep-dive-split-brain",
                    )
                journal_path = runtime_context.run_dir / DEEP_DIVE_JOURNAL_FILENAME
                if runtime_context.writer_execution_mode != "live" or not _journal_exists(
                    runtime_context.run_dir, journal_path
                ):
                    raise SpecialistDispatchError(
                        "new sidecar/old contribution requires a completed live journal",
                        tag="workbook-brief.deep-dive-split-brain",
                    )
                if runtime_context.course_source_root is None:
                    raise SpecialistDispatchError(
                        "Deep Dive roll-forward requires course source authority",
                        tag="workbook-brief.deep-dive-reconciliation-failed",
                    )
                try:
                    with pass1_generation_lock(
                        runtime_context.run_dir
                    ), _slide_authority_dispatch_lock(runtime_context.run_dir):
                        slide_authority, manifest_bytes = _resolve_slide_authority(
                            envelope=production_envelope,
                            runtime_context=runtime_context,
                            allow_legacy_absence=(
                                artifact.payload.deep_dive_skeleton.authority.slide_authority_map_digest
                                is None
                            ),
                            require_existing=(
                                artifact.payload.deep_dive_skeleton.authority.slide_authority_map_digest
                                is not None
                            ),
                        )
                        request = build_deep_dive_request(
                            runtime_context.run_dir,
                            runtime_context.course_source_root,
                            artifact.payload.pre_work.promise,
                            authority_map=slide_authority,
                            manifest_bytes=manifest_bytes,
                        )
                        replayed, replayed_receipt = _compose_deep_dive(
                            request=request,
                            context=runtime_context,
                            trial_id=production_envelope.trial_id,
                            prior_payload_digest=prior,
                        )
                except (
                    SlideAuthorityPersistenceError,
                    Pass1GenerationLockError,
                ) as exc:
                    raise SpecialistDispatchError(
                        str(exc), tag="workbook-brief.deep-dive-persistence-failed"
                    ) from exc
                except (
                    DeepDiveAuthorityInvalidError,
                    DeepDiveAuthorityUnavailableError,
                    SlideAuthorityInvalidError,
                ) as exc:
                    raise SpecialistDispatchError(
                        str(exc), tag="workbook-brief.deep-dive-reconciliation-failed"
                    ) from exc
                if (
                    replayed != artifact.payload.deep_dive_skeleton
                    or replayed_receipt != artifact.payload.deep_dive_writer_receipt
                ):
                    raise SpecialistDispatchError(
                        "Deep Dive sidecar/journal result or receipt mismatch",
                        tag="workbook-brief.deep-dive-reconciliation-failed",
                    )
                return _replace_brief_contribution(
                    production_envelope, artifact, runtime_context
                )
            if artifact.payload.deep_dive_skeleton is None:
                artifact = _activated_artifact(
                    artifact=artifact,
                    production_envelope=production_envelope,
                    runtime_context=runtime_context,
                )
                return _replace_brief_contribution(
                    production_envelope, artifact, runtime_context
                )
            if existing.output != workbook_brief_contribution_receipt(artifact):
                raise SpecialistDispatchError(
                    "07W.1 contribution/sidecar mismatch", tag="workbook-brief.sidecar-mismatch"
                )
            if artifact.payload.deep_dive_skeleton is not None:
                _reconcile_activated_artifact(
                    artifact=artifact,
                    production_envelope=production_envelope,
                    runtime_context=runtime_context,
                )
        return production_envelope

    if node_id == WORKBOOK_BRIEF_NODE_ID and runtime_context is not None:
        sidecar_path = runtime_context.run_dir / "workbook-brief.v1.json"
        if sidecar_path.is_symlink():
            raise SpecialistDispatchError(
                "workbook brief coordinate is a symlink",
                tag="workbook-brief.sidecar-invalid",
            )
        if sidecar_path.is_file():
            try:
                artifact = read_workbook_brief(runtime_context.run_dir)
            except ValueError as exc:
                raise SpecialistDispatchError(
                    str(exc), tag="workbook-brief.sidecar-invalid"
                ) from exc
            if artifact.payload.deep_dive_skeleton is not None:
                journal_path = runtime_context.run_dir / DEEP_DIVE_JOURNAL_FILENAME
                if not _journal_exists(runtime_context.run_dir, journal_path):
                    raise SpecialistDispatchError(
                        "activated sidecar without contribution requires completed journal",
                        tag="workbook-brief.deep-dive-split-brain",
                    )
                _reconcile_activated_artifact(
                    artifact=artifact,
                    production_envelope=production_envelope,
                    runtime_context=runtime_context,
                )
                return _replace_brief_contribution(
                    production_envelope, artifact, runtime_context
                )
            if artifact.payload.deep_dive_skeleton is None:
                raise SpecialistDispatchError(
                    "legacy-null sidecar requires its matching contribution for upgrade",
                    tag="workbook-brief.deep-dive-split-brain",
                )

    selected = DEFAULT_WORKBOOK_BAND_FACTORIES if factories is None else factories
    factory = selected.get(node_id)
    if factory is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    prior_ask_a = None
    if (
        node_id == ASK_A_ENRICHMENT_NODE_ID
        and factory is _ask_a_factory
        and existing is not None
        and existing.output.get("stub_status") != "not_yet_wired"
    ):
        from app.marcus.lesson_plan.ask_a_enrichment import (  # noqa: PLC0415
            AskAContributionOutputV1,
        )
        from app.marcus.orchestrator.ask_a_research_wiring import (  # noqa: PLC0415
            JOURNAL_FILENAME,
        )

        try:
            prior_ask_a = AskAContributionOutputV1.model_validate_json(
                json.dumps(existing.output, separators=(",", ":")), strict=True
            )
        except ValueError as exc:
            raise SpecialistDispatchError(
                f"existing Ask-A output is invalid: {exc}",
                tag="ask-a.reconciliation-failed",
            ) from exc
        if (
            prior_ask_a.disposition.startswith("completed")
            and runtime_context is not None
            and not (runtime_context.run_dir / JOURNAL_FILENAME).exists()
        ):
            raise SpecialistDispatchError(
                "completed Ask-A contribution has no call journal",
                tag="ask-a.split-brain",
            )
    try:
        if node_id == WORKBOOK_BRIEF_NODE_ID:
            requires_context = factory is DEFAULT_WORKBOOK_BAND_FACTORIES[node_id]
            if runtime_context is None and requires_context:
                raise SpecialistDispatchError(
                    "07W.1 requires explicit runtime context", tag="workbook-brief.context-missing"
                )
            if (
                runtime_context is not None
                and "runtime_context" in inspect.signature(factory).parameters
            ):
                output = factory(node_id, production_envelope, runtime_context=runtime_context)
            else:  # compatibility for injected pre-36.4 test/deterministic factories
                output = factory(node_id, production_envelope)
        elif node_id == ASK_A_ENRICHMENT_NODE_ID and factory is _ask_a_factory:
            if runtime_context is None:
                raise SpecialistDispatchError(
                    "07W.2 requires explicit runtime context",
                    tag="ask-a.runtime-context-missing",
                )
            output = factory(
                node_id,
                production_envelope,
                runtime_context=runtime_context,
                dispatch_live=bool(dispatch_live),
            )
        else:
            output = factory(node_id, production_envelope)
    except SpecialistDispatchError:
        raise
    except Exception as exc:
        raise SpecialistDispatchError(
            f"workbook band factory failed at node {node_id!r}: {exc}",
            tag="workbook.band.factory-failed",
        ) from exc
    if not isinstance(output, dict):
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned "
            f"{type(output).__name__}, expected dict",
            tag="workbook.band.invalid-output",
        )
    try:
        json.dumps(output, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned non-serializable output: {exc}",
            tag="workbook.band.invalid-output",
        ) from exc
    updated = production_envelope.model_copy(deep=True)
    if node_id == WORKBOOK_BRIEF_NODE_ID and legacy_matches:
        updated = updated.model_copy(
            update={
                "contributions": tuple(
                    contribution
                    for contribution in updated.contributions
                    if not (
                        contribution.specialist_id == LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID
                        and contribution.node_id == WORKBOOK_BRIEF_NODE_ID
                    )
                )
            }
        )
    model_used = (
        "deterministic-ask-a-research-wiring"
        if node_id == ASK_A_ENRICHMENT_NODE_ID and factory is _ask_a_factory
        else WORKBOOK_BAND_MODEL_MARKER
    )
    if node_id == WORKBOOK_BRIEF_NODE_ID and runtime_context is not None:
        if runtime_context.writer_execution_mode == "live":
            config = getattr(runtime_context.scene_writer, "model_config", None)
            model_used = getattr(config, "default_model", None) or "workbook-writer-live"
        else:
            model_used = "workbook-brief-offline"
    if (
        existing is not None
        and node_id == ASK_A_ENRICHMENT_NODE_ID
        and factory is _ask_a_factory
    ):
        from app.marcus.lesson_plan.ask_a_enrichment import (  # noqa: PLC0415
            AskAContributionOutputV1,
        )

        try:
            resolved = AskAContributionOutputV1.model_validate_json(
                json.dumps(output, separators=(",", ":")), strict=True
            )
        except ValueError as exc:
            raise SpecialistDispatchError(
                f"Ask-A output validation failed: {exc}", tag="ask-a.output-invalid"
            ) from exc
        if prior_ask_a is not None and prior_ask_a.disposition.startswith("completed"):
            if prior_ask_a != resolved:
                raise SpecialistDispatchError(
                    "completed Ask-A contribution conflicts with journal replay",
                    tag="ask-a.split-brain",
                )
            return production_envelope
        if prior_ask_a == resolved:
            return production_envelope
        updated = updated.model_copy(
            update={
                "contributions": tuple(
                    item
                    for item in updated.contributions
                    if not (
                        item.specialist_id == ASK_A_ENRICHMENT_SPECIALIST_ID
                        and item.node_id == ASK_A_ENRICHMENT_NODE_ID
                    )
                )
            }
        )
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=output,
            model_used=model_used,
        )
    )
    return updated


__all__ = [
    "DEFAULT_WORKBOOK_BAND_FACTORIES",
    "WORKBOOK_BAND_MODEL_MARKER",
    "WORKBOOK_BAND_NODE_IDS",
    "WORKBOOK_BAND_SPECIALIST_IDS",
    "WORKBOOK_BRIEF_NODE_ID",
    "WORKBOOK_BRIEF_SPECIALIST_ID",
    "LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID",
    "WORKBOOK_REVIEW_NODE_ID",
    "WORKBOOK_REVIEW_SPECIALIST_ID",
    "WorkbookBandFactory",
    "run_workbook_band_node",
    "runtime_context_for_run",
    "workbook_brief_contribution_receipt",
]

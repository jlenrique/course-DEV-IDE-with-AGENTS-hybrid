"""Strict, digest-bound projection of the 07W.1 Deep Dive into Ask-A demand."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import to_jsonable_python

from app.marcus.lesson_plan.deep_dive_projection import (
    BoldTermMarker,
    DeepDiveAbilityInput,
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonResult,
    DeepDiveSkeletonWriterResult,
    compose_deep_dive_skeleton,
    offline_deep_dive_writer,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    DEEP_DIVE_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_provider_payload,
    provider_payload_digest,
)
from app.marcus.lesson_plan.prework_artifact import (
    DEEP_DIVE_JOURNAL_FILENAME,
    WORKBOOK_BRIEF_FILENAME,
    DeepDiveExecutionReceiptV1,
    deep_dive_idempotency_key,
    read_workbook_brief,
    workbook_brief_contribution_receipt,
)
from app.marcus.lesson_plan.workbook_enrichment import (
    RunEnvelopeCorruptError,
    load_run_envelope,
)

AskAResearchDemandStatus = Literal["ready", "degraded", "unavailable"]
ResearchDemandLoss = Literal[
    "workbook_brief_absent",
    "workbook_brief_legacy_stub",
    "workbook_brief_legacy_null",
    "deep_dive_skeleton_unavailable",
    "deep_dive_skeleton_degraded",
    "deep_dive_skeleton_terms_empty",
]


class ResearchDemandShapeError(ValueError):
    """Raised when present authority cannot be reconciled exactly."""


def _digest(payload: object) -> str:
    canonical = json.dumps(
        to_jsonable_python(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


class AskAResearchDemandV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    schema_version: Literal["ask-a-research-demand.v1"] = "ask-a-research-demand.v1"
    status: AskAResearchDemandStatus
    specialist_id: Literal["workbook_brief"] = "workbook_brief"
    node_id: Literal["07W.1"] = "07W.1"
    workbook_brief_payload_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    skeleton_authority_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    skeleton_candidate_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    abilities: tuple[DeepDiveAbilityInput, ...]
    bold_terms: tuple[BoldTermMarker, ...]
    source_claim_refs: tuple[str, ...]
    known_losses: tuple[ResearchDemandLoss, ...]
    demand_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _closed_shape(self) -> AskAResearchDemandV1:
        payload = self.model_dump(mode="json", exclude={"demand_digest"})
        if self.demand_digest != _digest(payload):
            raise ValueError("research demand digest mismatch")
        if self.status == "ready":
            if (
                self.workbook_brief_payload_digest is None
                or self.skeleton_authority_digest is None
                or self.skeleton_candidate_digest is None
                or not self.abilities
                or not self.bold_terms
                or not self.source_claim_refs
                or self.known_losses
            ):
                raise ValueError("ready demand requires complete authority and no loss")
            if len({item.ability_id for item in self.abilities}) != len(self.abilities):
                raise ValueError("ready demand requires unique ability IDs")
            if len({item.term for item in self.bold_terms}) != len(self.bold_terms):
                raise ValueError("ready demand requires deduplicated bold terms")
            if any(
                not ref
                or ref != ref.strip()
                or any(mark in ref for mark in ("\r", "\n", "\u2028", "\u2029"))
                for ref in self.source_claim_refs
            ):
                raise ValueError("ready demand requires nonblank one-line source claim refs")
            if len(set(self.source_claim_refs)) != len(self.source_claim_refs):
                raise ValueError("ready demand requires unique source claim refs")
        else:
            if (
                self.abilities
                or self.bold_terms
                or self.source_claim_refs
                or len(self.known_losses) != 1
            ):
                raise ValueError("non-ready demand requires empty payload and one loss")
            if (self.workbook_brief_payload_digest is None) != (
                self.known_losses == ("workbook_brief_absent",)
            ):
                raise ValueError("only absent brief omits its payload digest")
            loss = self.known_losses[0]
            expected_status = {
                "workbook_brief_absent": "unavailable",
                "workbook_brief_legacy_stub": "unavailable",
                "workbook_brief_legacy_null": "unavailable",
                "deep_dive_skeleton_unavailable": "unavailable",
                "deep_dive_skeleton_degraded": "degraded",
                "deep_dive_skeleton_terms_empty": "degraded",
            }[loss]
            if self.status != expected_status:
                raise ValueError("non-ready demand status/loss mismatch")
            has_skeleton_digests = (
                self.skeleton_authority_digest is not None
                and self.skeleton_candidate_digest is not None
            )
            if (self.skeleton_authority_digest is None) != (
                self.skeleton_candidate_digest is None
            ):
                raise ValueError("skeleton digests must appear together")
            expects_skeleton = loss.startswith("deep_dive_skeleton_")
            if has_skeleton_digests != expects_skeleton:
                raise ValueError("non-ready loss/skeleton digest mismatch")
        return self


def _make(**values: object) -> AskAResearchDemandV1:
    raw = {
        "schema_version": "ask-a-research-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        **values,
    }
    raw["demand_digest"] = _digest(raw)
    return AskAResearchDemandV1.model_validate(raw, strict=True)


def _non_ready(
    *,
    status: Literal["degraded", "unavailable"],
    loss: ResearchDemandLoss,
    payload_digest: str | None,
    skeleton: DeepDiveSkeletonResult | None = None,
) -> AskAResearchDemandV1:
    return _make(
        status=status,
        workbook_brief_payload_digest=payload_digest,
        skeleton_authority_digest=skeleton.authority_digest if skeleton else None,
        skeleton_candidate_digest=skeleton.candidate_payload_digest if skeleton else None,
        abilities=(),
        bold_terms=(),
        source_claim_refs=(),
        known_losses=(loss,),
    )


def _reconcile_execution(
    *, run_dir: Path, trial_id: object, skeleton: DeepDiveSkeletonResult, receipt: object
) -> None:
    try:
        receipt = DeepDiveExecutionReceiptV1.model_validate(receipt, strict=True)
    except ValueError as exc:
        raise ResearchDemandShapeError(f"invalid Deep Dive receipt: {exc}") from exc
    if receipt.mode == "live" and receipt.model_config_digest is None:
        raise ResearchDemandShapeError("Deep Dive receipt lacks model config identity")
    model_config_digest = receipt.model_config_digest or "sha256:" + "0" * 64
    expected_key = deep_dive_idempotency_key(
        trial_id=trial_id,
        authority_digest=skeleton.authority_digest,
        model_config_digest=model_config_digest,
    )
    if receipt.idempotency_key != expected_key:
        raise ResearchDemandShapeError("Deep Dive receipt is not bound to this trial")
    if receipt.mode == "offline_stub":
        if receipt.calls != 0:
            raise ResearchDemandShapeError("offline Deep Dive receipt records a call")
        if compose_deep_dive_skeleton(
            skeleton.authority, offline_deep_dive_writer
        ) != skeleton:
            raise ResearchDemandShapeError("offline Deep Dive skeleton is not stub replay")
        return
    if receipt.calls != 1:
        raise ResearchDemandShapeError("live Deep Dive receipt must record one call")
    journal_path = run_dir / DEEP_DIVE_JOURNAL_FILENAME
    if journal_path.is_symlink() or not journal_path.is_file():
        raise ResearchDemandShapeError("live Deep Dive authority lacks a regular journal")
    try:
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchDemandShapeError(f"Deep Dive journal unreadable: {exc}") from exc
    try:
        if not isinstance(journal, dict):
            raise ValueError("journal must be an object")
        if (
            journal.get("schema_version") != "workbook-deep-dive-call.v1"
            or journal.get("state") != "completed"
        ):
            raise ValueError("journal schema/state mismatch")
        if (
            journal.get("idempotency_key") != expected_key
            or journal.get("authority_digest") != skeleton.authority_digest
            or journal.get("model_config_digest") != model_config_digest
        ):
            raise ValueError("journal execution identity mismatch")
        raw_provider_payload = journal["raw_provider_payload"]
        if not isinstance(raw_provider_payload, dict):
            raise ValueError("journal raw provider payload must be a mapping")
        if journal.get("raw_provider_payload_digest") != provider_payload_digest(
            raw_provider_payload
        ):
            raise ValueError("journal raw provider payload digest mismatch")
        if journal.get("provider_schema_digest") != provider_payload_digest(
            DeepDiveSkeletonWriterResult.model_json_schema()
        ):
            raise ValueError("journal provider schema digest mismatch")
        if (
            journal.get("provider_contract_mode") != DEEP_DIVE_PROVIDER_CONTRACT_MODE
            or journal.get("provider_normalizer_version")
            != DEEP_DIVE_PROVIDER_NORMALIZER_VERSION
        ):
            raise ValueError("journal provider contract identity mismatch")
        normalized, records = normalize_deep_dive_provider_payload(raw_provider_payload)
        if journal.get("provider_normalizations") != list(records):
            raise ValueError("journal provider normalization record mismatch")
        if journal.get("normalized_provider_payload_digest") != provider_payload_digest(
            normalized
        ):
            raise ValueError("journal normalized provider payload digest mismatch")
        request = DeepDiveSkeletonRequest.model_validate_json(
            json.dumps(journal["authority"], separators=(",", ":")), strict=True
        )
        candidate = DeepDiveSkeletonWriterResult.model_validate_json(
            json.dumps(normalized, separators=(",", ":")), strict=True
        )
        if candidate.model_dump(mode="json") != journal["candidate"]:
            raise ValueError("journal normalized candidate snapshot mismatch")
        result = DeepDiveSkeletonResult.model_validate_json(
            json.dumps(journal["result"], separators=(",", ":")), strict=True
        )
        replayed = compose_deep_dive_skeleton(request, lambda _: candidate)
        journal_receipt = DeepDiveExecutionReceiptV1.model_validate_json(
            json.dumps(journal["provider_receipt"], separators=(",", ":")), strict=True
        )
        if request != skeleton.authority or replayed != result or result != skeleton:
            raise ValueError("journal replay/result mismatch")
        if candidate != skeleton.candidate_snapshot:
            raise ValueError("journal candidate snapshot mismatch")
        if journal.get("candidate_digest") != skeleton.candidate_payload_digest:
            raise ValueError("journal candidate digest mismatch")
        if journal.get("result_digest") != _digest(skeleton.model_dump(mode="json")):
            raise ValueError("journal result digest mismatch")
        if journal_receipt != receipt:
            raise ValueError("journal/sidecar receipt mismatch")
    except (KeyError, TypeError, ValueError) as exc:
        raise ResearchDemandShapeError(f"Deep Dive journal mismatch: {exc}") from exc


def resolve_enrichment_demand(run_dir: Path) -> AskAResearchDemandV1:
    """Resolve only exact ``workbook_brief@07W.1`` authority; never fall back."""
    run_dir = Path(run_dir)
    brief_path = run_dir / WORKBOOK_BRIEF_FILENAME
    if brief_path.is_symlink():
        raise ResearchDemandShapeError("workbook brief coordinate is a symlink")
    try:
        envelope = load_run_envelope(run_dir)
    except RunEnvelopeCorruptError as exc:
        raise ResearchDemandShapeError(str(exc)) from exc
    if envelope is None:
        if brief_path.exists():
            raise ResearchDemandShapeError("workbook brief exists without run envelope")
        return _non_ready(
            status="unavailable",
            loss="workbook_brief_absent",
            payload_digest=None,
        )
    real_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief"
        and contribution.node_id == "07W.1"
    )
    legacy_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief_stub"
        and contribution.node_id == "07W.1"
    )
    real = real_matches[0] if real_matches else None
    legacy = legacy_matches[0] if legacy_matches else None
    allowed = {"workbook_brief", "workbook_brief_stub"}
    collisions = tuple(
        contribution
        for contribution in envelope.contributions
        if (
            contribution.node_id == "07W.1"
            and contribution.specialist_id not in allowed
        )
        or (
            contribution.specialist_id in allowed
            and contribution.node_id != "07W.1"
        )
    )
    if (
        collisions
        or len(real_matches) > 1
        or len(legacy_matches) > 1
        or (real is not None and legacy is not None)
    ):
        raise ResearchDemandShapeError("workbook brief coordinate collision")
    if real is None:
        if legacy is not None:
            if brief_path.exists():
                raise ResearchDemandShapeError("legacy stub contradicts real brief sidecar")
            return _non_ready(
                status="unavailable",
                loss="workbook_brief_legacy_stub",
                payload_digest="sha256:" + legacy.output_digest,
            )
        if brief_path.exists():
            raise ResearchDemandShapeError("brief sidecar has no exact contribution")
        return _non_ready(
            status="unavailable", loss="workbook_brief_absent", payload_digest=None
        )
    if not brief_path.is_file():
        raise ResearchDemandShapeError("exact workbook contribution has no sidecar")
    try:
        artifact = read_workbook_brief(run_dir)
    except ValueError as exc:
        raise ResearchDemandShapeError(str(exc)) from exc
    if real.output != workbook_brief_contribution_receipt(artifact):
        raise ResearchDemandShapeError("workbook contribution/sidecar mismatch")
    skeleton = artifact.payload.deep_dive_skeleton
    if skeleton is None:
        return _non_ready(
            status="unavailable",
            loss="workbook_brief_legacy_null",
            payload_digest=artifact.payload_digest,
        )
    try:
        skeleton = DeepDiveSkeletonResult.model_validate(skeleton.model_dump())
    except ValueError as exc:
        raise ResearchDemandShapeError(f"invalid nested skeleton: {exc}") from exc
    expected_abilities = tuple(
        (vow.objective_id, vow.text) for vow in artifact.payload.pre_work.promise.vows
    )
    actual_abilities = tuple(
        (ability.ability_id, ability.text) for ability in skeleton.authority.abilities
    )
    if (
        artifact.payload.pre_work.promise.status != "authored"
        or actual_abilities != expected_abilities
    ):
        raise ResearchDemandShapeError("Promise/skeleton ability authority mismatch")
    _reconcile_execution(
        run_dir=run_dir,
        trial_id=envelope.trial_id,
        skeleton=skeleton,
        receipt=artifact.payload.deep_dive_writer_receipt,
    )
    if skeleton.status == "unavailable":
        return _non_ready(
            status="unavailable",
            loss="deep_dive_skeleton_unavailable",
            payload_digest=artifact.payload_digest,
            skeleton=skeleton,
        )
    if skeleton.status == "degraded":
        return _non_ready(
            status="degraded",
            loss="deep_dive_skeleton_degraded",
            payload_digest=artifact.payload_digest,
            skeleton=skeleton,
        )
    if skeleton.gate.status != "pass":
        raise ResearchDemandShapeError("authored skeleton failed replay gate")
    if not skeleton.bold_terms:
        return _non_ready(
            status="degraded",
            loss="deep_dive_skeleton_terms_empty",
            payload_digest=artifact.payload_digest,
            skeleton=skeleton,
        )
    refs = tuple(claim.claim_id for claim in skeleton.authority.source_claims)
    if len(set(refs)) != len(refs):
        raise ResearchDemandShapeError("duplicate skeleton source claim reference")
    return _make(
        status="ready",
        workbook_brief_payload_digest=artifact.payload_digest,
        skeleton_authority_digest=skeleton.authority_digest,
        skeleton_candidate_digest=skeleton.candidate_payload_digest,
        abilities=skeleton.authority.abilities,
        bold_terms=skeleton.bold_terms,
        source_claim_refs=refs,
        known_losses=(),
    )


# --------------------------------------------------------------------------
# Ask-B (38.2) — hot-topics demand: beat-③ Promise vows + optional Scene.
#
# CLOSED loss→status lattice (38-2 AC 1 / A-1 — a NEW design; Ask-A's
# skeleton-digest-coupled 6-loss map does NOT transfer):
#
#   workbook_brief_absent       → unavailable
#   workbook_brief_legacy_stub  → unavailable
#   promise_vows_unavailable    → unavailable  (promise not "authored")
#   scene_identity_absent       → READY with recorded scope loss (W-3/A-1
#                                 decided: the scene is an optional
#                                 enhancement, never a blocking retryable)
#
# Corrupt/forged/mismatched authority raises ResearchDemandShapeError
# (→ ``ask-b.demand-invalid`` at the wiring seam); it is never a status.
# The status vocabulary is closed to {"ready", "unavailable"} — Ask-B binds
# no deep-dive skeleton, so Ask-A's "degraded" rows have no analog here.
# --------------------------------------------------------------------------

AskBHotTopicsDemandStatus = Literal["ready", "unavailable"]
AskBDemandLoss = Literal[
    "workbook_brief_absent",
    "workbook_brief_legacy_stub",
    "promise_vows_unavailable",
    "scene_identity_absent",
]
_ASK_B_UNAVAILABLE_LOSSES = (
    "workbook_brief_absent",
    "workbook_brief_legacy_stub",
    "promise_vows_unavailable",
)


class AskBHotTopicsDemandV1(BaseModel):
    """Strict Ask-B demand: ordered beat-③ ability vows + digest-bound Scene."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)

    schema_version: Literal["ask-b-hot-topics-demand.v1"] = "ask-b-hot-topics-demand.v1"
    status: AskBHotTopicsDemandStatus
    specialist_id: Literal["workbook_brief"] = "workbook_brief"
    node_id: Literal["07W.1"] = "07W.1"
    workbook_brief_payload_digest: str | None = Field(
        default=None, pattern=r"^sha256:[0-9a-f]{64}$"
    )
    abilities: tuple[DeepDiveAbilityInput, ...]
    scene_digest: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    scene_text: str | None = None
    known_losses: tuple[AskBDemandLoss, ...]
    demand_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def _closed_shape(self) -> AskBHotTopicsDemandV1:
        payload = self.model_dump(mode="json", exclude={"demand_digest"})
        if self.demand_digest != _digest(payload):
            raise ValueError("Ask-B demand digest mismatch")
        if (self.scene_digest is None) != (self.scene_text is None):
            raise ValueError("scene digest and scene text must appear together")
        if self.scene_text is not None and not self.scene_text.strip():
            raise ValueError("bound scene text must be nonblank")
        if self.status == "ready":
            if self.workbook_brief_payload_digest is None or not self.abilities:
                raise ValueError("ready Ask-B demand requires brief digest and vows")
            if len({item.ability_id for item in self.abilities}) != len(self.abilities):
                raise ValueError("ready Ask-B demand requires unique vow objective IDs")
            # T4 R5a (B6/E7): vow text with line-control characters is a forged
            # or corrupt authority — rejected here so the wiring seam types it
            # ``ask-b.demand-invalid`` instead of crashing at query build.
            # (Trailing/extra WHITESPACE stays contract-legal; the canonical
            # query collapses it — see ``derive_hot_topics_query``.)
            for item in self.abilities:
                if any(
                    mark in item.text
                    for mark in ("\r", "\n", "\u2028", "\u2029")
                ):
                    raise ValueError(
                        "ready Ask-B demand vow text must not carry line-control "
                        "characters"
                    )
            if self.known_losses not in ((), ("scene_identity_absent",)):
                raise ValueError(
                    "ready Ask-B demand admits only the scene_identity_absent loss"
                )
            scene_bound = self.scene_digest is not None
            if scene_bound == (self.known_losses == ("scene_identity_absent",)):
                raise ValueError("scene binding must mirror the scene_identity_absent loss")
        else:
            if self.abilities or self.scene_digest is not None:
                raise ValueError("non-ready Ask-B demand requires an empty payload")
            if (
                len(self.known_losses) != 1
                or self.known_losses[0] not in _ASK_B_UNAVAILABLE_LOSSES
            ):
                raise ValueError("non-ready Ask-B demand requires exactly one blocking loss")
            if (self.workbook_brief_payload_digest is None) != (
                self.known_losses == ("workbook_brief_absent",)
            ):
                raise ValueError("only an absent brief omits its payload digest")
        return self


def _make_ask_b(**values: object) -> AskBHotTopicsDemandV1:
    raw = {
        "schema_version": "ask-b-hot-topics-demand.v1",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        **values,
    }
    raw["demand_digest"] = _digest(raw)
    return AskBHotTopicsDemandV1.model_validate(raw, strict=True)


def _ask_b_non_ready(
    *, loss: AskBDemandLoss, payload_digest: str | None
) -> AskBHotTopicsDemandV1:
    return _make_ask_b(
        status="unavailable",
        workbook_brief_payload_digest=payload_digest,
        abilities=(),
        scene_digest=None,
        scene_text=None,
        known_losses=(loss,),
    )


def resolve_hot_topics_demand(run_dir: Path) -> AskBHotTopicsDemandV1:
    """Resolve only exact ``workbook_brief@07W.1`` authority; never fall back.

    Ask-B binds the ordered beat-③ Promise ability vows and — when authored —
    the digest-bound Scene identity, plus the workbook-brief payload digest.
    It never binds bold terms or the deep-dive skeleton (narrower than Ask-A
    by design), never scrapes prose, and never reads another run.
    """
    run_dir = Path(run_dir)
    brief_path = run_dir / WORKBOOK_BRIEF_FILENAME
    if brief_path.is_symlink():
        raise ResearchDemandShapeError("workbook brief coordinate is a symlink")
    try:
        envelope = load_run_envelope(run_dir)
    except RunEnvelopeCorruptError as exc:
        raise ResearchDemandShapeError(str(exc)) from exc
    if envelope is None:
        if brief_path.exists():
            raise ResearchDemandShapeError("workbook brief exists without run envelope")
        return _ask_b_non_ready(loss="workbook_brief_absent", payload_digest=None)
    real_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief"
        and contribution.node_id == "07W.1"
    )
    legacy_matches = tuple(
        contribution
        for contribution in envelope.contributions
        if contribution.specialist_id == "workbook_brief_stub"
        and contribution.node_id == "07W.1"
    )
    real = real_matches[0] if real_matches else None
    legacy = legacy_matches[0] if legacy_matches else None
    allowed = {"workbook_brief", "workbook_brief_stub"}
    collisions = tuple(
        contribution
        for contribution in envelope.contributions
        if (
            contribution.node_id == "07W.1"
            and contribution.specialist_id not in allowed
        )
        or (
            contribution.specialist_id in allowed
            and contribution.node_id != "07W.1"
        )
    )
    if (
        collisions
        or len(real_matches) > 1
        or len(legacy_matches) > 1
        or (real is not None and legacy is not None)
    ):
        raise ResearchDemandShapeError("workbook brief coordinate collision")
    if real is None:
        if legacy is not None:
            if brief_path.exists():
                raise ResearchDemandShapeError("legacy stub contradicts real brief sidecar")
            return _ask_b_non_ready(
                loss="workbook_brief_legacy_stub",
                payload_digest="sha256:" + legacy.output_digest,
            )
        if brief_path.exists():
            raise ResearchDemandShapeError("brief sidecar has no exact contribution")
        return _ask_b_non_ready(loss="workbook_brief_absent", payload_digest=None)
    if not brief_path.is_file():
        raise ResearchDemandShapeError("exact workbook contribution has no sidecar")
    try:
        artifact = read_workbook_brief(run_dir)
    except ValueError as exc:
        raise ResearchDemandShapeError(str(exc)) from exc
    if real.output != workbook_brief_contribution_receipt(artifact):
        raise ResearchDemandShapeError("workbook contribution/sidecar mismatch")
    promise = artifact.payload.pre_work.promise
    if promise.status != "authored":
        return _ask_b_non_ready(
            loss="promise_vows_unavailable", payload_digest=artifact.payload_digest
        )
    abilities = tuple(
        DeepDiveAbilityInput(ability_id=vow.objective_id, text=vow.text)
        for vow in promise.vows
    )
    if len({item.ability_id for item in abilities}) != len(abilities):
        raise ResearchDemandShapeError("duplicate Promise vow objective ID")
    scene = artifact.payload.pre_work.scene
    if scene.status == "authored":
        scene_digest = _digest(scene.model_dump(mode="json"))
        scene_text: str | None = scene.text
        losses: tuple[AskBDemandLoss, ...] = ()
    else:
        scene_digest = None
        scene_text = None
        losses = ("scene_identity_absent",)
    return _make_ask_b(
        status="ready",
        workbook_brief_payload_digest=artifact.payload_digest,
        abilities=abilities,
        scene_digest=scene_digest,
        scene_text=scene_text,
        known_losses=losses,
    )


__all__ = [
    "AskAResearchDemandStatus",
    "AskAResearchDemandV1",
    "AskBDemandLoss",
    "AskBHotTopicsDemandStatus",
    "AskBHotTopicsDemandV1",
    "ResearchDemandLoss",
    "ResearchDemandShapeError",
    "resolve_enrichment_demand",
    "resolve_hot_topics_demand",
]

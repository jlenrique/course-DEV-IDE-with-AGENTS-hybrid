"""Strict, model-free contracts for the workbook Ask-B hot-topics seam (38.2).

Ask-B is the LATE, narrowly-scoped hot-topics research pass at
``ask_b_hot_topics@07W.4`` — ability/scene-scoped by design (narrower than
Ask-A: it binds NO bold terms and NO deep-dive skeleton). Its packet is
minted by its own dispatch, distinct from the upfront ``04.55`` mint and
from Ask-A, and is consumed ONLY by the 39.2 Door-Ajar re-point.

DETERMINISTIC ABILITY-ASSOCIATION BASIS (38-2 AC 1 / A-5 — the rule is SAID
here and covered by the scope digest):
    The story's default rule (per-ability query segments whose produced rows
    inherit the segment's vow ``objective_id``) is not implementable on the
    landed substrate — one ``dispatch_intent`` invocation returns rows with
    no per-segment attribution, and partitioning the scope into per-segment
    dispatches is forbidden by the exactly-one-dispatch rule. The substituted
    simpler deterministic rule is: an entry's ``supports_ability_ids`` are
    the ordered scope abilities whose nontrivial ability-text tokens
    (NFC + casefold, length >= 3, stopword-filtered — the proven Ask-A token
    idiom, versioned here as ``ask-b-association.v1``) appear in the row's
    STORED evidence window (title + ``evidence_excerpt``; never the unstored
    full body). Matched tokens are recorded per ability on the entry; an
    entry with zero ability association is rejected into an indexed loss.
    The algorithm version participates in the scope digest, so any change to
    this rule changes every downstream digest.

Scene handling (W-3/A-1 decided): an authored Scene binds digest + full text
into the scope and its whitespace-collapsed single-line projection joins the
canonical query; an absent Scene is a recorded ``scene_identity_absent``
scope loss carried into the packet ``known_losses`` — never a blocking
retryable.

No orchestrator or Texas implementation-type imports (M3 held).
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from app.marcus.lesson_plan.ask_a_enrichment import (
    ability_tokens,
    canonical_digest,
    evidence_for_body,
    normalize_match_text,
)
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import AskBHotTopicsDemandV1

AskBPosture = Literal["hot_topics"]
AskBDisposition = Literal[
    "retryable_demand_not_ready",
    "retryable_dispatch_disabled",
    "retryable_credentials_unavailable",
    "completed_empty",
    "completed_degraded",
    "completed_ready",
]
AskBScopeLoss = Literal["scene_identity_absent"]

ASK_B_ASSOCIATION_ALGORITHM: Literal["ask-b-association.v1"] = "ask-b-association.v1"

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _nonblank_line(value: str) -> str:
    if not value or value != value.strip() or any(c in value for c in "\r\n  "):
        raise ValueError("value must be a nonblank single line")
    return value


def _digest_str(value: str) -> str:
    if not _DIGEST_RE.fullmatch(value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


NonBlankLine = Annotated[str, AfterValidator(_nonblank_line)]
Sha256Digest = Annotated[str, AfterValidator(_digest_str)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)


class AskBRetrievalScopeV1(_StrictModel):
    """Immutable pre-call Ask-B scope: digest-bound, no outcome fields."""

    schema_version: Literal["ask-b-retrieval-scope.v1"] = "ask-b-retrieval-scope.v1"
    demand_digest: Sha256Digest
    workbook_brief_payload_digest: Sha256Digest
    abilities: tuple[DeepDiveAbilityInput, ...]
    scene_digest: Sha256Digest | None
    scene_text: str | None
    query: NonBlankLine
    query_digest: Sha256Digest
    posture: AskBPosture = "hot_topics"
    provider_config_fingerprint: Sha256Digest
    association_algorithm: Literal["ask-b-association.v1"] = ASK_B_ASSOCIATION_ALGORITHM
    known_scope_losses: tuple[AskBScopeLoss, ...]
    scope_digest: Sha256Digest

    @model_validator(mode="after")
    def _bind(self) -> AskBRetrievalScopeV1:
        if not self.abilities:
            raise ValueError("Ask-B scope requires the ordered beat-③ abilities")
        if len({a.ability_id for a in self.abilities}) != len(self.abilities):
            raise ValueError("duplicate ability ID")
        if (self.scene_digest is None) != (self.scene_text is None):
            raise ValueError("scene digest and scene text must appear together")
        if self.scene_text is not None and not self.scene_text.strip():
            raise ValueError("bound scene text must be nonblank")
        scene_bound = self.scene_digest is not None
        if scene_bound == (self.known_scope_losses == ("scene_identity_absent",)):
            raise ValueError("scene binding must mirror the scene_identity_absent loss")
        if self.known_scope_losses not in ((), ("scene_identity_absent",)):
            raise ValueError("Ask-B scope admits only the scene_identity_absent loss")
        if self.query_digest != canonical_digest(self.query):
            raise ValueError("query digest mismatch")
        expected = canonical_digest(self.model_dump(mode="json", exclude={"scope_digest"}))
        if self.scope_digest != expected:
            raise ValueError("scope digest mismatch")
        return self


def derive_hot_topics_query(demand: AskBHotTopicsDemandV1) -> str:
    """Compose the canonical single-line query carrying the COMPLETE scope.

    Per 38-2 AC 2 the canonical query carries the complete ORDERED ability
    scope (+ the scene identity when present). Nothing is truncated, dropped,
    reordered, or partitioned — an over-limit query fails loud upstream with
    ``ask-b.scope-overflow``. Multiline scene prose is projected to one line
    by whitespace collapse only (deterministic; no content dropped) because
    the canonical query is a single-line contract field.
    """
    if demand.status != "ready":
        raise ValueError("Ask-B query requires ready demand")
    segments = " ; ".join(
        f"[{ability.ability_id}] {ability.text}" for ability in demand.abilities
    )
    query = (
        "hot topics, recent developments and emerging trends for these abilities: "
        + segments
    )
    if demand.scene_text is not None:
        query += " | scene: " + " ".join(demand.scene_text.split())
    return query


def build_scope(
    demand: AskBHotTopicsDemandV1,
    *,
    provider_config_fingerprint: str,
) -> AskBRetrievalScopeV1:
    if demand.status != "ready":
        raise ValueError("Ask-B scope requires ready demand")
    query = derive_hot_topics_query(demand)
    raw: dict[str, Any] = {
        "schema_version": "ask-b-retrieval-scope.v1",
        "demand_digest": demand.demand_digest,
        "workbook_brief_payload_digest": demand.workbook_brief_payload_digest,
        "abilities": demand.abilities,
        "scene_digest": demand.scene_digest,
        "scene_text": demand.scene_text,
        "query": query,
        "query_digest": canonical_digest(query),
        "posture": "hot_topics",
        "provider_config_fingerprint": provider_config_fingerprint,
        "association_algorithm": ASK_B_ASSOCIATION_ALGORITHM,
        "known_scope_losses": demand.known_losses,
    }
    raw["scope_digest"] = canonical_digest(raw)
    return AskBRetrievalScopeV1.model_validate(raw, strict=True)


def match_ability_associations(
    scope: AskBRetrievalScopeV1, *, title: str, body: str
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    """Apply ``ask-b-association.v1`` over the STORED evidence window.

    ``body`` MUST be the stored ``evidence_excerpt`` window (mirror of the
    Ask-A Scout MED #3 discipline): matching over the full body would let a
    token past the excerpt window be recorded against an excerpt that does
    not actually contain it.
    """
    haystack = normalize_match_text(f"{title}\n{body}")
    haystack_tokens = frozenset(_TOKEN_RE.findall(haystack))
    matched_by_ability: dict[str, tuple[str, ...]] = {}
    for ability in scope.abilities:
        matched = tuple(
            token for token in ability_tokens(ability.text) if token in haystack_tokens
        )
        if matched:
            matched_by_ability[ability.ability_id] = matched
    return tuple(matched_by_ability), matched_by_ability


class AskBKnowledgeEntryV1(_StrictModel):
    schema_version: Literal["ask-b-knowledge-entry.v1"] = "ask-b-knowledge-entry.v1"
    citation_id: NonBlankLine
    source_ref: NonBlankLine
    provider: NonBlankLine
    source_id: NonBlankLine
    title: str = ""
    source_hash: Sha256Digest
    evidence_hierarchy_tier: Literal[
        "T1_systematic",
        "T2_peer_rct_or_equiv",
        "T3_peer_observational",
        "T4_peer_other",
        "T5_preprint",
        "T6_grey_institutional",
    ]
    peer_reviewed: bool
    provider_provenance: tuple[NonBlankLine, ...]
    triangulation_status: Literal["dual_provider", "single_provider", "none"]
    reliability_score: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_excerpt: str
    evidence_truncated: bool
    evidence_body_sha256: Sha256Digest
    scope_digest: Sha256Digest
    supports_ability_ids: tuple[NonBlankLine, ...]
    association_algorithm: Literal["ask-b-association.v1"]
    matched_ability_tokens: dict[NonBlankLine, tuple[NonBlankLine, ...]]

    @model_validator(mode="after")
    def _entry_invariants(self) -> AskBKnowledgeEntryV1:
        if not re.fullmatch(r"ask-b-cite-[0-9]{3}", self.citation_id):
            raise ValueError("citation ID is not Ask-B namespaced")
        if not self.provider_provenance:
            raise ValueError("provider provenance required")
        if not self.evidence_excerpt.strip() or len(self.evidence_excerpt) > 2000:
            raise ValueError("evidence excerpt invalid")
        if not self.supports_ability_ids:
            raise ValueError("Ask-B entry requires a deterministic ability association")
        if tuple(self.matched_ability_tokens) != self.supports_ability_ids:
            raise ValueError("ability association evidence mismatch")
        if any(not tokens for tokens in self.matched_ability_tokens.values()):
            raise ValueError("ability association requires matched tokens")
        return self


class AskBExecutionReceiptV1(_StrictModel):
    schema_version: Literal["ask-b-execution-receipt.v1"] = "ask-b-execution-receipt.v1"
    scope: AskBRetrievalScopeV1
    scope_digest: Sha256Digest
    dispatcher_invocations: Literal[1]
    provider_iterations: tuple[int, ...]
    refinement_logs: tuple[dict[str, Any], ...]
    provider_outcomes: tuple[NonBlankLine, ...]
    provider_receipts: tuple[dict[str, Any], ...]
    receipt_digest: Sha256Digest

    @classmethod
    def build(cls, **values: Any) -> AskBExecutionReceiptV1:
        scope = values["scope"]
        raw = {
            "schema_version": "ask-b-execution-receipt.v1",
            **values,
            "scope_digest": scope.scope_digest,
        }
        raw["receipt_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _receipt_bind(self) -> AskBExecutionReceiptV1:
        if self.scope_digest != self.scope.scope_digest:
            raise ValueError("execution receipt scope mismatch")
        if any(value < 0 for value in self.provider_iterations):
            raise ValueError("provider iterations must be nonnegative")
        if self.receipt_digest != canonical_digest(
            self.model_dump(mode="json", exclude={"receipt_digest"})
        ):
            raise ValueError("execution receipt digest mismatch")
        return self


class AskBResearchIntakeV1(_StrictModel):
    schema_version: Literal["ask-b-research-intake.v1"] = "ask-b-research-intake.v1"
    scope: AskBRetrievalScopeV1
    execution_receipt: AskBExecutionReceiptV1
    covered_ability_ids: tuple[NonBlankLine, ...]
    uncovered_ability_ids: tuple[NonBlankLine, ...]
    intake_digest: Sha256Digest

    @classmethod
    def build(
        cls,
        *,
        scope: AskBRetrievalScopeV1,
        execution_receipt: AskBExecutionReceiptV1,
        entries: tuple[AskBKnowledgeEntryV1, ...],
    ) -> AskBResearchIntakeV1:
        covered = tuple(
            a.ability_id
            for a in scope.abilities
            if any(a.ability_id in e.supports_ability_ids for e in entries)
        )
        raw = {
            "schema_version": "ask-b-research-intake.v1",
            "scope": scope,
            "execution_receipt": execution_receipt,
            "covered_ability_ids": covered,
            "uncovered_ability_ids": tuple(
                a.ability_id for a in scope.abilities if a.ability_id not in covered
            ),
        }
        raw["intake_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _intake_bind(self) -> AskBResearchIntakeV1:
        if self.execution_receipt.scope != self.scope:
            raise ValueError("intake receipt scope mismatch")
        ability_order = tuple(a.ability_id for a in self.scope.abilities)
        if (
            tuple(x for x in ability_order if x in self.covered_ability_ids)
            != self.covered_ability_ids
        ):
            raise ValueError("covered ability order mismatch")
        if set(self.covered_ability_ids) | set(self.uncovered_ability_ids) != set(
            ability_order
        ):
            raise ValueError("ability coverage is not exhaustive")
        if set(self.covered_ability_ids) & set(self.uncovered_ability_ids):
            raise ValueError("ability coverage overlaps")
        if self.intake_digest != canonical_digest(
            self.model_dump(mode="json", exclude={"intake_digest"})
        ):
            raise ValueError("intake digest mismatch")
        return self


class AskBContributionOutputV1(_StrictModel):
    schema_version: Literal["ask-b-contribution-output.v1"] = "ask-b-contribution-output.v1"
    disposition: AskBDisposition
    research_entries: tuple[AskBKnowledgeEntryV1, ...]
    known_losses: tuple[NonBlankLine, ...]
    research_intake: AskBResearchIntakeV1 | None
    dispatcher_invocations: Literal[0, 1]
    output_digest: Sha256Digest

    @classmethod
    def build_retryable(cls, *, disposition: str, loss: str) -> AskBContributionOutputV1:
        raw = {
            "schema_version": "ask-b-contribution-output.v1",
            "disposition": disposition,
            "research_entries": (),
            "known_losses": (loss,),
            "research_intake": None,
            "dispatcher_invocations": 0,
        }
        raw["output_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @classmethod
    def build_completed(
        cls,
        *,
        disposition: str,
        intake: AskBResearchIntakeV1,
        entries: tuple[AskBKnowledgeEntryV1, ...],
        known_losses: tuple[str, ...],
    ) -> AskBContributionOutputV1:
        raw = {
            "schema_version": "ask-b-contribution-output.v1",
            "disposition": disposition,
            "research_entries": entries,
            "known_losses": known_losses,
            "research_intake": intake,
            "dispatcher_invocations": 1,
        }
        raw["output_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _disposition_rules(self) -> AskBContributionOutputV1:
        retry_loss = {
            "retryable_demand_not_ready": "ask_b_demand_not_ready",
            "retryable_dispatch_disabled": "ask_b_dispatch_disabled",
            "retryable_credentials_unavailable": "ask_b_credentials_unavailable",
        }
        if self.disposition in retry_loss:
            if (
                self.research_entries
                or self.dispatcher_invocations
                or self.research_intake is not None
                or self.known_losses != (retry_loss[self.disposition],)
            ):
                raise ValueError("retryable disposition shape mismatch")
        else:
            if self.dispatcher_invocations != 1 or self.research_intake is None:
                raise ValueError("completed disposition requires execution intake")
            if any(
                e.scope_digest != self.research_intake.scope.scope_digest
                for e in self.research_entries
            ):
                raise ValueError("entry scope mismatch")
            rebuilt = AskBResearchIntakeV1.build(
                scope=self.research_intake.scope,
                execution_receipt=self.research_intake.execution_receipt,
                entries=self.research_entries,
            )
            if rebuilt != self.research_intake:
                raise ValueError("intake coverage mismatch")
            scope_losses = self.research_intake.scope.known_scope_losses
            if tuple(self.known_losses[: len(scope_losses)]) != scope_losses:
                raise ValueError("scope losses must lead the completed loss order")
            expected = (
                "completed_empty"
                if not self.research_entries
                else ("completed_degraded" if self.known_losses else "completed_ready")
            )
            if self.disposition != expected:
                raise ValueError("completed disposition/content mismatch")
        if self.output_digest != canonical_digest(
            self.model_dump(mode="json", exclude={"output_digest"})
        ):
            raise ValueError("output digest mismatch")
        return self


__all__ = [
    "ASK_B_ASSOCIATION_ALGORITHM",
    "AskBContributionOutputV1",
    "AskBExecutionReceiptV1",
    "AskBKnowledgeEntryV1",
    "AskBResearchIntakeV1",
    "AskBRetrievalScopeV1",
    "build_scope",
    "canonical_digest",
    "derive_hot_topics_query",
    "evidence_for_body",
    "match_ability_associations",
]

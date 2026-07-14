"""Strict, model-free contracts for the workbook Ask-A research seam."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator
from pydantic_core import to_jsonable_python

from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import AskAResearchDemandV1

AskAPosture = Literal["corroborate", "gap_fill", "embellish"]
AskADisposition = Literal[
    "retryable_demand_not_ready",
    "retryable_dispatch_disabled",
    "retryable_credentials_unavailable",
    "completed_empty",
    "completed_degraded",
    "completed_ready",
]

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "understand",
        "with",
    }
)


def canonical_digest(value: object) -> str:
    canonical = json.dumps(
        to_jsonable_python(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def _nonblank_line(value: str) -> str:
    if not value or value != value.strip() or any(c in value for c in "\r\n\u2028\u2029"):
        raise ValueError("value must be a nonblank single line")
    return value


def _digest(value: str) -> str:
    if not _DIGEST_RE.fullmatch(value):
        raise ValueError("value must be a canonical sha256 digest")
    return value


NonBlankLine = Annotated[str, AfterValidator(_nonblank_line)]
Sha256Digest = Annotated[str, AfterValidator(_digest)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, validate_default=True)


def normalize_match_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def ability_tokens(value: str) -> tuple[str, ...]:
    tokens = []
    for token in _TOKEN_RE.findall(normalize_match_text(value)):
        if len(token) >= 3 and token not in _STOPWORDS and token not in tokens:
            tokens.append(token)
    return tuple(tokens)


class AskARetrievalScopeV1(_StrictModel):
    schema_version: Literal["ask-a-retrieval-scope.v1"] = "ask-a-retrieval-scope.v1"
    demand_digest: Sha256Digest
    workbook_brief_payload_digest: Sha256Digest
    skeleton_authority_digest: Sha256Digest
    skeleton_candidate_digest: Sha256Digest
    abilities: tuple[DeepDiveAbilityInput, ...]
    bold_terms: tuple[NonBlankLine, ...]
    source_claim_refs: tuple[NonBlankLine, ...]
    query: NonBlankLine
    query_digest: Sha256Digest
    posture: AskAPosture
    provider_config_fingerprint: Sha256Digest
    association_algorithm: Literal["ask-a-association.v1"] = "ask-a-association.v1"
    scope_digest: Sha256Digest

    @model_validator(mode="after")
    def _bind(self) -> AskARetrievalScopeV1:
        if not self.abilities or not self.bold_terms or not self.source_claim_refs:
            raise ValueError("Ask-A scope authority must be nonempty")
        if len({a.ability_id for a in self.abilities}) != len(self.abilities):
            raise ValueError("duplicate ability ID")
        if len(set(self.bold_terms)) != len(self.bold_terms):
            raise ValueError("duplicate bold term")
        if self.query_digest != canonical_digest(self.query):
            raise ValueError("query digest mismatch")
        expected = canonical_digest(self.model_dump(mode="json", exclude={"scope_digest"}))
        if self.scope_digest != expected:
            raise ValueError("scope digest mismatch")
        return self


def build_scope(
    demand: AskAResearchDemandV1,
    *,
    provider_config_fingerprint: str,
    posture: AskAPosture = "gap_fill",
) -> AskARetrievalScopeV1:
    if demand.status != "ready":
        raise ValueError("Ask-A scope requires ready demand")
    query = " | ".join(
        [
            "Ask-A cited enrichment",
            *(f"ability[{a.ability_id}]={a.text}" for a in demand.abilities),
            *(f"bold_term={t.term}" for t in demand.bold_terms),
            *(f"claim_ref={ref}" for ref in demand.source_claim_refs),
        ]
    )
    raw: dict[str, Any] = {
        "schema_version": "ask-a-retrieval-scope.v1",
        "demand_digest": demand.demand_digest,
        "workbook_brief_payload_digest": demand.workbook_brief_payload_digest,
        "skeleton_authority_digest": demand.skeleton_authority_digest,
        "skeleton_candidate_digest": demand.skeleton_candidate_digest,
        "abilities": demand.abilities,
        "bold_terms": tuple(t.term for t in demand.bold_terms),
        "source_claim_refs": demand.source_claim_refs,
        "query": query,
        "query_digest": canonical_digest(query),
        "posture": posture,
        "provider_config_fingerprint": provider_config_fingerprint,
        "association_algorithm": "ask-a-association.v1",
    }
    raw["scope_digest"] = canonical_digest(raw)
    return AskARetrievalScopeV1.model_validate(raw, strict=True)


def evidence_for_body(body: str) -> tuple[str, bool, str]:
    if not isinstance(body, str) or not body.strip():
        raise ValueError("Texas row body must be nonblank")
    return (
        body[:2000],
        len(body) > 2000,
        "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest(),
    )


def match_scope_associations(
    scope: AskARetrievalScopeV1, *, title: str, body: str
) -> tuple[tuple[str, ...], tuple[str, ...], dict[str, tuple[str, ...]], tuple[str, ...]]:
    haystack = normalize_match_text(f"{title}\n{body}")
    haystack_tokens = frozenset(_TOKEN_RE.findall(haystack))
    matched_terms = tuple(
        term for term in scope.bold_terms if normalize_match_text(term) in haystack
    )
    matched_by_ability: dict[str, tuple[str, ...]] = {}
    for ability in scope.abilities:
        matched = tuple(token for token in ability_tokens(ability.text) if token in haystack_tokens)
        if matched:
            matched_by_ability[ability.ability_id] = matched
    return tuple(matched_by_ability), matched_terms, matched_by_ability, matched_terms


class AskAKnowledgeEntryV1(_StrictModel):
    schema_version: Literal["ask-a-knowledge-entry.v1"] = "ask-a-knowledge-entry.v1"
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
    supports_bold_terms: tuple[NonBlankLine, ...]
    association_algorithm: Literal["ask-a-association.v1"]
    matched_ability_tokens: dict[NonBlankLine, tuple[NonBlankLine, ...]]
    matched_bold_terms: tuple[NonBlankLine, ...]

    @model_validator(mode="after")
    def _entry_invariants(self) -> AskAKnowledgeEntryV1:
        if not re.fullmatch(r"ask-a-cite-[0-9]{3}", self.citation_id):
            raise ValueError("citation ID is not Ask-A namespaced")
        if not self.provider_provenance:
            raise ValueError("provider provenance required")
        if not self.evidence_excerpt.strip() or len(self.evidence_excerpt) > 2000:
            raise ValueError("evidence excerpt invalid")
        if not self.supports_ability_ids and not self.supports_bold_terms:
            raise ValueError("entry requires at least one scope association")
        if tuple(self.matched_ability_tokens) != self.supports_ability_ids:
            raise ValueError("ability association evidence mismatch")
        if self.matched_bold_terms != self.supports_bold_terms:
            raise ValueError("bold-term association evidence mismatch")
        if any(not tokens for tokens in self.matched_ability_tokens.values()):
            raise ValueError("ability association requires matched tokens")
        return self


class AskAExecutionReceiptV1(_StrictModel):
    schema_version: Literal["ask-a-execution-receipt.v1"] = "ask-a-execution-receipt.v1"
    scope: AskARetrievalScopeV1
    scope_digest: Sha256Digest
    dispatcher_invocations: Literal[1]
    provider_iterations: tuple[int, ...]
    refinement_logs: tuple[dict[str, Any], ...]
    provider_outcomes: tuple[NonBlankLine, ...]
    provider_receipts: tuple[dict[str, Any], ...]
    receipt_digest: Sha256Digest

    @classmethod
    def build(cls, **values: Any) -> AskAExecutionReceiptV1:
        scope = values["scope"]
        raw = {
            "schema_version": "ask-a-execution-receipt.v1",
            **values,
            "scope_digest": scope.scope_digest,
        }
        raw["receipt_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _receipt_bind(self) -> AskAExecutionReceiptV1:
        if self.scope_digest != self.scope.scope_digest:
            raise ValueError("execution receipt scope mismatch")
        if any(value < 0 for value in self.provider_iterations):
            raise ValueError("provider iterations must be nonnegative")
        if self.receipt_digest != canonical_digest(
            self.model_dump(mode="json", exclude={"receipt_digest"})
        ):
            raise ValueError("execution receipt digest mismatch")
        return self


class AskAResearchIntakeV1(_StrictModel):
    schema_version: Literal["ask-a-research-intake.v1"] = "ask-a-research-intake.v1"
    scope: AskARetrievalScopeV1
    execution_receipt: AskAExecutionReceiptV1
    covered_ability_ids: tuple[NonBlankLine, ...]
    uncovered_ability_ids: tuple[NonBlankLine, ...]
    covered_bold_terms: tuple[NonBlankLine, ...]
    uncovered_bold_terms: tuple[NonBlankLine, ...]
    intake_digest: Sha256Digest

    @classmethod
    def build(
        cls,
        *,
        scope: AskARetrievalScopeV1,
        execution_receipt: AskAExecutionReceiptV1,
        entries: tuple[AskAKnowledgeEntryV1, ...],
    ) -> AskAResearchIntakeV1:
        covered_abilities = tuple(
            a.ability_id
            for a in scope.abilities
            if any(a.ability_id in e.supports_ability_ids for e in entries)
        )
        covered_terms = tuple(
            term for term in scope.bold_terms if any(term in e.supports_bold_terms for e in entries)
        )
        raw = {
            "schema_version": "ask-a-research-intake.v1",
            "scope": scope,
            "execution_receipt": execution_receipt,
            "covered_ability_ids": covered_abilities,
            "uncovered_ability_ids": tuple(
                a.ability_id for a in scope.abilities if a.ability_id not in covered_abilities
            ),
            "covered_bold_terms": covered_terms,
            "uncovered_bold_terms": tuple(t for t in scope.bold_terms if t not in covered_terms),
        }
        raw["intake_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _intake_bind(self) -> AskAResearchIntakeV1:
        if self.execution_receipt.scope != self.scope:
            raise ValueError("intake receipt scope mismatch")
        ability_order = tuple(a.ability_id for a in self.scope.abilities)
        if (
            tuple(x for x in ability_order if x in self.covered_ability_ids)
            != self.covered_ability_ids
        ):
            raise ValueError("covered ability order mismatch")
        if set(self.covered_ability_ids) | set(self.uncovered_ability_ids) != set(ability_order):
            raise ValueError("ability coverage is not exhaustive")
        if set(self.covered_ability_ids) & set(self.uncovered_ability_ids):
            raise ValueError("ability coverage overlaps")
        if set(self.covered_bold_terms) | set(self.uncovered_bold_terms) != set(
            self.scope.bold_terms
        ):
            raise ValueError("term coverage is not exhaustive")
        if self.intake_digest != canonical_digest(
            self.model_dump(mode="json", exclude={"intake_digest"})
        ):
            raise ValueError("intake digest mismatch")
        return self


class AskAContributionOutputV1(_StrictModel):
    schema_version: Literal["ask-a-contribution-output.v1"] = "ask-a-contribution-output.v1"
    disposition: AskADisposition
    research_entries: tuple[AskAKnowledgeEntryV1, ...]
    known_losses: tuple[NonBlankLine, ...]
    research_intake: AskAResearchIntakeV1 | None
    dispatcher_invocations: Literal[0, 1]
    output_digest: Sha256Digest

    @classmethod
    def build_retryable(cls, *, disposition: str, loss: str) -> AskAContributionOutputV1:
        raw = {
            "schema_version": "ask-a-contribution-output.v1",
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
        intake: AskAResearchIntakeV1,
        entries: tuple[AskAKnowledgeEntryV1, ...],
        known_losses: tuple[str, ...],
    ) -> AskAContributionOutputV1:
        raw = {
            "schema_version": "ask-a-contribution-output.v1",
            "disposition": disposition,
            "research_entries": entries,
            "known_losses": known_losses,
            "research_intake": intake,
            "dispatcher_invocations": 1,
        }
        raw["output_digest"] = canonical_digest(raw)
        return cls.model_validate(raw, strict=True)

    @model_validator(mode="after")
    def _disposition_rules(self) -> AskAContributionOutputV1:
        retry_loss = {
            "retryable_demand_not_ready": "ask_a_demand_not_ready",
            "retryable_dispatch_disabled": "ask_a_dispatch_disabled",
            "retryable_credentials_unavailable": "ask_a_credentials_unavailable",
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
            rebuilt = AskAResearchIntakeV1.build(
                scope=self.research_intake.scope,
                execution_receipt=self.research_intake.execution_receipt,
                entries=self.research_entries,
            )
            if rebuilt != self.research_intake:
                raise ValueError("intake coverage mismatch")
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
    "AskAContributionOutputV1",
    "AskAExecutionReceiptV1",
    "AskAKnowledgeEntryV1",
    "AskARetrievalScopeV1",
    "AskAResearchIntakeV1",
    "ability_tokens",
    "build_scope",
    "canonical_digest",
    "evidence_for_body",
    "match_scope_associations",
    "normalize_match_text",
]

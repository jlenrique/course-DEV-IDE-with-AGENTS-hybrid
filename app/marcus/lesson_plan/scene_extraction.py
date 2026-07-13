"""Traceable Scene extraction, adequacy gates, and the closed composer seam."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Mapping
from typing import Annotated, Any, Literal, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError, model_validator

from app.marcus.lesson_plan.lesson_type_classifier import (
    LessonTypeClassification,
    LessonTypeEvidence,
    classify_lesson_type,
)
from app.marcus.lesson_plan.prework_projection import (
    SceneBrief,
    SceneComposer,
    SceneComposeRequest,
)

SCENE_SOURCE_REQUEST_MARKER = "scene_source_request_required"
SourceKind = Literal["slide_narration", "slide_body", "assessment_scenario"]
Coverage = Literal["single_slide", "full_deck"]
Capability = Literal["scene", "motion"]


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


LocalNonBlank = Annotated[str, AfterValidator(_non_blank)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_default=True,
    )


class SceneSeed(_StrictModel):
    seed_id: LocalNonBlank
    text: LocalNonBlank
    source_ref: LocalNonBlank
    source_kind: SourceKind
    slide_key: LocalNonBlank | None
    sme_scenario: bool
    setup_only: bool = False
    forbidden_resolution_spans: tuple[LocalNonBlank, ...] = ()

    @model_validator(mode="after")
    def _scenario_flag_matches_source_kind(self) -> SceneSeed:
        if self.sme_scenario and self.source_kind != "assessment_scenario":
            raise ValueError("SME scenario flag requires assessment_scenario source kind")
        if self.setup_only and (
            self.source_kind != "assessment_scenario" or not self.forbidden_resolution_spans
        ):
            raise ValueError("setup-only seed requires explicit assessment resolution spans")
        return self


class SceneProjectionRequest(_StrictModel):
    seeds: tuple[SceneSeed, ...]
    candidate_ids: tuple[LocalNonBlank, ...]
    lesson_type_evidence: LessonTypeEvidence
    payoff_slide_inventory: tuple[LocalNonBlank, ...]
    payoff_slide_keys: tuple[LocalNonBlank, ...]
    requested_coverage: Coverage
    required_capabilities: tuple[Capability, ...]
    available_coverage: Coverage
    available_capabilities: tuple[Capability, ...]
    extraction_losses: tuple[LocalNonBlank, ...] = ()

    @classmethod
    def from_raw_candidates(
        cls, *, raw_candidates: tuple[object, ...], **request_fields: Any
    ) -> Self:
        """Normalize an untrusted candidate boundary before strict projection."""
        receipt = normalize_scene_candidates(raw_candidates)
        return cls(
            seeds=receipt.seeds,
            extraction_losses=receipt.rejection_losses,
            **request_fields,
        )

    @model_validator(mode="after")
    def _unique_inventory_coordinates(self) -> SceneProjectionRequest:
        identities = tuple(seed.seed_id for seed in self.seeds)
        refs = tuple(seed.source_ref for seed in self.seeds)
        for label, values in (
            ("seed ids", identities),
            ("seed refs", refs),
            ("candidate ids", self.candidate_ids),
            ("payoff inventory", self.payoff_slide_inventory),
            ("payoff targets", self.payoff_slide_keys),
            ("required capabilities", self.required_capabilities),
            ("available capabilities", self.available_capabilities),
        ):
            if len(set(values)) != len(values):
                raise ValueError(f"{label} must be unique")
        if "scene" not in self.required_capabilities:
            raise ValueError("Scene projection requires the scene capability")
        return self


class SceneGateReceipt(_StrictModel):
    failures: tuple[LocalNonBlank, ...]


class SceneFaithfulnessPromptConstraints(_StrictModel):
    meaningful_seed_anchors: tuple[str, ...]
    required_shared_count: int
    minimum_recall: float
    digit_multiset: tuple[tuple[str, int], ...]
    negator_multiset: tuple[tuple[str, int], ...]


class SceneNormalizationReceipt(_StrictModel):
    seeds: tuple[SceneSeed, ...]
    rejection_losses: tuple[LocalNonBlank, ...]


class SceneProjectionResult(_StrictModel):
    scene: SceneBrief
    selected_seed_id: LocalNonBlank | None
    selected_seed_ref: LocalNonBlank | None
    classification: LessonTypeClassification
    gate_receipt: SceneGateReceipt
    extraction_losses: tuple[LocalNonBlank, ...]
    operator_warnings: tuple[LocalNonBlank, ...]
    introduced_terms: tuple[LocalNonBlank, ...] = ()


def normalize_scene_candidates(
    raw_candidates: tuple[object, ...],
) -> SceneNormalizationReceipt:
    """Exclude malformed raw candidates with indexed, deterministic losses."""
    seeds: list[SceneSeed] = []
    losses: list[str] = []
    seen_ids: set[str] = set()
    seen_refs: set[str] = set()
    for index, raw in enumerate(raw_candidates):
        if isinstance(raw, SceneSeed):
            candidate = raw
        elif not isinstance(raw, Mapping):
            losses.append(f"scene_candidate_malformed:{index}")
            continue
        else:
            source_ref = raw.get("source_ref")
            if not isinstance(source_ref, str) or not source_ref.strip():
                losses.append(f"scene_candidate_unreferenced:{index}")
                continue
            if any(
                not isinstance(raw.get(field), str) or not raw.get(field, "").strip()
                for field in ("seed_id", "text")
            ):
                losses.append(f"scene_candidate_blank:{index}")
                continue
            try:
                candidate = SceneSeed.model_validate(dict(raw))
            except ValidationError:
                losses.append(f"scene_candidate_malformed:{index}")
                continue
        if candidate.seed_id in seen_ids or candidate.source_ref in seen_refs:
            losses.append(f"scene_candidate_duplicate:{index}")
            continue
        seeds.append(candidate)
        seen_ids.add(candidate.seed_id)
        seen_refs.add(candidate.source_ref)
    return SceneNormalizationReceipt(seeds=tuple(seeds), rejection_losses=tuple(losses))


def select_scene_seed(request: SceneProjectionRequest) -> SceneSeed | None:
    """Choose an eligible scenario first, then lexical source-ref/seed-id order."""
    by_id = {seed.seed_id: seed for seed in request.seeds}
    candidates = tuple(
        by_id[candidate] for candidate in request.candidate_ids if candidate in by_id
    )
    if not candidates:
        return None
    scenarios = tuple(seed for seed in candidates if seed.sme_scenario)
    eligible = scenarios or candidates
    return min(eligible, key=lambda seed: (seed.source_ref, seed.seed_id))


_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "being",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "he",
        "her",
        "hers",
        "him",
        "his",
        "i",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "our",
        "she",
        "that",
        "the",
        "their",
        "them",
        "they",
        "this",
        "through",
        "to",
        "was",
        "we",
        "were",
        "while",
        "with",
        "you",
        "your",
    }
)
_NEGATORS = frozenset({"no", "not", "never", "without"})
_WORD_NUMERALS = frozenset(
    {
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
        "hundred",
        "thousand",
        "million",
    }
)


def _tokens(text: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = normalized.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'}))
    normalized = re.sub(r"\bcan't\b", "can not", normalized)
    normalized = re.sub(r"\bwon't\b", "will not", normalized)
    normalized = re.sub(r"n't\b", " not", normalized)
    tokens: list[str] = []
    current: list[str] = []
    for character in normalized:
        if not character.isalnum():
            if current:
                tokens.append("".join(current))
                current.clear()
            continue
        name = unicodedata.name(character, "")
        if character.isascii() or character.isdigit() or "LATIN" in name:
            current.append(character)
        else:
            if current:
                tokens.append("".join(current))
                current.clear()
            tokens.append(character)
    if current:
        tokens.append("".join(current))
    return tuple(tokens)


def scene_faithfulness_prompt_constraints(seed_text: str) -> SceneFaithfulnessPromptConstraints:
    """Expose the deterministic gate anchors that an authored Scene must preserve."""
    tokens = _tokens(seed_text)
    meaningful = tuple(sorted({token for token in tokens if token not in _STOPWORDS}))
    return SceneFaithfulnessPromptConstraints(
        meaningful_seed_anchors=meaningful,
        required_shared_count=len(meaningful) if len(meaningful) < 2 else 2,
        minimum_recall=0.30,
        digit_multiset=tuple(sorted(Counter(token for token in tokens if token.isdigit()).items())),
        negator_multiset=tuple(
            sorted(Counter(token for token in tokens if token in _NEGATORS).items())
        ),
    )


def _faithfulness_failures(seed_text: str, scene_text: str) -> tuple[tuple[str, ...], bool, bool]:
    seed_tokens = _tokens(seed_text)
    scene_tokens = _tokens(scene_text)
    constraints = scene_faithfulness_prompt_constraints(seed_text)
    seed_meaningful = set(constraints.meaningful_seed_anchors)
    scene_meaningful = {token for token in scene_tokens if token not in _STOPWORDS}
    shared = seed_meaningful & scene_meaningful
    recall = len(shared) / len(seed_meaningful) if seed_meaningful else 0.0
    failures: list[str] = []
    if len(shared) < constraints.required_shared_count or recall < constraints.minimum_recall:
        failures.append("scene_faithfulness_overlap")

    seed_digits = Counter(token for token in seed_tokens if token.isdigit())
    scene_digits = Counter(token for token in scene_tokens if token.isdigit())
    seed_word_numerals = Counter(token for token in seed_tokens if token in _WORD_NUMERALS)
    scene_word_numerals = Counter(token for token in scene_tokens if token in _WORD_NUMERALS)
    removed_digit_anchors = seed_digits - scene_digits
    added_digits = scene_digits - seed_digits
    removed_word_numerals = seed_word_numerals - scene_word_numerals
    has_word_digit_uncertainty = bool(
        added_digits
        and not removed_digit_anchors
        and sum(added_digits.values()) <= sum(removed_word_numerals.values())
    )
    if removed_digit_anchors or (added_digits and not has_word_digit_uncertainty):
        failures.append("scene_faithfulness_numeral")

    seed_negators = Counter(token for token in seed_tokens if token in _NEGATORS)
    scene_negators = Counter(token for token in scene_tokens if token in _NEGATORS)
    if seed_negators != scene_negators:
        failures.append("scene_faithfulness_negator")
    return tuple(failures), has_word_digit_uncertainty, bool(seed_negators or scene_negators)


_INNOCENCE_CONNECTIVES = frozenset({"again", "still", "recurring", "notice", "notices"})
_DIAGNOSTIC_COMPLETION = re.compile(
    r"\b(?:barrier|cause|reason|solution|diagnosis)\b.{0,80}\b(?:is|are|was|were)\b",
    re.IGNORECASE,
)


def _setup_innocence_review(
    seed: SceneSeed, scene_text: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not seed.setup_only:
        return (), ()
    scene_tokens = _tokens(scene_text)
    scene_meaningful = {token for token in scene_tokens if token not in _STOPWORDS}
    seed_meaningful = {token for token in _tokens(seed.text) if token not in _STOPWORDS}
    failures: list[str] = []
    for forbidden in seed.forbidden_resolution_spans:
        forbidden_meaningful = {token for token in _tokens(forbidden) if token not in _STOPWORDS}
        shared = scene_meaningful & forbidden_meaningful
        recall = len(shared) / len(forbidden_meaningful) if forbidden_meaningful else 0.0
        if forbidden.casefold() in scene_text.casefold() or recall >= 0.60:
            failures.append("scene_innocence_forbidden_resolution")
            break
    if _DIAGNOSTIC_COMPLETION.search(scene_text):
        failures.append("scene_innocence_diagnostic_completion")
    invented = scene_meaningful - seed_meaningful - _INNOCENCE_CONNECTIVES
    return tuple(dict.fromkeys(failures)), tuple(sorted(invented))


def _degraded_scene(
    status: Literal["degraded", "unavailable"], failures: tuple[str, ...], ref: str | None
) -> SceneBrief:
    return SceneBrief(
        status=status,
        text=None,
        source_refs=(ref,) if ref else (),
        known_losses=failures,
        marker=SCENE_SOURCE_REQUEST_MARKER,
        lesson_type=None,
        archetype=None,
    )


def _scope_supported(request: SceneProjectionRequest) -> bool:
    coverage_ok = (
        request.requested_coverage == "single_slide" or request.available_coverage == "full_deck"
    )
    capabilities_ok = set(request.required_capabilities).issubset(request.available_capabilities)
    return coverage_ok and capabilities_ok


def compose_scene_projection(
    request: SceneProjectionRequest, composer: SceneComposer
) -> SceneProjectionResult:
    """Gate normalized evidence, call the injected composer once, then verify its output."""
    classification = classify_lesson_type(request.lesson_type_evidence)
    selected = select_scene_seed(request)
    failures: list[str] = []
    inventory_ids = {seed.seed_id for seed in request.seeds}
    inventory_refs = {seed.source_ref for seed in request.seeds}
    if any(candidate not in inventory_ids for candidate in request.candidate_ids):
        failures.append("scene_candidate_unresolved")
    if selected is None:
        failures.append("scene_seed_unavailable")
    if not set(request.lesson_type_evidence.evidence_refs).issubset(inventory_refs):
        failures.append("scene_lesson_evidence_unresolved")
    if classification.status == "ambiguous":
        failures.append("scene_lesson_type_ambiguous")
    elif classification.status == "insufficient":
        failures.append("scene_lesson_type_insufficient")
    if selected is not None and not _scope_supported(request):
        failures.append("scene_source_scope_unsupported")
    if selected is not None and (
        not request.payoff_slide_keys
        or not set(request.payoff_slide_keys).issubset(request.payoff_slide_inventory)
    ):
        failures.append("scene_payoff_unresolved")

    if failures:
        status: Literal["degraded", "unavailable"] = (
            "unavailable" if selected is None else "degraded"
        )
        failure_tuple = tuple(failures)
        return SceneProjectionResult(
            scene=_degraded_scene(status, failure_tuple, selected.source_ref if selected else None),
            selected_seed_id=selected.seed_id if selected else None,
            selected_seed_ref=selected.source_ref if selected else None,
            classification=classification,
            gate_receipt=SceneGateReceipt(failures=failure_tuple),
            extraction_losses=request.extraction_losses,
            operator_warnings=(),
        )

    assert selected is not None
    assert classification.lesson_type is not None and classification.archetype is not None
    formed = SceneComposeRequest(
        seed_text=selected.text,
        source_refs=(selected.source_ref,),
        orienting_hint=None,
        lesson_type=classification.lesson_type,
        archetype=classification.archetype,
        payoff_slide_keys=request.payoff_slide_keys,
        setup_only=selected.setup_only,
    )
    returned = composer(formed)
    if not isinstance(returned, SceneBrief):
        failures.append("scene_composer_contract_invalid")
        scene = _degraded_scene("degraded", tuple(failures), selected.source_ref)
    else:
        try:
            scene = SceneBrief.model_validate(returned.model_dump(mode="python"))
        except ValidationError:
            failures.append("scene_composer_contract_invalid")
            scene = _degraded_scene("degraded", tuple(failures), selected.source_ref)
        else:
            if scene.status != "authored":
                failures.append("scene_composer_not_authored")
            if scene.source_refs != (selected.source_ref,):
                failures.append("scene_provenance_mismatch")
            if scene.lesson_type != classification.lesson_type:
                failures.append("scene_lesson_type_mismatch")
            if scene.archetype != classification.archetype:
                failures.append("scene_archetype_mismatch")

    warnings = [
        "actual_payoff_sufficiency_operator_check",
        "semantic_faithfulness_operator_check",
    ]
    introduced_terms: tuple[str, ...] = ()
    if not failures and scene.text is not None:
        faithfulness, word_digit_uncertain, has_negation = _faithfulness_failures(
            selected.text, scene.text
        )
        failures.extend(faithfulness)
        innocence_failures, introduced_terms = _setup_innocence_review(selected, scene.text)
        failures.extend(innocence_failures)
        if introduced_terms:
            warnings.append("scene_invented_terms_operator_check")
        if word_digit_uncertain:
            warnings.append("word_digit_equivalence_operator_check")
        if has_negation:
            warnings.append("negation_scope_operator_check")
    if failures:
        scene = _degraded_scene("degraded", tuple(failures), selected.source_ref)

    return SceneProjectionResult(
        scene=scene,
        selected_seed_id=selected.seed_id,
        selected_seed_ref=selected.source_ref,
        classification=classification,
        gate_receipt=SceneGateReceipt(failures=tuple(failures)),
        extraction_losses=request.extraction_losses,
        operator_warnings=tuple(warnings),
        introduced_terms=introduced_terms,
    )


__all__ = [
    "SCENE_SOURCE_REQUEST_MARKER",
    "SceneGateReceipt",
    "SceneFaithfulnessPromptConstraints",
    "SceneNormalizationReceipt",
    "SceneProjectionRequest",
    "SceneProjectionResult",
    "SceneSeed",
    "compose_scene_projection",
    "normalize_scene_candidates",
    "scene_faithfulness_prompt_constraints",
    "select_scene_seed",
]

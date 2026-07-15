"""Named live structured-output adapters for 07W.1 semantic writers."""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Final, Generic, TypeVar

import yaml
from pydantic import BaseModel

from app.marcus.lesson_plan.deep_dive_projection import (
    DEEP_DIVE_DEGRADED_MARKER,
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonWriterResult,
    deep_dive_candidate_would_author,
    deterministic_deep_dive_writer,
    prose_bold_parity_is_valid,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    DEEP_DIVE_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_provider_payload,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    canonical_json_mapping as _canonical_json_mapping,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    provider_payload_digest as _payload_digest,
)
from app.marcus.lesson_plan.prework_projection import (
    PromiseProjection,
    PromiseTransformRequest,
    SceneBrief,
    SceneComposeRequest,
)
from app.marcus.lesson_plan.scene_extraction import scene_faithfulness_prompt_constraints
from app.models.adapter import ChatModelHandle, make_chat_model
from app.models.specialist_model_config import SpecialistModelConfig
from app.runtime.cascade_config import load_pricing

CONFIG_PATH = Path(__file__).with_name("workbook_writer_model_config.yaml")
WORKBOOK_WRITER_REQUEST_TIMEOUT_S: Final[float] = 120.0
WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS: Final[int] = 32000
"""Deep-Dive-only ceiling: GPT-5 spends completion budget on hidden reasoning first."""
WORKBOOK_DEEP_DIVE_REQUEST_TIMEOUT_S: Final[float] = 300.0
"""Deep-Dive-only live request budget for the full production authority packet."""
T = TypeVar("T", bound=BaseModel)


class DeepDiveProviderOutputError(ValueError):
    """Raw Deep-Dive provider mapping could not enter the strict candidate contract."""


def _load_config() -> tuple[SpecialistModelConfig, str]:
    raw = CONFIG_PATH.read_bytes()
    return (
        SpecialistModelConfig.model_validate(yaml.safe_load(raw), strict=True),
        "sha256:" + hashlib.sha256(raw).hexdigest(),
    )


class _StructuredWriter(Generic[T]):
    output_type: type[T]
    purpose: str

    def __init__(
        self,
        *,
        chat_factory: Callable[..., ChatModelHandle] = make_chat_model,
        max_completion_tokens: int = 4096,
        request_timeout: float = WORKBOOK_WRITER_REQUEST_TIMEOUT_S,
        effective_adapter: str | None = None,
        effective_identity_extra: Mapping[str, object] | None = None,
    ) -> None:
        if isinstance(request_timeout, bool) or not isinstance(
            request_timeout, (int, float)
        ):
            raise ValueError("request_timeout must be a positive finite number")
        try:
            request_timeout = float(request_timeout)
        except OverflowError as exc:
            raise ValueError("request_timeout must be a positive finite number") from exc
        if not math.isfinite(request_timeout) or request_timeout <= 0:
            raise ValueError("request_timeout must be a positive finite number")
        config, base_model_config_digest = _load_config()
        self.model_config_digest = base_model_config_digest
        if effective_adapter is not None:
            identity = {
                "adapter": effective_adapter,
                "base_workbook_writer_config_digest": base_model_config_digest,
                "max_completion_tokens": max_completion_tokens,
                "max_retries": 0,
                "request_timeout": request_timeout,
            }
            extras = dict(effective_identity_extra or {})
            reserved = identity.keys() & extras.keys()
            if reserved:
                raise ValueError(
                    "effective identity extras cannot override reserved keys: "
                    + ", ".join(sorted(reserved))
                )
            identity.update(extras)
            effective = json.dumps(
                identity,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
            self.model_config_digest = "sha256:" + hashlib.sha256(effective).hexdigest()
        self.model_config = config
        self._handle = chat_factory(
            config.specialist_id,
            per_call_override=config.default_model,
            temperature=config.temperature_default,
            request_timeout=request_timeout,
            max_retries=0,
            max_completion_tokens=max_completion_tokens,
            system_prompt_hash=self.model_config_digest,
        )
        self.calls_made = 0
        self.last_latency_ms: float | None = None
        self.last_request_id: str | None = None
        self.last_input_tokens: int | None = None
        self.last_output_tokens: int | None = None
        self.last_cost_usd: float | None = None
        self.last_cost_unavailable_reason: str | None = None

    def _invoke(self, request: BaseModel) -> T:
        self.calls_made += 1
        started = time.perf_counter()
        structured = self._handle.chat.with_structured_output(self.output_type, include_raw=True)
        response: Any = structured.invoke(
            [
                (
                    "system",
                    self._system_prompt(request),
                ),
                (
                    "human",
                    json.dumps(request.model_dump(mode="json"), sort_keys=True, ensure_ascii=False),
                ),
            ]
        )
        self.last_latency_ms = (time.perf_counter() - started) * 1000
        parsed = response
        raw = response
        if isinstance(response, dict) and "parsed" in response:
            if response.get("parsing_error") is not None:
                raise ValueError(f"structured writer parse failed: {response['parsing_error']}")
            parsed = response.get("parsed")
            raw = response.get("raw")
        self._record_metadata(raw)
        if isinstance(parsed, self.output_type):
            return parsed
        return self.output_type.model_validate(parsed, strict=True)

    def _record_metadata(self, raw: object) -> None:
        metadata = getattr(raw, "response_metadata", None)
        if isinstance(metadata, dict):
            self.last_request_id = metadata.get("request_id")
            usage = metadata.get("token_usage")
            if not isinstance(usage, dict):
                usage = metadata.get("usage")
            if not isinstance(usage, dict):
                usage = {}
            if isinstance(usage, dict):
                self.last_input_tokens = usage.get("prompt_tokens")
                if self.last_input_tokens is None:
                    self.last_input_tokens = usage.get("input_tokens")
                self.last_output_tokens = usage.get("completion_tokens")
                if self.last_output_tokens is None:
                    self.last_output_tokens = usage.get("output_tokens")
                supplied_cost = usage.get("cost_usd")
                if supplied_cost is None:
                    supplied_cost = usage.get("total_cost")
                if supplied_cost is not None:
                    self.last_cost_usd = float(supplied_cost)
            supplied_cost = metadata.get("cost_usd")
            if supplied_cost is None:
                supplied_cost = metadata.get("total_cost")
            if supplied_cost is not None:
                self.last_cost_usd = float(supplied_cost)
        if self.last_cost_usd is None:
            if self.last_input_tokens is not None and self.last_output_tokens is not None:
                try:
                    self.last_cost_usd = load_pricing().compute_cost(
                        self.model_config.default_model,
                        input_tokens=self.last_input_tokens,
                        output_tokens=self.last_output_tokens,
                    )
                except (OSError, ValueError, KeyError) as exc:
                    self.last_cost_unavailable_reason = (
                        f"pricing_calculation_unavailable:{type(exc).__name__}"
                    )
            else:
                self.last_cost_unavailable_reason = (
                    "provider_response_supplied_no_token_or_cost_evidence"
                )

    def _system_prompt(self, request: BaseModel) -> str:
        return (
            f"Author exactly one closed {self.purpose} object. "
            "Never add Markdown headings or unsupported facts."
        )


class LiveSceneComposer(_StructuredWriter[SceneBrief]):
    output_type = SceneBrief
    purpose = "SceneBrief"

    def __init__(
        self,
        *,
        chat_factory: Callable[..., ChatModelHandle] = make_chat_model,
        max_completion_tokens: int = 4096,
    ) -> None:
        super().__init__(
            chat_factory=chat_factory,
            max_completion_tokens=max_completion_tokens,
            request_timeout=WORKBOOK_WRITER_REQUEST_TIMEOUT_S,
        )

    def __call__(self, request: SceneComposeRequest) -> SceneBrief:
        return self._invoke(request)

    def _system_prompt(self, request: BaseModel) -> str:
        assert isinstance(request, SceneComposeRequest)
        faithfulness = scene_faithfulness_prompt_constraints(request.seed_text)
        setup_constraint = (
            "This is a setup-only assessment scenario: stage only the observable setup. "
            "Do not state or infer an answer, cause, barrier, reason, solution, diagnosis, "
            "ownership gap, authority gap, or resolution. Stay near-extractive to the seed. "
            "Payoff slides are coverage targets, not content authority. "
            if request.setup_only
            else ""
        )
        return (
            "Return exactly one SceneBrief. For status='authored': text MUST be non-empty; "
            "known_losses MUST be []; marker MUST be null; source_refs MUST equal exactly "
            f"{list(request.source_refs)!r}; lesson_type MUST equal {request.lesson_type!r}; "
            f"archetype MUST equal {request.archetype!r}. For status='degraded' or "
            "'unavailable': text MUST be null; known_losses MUST be non-empty; marker MUST "
            "be non-empty. Never mix authored with a marker/loss. No headings or list labels. "
            "For authored text, pass the deterministic faithfulness gate: preserve at least "
            f"{faithfulness.required_shared_count} meaningful anchors and at least "
            f"{faithfulness.minimum_recall:.0%} recall from "
            f"{list(faithfulness.meaningful_seed_anchors)!r}; preserve the exact digit "
            f"multiset {dict(faithfulness.digit_multiset)!r} and exact negator multiset "
            f"{dict(faithfulness.negator_multiset)!r}. Do not copy the Correct Answer and do "
            "not fabricate a resolution. "
            f"{setup_constraint}"
            f"Ground only in this seed: {request.seed_text!r}. Relevant payoff slides: "
            f"{list(request.payoff_slide_keys)!r}."
        )


class LivePromiseTransformer(_StructuredWriter[PromiseProjection]):
    output_type = PromiseProjection
    purpose = "PromiseProjection"

    def __init__(
        self,
        *,
        chat_factory: Callable[..., ChatModelHandle] = make_chat_model,
        max_completion_tokens: int = 4096,
    ) -> None:
        super().__init__(
            chat_factory=chat_factory,
            max_completion_tokens=max_completion_tokens,
            request_timeout=WORKBOOK_WRITER_REQUEST_TIMEOUT_S,
        )

    def __call__(self, request: PromiseTransformRequest) -> PromiseProjection:
        return self._invoke(request)

    def _system_prompt(self, request: BaseModel) -> str:
        assert isinstance(request, PromiseTransformRequest)
        objective_ids = [row.objective_id for row in request.objectives]
        objective_facts = [
            {"objective_id": row.objective_id, "text": row.text} for row in request.objectives
        ]
        return (
            "Return exactly one PromiseProjection. For status='authored': vows MUST contain "
            f"exactly these objective IDs in this order: {objective_ids!r}; known_losses MUST "
            "be []; marker MUST be null; every vow text is one non-empty line with no heading, "
            "bullet prefix, unresolved placeholder, or invented numeral. For status='degraded' "
            "or 'unavailable': vows MUST be []; known_losses MUST be non-empty; marker MUST be "
            "non-empty. Never mix authored with a marker/loss. Preserve pertinent ability and "
            f"transform only these ratified objective facts: {objective_facts!r}."
        )


def _compact_deep_dive_payload(request: DeepDiveSkeletonRequest) -> dict[str, Any]:
    """Build a single, de-duplicated model-facing view of the Deep-Dive request.

    Every source claim's text is a verbatim copy of its narration/source span
    text, so embedding both doubles the largest field and, together with the old
    system-prompt re-embedding, inflated the request to ~12K tokens. Here the
    request is expressed once: spans carry the text, and a claim whose text
    equals its single referenced span points at that span instead of repeating
    it. The request object, gate, journal authority, and digests are untouched;
    only the bytes the provider reads change.
    """
    span_text = {span.span_id: span.text for span in request.source_spans}
    claims: list[dict[str, object]] = []
    for claim in request.source_claims:
        entry: dict[str, object] = {
            "claim_id": claim.claim_id,
            "role": claim.role,
            "source_span_refs": list(claim.source_span_refs),
        }
        if (
            len(claim.source_span_refs) == 1
            and span_text.get(claim.source_span_refs[0]) == claim.text
        ):
            entry["text_same_as_span"] = claim.source_span_refs[0]
        else:
            entry["text"] = claim.text
        claims.append(entry)
    return {
        "lesson_ref": request.lesson_ref,
        "slide_authority_map_digest": request.slide_authority_map_digest,
        "source_spans": [
            {"span_id": span.span_id, "text": span.text, "source_ref": span.source_ref}
            for span in request.source_spans
        ],
        "source_claims": claims,
        "abilities": [
            {"ability_id": ability.ability_id, "text": ability.text}
            for ability in request.abilities
        ],
    }


def _is_bold_parity_failure(normalized: Mapping[str, Any]) -> bool:
    """True only when an authored payload fails strict bold-parity on its prose.

    Isolates the fragile bold-marker mismatch from every other structural defect
    so the safe-construction route never masks a genuine honesty failure.
    """
    if normalized.get("status") != "authored":
        return False
    sections = normalized.get("sections")
    if not isinstance(sections, list):
        return False
    proses: list[str] = []
    for section in sections:
        if not isinstance(section, Mapping):
            return False
        prose = section.get("prose")
        if not isinstance(prose, str):
            return False
        proses.append(prose)
    return not prose_bold_parity_is_valid(tuple(proses))


class LiveDeepDiveWriter(_StructuredWriter[DeepDiveSkeletonWriterResult]):
    output_type = DeepDiveSkeletonWriterResult
    purpose = "DeepDiveSkeletonWriterResult"

    def __init__(
        self,
        *,
        chat_factory: Callable[..., ChatModelHandle] = make_chat_model,
        max_completion_tokens: int = WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS,
        request_timeout: float = WORKBOOK_DEEP_DIVE_REQUEST_TIMEOUT_S,
    ) -> None:
        self.provider_schema = DeepDiveSkeletonWriterResult.model_json_schema()
        self.provider_schema_digest = _payload_digest(self.provider_schema)
        self.last_raw_provider_payload: dict[str, Any] | None = None
        self.last_raw_provider_payload_digest: str | None = None
        self.last_provider_normalizations: tuple[str, ...] = ()
        self.last_normalized_provider_payload_digest: str | None = None
        self.last_provider_normalization_error: str | None = None
        self.last_fallback_engaged: bool = False
        self.last_fallback_reason: str | None = None
        self.last_live_failed_provider_payload: dict[str, Any] | None = None
        super().__init__(
            chat_factory=chat_factory,
            max_completion_tokens=max_completion_tokens,
            request_timeout=request_timeout,
            effective_adapter="LiveDeepDiveWriter",
            effective_identity_extra={
                "provider_contract_mode": DEEP_DIVE_PROVIDER_CONTRACT_MODE,
                "provider_schema_digest": self.provider_schema_digest,
                "provider_normalizer_version": DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
            },
        )

    def __call__(self, request: DeepDiveSkeletonRequest) -> DeepDiveSkeletonWriterResult:
        self.calls_made += 1
        self.last_raw_provider_payload = None
        self.last_raw_provider_payload_digest = None
        self.last_provider_normalizations = ()
        self.last_normalized_provider_payload_digest = None
        self.last_provider_normalization_error = None
        self.last_fallback_engaged = False
        self.last_fallback_reason = None
        self.last_live_failed_provider_payload = None
        started = time.perf_counter()
        structured = self._handle.chat.with_structured_output(
            self.provider_schema, include_raw=True
        )
        response: Any = structured.invoke(
            [
                ("system", self._system_prompt(request)),
                (
                    "human",
                    json.dumps(
                        _compact_deep_dive_payload(request),
                        sort_keys=True,
                        ensure_ascii=False,
                    ),
                ),
            ]
        )
        self.last_latency_ms = (time.perf_counter() - started) * 1000
        parsed = response
        raw_response = response
        if isinstance(response, dict) and "parsed" in response:
            if response.get("parsing_error") is not None:
                raise DeepDiveProviderOutputError(
                    f"structured writer parse failed: {response['parsing_error']}"
                )
            parsed = response.get("parsed")
            raw_response = response.get("raw")
        self._record_metadata(raw_response)
        if not isinstance(parsed, dict):
            raise DeepDiveProviderOutputError("Deep Dive provider payload must be a mapping")
        try:
            raw_payload = _canonical_json_mapping(parsed)
            self.last_raw_provider_payload = raw_payload
            self.last_raw_provider_payload_digest = _payload_digest(raw_payload)
            try:
                normalized, records = normalize_deep_dive_provider_payload(parsed)
            except (TypeError, ValueError) as exc:
                self.last_provider_normalization_error = f"{type(exc).__name__}: {exc}"
                raise
            self.last_provider_normalizations = records
            self.last_normalized_provider_payload_digest = _payload_digest(normalized)
            try:
                candidate = DeepDiveSkeletonWriterResult.model_validate_json(
                    json.dumps(
                        normalized,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                        allow_nan=False,
                    ),
                    strict=True,
                )
            except (TypeError, ValueError):
                # B2: a fragile bold-parity mismatch (dense source tokens such as
                # ``$5.2 trillion`` or ``'Digital Front Door'``) must not hard-pause
                # 07W.1 when a deterministic safe construction is available. Genuine
                # structural defects (unsafe markers, extra fields, coercion) keep
                # failing loud, so honesty invariants for AUTHORED output are intact.
                if _is_bold_parity_failure(normalized):
                    return self._degrade_to_safe_construction(
                        request, raw_payload, reason="bold_parity_degrade"
                    )
                raise
        except (TypeError, ValueError) as exc:
            raise DeepDiveProviderOutputError(str(exc)) from exc
        if deep_dive_candidate_would_author(request, candidate):
            return candidate
        # B1: the live candidate validated but does not conform to the skeleton
        # gate. Prefer a deterministic authored construction when the authority
        # supports one; otherwise keep the live candidate's honest disposition
        # (and its live raw evidence) unchanged.
        fallback = deterministic_deep_dive_writer(request)
        if deep_dive_candidate_would_author(request, fallback):
            return self._emit_safe_construction(
                request, raw_payload, fallback, reason="live_gate_nonauthored"
            )
        return candidate

    def _degrade_to_safe_construction(
        self,
        request: DeepDiveSkeletonRequest,
        live_failed_payload: dict[str, Any],
        *,
        reason: str,
    ) -> DeepDiveSkeletonWriterResult:
        """Route an unvalidatable provider payload to the safe construction.

        Prefers the deterministic authored skeleton when the authority supports
        one; otherwise emits a clearly typed degraded candidate rather than
        hard-pausing 07W.1.
        """
        fallback = deterministic_deep_dive_writer(request)
        if deep_dive_candidate_would_author(request, fallback):
            return self._emit_safe_construction(
                request, live_failed_payload, fallback, reason=reason
            )
        degraded = DeepDiveSkeletonWriterResult(
            status="degraded",
            sections=(),
            bold_terms=(),
            known_losses=("deep_dive_execution_failed",),
            marker=DEEP_DIVE_DEGRADED_MARKER,
        )
        return self._emit_safe_construction(
            request, live_failed_payload, degraded, reason=reason
        )

    def _emit_safe_construction(
        self,
        request: DeepDiveSkeletonRequest,
        live_failed_payload: dict[str, Any] | None,
        candidate: DeepDiveSkeletonWriterResult,
        *,
        reason: str,
    ) -> DeepDiveSkeletonWriterResult:
        """Re-anchor provider evidence onto the returned safe construction.

        The provider evidence contract requires the recorded raw payload to
        normalize back to the returned candidate. The (failed) live payload is
        preserved on ``last_live_failed_provider_payload`` for telemetry and the
        fallback is surfaced through ``last_fallback_*`` so callers can attribute
        the disposition without changing the wiring's evidence invariants.
        """
        effective = _canonical_json_mapping(candidate.model_dump(mode="json"))
        self.last_live_failed_provider_payload = live_failed_payload
        self.last_raw_provider_payload = effective
        self.last_raw_provider_payload_digest = _payload_digest(effective)
        self.last_provider_normalizations = ()
        self.last_normalized_provider_payload_digest = _payload_digest(effective)
        self.last_provider_normalization_error = None
        self.last_fallback_engaged = True
        self.last_fallback_reason = reason
        del request
        return candidate

    def _system_prompt(self, request: BaseModel) -> str:
        assert isinstance(request, DeepDiveSkeletonRequest)
        has_delta = any(
            claim.role == "source_supported_delta" for claim in request.source_claims
        )
        coverage_instruction = (
            "Cover every VO claim and at least one source_supported_delta claim. "
            if has_delta
            else "Cover every VO claim; no source_supported_delta authority is declared. "
        )
        return (
            "Return exactly one strict DeepDiveSkeletonWriterResult. Author one section for "
            "each ability in the supplied order. Every claim must cite exactly one declared "
            "source claim and its exact source span. "
            + coverage_instruction
            + "Prose must be exactly the space-joined claim texts. "
            "Bold only an exact term present in that claim's single source text and list bold "
            "metadata once in prose order. Preserve all numerals and negations exactly. Never "
            "invent references, facts, headings, slide deixis, or extra abilities. The user "
            "message carries the authority packet exactly once; a source_claim with "
            "\"text_same_as_span\" reuses the named span's text verbatim as its claim text. "
            "Authority: The safest compliant construction is one skeleton claim per declared "
            "source claim, in authority order, copying its text verbatim except for wrapping "
            "one source-present educational term in **double asterisks**; set each skeleton "
            "claim's source_claim_refs to that claim ID and source_span_refs to its declared "
            "span IDs."
        )


__all__ = [
    "WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS",
    "WORKBOOK_DEEP_DIVE_REQUEST_TIMEOUT_S",
    "DEEP_DIVE_PROVIDER_CONTRACT_MODE",
    "DEEP_DIVE_PROVIDER_NORMALIZER_VERSION",
    "DeepDiveProviderOutputError",
    "LiveDeepDiveWriter",
    "LivePromiseTransformer",
    "LiveSceneComposer",
    "normalize_deep_dive_provider_payload",
]

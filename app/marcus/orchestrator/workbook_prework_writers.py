"""Named live structured-output adapters for 07W.1 semantic writers."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Generic, TypeVar

import yaml
from pydantic import BaseModel

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
T = TypeVar("T", bound=BaseModel)


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
    ) -> None:
        config, self.model_config_digest = _load_config()
        self.model_config = config
        self._handle = chat_factory(
            config.specialist_id,
            per_call_override=config.default_model,
            temperature=config.temperature_default,
            request_timeout=120.0,
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
        metadata = getattr(raw, "response_metadata", None)
        if isinstance(metadata, dict):
            self.last_request_id = metadata.get("request_id")
            usage = metadata.get("token_usage") or metadata.get("usage") or {}
            if isinstance(usage, dict):
                self.last_input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
                self.last_output_tokens = usage.get("completion_tokens") or usage.get(
                    "output_tokens"
                )
                supplied_cost = usage.get("cost_usd") or usage.get("total_cost")
                if supplied_cost is not None:
                    self.last_cost_usd = float(supplied_cost)
            supplied_cost = metadata.get("cost_usd") or metadata.get("total_cost")
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
        if isinstance(parsed, self.output_type):
            return parsed
        return self.output_type.model_validate(parsed, strict=True)

    def _system_prompt(self, request: BaseModel) -> str:
        return (
            f"Author exactly one closed {self.purpose} object. "
            "Never add Markdown headings or unsupported facts."
        )


class LiveSceneComposer(_StructuredWriter[SceneBrief]):
    output_type = SceneBrief
    purpose = "SceneBrief"

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


__all__ = ["LiveSceneComposer", "LivePromiseTransformer"]

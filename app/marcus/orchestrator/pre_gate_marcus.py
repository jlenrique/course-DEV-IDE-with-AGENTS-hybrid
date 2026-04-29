"""Pre-gate-marcus shared LLM node (Story 7a.3).

One LLM call site before each conversational pause-point (G1, G2C, G3, G4).
Renders a C1 template-with-slots prompt from docs/conversational-gates/<gate>.j2,
invokes app.models.adapter.make_chat_model("marcus", ...), and emits a structured
PreFillProposal that the runner threads into _build_decision_card's drafted_proposal.

Composition Spec Section 3.5 (per-specialist gate precedence) UNALTERED:
pre-gate-marcus does NOT promote any gate from non-blocking to blocking.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATE_DIR = Path(__file__).resolve().parents[3] / "docs" / "conversational-gates"


@dataclass(frozen=True)
class PreFillProposal:
    """Structured pre-fill output passed to runner._build_decision_card."""

    decision: str
    directive: str
    rationale: str
    confidence: float
    confidence_signals: tuple[str, ...] = field(default_factory=tuple)


def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
    )


def render_pre_fill_prompt(*, gate_id: str, slot_values: dict[str, Any]) -> str:
    """Render C1 template-with-slots prompt for a conversational gate."""
    template_name = f"{gate_id.lower()}.j2"
    if not (TEMPLATE_DIR / template_name).exists():
        raise FileNotFoundError(f"pre-gate-marcus template not found: {template_name}")
    env = _jinja_env()
    template = env.get_template(template_name)
    return template.render(**slot_values)


def invoke_pre_gate_marcus(
    *,
    gate_id: str,
    slot_values: dict[str, Any],
    chat_model_factory: Any | None = None,
) -> PreFillProposal:
    """Single LLM call site before a conversational gate."""
    if chat_model_factory is None:
        from app.models.adapter import make_chat_model

        chat_model_factory = make_chat_model

    prompt = render_pre_fill_prompt(gate_id=gate_id, slot_values=slot_values)
    handle = chat_model_factory("marcus")
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    return _parse_pre_fill_response(response.content)


def _parse_pre_fill_response(content: str) -> PreFillProposal:
    """Parse LLM JSON output into PreFillProposal; fail-loud on shape drift."""
    data = json.loads(content)
    rationale = data["rationale"]
    if len(rationale) < 20:
        raise ValueError(
            "pre-gate-marcus rationale shorter than NFR-OX3 floor (20 chars): "
            f"got {len(rationale)} chars"
        )
    confidence = float(data["confidence"])
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "pre-gate-marcus confidence must be between 0.0 and 1.0: "
            f"got {confidence}"
        )
    return PreFillProposal(
        decision=data["decision"],
        directive=data["directive"],
        rationale=rationale,
        confidence=confidence,
        confidence_signals=tuple(data.get("confidence_signals") or ()),
    )


__all__ = [
    "PreFillProposal",
    "TEMPLATE_DIR",
    "invoke_pre_gate_marcus",
    "render_pre_fill_prompt",
]

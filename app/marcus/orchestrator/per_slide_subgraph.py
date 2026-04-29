"""Per-slide subgraph fan-out helpers for Slab 7a Story 7a.4."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from langgraph.types import Send, interrupt

from app.models.decision_cards import EscapeCardOption

ESCAPE_RATIONALE_FLOOR = 20
MAX_REVISE_COUNT = 3


@dataclass(frozen=True)
class EscapeCard:
    """Decision-card surfaced when a slide exceeds the revise limit."""

    kind: str
    slide_index: int
    revise_count: int
    options: tuple[str, ...]
    rationale_floor_chars: int = ESCAPE_RATIONALE_FLOOR


class OscillationEscapeRequiredError(RuntimeError):
    """Raised when a fourth revise would violate the max-3 invariant."""

    def __init__(self, escape_card: EscapeCard) -> None:
        super().__init__("oscillation_escape_required")
        self.escape_card = escape_card


class EscapeCardValidationError(ValueError):
    """Raised when an escape-card writer payload is invalid."""


def fan_out_per_slide(
    *,
    gate_id: str,
    slides: list[dict[str, Any]],
    subgraph_node: str = "per_slide_review_subgraph",
) -> list[Send]:
    """Return one LangGraph Send per slide with an isolated checkpoint namespace."""
    sends: list[Send] = []
    for index, slide in enumerate(slides):
        checkpoint_ns = f"{gate_id}/slide-{index}"
        sends.append(
            Send(
                subgraph_node,
                {
                    "gate_id": gate_id,
                    "slide_index": index,
                    "slide": slide,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": f"{checkpoint_ns}/review",
                },
            )
        )
    return sends


def per_slide_review_subgraph(
    state: dict[str, Any],
    *,
    interrupt_fn: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Subgraph node: one isolated interrupt boundary for one slide."""
    pause = interrupt_fn or interrupt
    decision = pause(
        {
            "gate_id": state["gate_id"],
            "slide_index": state["slide_index"],
            "slide": state["slide"],
            "checkpoint_ns": state["checkpoint_ns"],
        }
    )
    return {
        "gate_id": state["gate_id"],
        "slide_index": state["slide_index"],
        "checkpoint_ns": state["checkpoint_ns"],
        "operator_decision": decision or {},
    }


def join_per_slide_results(
    results: list[dict[str, Any]],
    *,
    expected_count: int | None = None,
) -> list[dict[str, Any]]:
    """Join completed slide results in slide order after fan-out returns."""
    ordered = sorted(results, key=lambda item: int(item["slide_index"]))
    actual_count = len({item["slide_index"] for item in ordered})
    if expected_count is not None and actual_count != expected_count:
        raise ValueError(f"expected {expected_count} slide results, got {len(ordered)}")
    return ordered


def revise_or_escape(*, slide_index: int, revise_count: int) -> int:
    """Increment revise count, or surface an escape card before a fourth revise."""
    if revise_count < MAX_REVISE_COUNT:
        return revise_count + 1
    escape_card = _escape_card(slide_index=slide_index, revise_count=revise_count)
    raise OscillationEscapeRequiredError(escape_card)


def apply_escape_card(
    *,
    option: EscapeCardOption | str,
    slide_index: int,
    rationale: str = "",
) -> dict[str, Any]:
    """Validate and apply an oscillation escape-card choice."""
    selected = EscapeCardOption(option)
    if selected == EscapeCardOption.ACCEPT_AS_IS and len(rationale) < ESCAPE_RATIONALE_FLOOR:
        raise EscapeCardValidationError(
            f"accept-as-is rationale must be at least {ESCAPE_RATIONALE_FLOOR} chars"
        )
    if selected == EscapeCardOption.REJECT_AND_SKIP_SLIDE:
        return {"slide_index": slide_index, "status": "skipped", "escape_option": selected.value}
    if selected == EscapeCardOption.ABORT_RUN:
        return {"slide_index": slide_index, "status": "halted", "escape_option": selected.value}
    return {
        "slide_index": slide_index,
        "status": "accepted",
        "escape_option": selected.value,
        "rationale": rationale,
    }


def measure_escape_surface_ms(*, slide_index: int, revise_count: int) -> float:
    """Return elapsed time for the escape-card path; used by the NFR-OR1 test."""
    start = perf_counter()
    try:
        revise_or_escape(slide_index=slide_index, revise_count=revise_count)
    except OscillationEscapeRequiredError:
        return (perf_counter() - start) * 1000
    raise AssertionError("escape path was not reached")


def _escape_card(*, slide_index: int, revise_count: int) -> EscapeCard:
    return EscapeCard(
        kind="oscillation_escape_required",
        slide_index=slide_index,
        revise_count=revise_count,
        options=tuple(option.value for option in EscapeCardOption),
    )


__all__ = [
    "ESCAPE_RATIONALE_FLOOR",
    "MAX_REVISE_COUNT",
    "EscapeCard",
    "EscapeCardValidationError",
    "OscillationEscapeRequiredError",
    "apply_escape_card",
    "fan_out_per_slide",
    "join_per_slide_results",
    "measure_escape_surface_ms",
    "per_slide_review_subgraph",
    "revise_or_escape",
]

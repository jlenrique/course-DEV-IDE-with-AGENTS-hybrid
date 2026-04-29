from __future__ import annotations

import pytest

from app.marcus.orchestrator.per_slide_subgraph import (
    EscapeCardValidationError,
    OscillationEscapeRequiredError,
    apply_escape_card,
    measure_escape_surface_ms,
    revise_or_escape,
)


def test_revise_count_one_two_three_succeeds() -> None:
    count = 0
    count = revise_or_escape(slide_index=0, revise_count=count)
    count = revise_or_escape(slide_index=0, revise_count=count)
    count = revise_or_escape(slide_index=0, revise_count=count)

    assert count == 3


def test_fourth_revise_raises_with_escape_card() -> None:
    with pytest.raises(OscillationEscapeRequiredError) as exc:
        revise_or_escape(slide_index=2, revise_count=3)

    assert exc.value.escape_card.kind == "oscillation_escape_required"
    assert exc.value.escape_card.options == (
        "accept-as-is",
        "reject-and-skip-slide",
        "abort-run",
    )


def test_accept_as_is_with_rationale_succeeds() -> None:
    result = apply_escape_card(
        option="accept-as-is",
        slide_index=0,
        rationale="This rationale clears the floor.",
    )

    assert result["status"] == "accepted"


def test_accept_as_is_short_rationale_rejected() -> None:
    with pytest.raises(EscapeCardValidationError):
        apply_escape_card(option="accept-as-is", slide_index=0, rationale="too short")


def test_reject_and_skip_slide_succeeds() -> None:
    assert apply_escape_card(option="reject-and-skip-slide", slide_index=3)["status"] == "skipped"


def test_abort_run_succeeds_and_halts_trial() -> None:
    assert apply_escape_card(option="abort-run", slide_index=3)["status"] == "halted"


def test_escape_card_surfaces_under_500ms() -> None:
    assert measure_escape_surface_ms(slide_index=0, revise_count=3) < 500

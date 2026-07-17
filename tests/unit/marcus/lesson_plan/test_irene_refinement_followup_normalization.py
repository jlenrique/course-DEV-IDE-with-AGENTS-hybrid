"""Live-model adequacy-followup normalization (trial 1bc3bc4e, 2026-07-16).

The live refinement model decorates the closed ``AdequacyFollowup`` literals
("external-content-expected: expect a separate guide or workbook") and the
strict parse at the ``_parse_live_refinement`` seam red-rejected the WHOLE
G0E->G0R continuation. ``_normalize_adequacy_followups`` truncates
literal-prefixed decorations and drops unknowns with a warning — advisory
field only ("Never an action"); every other malformation still fails strict.
"""

from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.irene_refinement import _normalize_adequacy_followups
from app.marcus.lesson_plan.learning_objective import SourceAdequacy


def _adequacy_row(followups: list[str]) -> dict:
    return {
        "verdict": "thin",
        "rationale": "teach-leg supported but assess-leg partial",
        "missing": ["assessment-grade detail"],
        "suggested_followups": followups,
    }


def test_witnessed_decorated_literals_truncate_to_bare_literal() -> None:
    # The two shapes witnessed verbatim on trial 1bc3bc4e (colon and
    # space/dash decorations).
    row = _adequacy_row(
        [
            "external-content-expected: expect a separate guide or workbook",
            "special-artifact-guidance — verifying name and order",
        ]
    )
    adequacy = SourceAdequacy.model_validate(_normalize_adequacy_followups(row))
    assert adequacy.suggested_followups == [
        "external-content-expected",
        "special-artifact-guidance",
    ]


def test_unknown_followup_dropped_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    row = _adequacy_row(["research-run", "totally-invented-hint: do a thing"])
    with caplog.at_level(logging.WARNING, logger="app.marcus.lesson_plan.irene_refinement"):
        adequacy = SourceAdequacy.model_validate(_normalize_adequacy_followups(row))
    assert adequacy.suggested_followups == ["research-run"]
    assert any("dropping unknown advisory followup" in r.getMessage() for r in caplog.records)


def test_clean_literals_pass_through_and_dedup_after_truncation() -> None:
    row = _adequacy_row(
        [
            "research-run",
            "research-run: with an annotation",
            "external-content-expected",
        ]
    )
    adequacy = SourceAdequacy.model_validate(_normalize_adequacy_followups(row))
    assert adequacy.suggested_followups == [
        "research-run",
        "external-content-expected",
    ]


def test_prefix_match_is_exact_never_partial_literal() -> None:
    # A string that CONTAINS but does not START at a literal boundary must not
    # be laundered into a literal.
    row = _adequacy_row(["pre-research-run", "research-runway"])
    with pytest.raises(ValidationError):
        # Both dropped -> empty list is VALID; craft a row where a non-list
        # shape proves strict validation still owns malformation instead.
        SourceAdequacy.model_validate(
            _normalize_adequacy_followups({**row, "suggested_followups": "not-a-list"})
        )
    # And the droppable-partials case: both are unknown -> dropped, empty ok.
    adequacy = SourceAdequacy.model_validate(_normalize_adequacy_followups(row))
    assert adequacy.suggested_followups == []


def test_non_dict_adequacy_passes_through_untouched() -> None:
    assert _normalize_adequacy_followups(None) is None
    assert _normalize_adequacy_followups("garbage") == "garbage"
    with pytest.raises(ValidationError):
        SourceAdequacy.model_validate(_normalize_adequacy_followups("garbage"))

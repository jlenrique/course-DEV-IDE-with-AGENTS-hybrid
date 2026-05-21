from __future__ import annotations

import pytest

from app.composers.section_02a.directive_model import DirectiveRole
from app.gates.errors import GateError
from app.gates.section_02a.poll_surface import (
    apply_directive_edit,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_02a import DirectiveEditPayload
from tests.gates.section_02a._helpers import fixture_directive


def test_valid_expected_min_words_edit_revalidates_and_submits() -> None:
    directive = fixture_directive()
    payload = DirectiveEditPayload(edits={"src-001": {"expected_min_words": 180}})

    verdict = submit_verdict(
        directive,
        verb="edit",
        operator_id="operator_1",
        edit_payload=payload,
    )
    resumed = resume_from_verdict(directive, verdict)

    edited_source = resumed["directive"]["sources"][0]
    assert edited_source["expected_min_words"] == 180
    assert verdict.decision_card_digest != submit_verdict(
        directive,
        verb="approve",
        operator_id="operator_1",
    ).decision_card_digest


def test_binary_file_invariant_violation_is_rejected_before_submit() -> None:
    directive = fixture_directive()
    payload = DirectiveEditPayload(edits={"src-002": {"expected_min_words": 200}})

    with pytest.raises(GateError, match="directive_edit_invalid"):
        submit_verdict(
            directive,
            verb="edit",
            operator_id="operator_1",
            edit_payload=payload,
        )


def test_valid_role_reclassification_revalidates() -> None:
    directive = fixture_directive()
    payload = DirectiveEditPayload(
        edits={
            "src-003": {
                "role": DirectiveRole.IGNORED.value,
                "expected_min_words": None,
                "excluded_reason": "llm-classified-out-of-scope",
            }
        }
    )

    edited = apply_directive_edit(directive, payload)

    assert edited.sources[2].role is DirectiveRole.IGNORED
    assert edited.sources[2].excluded_reason is not None


def test_unknown_source_edit_is_rejected_explicitly() -> None:
    directive = fixture_directive()
    payload = DirectiveEditPayload(edits={"src-999": {"description": "missing"}})

    with pytest.raises(GateError, match="unknown DirectiveSource src_id"):
        submit_verdict(
            directive,
            verb="edit",
            operator_id="operator_1",
            edit_payload=payload,
        )

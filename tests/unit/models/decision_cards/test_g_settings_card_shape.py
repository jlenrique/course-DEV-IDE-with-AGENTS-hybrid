"""Shape pins for the Story 42.5 pre-walk settings DecisionCard (GSettingsCard).

Follows the "Adding a new gate" convention step 4 (shape-pin the new card) and
the g0e/g2b/g4a precedent (recent union cards; no per-card committed schema file /
frozen hash — those cover only the legacy g1/g2c/g3/g4 set).
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.decision_cards import AnyDecisionCardAdapter, GSettingsCard
from app.models.decision_cards._base import CacheState, DecisionCardMeta


def _meta() -> DecisionCardMeta:
    return DecisionCardMeta(cache_state=CacheState.MIXED, affected_nodes=["__prewalk__"])


def _card(**overrides) -> GSettingsCard:
    kwargs = dict(
        card_id=uuid4(),
        trial_id=uuid4(),
        decision_card_digest="0" * 64,
        meta=_meta(),
        verb="approve",
        operator_prompt="Confirm the resolved run settings, or change one.",
        run_settings={"trial_budget_usd": "unset", "preset": "production"},
    )
    kwargs.update(overrides)
    return GSettingsCard(**kwargs)


def test_valid_card_constructs_with_discriminator_and_focus() -> None:
    card = _card()
    assert card.gate_id == "G0S"
    assert card.gate_focus == "pre_walk_settings_confirm"
    assert card.schema_version == "v1"


def test_allowed_verbs_default_is_the_neutral_confirm_change_pair() -> None:
    # AC-2 neutrality: confirm(approve)/change(edit), no preselected verdict, and
    # no reject preselection at the pre-walk surface.
    assert _card().allowed_verbs == ["approve", "edit"]


def test_run_settings_readout_is_carried() -> None:
    card = _card(run_settings={"trial_budget_usd": "5.00"})
    assert card.run_settings["trial_budget_usd"] == "5.00"


def test_blank_operator_prompt_raises() -> None:
    with pytest.raises(ValidationError):
        _card(operator_prompt="   ")


def test_empty_allowed_verbs_raises() -> None:
    with pytest.raises(ValidationError):
        _card(allowed_verbs=[])


def test_extra_field_raises() -> None:
    with pytest.raises(ValidationError):
        _card(unexpected="nope")


def test_wrong_gate_id_literal_raises() -> None:
    with pytest.raises(ValidationError):
        _card(gate_id="G_OTHER")


def test_discriminated_union_routes_to_g_settings_card() -> None:
    payload = _card().model_dump(mode="json")
    parsed = AnyDecisionCardAdapter.validate_python(payload)
    assert isinstance(parsed, GSettingsCard)
    assert parsed.gate_id == "G0S"

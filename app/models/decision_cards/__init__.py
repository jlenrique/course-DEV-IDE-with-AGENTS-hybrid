"""DecisionCard model family for Marcus HIL gates."""

from __future__ import annotations

from typing import Annotated, TypeAlias

from pydantic import Field, TypeAdapter

from app.models.decision_cards.base import (
    DecisionCard,
    DecisionCardMeta,
    DecisionCardVerb,
)
from app.models.decision_cards.g1 import G1Card
from app.models.decision_cards.g2c import G2CCard
from app.models.decision_cards.g3 import G3Card
from app.models.decision_cards.g4 import G4Card
from app.models.decision_cards.override_event import OverrideEvent
from app.models.decision_cards.vocabulary import (
    REGISTRY_PATH,
    EscapeCardOption,
    GateDecisionToken,
    GateDirectiveToken,
    SharedGateDecision,
    SpecialistId,
    VocabularyDecisionCard,
    decision_card_schema_text,
    emit_decision_card_schema,
    load_vocabulary_registry,
)

AnyDecisionCard: TypeAlias = Annotated[
    G1Card | G2CCard | G3Card | G4Card,
    Field(discriminator="gate_id"),
]
AnyDecisionCardAdapter = TypeAdapter(AnyDecisionCard)

__all__ = [
    "AnyDecisionCard",
    "AnyDecisionCardAdapter",
    "DecisionCard",
    "DecisionCardMeta",
    "DecisionCardVerb",
    "EscapeCardOption",
    "GateDecisionToken",
    "GateDirectiveToken",
    "G1Card",
    "G2CCard",
    "G3Card",
    "G4Card",
    "OverrideEvent",
    "REGISTRY_PATH",
    "SharedGateDecision",
    "SpecialistId",
    "VocabularyDecisionCard",
    "decision_card_schema_text",
    "emit_decision_card_schema",
    "load_vocabulary_registry",
]

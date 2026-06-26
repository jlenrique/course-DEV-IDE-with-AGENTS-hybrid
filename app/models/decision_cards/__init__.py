"""DecisionCard model family for Marcus HIL gates."""

from __future__ import annotations

from typing import Annotated, TypeAlias

from pydantic import Field, TypeAdapter

from app.models.decision_cards._base import (
    CacheState,
    CacheStateLiteral,
    DecisionCardBase,
)
from app.models.decision_cards.base import (
    DecisionCard,
    DecisionCardMeta,
    DecisionCardVerb,
)
from app.models.decision_cards.g0 import G0Card
from app.models.decision_cards.g0e import G0ECard
from app.models.decision_cards.g1 import G1Card
from app.models.decision_cards.g2a import G2ACard
from app.models.decision_cards.g2b import G2BCard
from app.models.decision_cards.g2c import G2CCard
from app.models.decision_cards.g3 import G3Card
from app.models.decision_cards.g4 import G4Card
from app.models.decision_cards.g4a import G4ACard
from app.models.decision_cards.g5 import G5Card
from app.models.decision_cards.g6 import G6Card
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
    G0Card
    | G0ECard
    | G1Card
    | G2ACard
    | G2BCard
    | G2CCard
    | G3Card
    | G4Card
    | G4ACard
    | G5Card
    | G6Card,
    Field(discriminator="gate_id"),
]
AnyDecisionCardAdapter = TypeAdapter(AnyDecisionCard)

__all__ = [
    "AnyDecisionCard",
    "AnyDecisionCardAdapter",
    "CacheState",
    "CacheStateLiteral",
    "DecisionCard",
    "DecisionCardBase",
    "DecisionCardMeta",
    "DecisionCardVerb",
    "EscapeCardOption",
    "GateDecisionToken",
    "GateDirectiveToken",
    "G0Card",
    "G0ECard",
    "G1Card",
    "G2ACard",
    "G2BCard",
    "G2CCard",
    "G3Card",
    "G4Card",
    "G4ACard",
    "G5Card",
    "G6Card",
    "OverrideEvent",
    "REGISTRY_PATH",
    "SharedGateDecision",
    "SpecialistId",
    "VocabularyDecisionCard",
    "decision_card_schema_text",
    "emit_decision_card_schema",
    "load_vocabulary_registry",
]

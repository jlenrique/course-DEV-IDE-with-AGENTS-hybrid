"""Shared DecisionCard base classes for Slab 7c gate families."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from app.models.decision_cards.override_event import OverrideEvent

CacheStateLiteral = Literal["healthy", "mixed", "cold"]
_CACHE_STATE_ADAPTER: TypeAdapter[CacheStateLiteral] = TypeAdapter(CacheStateLiteral)


class CacheState(StrEnum):
    """Closed cache-state vocabulary for gate-family decision cards."""

    HEALTHY = "healthy"
    MIXED = "mixed"
    COLD = "cold"


class DecisionCardMeta(BaseModel):
    """Shared metadata attached to every Slab 7c gate-family DecisionCard."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    cache_state: CacheState = Field(..., description="Closed cache-state tier.")
    affected_nodes: list[str] = Field(
        default_factory=list,
        description="Manifest node ids affected by this decision card.",
    )
    override_trail: list[OverrideEvent] = Field(
        default_factory=list,
        description="Operator override events already applied to this run.",
    )

    @field_validator("cache_state", mode="before")
    @classmethod
    def _reject_unknown_cache_state(cls, value: object) -> object:
        if isinstance(value, CacheState):
            return value
        return _CACHE_STATE_ADAPTER.validate_python(value)

    @field_validator("affected_nodes")
    @classmethod
    def _reject_empty_affected_nodes(cls, value: list[str]) -> list[str]:
        if any(not node_id for node_id in value):
            raise ValueError("affected_nodes entries must be non-empty strings")
        return value


class DecisionCardBase(BaseModel):
    """Internal inheritance interface for Slab 7c gate-family DecisionCards."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    decision_card_digest: str = Field(
        ...,
        description="Lowercase sha256 digest of the canonical decision card.",
    )
    meta: DecisionCardMeta

    @field_validator("decision_card_digest")
    @classmethod
    def _require_sha256_hex(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("decision_card_digest must be lowercase sha256 hex")
        return value


__all__ = [
    "CacheState",
    "CacheStateLiteral",
    "DecisionCardBase",
    "DecisionCardMeta",
]

"""Warning model returned before a runtime model override is applied."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

CacheStateLiteral = Literal["healthy", "mixed", "cold"]


class ModelOverrideWarning(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    warning_id: UUID = Field(default_factory=uuid4)
    trial_id: UUID
    node_id: str = Field(..., min_length=1)
    requested_model: str = Field(..., min_length=1)
    current_model: str = Field(..., min_length=1)
    estimated_cost_delta_usd: float = Field(..., ge=0.0)
    affected_nodes: list[str] = Field(default_factory=list)
    cache_state_delta: dict[str, CacheStateLiteral]
    confirm_token: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime

    @field_validator("warning_id", "trial_id")
    @classmethod
    def _uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("issued_at", "expires_at")
    @classmethod
    def _tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("confirm_token")
    @classmethod
    def _sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("confirm_token must be lowercase sha256 hex")
        return value

    @model_validator(mode="after")
    def _expiry_order(self) -> ModelOverrideWarning:
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be after issued_at")
        return self


__all__ = ["CacheStateLiteral", "ModelOverrideWarning"]

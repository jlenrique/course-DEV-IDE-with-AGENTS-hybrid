"""Strict party-mode contribution contract."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

TRACE_LINK_PATTERN = re.compile(
    r"^(https://smith\.langchain\.com/traces/[A-Za-z0-9_-]+|[A-Za-z0-9._/\-]+)$"
)


class PartyModeContribution(BaseModel):
    """One persona's contribution to a consolidated party-mode review."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    contribution_id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 identity for the contribution.",
    )
    persona: str = Field(
        ...,
        min_length=1,
        description="Persona or reviewer identity that produced the contribution.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured contribution payload.",
    )
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware submission timestamp.",
    )
    trace_link: str | None = Field(
        default=None,
        description="LangSmith trace URL or repo-relative trace export path.",
    )

    @field_validator("contribution_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("persona")
    @classmethod
    def _enforce_persona(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("persona must be non-empty")
        return stripped

    @field_validator("submitted_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("trace_link")
    @classmethod
    def _enforce_trace_link(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not TRACE_LINK_PATTERN.fullmatch(value):
            raise ValueError("trace_link must be a LangSmith trace URL or repo-relative path")
        return value


__all__ = ["PartyModeContribution", "TRACE_LINK_PATTERN"]

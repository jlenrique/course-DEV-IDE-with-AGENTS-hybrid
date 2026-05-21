"""Section 11 HIL voice-selection verdict models."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

Section11VerdictVerb = Literal["select", "edit", "reject"]
Section11SurfaceId = Literal["section_11_g4a_voice_selection"]
SECTION_11_SURFACE_ID: Section11SurfaceId = "section_11_g4a_voice_selection"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class VoiceSelectionPayload(BaseModel):
    """Selected ElevenLabs voice for Section 11 handoff."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    selected_voice_id: str = Field(
        ...,
        min_length=1,
        description="Selected ElevenLabs voice identifier.",
    )
    rationale: str | None = Field(
        default=None,
        description="Optional operator rationale for the selected voice.",
    )

    @field_validator("selected_voice_id", mode="before")
    @classmethod
    def _strip_selected_voice_id(cls, value: object) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="selected_voice_id")
        return value

    @field_validator("rationale", mode="before")
    @classmethod
    def _strip_optional_rationale(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="rationale")
        return value


class VoiceSelectionEditPayload(BaseModel):
    """Field-level edits for voice candidates or voice-selection metadata."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of voice-selection field names or paths to replacement values.",
    )

    @field_validator("edits")
    @classmethod
    def _reject_blank_edit_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for field_name, field_value in value.items():
            if not isinstance(field_name, str):
                raise ValueError("edit field name must be a string")
            normalized[_strip_non_empty(field_name, field_name="edit field name")] = (
                field_value
            )
        return normalized


class Section11OperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 11 G4A poll surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(
        ...,
        description="UUID4 identity for the voice-selection run.",
    )
    surface_id: Section11SurfaceId = Field(
        default=SECTION_11_SURFACE_ID,
        description="Closed Section 11 voice-selection surface identifier.",
    )
    verb: Section11VerdictVerb = Field(
        ...,
        description="Closed verdict verb set: select | edit | reject.",
    )
    voice_selection_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the voice-selection card under review.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]+$",
        description="Operator identifier.",
    )
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware verdict submission time.",
    )
    decision_card_digest: str = Field(
        ...,
        description="Lowercase sha256 digest of the reviewed G4 card.",
    )
    select_payload: VoiceSelectionPayload | None = Field(
        default=None,
        description="Required iff verb is select.",
    )
    edit_payload: VoiceSelectionEditPayload | None = Field(
        default=None,
        description="Required iff verb is edit.",
    )
    reject_reason: str | None = Field(
        default=None,
        description="Required iff verb is reject.",
    )

    @field_validator("run_id")
    @classmethod
    def _require_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("voice_selection_id", "operator_id", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name=info.field_name)
        return value

    @field_validator("reject_reason", mode="before")
    @classmethod
    def _strip_optional_reject_reason(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="reject_reason")
        return value

    @field_validator("submitted_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("decision_card_digest", mode="before")
    @classmethod
    def _require_sha256(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("decision_card_digest must be lowercase sha256 hex")
        return value

    @model_validator(mode="after")
    def _enforce_verb_payload_consistency(self) -> Section11OperatorVerdict:
        if self.verb == "select":
            if self.select_payload is None:
                raise ValueError("verb='select' requires select_payload")
            if self.edit_payload is not None or self.reject_reason is not None:
                raise ValueError(
                    "verb='select' forbids edit_payload and reject_reason"
                )
            return self
        if self.verb == "edit":
            if self.edit_payload is None:
                raise ValueError("verb='edit' requires edit_payload")
            if self.select_payload is not None or self.reject_reason is not None:
                raise ValueError(
                    "verb='edit' forbids select_payload and reject_reason"
                )
            return self
        if self.reject_reason is None:
            raise ValueError("verb='reject' requires reject_reason")
        if self.select_payload is not None or self.edit_payload is not None:
            raise ValueError("verb='reject' forbids select_payload and edit_payload")
        return self


__all__ = [
    "SECTION_11_SURFACE_ID",
    "Section11OperatorVerdict",
    "Section11SurfaceId",
    "Section11VerdictVerb",
    "VoiceSelectionEditPayload",
    "VoiceSelectionPayload",
]

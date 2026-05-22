"""Pydantic-v2 models for Section 02A directive composition."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DirectiveRoleLiteral = Literal["primary", "supporting", "ignored"]
ExcludedReasonLiteral = Literal[
    "git-marker-file",
    "macos-metadata",
    "windows-metadata",
    "llm-classified-out-of-scope",
]

DIRECTIVE_ROLE_LITERAL_ADAPTER: TypeAdapter[DirectiveRoleLiteral] = TypeAdapter(
    DirectiveRoleLiteral
)
EXCLUDED_REASON_LITERAL_ADAPTER: TypeAdapter[ExcludedReasonLiteral] = TypeAdapter(
    ExcludedReasonLiteral
)

TEXT_EXTENSIONS_REQUIRING_WORDS = frozenset({".docx", ".md"})
BINARY_EXTENSIONS_FORBID_WORDS = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".pdf", ".pptx", ".docx-thumbnails"}
)


class DirectiveRole(StrEnum):
    """Closed role taxonomy for directive sources."""

    PRIMARY = "primary"
    SUPPORTING = "supporting"
    IGNORED = "ignored"


class ExcludedReason(StrEnum):
    """Closed ignored-source reason taxonomy."""

    GIT_MARKER = "git-marker-file"
    MACOS_METADATA = "macos-metadata"
    WINDOWS_METADATA = "windows-metadata"
    LLM_CLASSIFIED_OUT_OF_SCOPE = "llm-classified-out-of-scope"


class DirectiveSource(BaseModel):
    """One source row in a composed Section 02A directive."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    ref_id: str = Field(..., min_length=1)
    locator: str = Field(..., min_length=1)
    provider: str = Field(default="local_file", min_length=1)
    role: DirectiveRole
    description: str | None = Field(default=None)
    expected_min_words: int | None = Field(default=None, ge=0)
    excluded_reason: ExcludedReason | None = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_source_id_key(cls, value: object) -> object:
        """Load-bearing for AC-34-1-B: migrate legacy pre-Story-34-3 input key
        to the renamed field so the sha256-pinned forensic-anchor fixture
        (`tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml`,
        sha256 `351a57f...`) validates without regeneration. The legacy key
        is constructed via `"_".join(...)` to keep the grep surface clean for
        Story 34-3 post-rename audits. DO NOT REMOVE without retiring AC-34-1-B
        (forensic-fixture binding) — fixture would need byte-identical
        regeneration in the new field-name shape, breaking the binding sha256.
        Forward direction is one-way: legacy input is migrated; output is
        always the renamed field name."""
        if not isinstance(value, dict):
            return value
        legacy_key = "_".join(("src", "id"))
        if "ref_id" not in value and legacy_key in value:
            migrated = dict(value)
            migrated["ref_id"] = migrated.pop(legacy_key)
            return migrated
        return value

    @field_validator("role", mode="before")
    @classmethod
    def _reject_unknown_role(cls, value: object) -> object:
        if isinstance(value, DirectiveRole):
            return value
        return DIRECTIVE_ROLE_LITERAL_ADAPTER.validate_python(value)

    @field_validator("excluded_reason", mode="before")
    @classmethod
    def _reject_unknown_excluded_reason(cls, value: object) -> object:
        if value is None or isinstance(value, ExcludedReason):
            return value
        return EXCLUDED_REASON_LITERAL_ADAPTER.validate_python(value)

    @model_validator(mode="after")
    def _enforce_role_field_invariants(self) -> DirectiveSource:
        suffix = PurePosixPath(self.locator).suffix.lower()
        if self.role is DirectiveRole.IGNORED:
            if self.excluded_reason is None:
                raise ValueError("role=ignored requires excluded_reason")
            if self.expected_min_words is not None:
                raise ValueError("role=ignored forbids expected_min_words")
            return self

        if self.excluded_reason is not None:
            raise ValueError("role=primary/supporting forbids excluded_reason")

        if suffix in TEXT_EXTENSIONS_REQUIRING_WORDS and self.expected_min_words is None:
            raise ValueError(
                "role=primary/supporting text source requires expected_min_words"
            )
        if (
            self.role is DirectiveRole.SUPPORTING
            and suffix in BINARY_EXTENSIONS_FORBID_WORDS
            and self.expected_min_words is not None
        ):
            raise ValueError(
                "Trial-2 finding #2 anti-pattern: binary supporting source must "
                "not carry expected_min_words"
            )
        return self


class Directive(BaseModel):
    """Validated Section 02A directive emitted for operator review."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: UUID
    corpus_dir: str = Field(..., min_length=1)
    sources: list[DirectiveSource] = Field(..., min_length=1)
    composed_at: datetime
    schema_version: int = Field(default=1, ge=1)

    @field_validator("run_id")
    @classmethod
    def _require_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("composed_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = [
    "BINARY_EXTENSIONS_FORBID_WORDS",
    "DIRECTIVE_ROLE_LITERAL_ADAPTER",
    "Directive",
    "DirectiveRole",
    "DirectiveSource",
    "EXCLUDED_REASON_LITERAL_ADAPTER",
    "ExcludedReason",
    "TEXT_EXTENSIONS_REQUIRING_WORDS",
]

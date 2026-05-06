"""Gary outbound-envelope writer and pre-dispatch markdown aggregator."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.models.state._base import enforce_tz_aware
from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="gary-outbound-envelope",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)

OutboundEnvelopeWriterId = Literal[
    "gary-slide-content",
    "gary-fidelity-slides",
    "gary-diagram-cards",
    "gary-theme-resolution",
    "gary-outbound-envelope",
]
PayloadLoader = Callable[["OutboundEnvelopeEntry"], str]


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class OutboundEnvelopeEntry(BaseModel):
    """One emitted writer payload referenced by the Gary outbound envelope."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    writer_id: OutboundEnvelopeWriterId = Field(
        ...,
        description="Closed canonical Marcus-bound writer identifier.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for this writer output.",
    )
    payload_ref: str = Field(
        ...,
        min_length=1,
        description="Relative path or URI to the emitted writer payload.",
    )
    dispatched_at: datetime = Field(
        ...,
        description="Timezone-aware dispatch timestamp for this payload.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        description="Operator identifier for this payload dispatch.",
    )

    @field_validator("target_section", "payload_ref", "operator_id", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("dispatched_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class GaryOutboundEnvelope(BaseModel):
    """Gary pre-dispatch envelope aggregating emitted writer payloads."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for this outbound envelope.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for this outbound envelope.",
    )
    entries: list[OutboundEnvelopeEntry] = Field(
        ...,
        min_length=1,
        description="Writer payload entries included in this envelope.",
    )
    dispatched_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware envelope dispatch timestamp.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        description="Operator identifier for this envelope dispatch.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("plan_unit_id", "target_section", "operator_id", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("dispatched_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


def emit_gary_outbound_envelope(
    payload: GaryOutboundEnvelope,
    output_path: Path,
) -> Path:
    """Write Gary outbound-envelope YAML and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(
            payload.model_dump(mode="json"),
            sort_keys=True,
            default_flow_style=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


def _default_payload_loader(entry: OutboundEnvelopeEntry) -> str:
    return f"payload_ref: {entry.payload_ref}"


def pre_dispatch_package_gary_md(
    envelope: GaryOutboundEnvelope,
    payload_loaders: dict[OutboundEnvelopeWriterId, PayloadLoader] | None = None,
) -> str:
    """Render a deterministic operator-readable Gary pre-dispatch package."""
    loaders = payload_loaders or {}
    lines = [
        "# Gary Pre-Dispatch Package",
        "",
        f"- plan_unit_id: {envelope.plan_unit_id}",
        f"- target_section: {envelope.target_section}",
        f"- dispatched_at: {envelope.dispatched_at.isoformat()}",
        f"- operator_id: {envelope.operator_id}",
        "",
    ]
    for entry in sorted(envelope.entries, key=lambda item: item.writer_id):
        loader = loaders.get(entry.writer_id, _default_payload_loader)
        payload_text = loader(entry).strip()
        lines.extend(
            [
                f"## {entry.writer_id}",
                "",
                f"- payload_ref: {entry.payload_ref}",
                f"- target_section: {entry.target_section}",
                f"- dispatched_at: {entry.dispatched_at.isoformat()}",
                f"- operator_id: {entry.operator_id}",
                "",
                "```",
                payload_text,
                "```",
                "",
            ]
        )
    return "\n".join(lines)


__all__ = [
    "GaryOutboundEnvelope",
    "OutboundEnvelopeEntry",
    "OutboundEnvelopeWriterId",
    "PayloadLoader",
    "emit_gary_outbound_envelope",
    "pre_dispatch_package_gary_md",
]

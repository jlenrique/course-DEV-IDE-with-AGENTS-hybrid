"""Shared Marcus specialist dispatch contract."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DispatchKind(StrEnum):
    IRENE_PASS2 = "irene_pass2"
    KIRA_MOTION = "kira_motion"
    TEXAS_RETRIEVAL = "texas_retrieval"
    WANDA_PODCAST_EPISODE = "wanda_podcast_episode"
    WANDA_PODCAST_DIALOGUE = "wanda_podcast_dialogue"
    WANDA_AUDIO_SUMMARY = "wanda_audio_summary"
    WANDA_MUSIC_BED_APPLY = "wanda_music_bed_apply"
    WANDA_CHAPTER_MARKERS_EMIT = "wanda_chapter_markers_emit"
    WANDA_AUDIO_ASSEMBLY_HANDOFF = "wanda_audio_assembly_handoff"


class DispatchOutcome(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


_SPECIALIST_ID_BY_KIND: dict[DispatchKind, str] = {
    DispatchKind.IRENE_PASS2: "irene",
    DispatchKind.KIRA_MOTION: "kira",
    DispatchKind.TEXAS_RETRIEVAL: "texas",
    DispatchKind.WANDA_PODCAST_EPISODE: "wanda",
    DispatchKind.WANDA_PODCAST_DIALOGUE: "wanda",
    DispatchKind.WANDA_AUDIO_SUMMARY: "wanda",
    DispatchKind.WANDA_MUSIC_BED_APPLY: "wanda",
    DispatchKind.WANDA_CHAPTER_MARKERS_EMIT: "wanda",
    DispatchKind.WANDA_AUDIO_ASSEMBLY_HANDOFF: "wanda",
}


class DispatchEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str = Field(..., min_length=1)
    specialist_id: str = Field(..., min_length=1)
    dispatch_kind: DispatchKind
    input_packet: dict[str, Any] = Field(default_factory=dict)
    context_refs: list[str] = Field(default_factory=list)
    correlation_id: str = Field(..., min_length=1)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DispatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    correlation_id: str = Field(..., min_length=1)
    specialist_id: str = Field(..., min_length=1)
    outcome: DispatchOutcome
    output_artifacts: list[Any] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(..., ge=0)
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))


def build_dispatch_envelope(
    *,
    dispatch_kind: DispatchKind,
    run_id: str,
    input_packet: dict[str, Any],
    context_refs: list[str],
    correlation_id: str,
) -> DispatchEnvelope:
    return DispatchEnvelope(
        run_id=run_id,
        specialist_id=_SPECIALIST_ID_BY_KIND[dispatch_kind],
        dispatch_kind=dispatch_kind,
        input_packet=input_packet,
        context_refs=context_refs,
        correlation_id=correlation_id,
    )


def build_dispatch_receipt(
    *,
    correlation_id: str,
    specialist_id: str,
    outcome: DispatchOutcome,
    output_artifacts: list[Any],
    diagnostics: dict[str, Any],
    duration_ms: int,
) -> DispatchReceipt:
    return DispatchReceipt(
        correlation_id=correlation_id,
        specialist_id=specialist_id,
        outcome=outcome,
        output_artifacts=output_artifacts,
        diagnostics=diagnostics,
        duration_ms=duration_ms,
    )


__all__ = [
    "DispatchEnvelope",
    "DispatchKind",
    "DispatchOutcome",
    "DispatchReceipt",
    "build_dispatch_envelope",
    "build_dispatch_receipt",
]

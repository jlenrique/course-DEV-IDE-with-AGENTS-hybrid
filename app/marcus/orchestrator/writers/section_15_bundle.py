"""Section 15 final operator handoff bundle writer."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.gates.errors import GateError
from app.marcus.orchestrator.writers.outbound_envelope import (
    GaryOutboundEnvelope,
    OutboundEnvelopeEntry,
)
from app.models.operator_verdict_section_15 import Section15OperatorVerdict
from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="section-15-bundle",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Section15Bundle(BaseModel):
    """Artifacts emitted when the Section 15 G5 handoff is completed."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    assembly_bundle_path: Path = Field(
        ...,
        description="Path to the consolidated assembly bundle directory.",
    )
    descript_assembly_guide_md_digest: str = Field(
        ...,
        pattern=r"^[0-9a-f]{64}$",
        description="Sha256 digest of the regenerated DESCRIPT-ASSEMBLY-GUIDE.md.",
    )
    trial_3_transcript_anchor: str = Field(
        ...,
        pattern=r"^[0-9a-f]{64}$",
        description="Sha256 anchor for the Trial-3 transcript artifact.",
    )
    slab_close_evidence_path: Path = Field(
        ...,
        description="Path to the emitted slab-close evidence pointer.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("assembly_bundle_path", "slab_close_evidence_path", mode="before")
    @classmethod
    def _reject_blank_paths(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return Path(_strip_non_empty(value, field_name=info.field_name))
        return value


def load_outbound_envelope(envelope_path: Path) -> GaryOutboundEnvelope:
    """Load a Gary outbound envelope from YAML or JSON."""
    raw_text = envelope_path.read_text(encoding="utf-8")
    if envelope_path.suffix.lower() == ".json":
        return GaryOutboundEnvelope.model_validate_json(raw_text)
    return GaryOutboundEnvelope.model_validate(yaml.safe_load(raw_text))


def _coerce_outbound_envelope(
    outbound_envelope: GaryOutboundEnvelope | Mapping[str, Any] | Path,
) -> GaryOutboundEnvelope:
    if isinstance(outbound_envelope, GaryOutboundEnvelope):
        return outbound_envelope
    if isinstance(outbound_envelope, Path):
        return load_outbound_envelope(outbound_envelope)
    return GaryOutboundEnvelope.model_validate(dict(outbound_envelope))


def _entry_payload_text(entry: OutboundEnvelopeEntry, base_path: Path | None) -> str:
    candidate = Path(entry.payload_ref)
    if not candidate.is_absolute() and base_path is not None:
        candidate = base_path / candidate
    if candidate.exists() and candidate.is_file():
        return candidate.read_text(encoding="utf-8").strip()
    return f"payload_ref: {entry.payload_ref}"


def render_descript_assembly_guide(
    envelope: GaryOutboundEnvelope,
    *,
    payload_base_path: Path | None = None,
) -> str:
    """Render deterministic DESCRIPT-ASSEMBLY-GUIDE.md content."""
    lines = [
        "# DESCRIPT Assembly Guide",
        "",
        f"- plan_unit_id: {envelope.plan_unit_id}",
        f"- target_section: {envelope.target_section}",
        f"- operator_id: {envelope.operator_id}",
        f"- dispatched_at: {envelope.dispatched_at.isoformat()}",
        "",
        "## Source Payloads",
        "",
    ]
    for entry in sorted(envelope.entries, key=lambda item: item.writer_id):
        lines.extend(
            [
                f"### {entry.writer_id}",
                "",
                f"- payload_ref: {entry.payload_ref}",
                f"- target_section: {entry.target_section}",
                f"- dispatched_at: {entry.dispatched_at.isoformat()}",
                f"- operator_id: {entry.operator_id}",
                "",
                "```",
                _entry_payload_text(entry, payload_base_path),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def emit_section_15_bundle(
    g5_verdict: Section15OperatorVerdict,
    outbound_envelope: GaryOutboundEnvelope | Mapping[str, Any] | Path,
    *,
    assembly_bundle_path: Path,
    trial_3_transcript_path: Path,
    slab_close_evidence_path: Path,
    descript_assembly_guide_path: Path | None = None,
) -> Section15Bundle:
    """Emit the Section 15 slab-close bundle after G5 completion."""
    if g5_verdict.verb != "complete":
        raise GateError(
            "section_15_handoff_not_complete",
            "Section 15 bundle emission requires verb='complete'",
        )
    envelope = _coerce_outbound_envelope(outbound_envelope)
    if not trial_3_transcript_path.exists():
        raise GateError(
            "trial_3_transcript_missing",
            f"Trial-3 transcript not found: {trial_3_transcript_path}",
        )
    assembly_bundle_path.mkdir(parents=True, exist_ok=True)
    guide_path = descript_assembly_guide_path or (
        assembly_bundle_path / "DESCRIPT-ASSEMBLY-GUIDE.md"
    )
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    payload_base_path = None
    if isinstance(outbound_envelope, Path):
        payload_base_path = outbound_envelope.parent
    guide_path.write_text(
        render_descript_assembly_guide(envelope, payload_base_path=payload_base_path),
        encoding="utf-8",
        newline="\n",
    )
    guide_digest = _sha256_file(guide_path)
    transcript_anchor = _sha256_file(trial_3_transcript_path)
    evidence_payload = {
        "descript_assembly_guide_md_digest": guide_digest,
        "handoff_id": g5_verdict.handoff_id,
        "operator_id": g5_verdict.operator_id,
        "plan_unit_id": envelope.plan_unit_id,
        "schema_version": 1,
        "trial_3_transcript_anchor": transcript_anchor,
    }
    slab_close_evidence_path.parent.mkdir(parents=True, exist_ok=True)
    slab_close_evidence_path.write_text(
        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return Section15Bundle(
        assembly_bundle_path=assembly_bundle_path,
        descript_assembly_guide_md_digest=guide_digest,
        trial_3_transcript_anchor=transcript_anchor,
        slab_close_evidence_path=slab_close_evidence_path,
    )


__all__ = [
    "Section15Bundle",
    "emit_section_15_bundle",
    "load_outbound_envelope",
    "render_descript_assembly_guide",
]

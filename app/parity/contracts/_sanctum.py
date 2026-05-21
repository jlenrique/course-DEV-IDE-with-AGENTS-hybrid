"""Sanctum-alignment declarations for parity writers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AlignmentKind = Literal["bmb-pattern", "cora-sidecar-exception"]

_SANCTUM_ALIGNMENTS: dict[str, SanctumAlignmentDeclaration] = {}


class DuplicateSanctumAlignmentError(ValueError):
    """Raised when a writer_id is registered more than once."""


class SanctumAlignmentDeclaration(BaseModel):
    """Declared memory-sanctum alignment for one downstream writer."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    writer_id: str = Field(..., min_length=1)
    sanctum_path: str = Field(..., min_length=1)
    alignment_kind: AlignmentKind = "bmb-pattern"
    exception_rationale: str | None = None

    @model_validator(mode="after")
    def _require_exception_rationale(self) -> SanctumAlignmentDeclaration:
        if self.alignment_kind == "cora-sidecar-exception" and not (
            self.exception_rationale or ""
        ).strip():
            raise ValueError(
                "exception_rationale is required for cora-sidecar-exception"
            )
        return self


def declare_sanctum_alignment(
    *,
    writer_id: str,
    sanctum_path: str,
    alignment_kind: AlignmentKind = "bmb-pattern",
    exception_rationale: str | None = None,
) -> SanctumAlignmentDeclaration:
    """Construct and register a sanctum-alignment declaration."""
    declaration = SanctumAlignmentDeclaration(
        writer_id=writer_id,
        sanctum_path=sanctum_path,
        alignment_kind=alignment_kind,
        exception_rationale=exception_rationale,
    )
    if writer_id in _SANCTUM_ALIGNMENTS:
        raise DuplicateSanctumAlignmentError(
            f"writer_id already registered: {writer_id}"
        )
    _SANCTUM_ALIGNMENTS[writer_id] = declaration
    return declaration


def iter_sanctum_alignments() -> Iterable[SanctumAlignmentDeclaration]:
    """Yield sanctum declarations in deterministic writer_id order."""
    for writer_id in sorted(_SANCTUM_ALIGNMENTS):
        yield _SANCTUM_ALIGNMENTS[writer_id]


def emit_sanctum_alignment_manifest(manifest_path: Path) -> Path:
    """Write the current sanctum-alignment registry manifest as UTF-8 JSON."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    alignments = [
        alignment.model_dump(mode="json")
        for alignment in iter_sanctum_alignments()
    ]
    payload = {
        "alignments": alignments,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "schema_version": 1,
    }
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _clear_sanctum_alignments_for_tests() -> None:
    _SANCTUM_ALIGNMENTS.clear()


__all__ = [
    "DuplicateSanctumAlignmentError",
    "SanctumAlignmentDeclaration",
    "declare_sanctum_alignment",
    "emit_sanctum_alignment_manifest",
    "iter_sanctum_alignments",
]

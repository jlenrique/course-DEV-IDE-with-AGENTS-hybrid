"""Vocabulary-backed decision-card tokens for Slab 7a Story 7a.6.

Loads docs/conversational-gates/_registry/vocabulary.yaml at module-load time
and exposes closed StrEnum classes for downstream gate-card emitters.
"""

from __future__ import annotations

import argparse
import json
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "conversational-gates"
    / "_registry"
    / "vocabulary.yaml"
)
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "schemas"
    / "decision_cards.schema.json"
)


def load_vocabulary_registry(registry_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load the vocabulary registry as plain data."""
    return yaml.safe_load(registry_path.read_text(encoding="utf-8"))


_REGISTRY = load_vocabulary_registry()


def _enum(group_path: str, name: str) -> type[StrEnum]:
    """Build a StrEnum from a registry token group like 'gates.decision'."""
    namespace, token_group = group_path.split(".")
    tokens = _REGISTRY["namespaces"][namespace]["tokens"][token_group]
    return StrEnum(name, {token.upper().replace("-", "_"): token for token in tokens})


GateDecisionToken = _enum("gates.decision", "GateDecisionToken")
GateDirectiveToken = _enum("gates.directive", "GateDirectiveToken")
SpecialistId = _enum("specialists.roster", "SpecialistId")
SharedGateDecision = _enum("shared.gate_decision", "SharedGateDecision")
EscapeCardOption = _enum("shared.escape_card_options", "EscapeCardOption")

_SPECIALIST_ROSTER_FLOOR = 11
assert len(SpecialistId) == _SPECIALIST_ROSTER_FLOOR, (
    f"SG-1 floor violation: vocabulary registry roster has {len(SpecialistId)} "
    f"specialists; expected exactly {_SPECIALIST_ROSTER_FLOOR}. Adding/removing "
    "specialists requires Slab 7b party-mode consensus."
)


class VocabularyDecisionCard(BaseModel):
    """Minimal closed-enum vocabulary card pinned by Story 7a.6."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    decision: GateDecisionToken
    directive: GateDirectiveToken
    rationale: str = Field(..., min_length=20)


def decision_card_schema_text() -> str:
    """Return the canonical emitted JSON Schema bytes as text."""
    return json.dumps(
        VocabularyDecisionCard.model_json_schema(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def emit_decision_card_schema(schema_path: Path = SCHEMA_PATH) -> None:
    """Emit the vocabulary decision-card JSON Schema."""
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(decision_card_schema_text(), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.models.decision_cards")
    parser.add_argument("--emit-schema", action="store_true")
    args = parser.parse_args(argv)
    if args.emit_schema:
        emit_decision_card_schema()
    return 0


__all__ = [
    "EscapeCardOption",
    "GateDecisionToken",
    "GateDirectiveToken",
    "REGISTRY_PATH",
    "SCHEMA_PATH",
    "SharedGateDecision",
    "SpecialistId",
    "VocabularyDecisionCard",
    "decision_card_schema_text",
    "emit_decision_card_schema",
    "load_vocabulary_registry",
    "main",
]

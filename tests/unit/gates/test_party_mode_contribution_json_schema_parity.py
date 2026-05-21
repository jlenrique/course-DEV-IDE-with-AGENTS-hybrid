from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.models.gates.party_mode_contribution import PartyModeContribution

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "models"
    / "gates"
    / "schema"
    / "party_mode_contribution.v1.schema.json"
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def test_party_mode_contribution_json_schema_parity() -> None:
    committed = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    generated = PartyModeContribution.model_json_schema()

    assert _hash(committed) == _hash(generated)

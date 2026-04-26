from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.models.decision_cards import G1Card, G2CCard, G3Card, G4Card

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "decision_cards"
SCHEMA_DIR = (
    Path(__file__).resolve().parents[3]
    / ".."
    / "app"
    / "models"
    / "decision_cards"
    / "schema"
).resolve()

GATE_MODELS: list[tuple[str, type[BaseModel]]] = [
    ("g1", G1Card),
    ("g2c", G2CCard),
    ("g3", G3Card),
    ("g4", G4Card),
]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_json_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / f"{name}_golden.json").read_text(encoding="utf-8"))


def schema_hash_for_model(model_class: type[BaseModel]) -> str:
    return canonical_json_hash(model_class.model_json_schema())


def schema_hash_for_file(filename: str) -> str:
    return canonical_json_hash(json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8")))

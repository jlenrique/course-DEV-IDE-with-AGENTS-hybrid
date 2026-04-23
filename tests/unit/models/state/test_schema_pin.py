"""Schema-pin emission tests (Story 1.2 AC-1.2-E).

For each of the 9 state models, asserts that the live `model_json_schema()`
emission matches the pinned JSON Schema fixture under
`tests/fixtures/models/state/schema_pin_<name>.json`. Drift = test failure;
intentional schema changes update the pin in the same PR (per the bundle
§3 idiom #11 + 31-1 R2 rider AM-1).

Also includes the AC-1.2-A FR34 third red-rejection layer: the operator
verdict's emitted JSON Schema enum array MUST contain exactly
``["approve", "edit", "reject"]`` — never ``timeout`` or ``auto_approve``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.models.state import (
    CacheState,
    ModelResolutionEntry,
    NodeCheckpoint,
    OperatorVerdict,
    RunState,
    SanctumFingerprint,
    SpecialistEnvelope,
    SpecialistReturn,
    StoryState,
)

_FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "models" / "state"

_PIN_TARGETS: list[tuple[str, type[BaseModel]]] = [
    ("sanctum_fingerprint", SanctumFingerprint),
    ("operator_verdict", OperatorVerdict),
    ("cache_state", CacheState),
    ("node_checkpoint", NodeCheckpoint),
    ("specialist_return", SpecialistReturn),
    ("specialist_envelope", SpecialistEnvelope),
    ("story_state", StoryState),
    ("run_state", RunState),
    ("model_resolution_entry", ModelResolutionEntry),
]


@pytest.mark.parametrize(("name", "model_class"), _PIN_TARGETS, ids=[n for n, _ in _PIN_TARGETS])
def test_live_schema_matches_pinned_fixture(name: str, model_class: type[BaseModel]) -> None:
    pin_path = _FIXTURES_DIR / f"schema_pin_{name}.json"
    pinned = json.loads(pin_path.read_text(encoding="utf-8"))
    live = model_class.model_json_schema()
    assert live == pinned, (
        f"{model_class.__name__} JSON Schema drifted from pin.\n"
        f"  pin file: {pin_path}\n"
        f"  Update the pin in the SAME PR if the change is intentional, OR fix the model.\n"
        f"  pinned keys top-level: {sorted(pinned.keys())}\n"
        f"  live   keys top-level: {sorted(live.keys())}"
    )


def test_operator_verdict_schema_enum_excludes_tamper_verbs() -> None:
    """FR34 third red-rejection layer (AC-1.2-A schema-pin layer).

    The emitted JSON Schema's `verb` enum array MUST contain exactly the three
    legitimate verbs and NEVER include ``timeout`` or ``auto_approve``. This
    is the third surface of the triple-layer red-rejection (Pydantic Literal +
    model_validator + JSON Schema enum) that closes FR34's tamper-evidence
    contract for external consumers (jsonschema-lib validators, OpenAPI
    generators, etc.) that don't go through the Pydantic class.
    """
    schema = OperatorVerdict.model_json_schema()
    verb_field = schema["properties"]["verb"]
    enum_values = verb_field.get("enum", [])
    assert sorted(enum_values) == sorted(["approve", "edit", "reject"]), (
        f"OperatorVerdict.verb enum drifted from FR34 contract: {enum_values}"
    )
    assert "timeout" not in enum_values, "FR34 violation: tamper verb 'timeout' in schema enum"
    assert "auto_approve" not in enum_values, (
        "FR34 violation: tamper verb 'auto_approve' in schema enum"
    )

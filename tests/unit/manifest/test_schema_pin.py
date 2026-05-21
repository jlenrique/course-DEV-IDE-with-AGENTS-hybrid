"""Schema-pin tests for the manifest family (AC-1.4-A four-file-lockstep).

Per-family pins per `docs/dev-guide/pydantic-v2-schema-checklist.md §8`:
`PipelineManifest`, `NodeSpec`, `EdgeSpec` each own their own pin file.
Drift = test failure; intentional schema changes update the pin in the same PR.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "manifest"

_PIN_TARGETS: list[tuple[str, type[BaseModel]]] = [
    ("pipeline_manifest", PipelineManifest),
    ("node_spec", NodeSpec),
    ("edge_spec", EdgeSpec),
]


@pytest.mark.parametrize(("name", "model_class"), _PIN_TARGETS, ids=[n for n, _ in _PIN_TARGETS])
def test_live_schema_matches_pinned_fixture(name: str, model_class: type[BaseModel]) -> None:
    pin_path = _FIXTURES / f"schema_pin_{name}.json"
    pinned = json.loads(pin_path.read_text(encoding="utf-8"))
    live = model_class.model_json_schema()
    assert live == pinned, (
        f"{model_class.__name__} JSON Schema drifted from pin.\n"
        f"  pin file: {pin_path}\n"
        f"  Update the pin in the SAME PR if the change is intentional, OR fix the model.\n"
        f"  pinned keys top-level: {sorted(pinned.keys())}\n"
        f"  live   keys top-level: {sorted(live.keys())}"
    )


def test_pipeline_manifest_json_schema_additional_properties_false() -> None:
    """Checklist §14 — `extra='forbid'` must propagate to `additionalProperties: false`."""
    schema = PipelineManifest.model_json_schema()
    assert schema.get("additionalProperties") is False


def test_node_spec_json_schema_additional_properties_false() -> None:
    schema = NodeSpec.model_json_schema()
    assert schema.get("additionalProperties") is False


def test_edge_spec_json_schema_additional_properties_false() -> None:
    schema = EdgeSpec.model_json_schema()
    assert schema.get("additionalProperties") is False

from __future__ import annotations

from pathlib import Path

import yaml

from app.runtime.cascade_config import load_cascade, normalize_agent_name

REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "bmad-agent-marcus"
    / "references"
    / "specialist-registry.yaml"
)


def test_every_active_registry_id_resolves_to_exactly_one_cascade_entry() -> None:
    cascade = load_cascade()
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    active_registry_ids = sorted(
        specialist_id
        for specialist_id, payload in registry["specialists"].items()
        if payload.get("status") == "active"
    )

    for specialist_id in active_registry_ids:
        normalized_id = normalize_agent_name(specialist_id)
        matches = [
            name
            for name, entry in cascade.specialists.items()
            if normalize_agent_name(name) == normalized_id
            or any(normalize_agent_name(alias) == normalized_id for alias in entry.aliases)
        ]
        assert matches, f"registry id {specialist_id!r} did not resolve in model_cascade.yaml"
        assert len(matches) == 1, (
            f"registry id {specialist_id!r} resolved to multiple cascade entries: {matches}"
        )

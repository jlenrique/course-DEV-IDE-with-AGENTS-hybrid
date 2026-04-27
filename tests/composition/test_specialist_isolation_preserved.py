from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REGISTRY_PATH = Path("state/config/dispatch-registry.yaml")


def _registry_specialists() -> list[tuple[str, str]]:
    payload = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    specialists = payload["specialists"]
    return sorted(specialists.items())


@pytest.mark.parametrize(("specialist_id", "builder_ref"), _registry_specialists())
def test_specialist_isolated_scaffold_contract_still_builds(
    specialist_id: str,
    builder_ref: str,
) -> None:
    module_name, function_name = builder_ref.split(":", 1)
    builder = getattr(importlib.import_module(module_name), function_name)

    graph: Any = builder()

    assert specialist_id
    assert frozenset(graph.nodes.keys()) == SCAFFOLD_NODE_IDS

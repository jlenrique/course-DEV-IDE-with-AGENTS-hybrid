from __future__ import annotations

import re
from pathlib import Path

import yaml

REGISTRY_PATH = Path("docs/conversational-gates/_registry/vocabulary.yaml")
TEMPLATE_DIR = Path("docs/conversational-gates")
PRE_GATE_MODULE = Path("app/marcus/orchestrator/pre_gate_marcus.py")


def _quoted_tokens(text: str) -> set[str]:
    return set(re.findall(r'"([a-z][a-z0-9-]*)"', text))


def test_pre_gate_marcus_templates_emit_only_registry_tokens() -> None:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    gate_tokens = registry["namespaces"]["gates"]["tokens"]
    allowed = set(gate_tokens["decision"]) | set(gate_tokens["directive"])

    emitted: set[str] = set()
    for template_name in ("g1.j2", "g2c.j2", "g3.j2", "g4.j2"):
        emitted |= _quoted_tokens(
            (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        )
    emitted &= allowed

    assert {"confirm", "revise", "reject", "escape"}.issubset(emitted)
    assert {"accept-as-is", "apply-edit", "re-emit", "halt-for-repair"}.issubset(
        emitted
    )
    assert emitted <= allowed


def test_pre_gate_marcus_parser_uses_vocabulary_field_names() -> None:
    text = PRE_GATE_MODULE.read_text(encoding="utf-8")

    assert 'data["decision"]' in text
    assert 'data["directive"]' in text
    assert 'data["rationale"]' in text

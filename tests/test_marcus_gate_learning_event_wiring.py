"""AST checks for Marcus gate learning-event call-sites."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIRING = ROOT / "app" / "marcus" / "orchestrator" / "learning_event_wiring.py"


def test_marcus_calls_append_at_gates_234() -> None:
    tree = ast.parse(WIRING.read_text(encoding="utf-8"))
    calls: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "create_event":
            continue
        gate = None
        event_type = None
        for kw in node.keywords:
            if kw.arg == "gate" and isinstance(kw.value, ast.Constant):
                gate = kw.value.value
            if kw.arg == "event_type" and isinstance(kw.value, ast.Constant):
                event_type = kw.value.value
        if isinstance(gate, str) and isinstance(event_type, str):
            calls.append((gate, event_type))

    assert len(calls) == 3
    assert set(calls) == {("G2C", "approval"), ("G3", "revision"), ("G4", "waiver")}

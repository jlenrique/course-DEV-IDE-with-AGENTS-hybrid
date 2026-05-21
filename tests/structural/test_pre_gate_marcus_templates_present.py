from __future__ import annotations

from pathlib import Path

TEMPLATE_DIR = Path("docs/conversational-gates")
EXPECTED_SLOTS = {
    "trial_id",
    "gate_id",
    "upstream_contributions",
    "pending_nodes",
    "artifact_paths",
}
DECISION_ENUM = '["confirm", "revise", "reject", "escape"]'
DIRECTIVE_ENUM = '["accept-as-is", "apply-edit", "re-emit", "halt-for-repair"]'


def test_pre_gate_marcus_templates_exist_with_slots_and_closed_enums() -> None:
    for template_name in ("g1.j2", "g2c.j2", "g3.j2", "g4.j2"):
        path = TEMPLATE_DIR / template_name
        assert path.exists(), f"missing pre-gate-marcus template: {path}"
        text = path.read_text(encoding="utf-8")
        for slot in EXPECTED_SLOTS:
            assert f"{{{{ {slot}" in text
        assert DECISION_ENUM in text
        assert DIRECTIVE_ENUM in text

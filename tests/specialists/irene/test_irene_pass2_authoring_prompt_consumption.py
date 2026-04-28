from __future__ import annotations

from app.specialists.irene.graph import _read_pass_2_references


def test_pass_2_prompt_references_authoring_contract_and_schema() -> None:
    references = _read_pass_2_references()

    assert "pass-2-authoring-template.md" in references
    assert "app/specialists/irene/authoring/pass_2_template.py" in references
    assert "schema/irene_pass_2_authoring.v1.schema.json" in references
    assert "composition_mode" in references

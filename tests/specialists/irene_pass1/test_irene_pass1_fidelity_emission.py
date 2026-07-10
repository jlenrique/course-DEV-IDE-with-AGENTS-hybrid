"""Irene Pass-1 fidelity emit recovery — RED-first (spec-irene-pass1-fidelity-emit-recovery).

No network/LLM calls. Assert field names / phrases, not full prompt goldens.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.specialists.irene_pass1 import _act as pass1_act


def _unit(**overrides: Any) -> dict[str, Any]:
    base = {
        "unit_id": "u1",
        "title": "Assessment topics",
        "learning_objective": "List the KC topics",
        "scope_decision": "in-scope",
        "rationale": "Must appear verbatim.",
        "cluster_id": "c-u1",
        "cluster_role": "head",
        "cluster_position": "establish",
        "cluster_interstitial_count": 0,
    }
    base.update(overrides)
    return base


def test_emission_contract_requests_fidelity_modes_and_anti_over_tag() -> None:
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1"}, extracted_source="Corpus."
    )
    lower = user.lower()
    assert '"fidelity"' in user or "fidelity" in lower
    assert "literal-text" in user
    assert "literal-visual" in user
    assert "creative" in lower
    assert "over-tag" in lower or "do not over" in lower or "don't over" in lower


def test_fidelity_guidance_visible_in_assembled_prompt() -> None:
    guidance = {
        "literal_text": [
            {
                "description": "10 KC topics from Chapters 2 & 3",
                "source_ref": "extracted.md#KC",
            }
        ]
    }
    _system, user = pass1_act.assemble_pass1_prompt(
        {"mode": "pass-1", "fidelity_guidance": guidance},
        extracted_source="Corpus.",
    )
    assert "fidelity_guidance" in user
    assert "10 KC topics" in user


def test_normalize_keeps_literal_text_and_literal_visual() -> None:
    plan = {
        "plan_units": [
            _unit(unit_id="u1", fidelity="literal-text"),
            _unit(unit_id="u2", title="Chart", fidelity="literal-visual"),
            _unit(unit_id="u3", title="Concept", fidelity="creative"),
        ]
    }
    out = pass1_act.normalize_fidelity(plan)
    by_id = {u["unit_id"]: u for u in out["plan_units"]}
    assert by_id["u1"]["fidelity"] == "literal-text"
    assert by_id["u2"]["fidelity"] == "literal-visual"
    assert by_id["u3"]["fidelity"] == "creative"


def test_normalize_omits_missing_and_unknown_without_inventing() -> None:
    plan = {
        "plan_units": [
            _unit(unit_id="u1"),  # missing
            _unit(unit_id="u2", fidelity="strict"),
            _unit(unit_id="u3", fidelity=""),
            _unit(unit_id="u4", fidelity=None),
        ]
    }
    out = pass1_act.normalize_fidelity(plan)
    for unit in out["plan_units"]:
        assert "fidelity" not in unit


def test_normalize_coerces_known_aliases() -> None:
    plan = {
        "plan_units": [
            _unit(unit_id="u1", fidelity="literal_text"),
            _unit(unit_id="u2", fidelity="literal-image"),
            _unit(unit_id="u3", fidelity="Literal-Text"),
        ]
    }
    out = pass1_act.normalize_fidelity(plan)
    by_id = {u["unit_id"]: u for u in out["plan_units"]}
    assert by_id["u1"]["fidelity"] == "literal-text"
    assert by_id["u2"]["fidelity"] == "literal-visual"
    assert by_id["u3"]["fidelity"] == "literal-text"


def test_parse_preserves_structured_fidelity_not_prose_theater() -> None:
    structured = {
        "lesson_summary": "Plan",
        "plan_units": [
            _unit(unit_id="u1", fidelity="literal-text"),
            _unit(unit_id="u2", title="Other"),  # no fidelity
        ],
    }
    parsed = pass1_act.parse_pass1_response(json.dumps(structured))
    by_id = {u["unit_id"]: u for u in parsed["plan_units"]}
    assert by_id["u1"]["fidelity"] == "literal-text"
    assert "fidelity" not in by_id["u2"]

    # Prose mentions fidelity but structured field absent → no manufactured tag
    theater = {
        "lesson_summary": "Mark fidelity complete for all slides",
        "plan_units": [_unit(unit_id="u9", rationale="fidelity guidance noted")],
    }
    parsed_theater = pass1_act.parse_pass1_response(json.dumps(theater))
    assert "fidelity" not in parsed_theater["plan_units"][0]


def test_write_lesson_plan_surfaces_fidelity_line(tmp_path: Path) -> None:
    plan = {
        "lesson_summary": "Summary",
        "plan_units": [
            _unit(unit_id="u1", fidelity="literal-text"),
            _unit(unit_id="u2", title="Concept"),  # omit
        ],
        "collateral": {"declaration": "none"},
    }
    path = pass1_act.write_lesson_plan(plan, run_id="fid-test", runs_root=tmp_path)
    text = path.read_text(encoding="utf-8")
    assert "- Fidelity: literal-text" in text
    # Untagged unit must not invent a fidelity line — only one fidelity line total
    assert text.count("- Fidelity:") == 1
    assert "## u2:" in text
    u2_block = text.split("## u2:", 1)[1]
    assert "- Fidelity:" not in u2_block.split("## Workbook", 1)[0]


def test_write_lesson_plan_canonicalizes_alias_fidelity(tmp_path: Path) -> None:
    plan = {
        "lesson_summary": "Summary",
        "plan_units": [_unit(unit_id="u1", fidelity="literal_text")],
        "collateral": {"declaration": "none"},
    }
    path = pass1_act.write_lesson_plan(plan, run_id="fid-alias", runs_root=tmp_path)
    assert "- Fidelity: literal-text" in path.read_text(encoding="utf-8")

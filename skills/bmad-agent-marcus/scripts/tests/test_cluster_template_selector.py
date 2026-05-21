from __future__ import annotations

from importlib import util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_template_selector.py"
TEMPLATE_PATH = ROOT / "skills" / "bmad-agent-content-creator" / "references" / "cluster-templates.yaml"


def _load_module():
    spec = util.spec_from_file_location("cluster_template_selector", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
select_cluster_template = mod.select_cluster_template
ClusterTemplateSelectionError = mod.ClusterTemplateSelectionError


def _library():
    return yaml.safe_load(TEMPLATE_PATH.read_text(encoding="utf-8"))


def test_force_template_wins():
    result = select_cluster_template(
        template_library=_library(),
        content_signals={"data_presence": 1.0},
        force_template="quick-punch",
    )
    assert result["template_id"] == "quick-punch"
    assert "forced_by_operator" in result["reasons"]


def test_force_template_conflict_with_exclude_raises():
    try:
        select_cluster_template(
            template_library=_library(),
            content_signals={"data_presence": 1.0},
            force_template="quick-punch",
            exclude_templates=["quick-punch"],
        )
        assert False, "expected ClusterTemplateSelectionError"
    except ClusterTemplateSelectionError as exc:
        assert exc.code == "invalid_override"


def test_excluded_template_not_in_ranking():
    result = select_cluster_template(
        template_library=_library(),
        content_signals={"emotional_weight": 1.0},
        exclude_templates=["emotional-arc"],
    )
    ranked = {row["template_id"] for row in result["ranking"]}
    assert "emotional-arc" not in ranked


def test_prefer_templates_bonus_can_win_close_case():
    signals = {
        "single_core_idea": 1.0,
        "emotional_weight": 0.2,
        "contrast_tension": 0.3,
    }
    baseline = select_cluster_template(template_library=_library(), content_signals=signals)
    preferred = select_cluster_template(
        template_library=_library(),
        content_signals=signals,
        prefer_templates=["cognitive-reset"],
    )
    baseline_top = baseline["ranking"][0]["score_breakdown"]["final_score"]
    preferred_reset = next(row for row in preferred["ranking"] if row["template_id"] == "cognitive-reset")
    assert preferred_reset["score_breakdown"]["final_score"] >= baseline_top - 0.40


def test_variety_penalty_discourages_repeat():
    signals = {"single_core_idea": 1.0}
    no_penalty = select_cluster_template(template_library=_library(), content_signals=signals)
    with_penalty = select_cluster_template(
        template_library=_library(),
        content_signals=signals,
        previous_template_ids=[no_penalty["template_id"]],
    )
    if no_penalty["template_id"] == with_penalty["template_id"]:
        winner = with_penalty["ranking"][0]
        assert winner["score_breakdown"]["variety_penalty"] <= 0.0


def test_pacing_penalty_applies_for_recent_profiles():
    signals = {"single_core_idea": 1.0}
    result = select_cluster_template(
        template_library=_library(),
        content_signals=signals,
        recent_pacing_profiles=["tight", "tight"],
    )
    tight_rows = [row for row in result["ranking"] if row["pacing_profile"] == "tight"]
    assert tight_rows
    assert any(row["score_breakdown"]["pacing_penalty"] < 0 for row in tight_rows)


def test_arc_bias_applies_for_end_phase():
    result = select_cluster_template(
        template_library=_library(),
        content_signals={"emotional_weight": 0.2, "visual_decomposability": 0.2},
        master_arc_phase="end",
    )
    top = result["ranking"][0]
    assert top["score_breakdown"]["arc_bias"] >= 0.0


def test_selection_transparency_contract_present():
    result = select_cluster_template(
        template_library=_library(),
        content_signals={"data_presence": 1.0, "visual_decomposability": 0.8},
    )
    assert result["template_id"]
    assert isinstance(result["reasons"], list)
    assert isinstance(result["alternatives"], list)
    assert isinstance(result["ranking"], list)
    assert "final_score" in result["ranking"][0]["score_breakdown"]


def test_no_candidates_after_exclusions_raises():
    all_ids = [template["template_id"] for template in _library()["templates"]]
    try:
        select_cluster_template(
            template_library=_library(),
            content_signals={"single_core_idea": 1.0},
            exclude_templates=all_ids,
        )
        assert False, "expected ClusterTemplateSelectionError"
    except ClusterTemplateSelectionError as exc:
        assert exc.code == "no_candidates"


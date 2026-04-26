from __future__ import annotations

from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_template_planner.py"


def _load_module():
    spec = util.spec_from_file_location("cluster_template_planner", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
build_cluster_template_plan = mod.build_cluster_template_plan
load_default_template_library = mod.load_default_template_library
load_operator_template_overrides = mod.load_operator_template_overrides


def _clustered_rows():
    return [
        {
            "slide_id": "slide-01",
            "card_number": 1,
            "cluster_id": "c1",
            "cluster_role": "head",
            "visual_description": "Framework with multiple components and data table",
            "narrative_arc": "Start broad, then sharpen",
        },
        {
            "slide_id": "slide-02",
            "card_number": 2,
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "parent_slide_id": "slide-01",
        },
        {
            "slide_id": "slide-03",
            "card_number": 3,
            "cluster_id": "c2",
            "cluster_role": "head",
            "visual_description": "Single key point and pace reset",
            "narrative_arc": "Resolve",
        },
    ]


def test_returns_empty_when_no_cluster_heads():
    plan = build_cluster_template_plan(
        gary_slide_output=[{"slide_id": "slide-01", "cluster_role": "interstitial"}],
        template_library=load_default_template_library(),
    )
    assert plan["schema_version"] == "1.0"
    assert plan["clusters"] == []


def test_builds_plan_for_clustered_heads():
    plan = build_cluster_template_plan(
        gary_slide_output=_clustered_rows(),
        template_library=load_default_template_library(),
    )
    assert plan["schema_version"] == "1.0"
    assert len(plan["clusters"]) == 2
    assert plan["clusters"][0]["cluster_id"] == "c1"
    assert plan["clusters"][0]["selected_template_id"]
    assert isinstance(plan["clusters"][0]["selection_reasons"], list)
    assert isinstance(plan["clusters"][0]["selection_ranking"], list)
    assert plan["selected_template_ids_by_cluster"]["c1"] == plan["clusters"][0]["selected_template_id"]
    assert isinstance(plan["clusters"][0]["expected_interstitial_sequence"], list)
    assert isinstance(plan["clusters"][0]["template_constraints"], dict)


def test_assigns_master_arc_phase_ordering():
    rows = _clustered_rows()
    rows.append(
        {
            "slide_id": "slide-05",
            "card_number": 5,
            "cluster_id": "c3",
            "cluster_role": "head",
            "visual_description": "Story and emotional stakes",
        }
    )
    plan = build_cluster_template_plan(
        gary_slide_output=rows,
        template_library=load_default_template_library(),
    )
    phases = [item["master_arc_phase"] for item in plan["clusters"]]
    assert phases == ["beginning", "middle", "end"]


def test_applies_force_template_per_cluster_override():
    plan = build_cluster_template_plan(
        gary_slide_output=_clustered_rows(),
        template_library=load_default_template_library(),
        operator_overrides={"global": {}, "per_cluster": {"c2": {"force_template": "quick-punch"}}},
    )
    cluster_two = next(item for item in plan["clusters"] if item["cluster_id"] == "c2")
    assert cluster_two["selected_template_id"] == "quick-punch"
    assert "forced_by_operator" in cluster_two["selection_reasons"]


def test_load_operator_overrides_parses_directives(tmp_path: Path):
    directives = tmp_path / "operator-directives.md"
    directives.write_text(
        "\n".join(
            [
                "force_template: deep-dive",
                "exclude_templates: [quick-punch, cognitive-reset]",
                "prefer_templates: [contrast-pair]",
                "cluster c2: force_template=quick-punch",
            ]
        ),
        encoding="utf-8",
    )
    overrides = load_operator_template_overrides(directives)
    assert overrides["global"]["force_template"] == "deep-dive"
    assert "quick-punch" in overrides["global"]["exclude_templates"]
    assert "contrast-pair" in overrides["global"]["prefer_templates"]
    assert overrides["per_cluster"]["c2"]["force_template"] == "quick-punch"


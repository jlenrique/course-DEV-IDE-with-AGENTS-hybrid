"""Operator-control parity shell for the 33-row Slab 7 mapping floor."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from app.manifest.compiler import SPECIALIST_ALIASES, production_gate_ids
from app.manifest.loader import load
from app.marcus.cli.trial import build_trial_parser
from app.models.decision_cards import GateDecisionToken, SpecialistId

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

REFERENCES_FRS_BY_ROW = {
    1: ["FR25", "FR-A22"],
    2: ["FR26", "FR27"],
    3: ["FR-O13", "FR-O14"],
    4: ["FR26", "FR-O25"],
    5: ["FR25", "FR-O23"],
    6: ["FR-A21", "FR-O9"],
    7: ["FR-O13", "FR-O14"],
    8: ["FR-O15", "FR-O16"],
    9: ["FR36", "FR37"],
    10: ["FR25", "FR26"],
    11: ["FR-A21", "FR-O9"],
    12: ["FR27", "FR28"],
    13: ["FR-O13", "FR-O14"],
    14: ["FR-O13", "FR-O15"],
    15: ["FR-O16", "FR-O23"],
    16: ["FR25", "FR28"],
    17: ["FR-A21", "FR-O9"],
    18: ["FR-A21", "FR-O9"],
    19: ["FR25", "FR-A24"],
    20: ["FR-A21", "FR-O9"],
    21: ["FR25", "FR28"],
    22: ["FR-A21", "FR-O9"],
    23: ["FR26", "FR27"],
    24: ["FR-A21", "FR-O9"],
    25: ["FR25", "FR-A24"],
    26: ["FR25", "FR-O24"],
    27: ["FR36", "FR37"],
    28: ["FR36", "FR37"],
    29: ["FR36", "FR37"],
    30: ["FR25", "FR-O24"],
    31: ["FR36", "FR37"],
    32: ["FR36", "FR37"],
    33: ["FR-O15", "FR-O16"],
}


def mapping_checklist_row(row: int):
    """Attach AC-7.8-A row metadata to parity tests."""

    def decorate(func):
        func.MAPPING_CHECKLIST_ROW = row
        func.REFERENCES_FRS = REFERENCES_FRS_BY_ROW[row]
        return func

    return decorate


def _trial_parser_actions() -> dict[str, argparse.Action]:
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    start_parser = next(
        action.choices["start"]
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    return {action.dest: action for action in start_parser._actions}


def _active_pause_points() -> frozenset[str]:
    return production_gate_ids(load(LIVE_MANIFEST))


@mapping_checklist_row(1)
def test_row_01_g0_directive_composition_confirm() -> None:
    action = _trial_parser_actions()["auto_confirm_directive"]
    assert "--auto-confirm-directive" in action.option_strings
    assert isinstance(action, argparse._StoreTrueAction)


@pytest.mark.skip(reason="awaits Slab 7b source-authority active-mode implementation")
@mapping_checklist_row(2)
def test_row_02_source_authority_map_gate() -> None:
    assert "G0A" not in _active_pause_points()


@mapping_checklist_row(3)
def test_row_03_operator_directives_capture() -> None:
    assert (REPO_ROOT / "docs" / "operator" / "step-02a-prior-run-defaults.md").is_file()


@pytest.mark.skip(reason="awaits Slab 7b ingestion active-mode implementation")
@mapping_checklist_row(4)
def test_row_04_ingestion_evidence_log() -> None:
    assert (REPO_ROOT / "app" / "specialists" / "texas" / "graph.py").is_file()


@mapping_checklist_row(5)
def test_row_05_ingestion_quality_gate() -> None:
    assert {token.value for token in GateDecisionToken} == {
        "confirm",
        "revise",
        "reject",
        "escape",
        "skip-slide",
        "abort-run",
    }


@pytest.mark.skip(reason="awaits Slab 7b lesson-plan scope-lock active-mode implementation")
@mapping_checklist_row(6)
def test_row_06_lesson_plan_scope_lock() -> None:
    assert "G1A" not in _active_pause_points()


@pytest.mark.skip(reason="awaits Slab 7b parent-slide-count active-mode implementation")
@mapping_checklist_row(7)
def test_row_07_parent_slide_count_poll() -> None:
    assert "04.5" in LIVE_MANIFEST.read_text(encoding="utf-8")


@pytest.mark.skip(reason="awaits Slab 7b run-constants lock active-mode implementation")
@mapping_checklist_row(8)
def test_row_08_run_constants_lock() -> None:
    assert "04.55" in LIVE_MANIFEST.read_text(encoding="utf-8")


@mapping_checklist_row(9)
def test_row_09_creative_directive_resolution() -> None:
    assert (REPO_ROOT / "state" / "config" / "experience-profiles.yaml").is_file()


@mapping_checklist_row(10)
def test_row_10_irene_pass1_gate() -> None:
    assert (REPO_ROOT / "app" / "specialists" / "irene" / "graph.py").is_file()


@pytest.mark.skip(reason="awaits Slab 7b cluster-plan active-mode implementation")
@mapping_checklist_row(11)
def test_row_11_cluster_plan_gate() -> None:
    assert "G1.5" not in _active_pause_points()


@pytest.mark.skip(reason="awaits Slab 7b pre-dispatch package active-mode implementation")
@mapping_checklist_row(12)
def test_row_12_pre_dispatch_package() -> None:
    assert "06" in LIVE_MANIFEST.read_text(encoding="utf-8")


@pytest.mark.skip(reason="awaits Slab 7b cluster prompt-engineering active-mode implementation")
@mapping_checklist_row(13)
def test_row_13_cluster_prompt_engineering() -> None:
    assert "6.2" in LIVE_MANIFEST.read_text(encoding="utf-8")


@pytest.mark.skip(reason="awaits Slab 7b cluster dispatch-sequencing active-mode implementation")
@mapping_checklist_row(14)
def test_row_14_cluster_dispatch_sequencing() -> None:
    assert "6.3" in LIVE_MANIFEST.read_text(encoding="utf-8")


@mapping_checklist_row(15)
def test_row_15_literal_visual_operator_build() -> None:
    assert (
        REPO_ROOT
        / "skills"
        / "bmad-agent-marcus"
        / "scripts"
        / "validate-literal-visual-pre-dispatch.py"
    ).is_file()


@pytest.mark.skip(reason="awaits Slab 7b Gary active-mode implementation")
@mapping_checklist_row(16)
def test_row_16_gary_dispatch_export() -> None:
    assert "gary" in {specialist.value for specialist in SpecialistId}


@pytest.mark.skip(reason="awaits Slab 7b cluster-coherence active-mode implementation")
@mapping_checklist_row(17)
def test_row_17_cluster_coherence_gate() -> None:
    assert "G2.5" not in _active_pause_points()


@pytest.mark.skip(reason="awaits Slab 7b variant-selection active-mode implementation")
@mapping_checklist_row(18)
def test_row_18_variant_selection_gate() -> None:
    assert (REPO_ROOT / "app" / "marcus" / "orchestrator" / "per_slide_subgraph.py").is_file()


@mapping_checklist_row(19)
def test_row_19_storyboard_a_gate2_approval() -> None:
    assert "G2C" in _active_pause_points()


@pytest.mark.skip(reason="awaits Slab 7b motion-designation active-mode implementation")
@mapping_checklist_row(20)
def test_row_20_motion_designation_gate() -> None:
    assert "G2M" not in _active_pause_points()


@pytest.mark.skip(reason="awaits Slab 7b Kira active-mode implementation")
@mapping_checklist_row(21)
def test_row_21_motion_generation_import() -> None:
    assert "kira" in {specialist.value for specialist in SpecialistId}


@pytest.mark.skip(reason="awaits Slab 7b motion-gate active-mode implementation")
@mapping_checklist_row(22)
def test_row_22_motion_gate() -> None:
    assert "G2F" not in _active_pause_points()


@mapping_checklist_row(23)
def test_row_23_irene_pass2_segment_manifest() -> None:
    assert (REPO_ROOT / "app" / "specialists" / "irene" / "graph.py").is_file()


@pytest.mark.skip(reason="awaits Slab 7b Storyboard B active-mode implementation")
@mapping_checklist_row(24)
def test_row_24_storyboard_b_hil_review() -> None:
    assert (REPO_ROOT / "app" / "marcus" / "orchestrator" / "html_review_pack.py").is_file()


@mapping_checklist_row(25)
def test_row_25_gate3_lock_pass2_package() -> None:
    assert "G3" in _active_pause_points()


@mapping_checklist_row(26)
def test_row_26_fidelity_quality_pre_spend() -> None:
    assert "G4" in _active_pause_points()


@mapping_checklist_row(27)
def test_row_27_voice_selection_hil() -> None:
    assert SPECIALIST_ALIASES["elevenlabs"] == "enrique"
    assert "enrique" in {specialist.value for specialist in SpecialistId}


@mapping_checklist_row(28)
def test_row_28_elevenlabs_input_package_hil() -> None:
    assert SPECIALIST_ALIASES["elevenlabs"] == "enrique"


@pytest.mark.skip(reason="awaits Slab 7b Enrique active-mode implementation")
@mapping_checklist_row(29)
def test_row_29_elevenlabs_audio_generation() -> None:
    assert "enrique" in {specialist.value for specialist in SpecialistId}


@mapping_checklist_row(30)
def test_row_30_quinn_r_pre_composition_qa() -> None:
    assert SPECIALIST_ALIASES["quinn-r"] == "quinn_r"
    assert "quinn_r" in {specialist.value for specialist in SpecialistId}


@mapping_checklist_row(31)
def test_row_31_compositor_assembly_bundle() -> None:
    assert "compositor" in {specialist.value for specialist in SpecialistId}


@pytest.mark.skip(reason="awaits post-7a operator brief implementation")
@mapping_checklist_row(32)
def test_row_32_desmond_operator_brief() -> None:
    assert "desmond" in {specialist.value for specialist in SpecialistId}


@mapping_checklist_row(33)
def test_row_33_operator_handoff_descript_ready() -> None:
    assert (REPO_ROOT / "app" / "marcus" / "orchestrator" / "gate_runner.py").is_file()

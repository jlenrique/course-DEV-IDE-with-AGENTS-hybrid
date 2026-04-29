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


def test_row_01_g0_directive_composition_confirm() -> None:
    action = _trial_parser_actions()["auto_confirm_directive"]
    assert "--auto-confirm-directive" in action.option_strings
    assert isinstance(action, argparse._StoreTrueAction)


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_02_source_authority_map_gate() -> None:
    raise AssertionError("placeholder")


def test_row_03_operator_directives_capture() -> None:
    assert (REPO_ROOT / "docs" / "operator" / "step-02a-prior-run-defaults.md").is_file()


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_04_ingestion_evidence_log() -> None:
    raise AssertionError("placeholder")


def test_row_05_ingestion_quality_gate() -> None:
    assert {token.value for token in GateDecisionToken} == {
        "confirm",
        "revise",
        "reject",
        "escape",
        "skip-slide",
        "abort-run",
    }


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_06_lesson_plan_scope_lock() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_07_parent_slide_count_poll() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_08_run_constants_lock() -> None:
    raise AssertionError("placeholder")


def test_row_09_creative_directive_resolution() -> None:
    assert (REPO_ROOT / "state" / "config" / "experience-profiles.yaml").is_file()


def test_row_10_irene_pass1_gate() -> None:
    assert (REPO_ROOT / "app" / "specialists" / "irene" / "graph.py").is_file()


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_11_cluster_plan_gate() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_12_pre_dispatch_package() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_13_cluster_prompt_engineering() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.5 implementation")
def test_row_14_cluster_dispatch_sequencing() -> None:
    raise AssertionError("placeholder")


def test_row_15_literal_visual_operator_build() -> None:
    assert (
        REPO_ROOT
        / "skills"
        / "bmad-agent-marcus"
        / "scripts"
        / "validate-literal-visual-pre-dispatch.py"
    ).is_file()


@pytest.mark.skip(reason="awaits Slab 7b Gary active-mode implementation")
def test_row_16_gary_dispatch_export() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_17_cluster_coherence_gate() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_18_variant_selection_gate() -> None:
    raise AssertionError("placeholder")


def test_row_19_storyboard_a_gate2_approval() -> None:
    assert "G2C" in _active_pause_points()


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_20_motion_designation_gate() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Slab 7b Kira active-mode implementation")
def test_row_21_motion_generation_import() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_22_motion_gate() -> None:
    raise AssertionError("placeholder")


def test_row_23_irene_pass2_segment_manifest() -> None:
    assert (REPO_ROOT / "app" / "specialists" / "irene" / "graph.py").is_file()


@pytest.mark.skip(reason="awaits Story 7a.4 implementation")
def test_row_24_storyboard_b_hil_review() -> None:
    raise AssertionError("placeholder")


def test_row_25_gate3_lock_pass2_package() -> None:
    assert "G3" in _active_pause_points()


def test_row_26_fidelity_quality_pre_spend() -> None:
    assert "G4" in _active_pause_points()


def test_row_27_voice_selection_hil() -> None:
    assert SPECIALIST_ALIASES["elevenlabs"] == "enrique"
    assert "enrique" in {specialist.value for specialist in SpecialistId}


def test_row_28_elevenlabs_input_package_hil() -> None:
    assert SPECIALIST_ALIASES["elevenlabs"] == "enrique"


@pytest.mark.skip(reason="awaits Slab 7b Enrique active-mode implementation")
def test_row_29_elevenlabs_audio_generation() -> None:
    raise AssertionError("placeholder")


def test_row_30_quinn_r_pre_composition_qa() -> None:
    assert SPECIALIST_ALIASES["quinn-r"] == "quinn_r"
    assert "quinn_r" in {specialist.value for specialist in SpecialistId}


def test_row_31_compositor_assembly_bundle() -> None:
    assert "compositor" in {specialist.value for specialist in SpecialistId}


@pytest.mark.skip(reason="awaits post-7a operator brief implementation")
def test_row_32_desmond_operator_brief() -> None:
    raise AssertionError("placeholder")


@pytest.mark.skip(reason="awaits Story 7a.8 implementation")
def test_row_33_operator_handoff_descript_ready() -> None:
    raise AssertionError("placeholder")

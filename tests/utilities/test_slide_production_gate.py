"""Tests for the DP6 frozen-Gamma reuse gate (scripts/utilities/slide_production_gate.py).

Authority: braid-green-light-ratification-2026-06-24.md §DP6.

Pins the load-set well-formedness, the fresh-required predicate on REAL slide-
production paths (gary + v4.2 pack -> True = fresh-required), the reuse-OK case
on slide-INDEPENDENT diffs (workbook/collateral/README -> False = reuse-OK), the
stale-pack rule, and the run-record stamp shape.
"""

from __future__ import annotations

import pytest

from scripts.utilities.slide_production_gate import (
    fresh_gamma_required,
    load_current_pack_version,
    load_slide_production_paths,
    pack_version_stale,
    reuse_stamp,
)

# Real slide-production diff files — each MUST trip the gate (fresh required).
SLIDE_PRODUCTION_DIFFS = [
    "app/specialists/gary/_act.py",
    "app/specialists/gary/gamma_dispatch.py",
    "docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md",
    "scripts/generators/v42/render.py",
    "scripts/generators/v42/templates/sections/05B-cluster-plan-g1-5-gate.md.j2",
    "app/specialists/irene_pass1/_act.py",
    "scripts/api_clients/gamma_client.py",
    "app/marcus/orchestrator/chooser_publisher.py",
    "app/marcus/orchestrator/slide_variant_selection.py",
    "app/gates/section_07c/chooser_html_emitter.py",
    "app/specialists/_shared/figure_tokens.py",
    "app/specialists/quinn_r/fidelity_detector.py",
    "app/specialists/irene/authoring/pass_2_template.py",
    "app/specialists/irene/graph.py",
    "app/models/decision_cards/g5.py",
]

# Slide-INDEPENDENT diff files — none may trip the gate (reuse OK).
SLIDE_INDEPENDENT_DIFFS = [
    "app/marcus/lesson_plan/collateral_spec.py",
    "app/marcus/lesson_plan/workbook_producer.py",
    "README.md",
    "docs/dev-guide/pipeline-manifest-regime.md",
    "tests/utilities/test_slide_production_gate.py",
    "_bmad-output/planning-artifacts/epics.md",
    "state/config/dispatch-registry.yaml",
]


def test_load_set_is_non_empty_and_well_formed() -> None:
    globs = load_slide_production_paths()
    assert isinstance(globs, tuple)
    assert len(globs) > 0
    assert all(isinstance(g, str) and g.strip() for g in globs)
    # The headline anchors must be present in the operand.
    assert any("gary" in g for g in globs)
    assert any("production-prompt-pack-v4.2" in g for g in globs)
    assert any("irene_pass1" in g for g in globs)


def test_current_pack_version_loads() -> None:
    assert load_current_pack_version() == "v4.2"


@pytest.mark.parametrize("diff_file", SLIDE_PRODUCTION_DIFFS)
def test_fresh_required_true_for_slide_production_paths(diff_file: str) -> None:
    # A diff touching ANY real slide-production path => fresh Gamma required.
    assert fresh_gamma_required([diff_file]) is True


@pytest.mark.parametrize("diff_file", SLIDE_INDEPENDENT_DIFFS)
def test_reuse_ok_for_slide_independent_paths(diff_file: str) -> None:
    # A diff touching only slide-INDEPENDENT files => reuse permitted.
    assert fresh_gamma_required([diff_file]) is False


def test_collateral_only_diff_is_reuse_ok() -> None:
    # The S2 workbook/collateral case: NONE of these touch slide pixels.
    diff = [
        "app/marcus/lesson_plan/collateral_spec.py",
        "app/marcus/lesson_plan/workbook_producer.py",
        "tests/marcus/test_collateral_spec.py",
    ]
    assert fresh_gamma_required(diff) is False


def test_mixed_diff_with_one_slide_path_is_fresh_required() -> None:
    diff = [
        "README.md",
        "app/marcus/lesson_plan/collateral_spec.py",
        "app/specialists/gary/_act.py",  # the single slide-production path
    ]
    assert fresh_gamma_required(diff) is True


def test_empty_diff_is_reuse_ok() -> None:
    assert fresh_gamma_required([]) is False


def test_explicit_paths_override() -> None:
    custom = ("app/foo/**",)
    assert fresh_gamma_required(["app/foo/bar.py"], paths=custom) is True
    assert fresh_gamma_required(["app/specialists/gary/_act.py"], paths=custom) is False


def test_backslash_diff_paths_normalised() -> None:
    # git on Windows / mixed tooling may emit backslashes; must still match.
    assert fresh_gamma_required(["app\\specialists\\gary\\_act.py"]) is True


def test_pack_version_stale_true_when_frozen_older() -> None:
    assert pack_version_stale("v4.1", "v4.2") is True
    assert pack_version_stale("v4.0", "v4.2") is True
    assert pack_version_stale("3.9", "4.2") is True


def test_pack_version_not_stale_when_equal() -> None:
    assert pack_version_stale("v4.2", "v4.2") is False


def test_pack_version_not_stale_when_frozen_newer() -> None:
    assert pack_version_stale("v4.3", "v4.2") is False


def test_pack_version_stale_when_unknown() -> None:
    # Unknown version -> safe direction (fresh required).
    assert pack_version_stale(None, "v4.2") is True
    assert pack_version_stale("v4.2", None) is True


def test_reuse_stamp_shape() -> None:
    assert reuse_stamp("abc1234") == "empty-intersection@abc1234"

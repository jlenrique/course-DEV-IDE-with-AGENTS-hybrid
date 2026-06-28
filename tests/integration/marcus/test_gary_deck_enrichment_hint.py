"""P5-S2 (Step 6) RED-first floors: Gary's deck directive consumes the G0 card.

Consumer B — the enrichment hint is routed ONLY into Gary's
``additional_instructions`` (deck-level), so the directive SENT to Gamma is
enrichment-shaped, byte-deterministically (Murat MUR-5: the live render is a
confirmation, NOT a deterministic gate). The blocking guarantees:

  * B1 — a SENTINEL-bearing LO statement in the card appears VERBATIM in the
    ``additional_instructions`` payload (and therefore in the per-variant Gamma
    directive), and is ABSENT when the card is absent;
  * GARY-A1 (content-channel firewall) — the hint is STRUCTURALLY BARRED from the
    ``text_mode="preserve"`` card body (``_input_text``) and the Studio lock
    (``_studio_slide_content`` / ``_STUDIO_LOCK_WRAPPER``); the Studio path no-ops it;
  * B2 — card-absent / flag-OFF ⇒ the directive is byte-identical, and the
    ``gamma_settings`` roster + ``text_mode`` defaults + ``_STUDIO_LOCK_WRAPPER`` are
    object-equal to baseline (pinned by name);
  * A6 — the consumer finds ``g0-enrichment.json`` on the resume/recover walk (a
    FRESH envelope rebuilding §06 still picks up the on-disk card).

OFFLINE ONLY: no Gamma dispatch; the projection + directive assembly are pure.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.marcus.orchestrator import enrichment_consumption as ec
from app.marcus.orchestrator.package_builders import build_gary_briefs, run_builder_node
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.specialists.gary import _act as gary_act

REPO_ROOT = Path(__file__).resolve().parents[3]
LEGACY_ENVELOPE_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "integration" / "marcus" / "legacy_envelope_50b7d353.json"
)
CARD_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "p5_workbook_corpus" / "live_enriched_result_card.json"
)
TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
DECK_FLAG = ec.MARCUS_DECK_ENRICHMENT_ACTIVE_ENV
SENTINEL_LO = "ENRICHED-LO-SENTINEL-deck-quantify-redesignable-administrative-waste"


def _fixture_outputs() -> tuple[dict, dict]:
    raw = json.loads(LEGACY_ENVELOPE_FIXTURE.read_text(encoding="utf-8-sig"))
    by_id = {c["specialist_id"]: c["output"] for c in raw["contributions"]}
    return by_id["irene_pass1"]["lesson_plan"], by_id["cd"]["cd_directive"]


def _contribution(specialist_id: str, output: dict, node_id: str | None = None):
    return SpecialistContribution.from_output(
        specialist_id=specialist_id, output=output, model_used="gpt-5-nano", node_id=node_id
    )


def _envelope() -> ProductionEnvelope:
    lesson_plan, cd_directive = _fixture_outputs()
    env = ProductionEnvelope(trial_id=TRIAL_ID)
    env.add_contribution(_contribution("irene_pass1", {"lesson_plan": lesson_plan}, node_id="04A"))
    env.add_contribution(_contribution("cd", {"cd_directive": cd_directive}, node_id="4.75"))
    return env


def _write_card(run_dir: Path, *, lo_sentinel: str | None = None) -> None:
    card = json.loads(CARD_FIXTURE.read_text(encoding="utf-8"))
    if lo_sentinel is not None:
        card["provisional_los"][0]["statement"] = lo_sentinel
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / ec.ENRICHMENT_CARD_BASENAME).write_text(json.dumps(card), encoding="utf-8")


# --------------------------------------------------------------------------- #
# B1 — sentinel LO statement reaches additional_instructions verbatim.
# --------------------------------------------------------------------------- #
def test_b1_sentinel_in_additional_instructions(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(DECK_FLAG, "1")
    run_dir = tmp_path / str(TRIAL_ID)
    _write_card(run_dir, lo_sentinel=SENTINEL_LO)
    updated = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    )
    package = updated.get_contribution("package_builder", node_id="06").output
    assert SENTINEL_LO in package["additional_instructions"]
    # No new payload key — the hint rides additional_instructions (Ratchet-D safe).
    assert set(package) == {"slides", "prompt", "additional_instructions"}


def test_b1_sentinel_reaches_per_variant_directive(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(DECK_FLAG, "1")
    run_dir = tmp_path / str(TRIAL_ID)
    _write_card(run_dir, lo_sentinel=SENTINEL_LO)
    updated = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    )
    package = updated.get_contribution("package_builder", node_id="06").output
    directive = gary_act._instructions_for_variant(
        package, variant="A", settings=dict(gary_act.DEFAULT_VARIANT_PAIR[0])
    )
    assert SENTINEL_LO in directive


# --------------------------------------------------------------------------- #
# GARY-A1 (firewall) — hint NEVER enters the card body or the Studio lock.
# --------------------------------------------------------------------------- #
def test_gary_a1_hint_absent_from_card_body_and_studio(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(DECK_FLAG, "1")
    run_dir = tmp_path / str(TRIAL_ID)
    _write_card(run_dir, lo_sentinel=SENTINEL_LO)
    updated = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    )
    package = updated.get_contribution("package_builder", node_id="06").output
    slides = package["slides"]
    # The card body (text_mode="preserve" input_text) NEVER carries the hint.
    body = gary_act._input_text(slides, package)
    assert SENTINEL_LO not in body
    # The Studio lock-and-replace prompt NEVER carries the hint (it reads only the
    # slide subject + the frozen wrapper, never additional_instructions).
    studio_prompt = gary_act._STUDIO_LOCK_WRAPPER.format(
        slide_content=gary_act._studio_slide_content(slides[0], 1)
    )
    assert SENTINEL_LO not in studio_prompt


def test_studio_prompt_byte_identical_with_or_without_hint(tmp_path: Path) -> None:
    # The Studio path no-ops the hint: the per-slide prompt is identical whether or
    # not additional_instructions carries the enrichment hint.
    lesson_plan, cd_directive = _fixture_outputs()
    plain = build_gary_briefs(lesson_plan, cd_directive)
    hinted = build_gary_briefs(lesson_plan, cd_directive, enrichment_hint="[g0-enrichment] X.")
    slide = plain["slides"][0]
    p_plain = gary_act._STUDIO_LOCK_WRAPPER.format(
        slide_content=gary_act._studio_slide_content(slide, 1)
    )
    p_hint = gary_act._STUDIO_LOCK_WRAPPER.format(
        slide_content=gary_act._studio_slide_content(hinted["slides"][0], 1)
    )
    assert p_plain == p_hint


# --------------------------------------------------------------------------- #
# B2 — card-absent / flag-OFF ⇒ directive byte-identical; guards untouched.
# --------------------------------------------------------------------------- #
def test_b2_card_absent_directive_byte_identical(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(DECK_FLAG, "1")  # flag ON but NO card on disk
    baseline = run_builder_node(
        node_id="06", production_envelope=_envelope()
    ).get_contribution("package_builder", node_id="06").output
    with_runs = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    ).get_contribution("package_builder", node_id="06").output
    assert with_runs["additional_instructions"] == baseline["additional_instructions"]


def test_b2_flag_off_directive_byte_identical(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(DECK_FLAG, raising=False)  # flag OFF, card present
    _write_card(tmp_path / str(TRIAL_ID), lo_sentinel=SENTINEL_LO)
    baseline = build_gary_briefs(*_fixture_outputs())
    gated = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    ).get_contribution("package_builder", node_id="06").output
    assert gated["additional_instructions"] == baseline["additional_instructions"]
    assert SENTINEL_LO not in gated["additional_instructions"]


def test_b2_gamma_settings_and_studio_guards_object_equal_by_name() -> None:
    # Regression pins by name: the proven deck defaults are untouched by Step 6.
    assert gary_act.DEFAULT_VARIANT_PAIR[0]["text_mode"] == "preserve"
    assert gary_act.DEFAULT_VARIANT_PAIR[1]["text_mode"] == "preserve"
    assert [v["variant_id"] for v in gary_act.DEFAULT_VARIANT_PAIR] == ["A", "B"]
    assert gary_act._STUDIO_LOCK_WRAPPER.startswith("LOCK THE DESIGN.")
    assert "{slide_content}" in gary_act._STUDIO_LOCK_WRAPPER


# --------------------------------------------------------------------------- #
# A6 — both-walks: a FRESH envelope (resume/recover) finds the on-disk card.
# --------------------------------------------------------------------------- #
def test_a6_continuation_walk_finds_card(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(DECK_FLAG, "1")
    run_dir = tmp_path / str(TRIAL_ID)
    _write_card(run_dir, lo_sentinel=SENTINEL_LO)
    # Simulate the resume/recover walk: a brand-new ProductionEnvelope (the §06
    # contribution was not carried) rebuilds the package and must still find the
    # g0-enrichment.json written on the earlier (start) walk.
    resumed = run_builder_node(
        node_id="06", production_envelope=_envelope(), runs_root=tmp_path, trial_id=TRIAL_ID
    )
    package = resumed.get_contribution("package_builder", node_id="06").output
    assert SENTINEL_LO in package["additional_instructions"]


def test_a6_load_enrichment_result_reads_disk_artifact(tmp_path: Path) -> None:
    # The consumer's loader reads the on-disk artifact (not an envelope contribution),
    # so it is available on whichever walk reaches the consumer.
    from app.marcus.orchestrator import g0_enrichment_wiring

    run_dir = tmp_path / str(TRIAL_ID)
    assert g0_enrichment_wiring.load_enrichment_result(run_dir) is None  # absent pre-write
    _write_card(run_dir, lo_sentinel=SENTINEL_LO)
    card = g0_enrichment_wiring.load_enrichment_result(run_dir)
    assert card is not None
    assert any(lo.get("statement") == SENTINEL_LO for lo in card["provisional_los"])

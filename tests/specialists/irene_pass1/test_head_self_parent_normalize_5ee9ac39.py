"""Spec 38-3a: normalize self-referential parent_slide_id on HEAD units.

Frozen negative witness: governed live trial 5ee9ac39-347b-485e-bcab-81928f8d4379
paused at node 04A with ``[irene-pass1.authority-invalid] head unit u01 must not
carry parent_slide_id`` — the live model stamped every HEAD with its OWN unit_id
as ``parent_slide_id`` (u01->u01 ... u06->u06) while emitting perfectly-formed
interstitials (u03i1/u03i2 -> u03). The fix lives at the deterministic
reconciliation seam (``normalize_clusters`` Pass 2 head branch): pop the key
when a head's parent is empty/whitespace or stripped-equal to its RAW unit_id.
``_validate_cluster_authority`` stays exactly as strict (no loosening).

Pins the spec's I/O & edge-case matrix rows plus T4-review boundary cases
(predicate type-guards, positional-fallback discrimination, unit_id-side
whitespace); the INITIAL-pass seam only — the refinement-identity path is a
filed follow-on (deferred-work). Cluster-topology fields below are lifted
VERBATIM from the witness raw_response (the run dir is read-only evidence);
source authority is re-bound to a synthetic span catalog via
``build_pass1_source_span_catalog`` (the amendment6 pattern — the raw digests
bind the live run's source bytes, which tests must not depend on).

No network/LLM calls.
"""

from __future__ import annotations

from copy import deepcopy

import pytest

from app.marcus.lesson_plan.pass1_authority import (
    SCHEMA_VERSION,
    Pass1PlanAuthorityError,
    finalize_plan_authority,
)
from app.marcus.lesson_plan.pass1_source_span_catalog import (
    build_pass1_source_span_catalog,
)
from app.marcus.lesson_plan.slide_authority import canonical_source_content_digest
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.specialists.irene_pass1 import _act as pass1_act

# --------------------------------------------------------------------------- #
# Witness topology — cluster fields verbatim from trial 5ee9ac39 raw_response  #
# (6 self-parent heads + 2 well-formed interstitials under u03).               #
# --------------------------------------------------------------------------- #
_ARC_U01 = (
    "From clinic-level assumptions to enterprise-level awareness through "
    "economic and structural evidence."
)
_ARC_U02 = (
    "From recognizing inefficiency to seeing redesign opportunities through "
    "waste and burnout evidence."
)
_ARC_U03 = (
    "From static-training assumptions to active technology stewardship through "
    "evidence of accelerating knowledge and tool adoption."
)
_ARC_U04 = (
    "From passive-care assumptions to designed consumer journeys through "
    "digital access expectations and examples."
)
_ARC_U05 = (
    "From leadership interest to leadership necessity through evidence of the "
    "training gap and translational need."
)
_ARC_U06 = (
    "From fragmented trends to a unified case for clinician-led change through "
    "concise synthesis and learner activation."
)

_LIVE_TOPOLOGY: tuple[dict[str, object], ...] = (
    {
        "unit_id": "u01",
        "cluster_id": "c-u01",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": "u01",  # live self-parent defect, verbatim
        "narrative_arc": _ARC_U01,
        "master_behavioral_intent": "credible",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u02",
        "cluster_id": "c-u02",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": "u02",
        "narrative_arc": _ARC_U02,
        "master_behavioral_intent": "alarming",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u03",
        "cluster_id": "c-u03",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": "u03",
        "narrative_arc": _ARC_U03,
        "master_behavioral_intent": "credible",
        "develop_type": None,
        "cluster_interstitial_count": 2,
        "scope_decision": "in-scope",
        "fidelity": "creative",
    },
    {
        "unit_id": "u03i1",
        "cluster_id": "c-u03",
        "cluster_role": "interstitial",
        "cluster_position": "tension",
        "parent_slide_id": "u03",  # well-formed, must stay untouched
        "narrative_arc": _ARC_U03,
        "master_behavioral_intent": "credible",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u03i2",
        "cluster_id": "c-u03",
        "cluster_role": "interstitial",
        "cluster_position": "develop",
        "parent_slide_id": "u03",
        "narrative_arc": _ARC_U03,
        "master_behavioral_intent": "credible",
        "develop_type": "exemplify",
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u04",
        "cluster_id": "c-u04",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": "u04",
        "narrative_arc": _ARC_U04,
        "master_behavioral_intent": "clear-guidance",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u05",
        "cluster_id": "c-u05",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": "u05",
        "narrative_arc": _ARC_U05,
        "master_behavioral_intent": "provocative",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
    {
        "unit_id": "u06",
        "cluster_id": "c-u06",
        "cluster_role": "head",
        "cluster_position": "resolve",
        "parent_slide_id": "u06",
        "narrative_arc": _ARC_U06,
        "master_behavioral_intent": "clear-guidance",
        "develop_type": None,
        "cluster_interstitial_count": 0,
        "scope_decision": "in-scope",
        "fidelity": "literal-text",
    },
)

_HEAD_IDS = ("u01", "u02", "u03", "u04", "u05", "u06")
_INTERSTITIAL_IDS = ("u03i1", "u03i2")

# Synthetic source anchors (one distinct sentence per unit, all on one slide)
# so the e2e floor re-binds source authority without the live run's bytes.
_ANCHOR_BY_UNIT: dict[str, str] = {
    "u01": "Enterprise economics reshape clinic-level assumptions.",
    "u02": "Waste and burnout expose redesign opportunities.",
    "u03": "Knowledge doubling outpaces static training.",
    "u03i1": "Accelerating knowledge strains legacy curricula.",
    "u03i2": "Tool adoption illustrates active technology stewardship.",
    "u04": "Consumer journeys demand designed digital access.",
    "u05": "Leadership training gaps create translational need.",
    "u06": "Clinician-led change unifies fragmented trends.",
}
_SOURCE_TEXT = " ".join(
    _ANCHOR_BY_UNIT[unit["unit_id"]] for unit in _LIVE_TOPOLOGY
)


def _source_sections() -> tuple[Pass1AuthenticatedSourceSection, ...]:
    digest = canonical_source_content_digest(_SOURCE_TEXT)
    return (
        Pass1AuthenticatedSourceSection(
            source_id=f"slides/slide-5-training.md|{digest}",
            source_content_digest=digest,
            extracted_content_digest=canonical_extracted_content_digest(_SOURCE_TEXT),
            body=_SOURCE_TEXT,
        ),
    )


def _live_plan() -> dict[str, object]:
    """The witness cluster topology with re-bound synthetic source authority."""
    sections = _source_sections()
    catalog = build_pass1_source_span_catalog(sections)
    entry_by_text = {entry.text: entry for entry in catalog.entries}
    units: list[dict[str, object]] = []
    for topology in _LIVE_TOPOLOGY:
        unit = deepcopy(topology)
        entry = entry_by_text[_ANCHOR_BY_UNIT[str(unit["unit_id"])]]
        unit["source_ref_ids"] = [entry.span_id]
        unit["source_refs"] = [entry.text]
        units.append(unit)
    return {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": units,
    }


def _legacy_plan(*units: dict[str, object]) -> dict[str, object]:
    """Minimal legacy-shape plan (no v2 catalog plumbing) for seam pins."""
    return {"plan_units": [deepcopy(unit) for unit in units]}


def _head(unit_id: str, **overrides: object) -> dict[str, object]:
    unit: dict[str, object] = {
        "unit_id": unit_id,
        "cluster_id": f"c-{unit_id}",
        "cluster_role": "head",
        "cluster_position": "establish",
        "scope_decision": "out-of-scope",
    }
    unit.update(overrides)
    return unit


def _interstitial(unit_id: str, parent: object, **overrides: object) -> dict[str, object]:
    unit: dict[str, object] = {
        "unit_id": unit_id,
        "cluster_id": f"c-{unit_id}",
        "cluster_role": "interstitial",
        "cluster_position": "develop",
        "parent_slide_id": parent,
        "scope_decision": "out-of-scope",
    }
    unit.update(overrides)
    return unit


def _by_id(plan: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(unit["unit_id"]): unit for unit in plan["plan_units"]}


# --------------------------------------------------------------------------- #
# Matrix row 1 — the live 5ee9ac39 shape: heads normalize to KEY-ABSENT,       #
# interstitials untouched, finalize_plan_authority passes end-to-end.          #
# --------------------------------------------------------------------------- #
def test_live_shape_normalizes_heads_and_authority_finalizes() -> None:
    plan = _live_plan()
    normalized = pass1_act.normalize_clusters(plan)
    units = _by_id(normalized)

    for head_id in _HEAD_IDS:
        assert "parent_slide_id" not in units[head_id], head_id
        assert units[head_id]["cluster_role"] == "head"
        assert units[head_id]["cluster_id"] == f"c-{head_id}"
    for inter_id in _INTERSTITIAL_IDS:
        assert units[inter_id]["cluster_role"] == "interstitial"
        assert units[inter_id]["parent_slide_id"] == "u03"
        assert units[inter_id]["cluster_id"] == "c-u03"
        assert units[inter_id]["narrative_arc"] == _ARC_U03
    assert units["u03"]["cluster_interstitial_count"] == 2

    receipt = finalize_plan_authority(
        normalized, source_sections=_source_sections()
    )
    assert receipt["schema_version"] == SCHEMA_VERSION
    rows = {row["unit_id"]: row for row in receipt["identities"]}
    for head_id in _HEAD_IDS:
        assert rows[head_id]["parent_slide_id"] is None
    for inter_id in _INTERSTITIAL_IDS:
        assert rows[inter_id]["parent_slide_id"] == "u03"


def test_live_shape_without_normalization_red_rejects_exactly_as_witnessed() -> None:
    """The frozen negative witness: raw shape must still red-reject unfixed."""
    with pytest.raises(
        Pass1PlanAuthorityError, match="head unit u01 must not carry parent_slide_id"
    ):
        finalize_plan_authority(_live_plan(), source_sections=_source_sections())


def test_normalize_is_pure_and_idempotent_on_live_shape() -> None:
    plan = _live_plan()
    pristine = deepcopy(plan)
    once = pass1_act.normalize_clusters(plan)
    assert plan == pristine, "normalize_clusters must not mutate its input"
    assert pass1_act.normalize_clusters(once) == once


# --------------------------------------------------------------------------- #
# Matrix rows 2-3 — whitespace-padded self parent and empty/whitespace parent  #
# on a head normalize (stripped-equality predicate); authority passes.         #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("parent", [" u01 ", "u01 ", "\tu01"])
def test_whitespace_padded_self_parent_normalizes(parent: str) -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id=parent))
    normalized = pass1_act.normalize_clusters(plan)
    assert "parent_slide_id" not in normalized["plan_units"][0]
    receipt = finalize_plan_authority(normalized, source_sections=())
    assert receipt["identities"][0]["parent_slide_id"] is None


@pytest.mark.parametrize("parent", ["", "  ", " \t "])
def test_empty_or_whitespace_parent_on_head_normalizes(parent: str) -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id=parent))
    normalized = pass1_act.normalize_clusters(plan)
    assert "parent_slide_id" not in normalized["plan_units"][0]
    receipt = finalize_plan_authority(normalized, source_sections=())
    assert receipt["identities"][0]["parent_slide_id"] is None


# --------------------------------------------------------------------------- #
# Matrix rows 4-7 — anything that is NOT unambiguously self-referential stays  #
# put and remains fail-loud at the (unchanged) validator.                      #
# --------------------------------------------------------------------------- #
def test_ambiguous_head_parent_not_normalized_and_fail_loud() -> None:
    plan = _legacy_plan(_head("u01"), _head("u02", parent_slide_id="u01"))
    normalized = pass1_act.normalize_clusters(plan)
    assert _by_id(normalized)["u02"]["parent_slide_id"] == "u01"
    with pytest.raises(
        Pass1PlanAuthorityError, match="head unit u02 must not carry parent_slide_id"
    ):
        finalize_plan_authority(normalized, source_sections=())


def test_case_differing_self_parent_not_normalized_and_fail_loud() -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id="U01"))
    normalized = pass1_act.normalize_clusters(plan)
    assert normalized["plan_units"][0]["parent_slide_id"] == "U01"
    with pytest.raises(
        Pass1PlanAuthorityError, match="head unit u01 must not carry parent_slide_id"
    ):
        finalize_plan_authority(normalized, source_sections=())


def test_non_string_parent_not_normalized_and_fail_loud() -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id=1))
    normalized = pass1_act.normalize_clusters(plan)
    assert normalized["plan_units"][0]["parent_slide_id"] == 1
    with pytest.raises(
        Pass1PlanAuthorityError, match="head unit u01 must not carry parent_slide_id"
    ):
        finalize_plan_authority(normalized, source_sections=())


def test_head_parent_equal_to_cluster_id_not_normalized_and_fail_loud() -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id="c-u01"))
    normalized = pass1_act.normalize_clusters(plan)
    assert normalized["plan_units"][0]["parent_slide_id"] == "c-u01"
    with pytest.raises(
        Pass1PlanAuthorityError, match="head unit u01 must not carry parent_slide_id"
    ):
        finalize_plan_authority(normalized, source_sections=())


# --------------------------------------------------------------------------- #
# Matrix row 8 — interstitial self-parent at the VALIDATOR seam (raw units fed #
# DIRECTLY to finalize_plan_authority, bypassing reconciliation): the          #
# validator's strictness is unchanged (party W1/M-F1/A-F2).                    #
# --------------------------------------------------------------------------- #
def test_interstitial_self_parent_validator_seam_red_rejects() -> None:
    plan = _legacy_plan(
        _head("u01"),
        _interstitial("u02", "u02", cluster_id="c-u01"),
    )
    with pytest.raises(
        Pass1PlanAuthorityError,
        match="interstitial unit u02 has invalid parent authority",
    ):
        finalize_plan_authority(plan, source_sections=())


# --------------------------------------------------------------------------- #
# Matrix row 9 — interstitial self-parent at the RECONCILIATION seam: Pass 3   #
# resolve-or-demote exactly as today (pinned AS-IS; this fix must not touch    #
# interstitial handling — never silently corrupt into a wrong parent).         #
# --------------------------------------------------------------------------- #
def test_interstitial_self_parent_with_matching_head_cluster_resolves_to_head() -> None:
    plan = _legacy_plan(
        _head("h1"),
        _interstitial("i1", "i1", cluster_id="c-h1"),
    )
    normalized = pass1_act.normalize_clusters(plan)
    resolved = _by_id(normalized)["i1"]
    assert resolved["cluster_role"] == "interstitial"
    assert resolved["parent_slide_id"] == "h1"
    assert resolved["cluster_id"] == "c-h1"


def test_interstitial_self_parent_with_no_resolvable_head_demotes_to_singleton() -> None:
    plan = _legacy_plan(
        _head("h1"),
        _interstitial("i1", "i1"),  # own cluster_id, no matching head cluster
    )
    normalized = pass1_act.normalize_clusters(plan)
    demoted = _by_id(normalized)["i1"]
    assert demoted["cluster_role"] == "head"
    assert "parent_slide_id" not in demoted
    assert demoted["cluster_id"] != _by_id(normalized)["h1"]["cluster_id"]


# --------------------------------------------------------------------------- #
# Matrix row 10 — today's happy path is byte-identical: a head with            #
# parent_slide_id None (or key absent) is untouched by the new branch.         #
# --------------------------------------------------------------------------- #
def test_head_with_none_parent_stays_none_and_passes_authority() -> None:
    plan = _legacy_plan(_head("u01", parent_slide_id=None))
    normalized = pass1_act.normalize_clusters(plan)
    unit = normalized["plan_units"][0]
    assert "parent_slide_id" in unit
    assert unit["parent_slide_id"] is None
    receipt = finalize_plan_authority(normalized, source_sections=())
    assert receipt["identities"][0]["parent_slide_id"] is None


def test_head_with_absent_parent_key_stays_absent() -> None:
    plan = _legacy_plan(_head("u01"))
    normalized = pass1_act.normalize_clusters(plan)
    assert "parent_slide_id" not in normalized["plan_units"][0]
    receipt = finalize_plan_authority(normalized, source_sections=())
    assert receipt["identities"][0]["parent_slide_id"] is None


# --------------------------------------------------------------------------- #
# Prompt hardening (party J-B, additive only): heads told to OMIT the key.     #
# --------------------------------------------------------------------------- #
def test_prompt_clarifies_heads_omit_parent_slide_id() -> None:
    instructions = pass1_act._cluster_emission_instructions()
    assert "HEAD units must OMIT parent_slide_id" in instructions
    # The original interstitial guidance line is untouched (additive change).
    assert '"parent_slide_id":"<head unit_id>",   // interstitials only' in instructions


# --------------------------------------------------------------------------- #
# T4 review — predicate type-guards + fallback discrimination (Blind/Edge)    #
# --------------------------------------------------------------------------- #


def test_missing_unit_id_with_none_string_parent_stays_and_fails_loud() -> None:
    """`str(None) == "None"` must never manufacture a self-reference match: a
    head with NO unit_id and parent `"None"` keeps its parent and red-rejects."""
    unit = _head("placeholder", parent_slide_id="None")
    del unit["unit_id"]
    plan = _legacy_plan(unit, _head("u02"))
    normalized = pass1_act.normalize_clusters(plan)
    kept = [u for u in normalized["plan_units"] if u.get("unit_id") != "u02"][0]
    assert kept.get("parent_slide_id") == "None"
    # Fail-loud is preserved — the blank-id gate fires first, before any
    # parent-authority check could be reached; the parent was never stripped.
    with pytest.raises(Pass1PlanAuthorityError, match="blank or duplicate unit_id"):
        finalize_plan_authority(normalized, source_sections=())


def test_non_string_unit_id_never_matches_its_string_form() -> None:
    """`unit_id=1` with parent `"1"` is a type-mismatched claim, not a
    self-reference — parent stays and the plan red-rejects downstream."""
    unit = _head("placeholder", parent_slide_id="1")
    unit["unit_id"] = 1
    plan = _legacy_plan(unit, _head("u02"))
    normalized = pass1_act.normalize_clusters(plan)
    kept = [u for u in normalized["plan_units"] if u.get("unit_id") == 1][0]
    assert kept.get("parent_slide_id") == "1"


def test_blank_unit_id_with_positional_fallback_parent_stays_put() -> None:
    """Discriminating `_uid()` pin: a head with a BLANK unit_id whose parent
    happens to equal the positional fallback id must NOT normalize — the
    predicate compares the raw unit_id only, never `_uid(unit, idx)`."""
    unit = _head("placeholder", parent_slide_id="u0")
    unit["unit_id"] = ""
    plan = _legacy_plan(unit, _head("u02"))
    normalized = pass1_act.normalize_clusters(plan)
    kept = [u for u in normalized["plan_units"] if u.get("parent_slide_id") == "u0"]
    assert len(kept) == 1  # parent survived normalization


def test_whitespace_padded_unit_id_side_also_normalizes() -> None:
    """Both sides are stripped: unit_id `" u01 "` with parent `"u01"` is a
    self-reference and normalizes (pins the two-sided strip in the code)."""
    unit = _head(" u01 ", parent_slide_id="u01")
    plan = _legacy_plan(unit, _head("u02"))
    normalized = pass1_act.normalize_clusters(plan)
    kept = [u for u in normalized["plan_units"] if u.get("unit_id") == " u01 "][0]
    assert "parent_slide_id" not in kept


def test_normalization_warns_observably_when_it_fires(caplog) -> None:
    """T4: the scrub is OBSERVABLE (sibling FIX-1 discipline) — a run where the
    live model tics must be distinguishable from a clean run in the logs."""
    import logging

    with caplog.at_level(logging.WARNING, logger=pass1_act.__name__):
        pass1_act.normalize_clusters(_legacy_plan(_head("u01", parent_slide_id="u01")))
    assert any(
        "stripping self-referential parent_slide_id" in r.getMessage()
        for r in caplog.records
    )

"""Story Q3.4 — calibration signal reader + cross-dimensional integration (hermetic + real).

The calibration dimension (the 8th and FINAL — closing it closes the whole scorecard) REPORTS the
recorded calibration posture of the reading-path neck. CAL1 is ``signal-derived`` + REPORT-ONLY:

  * CAL1 (``reading_path_calibration_signal``) — reads the RECORDED posture and reports whether a
    fresh-naive-holdout MEASUREMENT exists for the reading-path neck: it does NOT (OWED/unmeasured —
    the owed epic ``reading-path-fresh-naive-holdout-pre-trial`` = DID Leak-4) →
    ``reading_path_calibrated`` False → ``weak`` (an owed/unmeasured neck scored UNCALIBRATED, NOT
    passing). It keys off the REAL owed-state, NOT the presence of a resubstitution number
    (resubstitution ≠ calibrated). The single pinned resubstitution fact (subject=built-classifier,
    substrate=fresh@2026-06-23, primary-key 0.071/14 on the consumed-14) is surfaced as LABELED
    evidence of what WAS run — ``measurement_kind='resubstitution/upper-bound'`` +
    ``is_generalization=False`` — NEVER a generalization, NEVER a fresh-naive number.

⛔ REPORT-ONLY: this reads the RECORDED posture as PLAIN DATA — it NEVER builds the fresh-naive-
holdout harness, runs a measurement, or fabricates a fresh number (that stays the owed epic). No
live-network / paid calls. Fail-soft: nothing-checkable → ``unavailable``, NEVER calibrated.

This module covers: the reader against the REAL recorded posture (uncalibrated/owed → weak) + a
hermetic fixture where a fresh-holdout measurement EXISTS (→ can improve — the close-path); the
consult-real-owed-state / nothing-checkable→unavailable discipline; the isolating pin (owed-state vs
resubstitution-present); the resubstitution-as-labeled-evidence-not-generalization guarantee; the
signal→level derivation; the calibration leak-count reader; the cross-dimensional GL-13 interleave
(the 8th dimension); and the deterministic projector picking up the 8th dimension with NO projector
change. The honesty-pin RED-under-seeded proofs live in ``test_scorecard_honesty_pins``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _CALIBRATION_KEY, read_scorecard_block
from app.quality.signals import (
    calibration_leak_count_signal,
    level_from_signal,
    reading_path_calibration_signal,
)

_CLEAN = {"strong", "uniform"}
_CAL1_KEY = "reading_path_calibration_posture"
_DID_KEY = "dynamic_intelligence_vs_determinism"
_COST_KEY = "cost_efficiency"
_COVERAGE_KEY = "coverage_honesty"
_FIDELITY_KEY = "fidelity_trust"
_CAPABILITY_KEY = "capability_honesty"
_TRACKER_KEY = "tracker_coherence"
_LANE_KEY = "lane_discipline"


# =========================== CAL1 — the recorded posture (real) ================= #


def test_cal1_real_recorded_posture_is_uncalibrated_weak() -> None:
    """Real posture: the reading-path neck's fresh-naive holdout is OWED/UNMEASURED
    (``fresh_naive_holdout_measured`` False) → ``reading_path_calibrated`` False → uncalibrated →
    ``weak``. This is the honest baseline (the reading-path is uncalibrated, the holdout owed).
    """
    sig = reading_path_calibration_signal()
    assert sig["status"] == "ok"
    assert sig["fresh_naive_holdout_measured"] is False
    assert sig["reading_path_calibrated"] is False
    assert sig["calibration_status"] == "uncalibrated"
    assert level_from_signal(_CAL1_KEY, sig) == "weak"
    assert level_from_signal(_CAL1_KEY, sig) not in _CLEAN


def test_cal1_is_report_only_reads_recorded_posture_no_measurement() -> None:
    """⛔ REPORT-ONLY: the reader reads the RECORDED posture as plain data — it takes no measurement
    input and produces the same owed/uncalibrated read deterministically (no live run, no cost)."""
    a = reading_path_calibration_signal()
    b = reading_path_calibration_signal()
    assert a == b  # deterministic plain-data read
    # the owed epic (DID Leak-4):
    assert a["owed_epic"] == "reading-path-fresh-naive-holdout-pre-trial"


def test_cal1_surfaces_resubstitution_as_labeled_evidence_not_generalization() -> None:
    """The single pinned resubstitution fact is surfaced as LABELED evidence of what WAS run —
    ``measurement_kind='resubstitution/upper-bound'`` + ``is_generalization=False`` — NEVER a
    generalization and NEVER a fresh-naive number. Mary's ``(subject, substrate@date)`` citation
    rides every reading-path number."""
    resub = reading_path_calibration_signal()["resubstitution_evidence"]
    assert resub["subject"] == "built-classifier (S1/S2/S3)"
    assert resub["substrate"] == "fresh@2026-06-23"
    assert resub["dataset"] == "consumed-14"
    assert resub["measurement_kind"] == "resubstitution/upper-bound"
    assert resub["is_generalization"] is False
    assert abs(resub["primary_key_top1"] - 1 / 14) < 1e-9  # 0.071 (1/14)
    assert resub["report"] == "honest-built-classifier-measurement.json"


# =========================== CAL1 — seeded posture (close-path / isolating) ===== #


def test_cal1_close_path_reachable_when_fresh_holdout_recorded() -> None:
    """The close-path is REACHABLE and REPORT-ONLY: a SEEDED posture where a fresh-naive-holdout
    MEASUREMENT is recorded (``fresh_naive_holdout_measured`` True) → calibrated → ``strong`` (the
    reader detects it; the pin never blocks the honest upgrade). Seeded, NOT a measurement."""
    recorded = reading_path_calibration_signal({"fresh_naive_holdout_measured": True})
    assert recorded["reading_path_calibrated"] is True
    assert recorded["calibration_status"] == "calibrated"
    assert level_from_signal(_CAL1_KEY, recorded) == "strong"


def test_cal1_isolating_owed_state_not_resubstitution_presence() -> None:
    """The isolating pin (Q2.3 FT2 / Q3.1 CH1 lesson): HOLD the resubstitution fact present, VARY
    the owed-state. A resubstitution number present + fresh holdout OWED → ``weak`` (uncalibrated);
    the SAME resubstitution present + fresh holdout measured → ``strong``. A declared-count / raw
    'a resubstitution number exists' reader would say strong for both — the real reader consults the
    owed-state and keeps the owed one weak (resubstitution ≠ calibrated)."""
    resub = {"subject": "built-classifier (S1/S2/S3)", "substrate": "fresh@2026-06-23",
             "primary_key_top1": 1 / 14, "measurement_kind": "resubstitution/upper-bound"}
    owed = reading_path_calibration_signal(
        {"fresh_naive_holdout_measured": False, "resubstitution": resub}
    )
    measured = reading_path_calibration_signal(
        {"fresh_naive_holdout_measured": True, "resubstitution": resub}
    )
    # a resubstitution number does not calibrate:
    assert level_from_signal(_CAL1_KEY, owed) == "weak"
    assert level_from_signal(_CAL1_KEY, measured) == "strong"


def test_cal1_nothing_checkable_is_unavailable_never_calibrated() -> None:
    """Consult-real-owed-state / nothing-checkable→unavailable: a posture missing the owed-state (or
    a non-bool owed-state), or a non-mapping posture, degrades to ``unavailable`` — NEVER a
    false-calibrated. A resubstitution number alone can NEVER stand in for a fresh-naive read.
    """
    # missing fresh_naive_holdout_measured (only a resubstitution number present) → unavailable.
    only_resub = reading_path_calibration_signal({"resubstitution": {"primary_key_top1": 0.99}})
    assert only_resub["status"] == "unavailable"
    assert level_from_signal(_CAL1_KEY, only_resub) == "unavailable"
    # non-bool owed-state → unavailable.
    assert reading_path_calibration_signal({"fresh_naive_holdout_measured": "yes"})[
        "status"
    ] == "unavailable"
    # non-mapping posture → unavailable.
    assert reading_path_calibration_signal("garbage")["status"] == "unavailable"
    assert level_from_signal(_CAL1_KEY, reading_path_calibration_signal([1, 2])) == "unavailable"


# =========================== signal→level totals ============================== #


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "reading_path_calibrated": False}, "weak"),
        ({"status": "ok", "reading_path_calibrated": True}, "strong"),
        ({"status": "ok", "reading_path_calibrated": "yes"}, "unavailable"),
        ({"status": "ok"}, "unavailable"),  # missing owed-state
        ({"status": "unavailable"}, "unavailable"),
        ({}, "unavailable"),
        ("garbage", "unavailable"),
    ],
)
def test_cal1_level_totals(sig: Any, expected: str) -> None:
    """CAL1 returns a real level for every signal and never awards a clean level on a non-ok /
    malformed / nothing-checkable signal (resubstitution can never award calibrated)."""
    got = level_from_signal(_CAL1_KEY, sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


def test_band_ceiling_is_b() -> None:
    """The single signal-derived criterion caps at ``strong`` (3) mechanically — ``level_from_
    signal`` never awards ``uniform``/4. Max = 3/4 = 75 → Band B. Today OWED → weak → 1/4 = 25 → D.
    """
    recorded = reading_path_calibration_signal({"fresh_naive_holdout_measured": True})
    assert level_from_signal(_CAL1_KEY, recorded) == "strong"  # never 'uniform'
    assert round(3 / 4 * 100) == 75  # → Band B (A unreachable)
    assert round(1 / 4 * 100) == 25  # today (OWED) → Band D


def test_cal1_criterion_is_signal_derived_in_the_block() -> None:
    """CAL1 carries ``derivation: signal-derived`` with a real reader + evidence_ref, and
    ``level_from_signal`` returns a real level (not None)."""
    crit = read_scorecard_block()["dimensions"][_CALIBRATION_KEY]["criteria"]
    assert set(crit) == {_CAL1_KEY}
    c = crit[_CAL1_KEY]
    assert c["derivation"] == "signal-derived"
    assert c["signal"]["reader"] == "app.quality.signals.reading_path_calibration_signal"
    assert isinstance(c["evidence_ref"], str) and c["evidence_ref"]
    assert level_from_signal(_CAL1_KEY, reading_path_calibration_signal()) is not None


# =========================== calibration leak-count reader ==================== #


def test_calibration_leak_count_real_repo_is_one() -> None:
    """The real repo carries 1 ``cal_leak:`` tag — the reading-path fresh-naive-holdout OWED gap
    (cross-links DID Leak-4). The reader returns a clean ``1``."""
    sig = calibration_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["calibration_leak_count"] == 1


def test_calibration_leak_count_fixture(tmp_path: Path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Calibration Scorecard Leak Registry\n\n"
        "- cal_leak: alpha\n- cal_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- cal_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert calibration_leak_count_signal(p)["calibration_leak_count"] == 2


def test_calibration_leak_count_ignores_other_namespaces(tmp_path: Path) -> None:
    """The ``cal_leak:`` reader must NOT count the other seven namespaces."""
    doc = (
        "## Calibration Scorecard Leak Registry\n\n"
        "- cal_leak: only-this\n"
        "- did_leak: nope\n- cost_leak: nope\n- cov_leak: nope\n- fid_leak: nope\n"
        "- cap_leak: nope\n- trk_leak: nope\n- lane_leak: nope\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert calibration_leak_count_signal(p)["calibration_leak_count"] == 1


def test_calibration_leak_count_zero_when_registry_empty(tmp_path: Path) -> None:
    """A registry with NO ``cal_leak:`` line → count 0 — a clean ``0``, not ``unavailable`` (the
    zero-leak machinery path)."""
    doc = "## Calibration Scorecard Leak Registry\n\n(none open).\n"
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    sig = calibration_leak_count_signal(p)
    assert sig["status"] == "ok"
    assert sig["calibration_leak_count"] == 0


def test_calibration_leak_count_unavailable_on_unreadable_file(tmp_path: Path) -> None:
    """Fail-soft: an unreadable inventory path → ``{"status": "unavailable",
    "calibration_leak_count": None}`` (never a fabricated 0)."""
    missing = tmp_path / "does-not-exist.md"
    sig = calibration_leak_count_signal(missing)
    assert sig["status"] == "unavailable"
    assert sig["calibration_leak_count"] is None


# =========================== GL-13 cross-dimensional (closes the scorecard) ===== #


def test_calibration_leak_aggregates_into_shared_ranked_list() -> None:
    """GL-13 (CLOSES the scorecard): calibration's ONE learner-trust leak (reading-path OWED)
    aggregates into the ONE shared ranked list. EIGHT dimensions now contribute; the
    cross-dimensional total is 13 (5 DID + 1 cost + 1 cov + 1 fid + 1 cap + 2 tracker + 1 lane +
    1 calibration). The calibration leak is learner-trust (sorts after paid-walk, before gov).
    """
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    dims = {e["dimension"] for e in ranked}
    cal_slug = "calibration-reading-path-fresh-naive-holdout-owed"
    assert cal_slug in slugs
    assert ranked[slugs.index(cal_slug)]["lane"] == "learner-trust"
    assert dims == {
        _DID_KEY, _COST_KEY, _COVERAGE_KEY, _FIDELITY_KEY, _CAPABILITY_KEY, _TRACKER_KEY,
        _LANE_KEY, _CALIBRATION_KEY,
    }
    assert len(ranked) == 13  # the 8th (final) dimension adds its one learner-trust leak


def test_leak_coverage_clean_with_calibration_dimension() -> None:
    """The coverage guard stays clean: calibration declares ``open_leaks: 1`` AND carries a
    ``leaks`` list of length 1, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


def test_live_calibration_leak_count_identity_reconciles_at_one() -> None:
    """The live dimension's identity holds at 1: ``open_leaks`` == ``len(leaks)`` ==
    ``calibration_leak_count_signal()`` == 1 (the reading-path OWED gap)."""
    dim = read_scorecard_block()["dimensions"][_CALIBRATION_KEY]
    count = calibration_leak_count_signal()["calibration_leak_count"]
    assert dim["open_leaks"] == len(dim["leaks"]) == count == 1


# =========================== projector picks it up (no code change) — all 8 ==== #


def test_projector_renders_calibration_dimension_with_no_code_change() -> None:
    """AC5: ``render_scorecard_final_report`` picks up calibration automatically — its Band row, its
    per-criterion trace, its reading-path-OWED leak on the ranked list, and its ▬ baseline trend all
    render with NO projector change. This is the 8th and FINAL dimension — the projector renders all
    eight cleanly."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Calibration | D |" in out
    assert "| Calibration | ▬ baseline |" in out
    cal1_row = "| Calibration | reading_path_calibration_posture | weak | 1/4 |"
    assert cal1_row in out
    assert "calibration-reading-path-fresh-naive-holdout-owed" in out  # leak on ranked list
    assert "/100" not in out  # never a false-precise headline


def test_projector_renders_all_eight_dimensions() -> None:
    """CLOSES the scorecard: all eight dimension Band rows render in the final report (no projector
    change was needed to add the 8th)."""
    block = read_scorecard_block()
    out = render_scorecard_final_report(block=block, history=None, fence_state=None)
    for label in (
        "Dynamic Intelligence vs Determinism",
        "Cost-efficiency",
        "Coverage-honesty",
        "Fidelity-trust",
        "Capability-honesty",
        "Governance / tracker-coherence",
        "Lane-discipline / scope-fidelity",
        "Calibration",
    ):
        assert f"| {label} |" in out, f"missing Band row for {label!r}"

"""Story Q3.2 — tracker_coherence signal readers + cross-dimensional integration
(hermetic + real). No live calls, no ``--run-live``.

The tracker_coherence dimension is the ONLY FULLY-COMPUTED dimension (GL-7): BOTH criteria are
``signal-derived`` — there is NO hand-authored judgment level. It is scored ENTIRELY from the
EXISTING status-tracker qualifiers (GL-15 — reuse, no parallel plumbing), and BOTH signals are
DETERMINISTIC (post-review hardening):

  * TC1 (``tracker_coherence_signal``) — recomputes a STRUCTURAL coherence verdict from
    ``progress_map.qualify_sources()`` findings, EXCLUDING time-based staleness (FIX-B) so the
    level does not flap on wall-clock time; cross-checks a supplied verdict↔count (FIX-C).
  * TC2 (``tracker_doc_drift_signal``) — reads the STABLE code↔doc drift-MONITORING POSTURE
    (is ``doc_drift_monitor`` wired, and does it GATE production or is it advisory?) — it does
    NOT run git at read time (FIX-A): no per-commit flapping, no git-unavailable false-clean, no
    subprocess hang. Honest today: the monitor exists but is advisory (never gates) → weak.

This module covers: the readers against hermetic fixtures + the real repo; the consult-real-
signal / nothing-checked→unavailable discipline; determinism (staleness excluded; no read-time
git); the signal→level derivation (fully-computed); the cross-dimensional GL-13 interleave; the
⚠️ ZERO-LEAK-PATH lock-in; and the deterministic projector picking up the new dimension with NO
projector change. The honesty-pin RED-under-seeded proofs live in ``test_scorecard_honesty_pins``.

**⛔ READ-ONLY.** This dimension SCORES the tracker coherence; it CONSUMES ``qualify_sources`` /
``doc_drift_monitor`` read-only and NEVER edits a tracker or its tooling.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _TRACKER_KEY, read_scorecard_block
from app.quality.signals import (
    level_from_signal,
    tracker_coherence_signal,
    tracker_doc_drift_signal,
    tracker_leak_count_signal,
)

_CLEAN = {"strong", "uniform"}
_TC1_KEY = "tracker_divergence_coherence"
_TC2_KEY = "tracker_doc_drift"
_DID_KEY = "dynamic_intelligence_vs_determinism"
_COST_KEY = "cost_efficiency"
_COVERAGE_KEY = "coverage_honesty"
_FIDELITY_KEY = "fidelity_trust"
_CAPABILITY_KEY = "capability_honesty"


def _qresult(findings: list[tuple[str, str]]) -> dict[str, Any]:
    """Build a qualify_sources-shaped result (internally consistent) from ``(level, check)``
    pairs — mirrors ``progress_map.qualify_sources`` so seeded tests read a real shape."""
    errs = sum(1 for lvl, _ in findings if lvl == "error")
    warns = sum(1 for lvl, _ in findings if lvl == "warn")
    verdict = "FAIL" if errs else "DEGRADED" if warns else "CLEAN"
    return {
        "verdict": verdict,
        "error_count": errs,
        "warning_count": warns,
        "findings": [
            {"level": lvl, "check": chk, "source": "x", "message": "m"} for lvl, chk in findings
        ],
    }


def _wired_monitor(*, gates_production: Any = False) -> SimpleNamespace:
    """A ``doc_drift_monitor``-like module: the drift-check functions exist (monitoring wired);
    ``gates_production`` controls the gating posture (default advisory/False)."""
    ns = SimpleNamespace(
        check_documentation_drift=lambda *a, **k: None,
        get_changed_files=lambda: [],
    )
    if gates_production is not None:
        ns.gates_production = gates_production
    return ns


# =========================== TC1 — tracker-divergence coherence ================= #


def test_tc1_real_repo_is_structurally_degraded_partial() -> None:
    """Real posture: qualify_sources' STRUCTURAL verdict is DEGRADED today (the orphan_stories
    warning; time-based staleness excluded) → ``trackers_coherent`` False → ``partial``."""
    sig = tracker_coherence_signal()
    assert sig["status"] == "ok"
    assert sig["verdict"] == "DEGRADED"
    assert sig["error_count"] == 0
    assert sig["warning_count"] >= 1
    assert sig["divergence_count"] == sig["error_count"] + sig["warning_count"]
    assert sig["trackers_coherent"] is False
    assert level_from_signal(_TC1_KEY, sig) == "partial"


@pytest.mark.parametrize(
    ("findings", "expected_level"),
    [
        ([("ok", "exists")], "strong"),  # CLEAN structural → strong
        ([("warn", "orphan_stories")], "partial"),  # structural warning → partial
        ([("warn", "next_step_conflict"), ("warn", "headings")], "partial"),
        ([("error", "dev_status_key")], "weak"),  # structural error → weak
    ],
)
def test_tc1_structural_verdict_drives_level(
    findings: list[tuple[str, str]], expected_level: str
) -> None:
    """Fully-computed: the level derives ENTIRELY from the STRUCTURAL qualify_sources verdict —
    CLEAN→strong (the reachable close-path), DEGRADED→partial, FAIL→weak."""
    sig = tracker_coherence_signal(_qresult(findings))
    assert sig["status"] == "ok"
    assert level_from_signal(_TC1_KEY, sig) == expected_level
    if expected_level != "strong":
        assert level_from_signal(_TC1_KEY, sig) not in _CLEAN


def test_tc1_staleness_excluded_is_deterministic() -> None:
    """FIX-B (determinism): a TIME-BASED staleness / last_updated finding is EXCLUDED from the
    coherence verdict — a stale-but-structurally-coherent tracker set scores the SAME as a fresh
    one (``strong``). So the level cannot flip merely because time elapsed."""
    coherent = tracker_coherence_signal(_qresult([("ok", "exists")]))
    stale = tracker_coherence_signal(_qresult([("warn", "staleness")]))
    stale_last = tracker_coherence_signal(_qresult([("warn", "last_updated")]))
    assert level_from_signal(_TC1_KEY, coherent) == "strong"
    assert level_from_signal(_TC1_KEY, stale) == "strong"  # staleness excluded → still coherent
    assert level_from_signal(_TC1_KEY, stale_last) == "strong"
    # the raw (all-findings) verdict still surfaces the staleness as evidence (DEGRADED), but the
    # SCORED structural verdict is CLEAN — the exclusion is visible, not hidden.
    assert stale["raw_verdict"] == "DEGRADED" and stale["verdict"] == "CLEAN"


def test_tc1_staleness_plus_structural_still_scores_structural() -> None:
    """A staleness warning ALONGSIDE a structural warning scores the STRUCTURAL divergence
    (partial) — staleness neither inflates nor deflates the coherence level."""
    sig = tracker_coherence_signal(_qresult([("warn", "staleness"), ("warn", "orphan_stories")]))
    assert sig["verdict"] == "DEGRADED"  # structural (orphan_stories)
    assert sig["warning_count"] == 1  # structural count excludes staleness
    assert level_from_signal(_TC1_KEY, sig) == "partial"


@pytest.mark.parametrize(
    ("result", "label"),
    [
        (
            {"verdict": "CLEAN", "warning_count": 3,
             "findings": [{"level": "warn", "check": "orphan_stories"}] * 3},
            "CLEAN-with-warnings",
        ),
        (
            {"verdict": "DEGRADED", "error_count": 1,
             "findings": [{"level": "error", "check": "dev_status_key"}]},
            "DEGRADED-with-errors",
        ),
        ({"verdict": "CLEAN", "error_count": 5, "findings": []}, "count-contradicts-findings"),
    ],
)
def test_tc1_verdict_count_contradiction_is_unavailable(result: dict, label: str) -> None:
    """FIX-C: a supplied verdict / count that CONTRADICTS the findings tally is an unexpected /
    malformed shape → ``unavailable`` (never coerced to coherent/strong)."""
    sig = tracker_coherence_signal(result)
    assert sig["status"] == "unavailable", f"{label}: expected unavailable, got {sig}"
    assert "trackers_coherent" not in sig
    assert level_from_signal(_TC1_KEY, sig) == "unavailable"


@pytest.mark.parametrize(
    ("result", "label"),
    [
        ({"verdict": "CLEAN"}, "missing-findings"),
        ({"findings": "not-a-list"}, "non-list-findings"),
        ({"findings": [{"level": "mystery", "check": "x"}]}, "malformed-finding-level"),
        ({"findings": ["not-a-mapping"]}, "non-mapping-finding"),
        ("not-a-mapping", "non-mapping-result"),
        ({}, "empty"),
    ],
)
def test_tc1_nothing_checked_is_unavailable(result: Any, label: str) -> None:
    """Consult-real-signal / nothing-checked→unavailable (Q3.1 FIX-3): a missing/non-list
    ``findings``, a malformed finding, or a non-mapping degrades to ``unavailable`` — "we could
    not actually qualify the trackers" is UNKNOWN, NEVER silently coherent."""
    sig = tracker_coherence_signal(result)
    assert sig["status"] == "unavailable", f"{label}: expected unavailable, got {sig}"
    assert "trackers_coherent" not in sig
    assert level_from_signal(_TC1_KEY, sig) == "unavailable"


def test_tc1_status_unavailable_when_qualifier_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If ``qualify_sources`` cannot be imported / raises, the reader reports
    ``status='unavailable'`` — never wiring-absent as a clean or silently-coherent posture."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "scripts.utilities.progress_map", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "scripts.utilities.progress_map":
            raise ImportError("seeded: progress_map unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = tracker_coherence_signal()
    assert sig["status"] == "unavailable"
    assert level_from_signal(_TC1_KEY, sig) == "unavailable"


# =========================== TC2 — code↔doc drift-monitoring posture =========== #


def test_tc2_real_repo_monitoring_wired_but_advisory_weak() -> None:
    """Real posture (FIX-A): ``doc_drift_monitor`` EXISTS (monitoring wired) but is ADVISORY —
    it exposes no ``gates_production`` affordance → ``gates_production`` False → ``weak`` (the
    fence-not-gating pattern). A STABLE posture read — no git run at read time."""
    sig = tracker_doc_drift_signal()
    assert sig["status"] == "ok"
    assert sig["monitoring_wired"] is True
    assert sig["gates_production"] is False
    assert level_from_signal(_TC2_KEY, sig) == "weak"


def test_tc2_gating_posture_close_path_is_strong() -> None:
    """Reachable close-path grounded in the real module shape: a monitor that GATES production
    (``gates_production`` truthy) → ``strong``. An injectable module-like object reads a SEEDED
    posture without touching the real module."""
    sig = tracker_doc_drift_signal(_wired_monitor(gates_production=True))
    assert sig["monitoring_wired"] is True
    assert sig["gates_production"] is True
    assert level_from_signal(_TC2_KEY, sig) == "strong"


def test_tc2_advisory_posture_is_weak() -> None:
    """Wired but advisory (``gates_production`` False / absent) → ``weak`` (mechanism exists,
    never gates)."""
    assert level_from_signal(_TC2_KEY, tracker_doc_drift_signal(_wired_monitor())) == "weak"
    no_flag = SimpleNamespace(
        check_documentation_drift=lambda *a: None, get_changed_files=lambda: []
    )
    assert level_from_signal(_TC2_KEY, tracker_doc_drift_signal(no_flag)) == "weak"


@pytest.mark.parametrize(
    "monitor",
    [
        SimpleNamespace(),  # no drift-check functions → not wired
        SimpleNamespace(check_documentation_drift=lambda *a: None),  # missing get_changed_files
        SimpleNamespace(get_changed_files=lambda: []),  # missing check_documentation_drift
        SimpleNamespace(check_documentation_drift="not-callable", get_changed_files=lambda: []),
    ],
)
def test_tc2_monitoring_not_wired_is_unavailable(monitor: Any) -> None:
    """Substrate absent / not wired (the drift-check functions missing or non-callable) →
    ``unavailable`` (never a clean or silently-``False`` gating claim)."""
    sig = tracker_doc_drift_signal(monitor)
    assert sig["status"] == "unavailable"
    assert level_from_signal(_TC2_KEY, sig) == "unavailable"


def test_tc2_status_unavailable_when_monitor_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """git-substrate absent (``doc_drift_monitor`` unimportable) → ``unavailable``, NOT clean."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "scripts.utilities.doc_drift_monitor", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "scripts.utilities.doc_drift_monitor":
            raise ImportError("seeded: doc_drift_monitor unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = tracker_doc_drift_signal()
    assert sig["status"] == "unavailable"
    assert level_from_signal(_TC2_KEY, sig) == "unavailable"


def test_tc2_runs_no_git_at_read_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """FIX-A (the design fix): the reader measures the STABLE posture and runs NO git at read
    time — monkeypatch ``subprocess.run`` to RAISE and the live reader is UNAFFECTED (still ok /
    weak). The prior HEAD~1..HEAD design would have hung / flapped / false-cleaned here."""
    import subprocess

    def _boom(*args, **kwargs):
        raise AssertionError("git must not be invoked at scorecard-read time (FIX-A)")

    monkeypatch.setattr(subprocess, "run", _boom)
    sig = tracker_doc_drift_signal()  # real module import — no git call
    assert sig["status"] == "ok"
    assert level_from_signal(_TC2_KEY, sig) == "weak"


# =========================== signal→level totals (fully-computed) ============== #


@pytest.mark.parametrize(
    ("key", "sig", "expected"),
    [
        (_TC1_KEY, {"status": "ok", "verdict": "CLEAN"}, "strong"),
        (_TC1_KEY, {"status": "ok", "verdict": "DEGRADED"}, "partial"),
        (_TC1_KEY, {"status": "ok", "verdict": "FAIL"}, "weak"),
        (_TC1_KEY, {"status": "ok", "verdict": "MYSTERY"}, "unavailable"),
        (_TC1_KEY, {"status": "unavailable"}, "unavailable"),
        (_TC1_KEY, "garbage", "unavailable"),
        (_TC2_KEY, {"status": "ok", "monitoring_wired": True, "gates_production": True}, "strong"),
        (_TC2_KEY, {"status": "ok", "monitoring_wired": True, "gates_production": False}, "weak"),
        (_TC2_KEY, {"status": "ok", "monitoring_wired": True, "gates_production": None},
         "unavailable"),
        (_TC2_KEY, {"status": "ok", "monitoring_wired": False}, "unavailable"),
        (_TC2_KEY, {"status": "unavailable"}, "unavailable"),
        (_TC2_KEY, {}, "unavailable"),
    ],
)
def test_tracker_level_totals(key: str, sig: Any, expected: str) -> None:
    """Both tracker criteria return a REAL level for every signal (fully-computed — never
    ``None``), and never award a clean level on a non-ok / malformed signal."""
    got = level_from_signal(key, sig)
    assert got == expected
    assert got is not None  # fully-computed: a real level for every criterion (GL-7)
    if expected != "strong":
        assert got not in _CLEAN


def test_both_tracker_criteria_are_signal_derived_in_the_block() -> None:
    """GL-7: BOTH tracker_coherence criteria carry ``derivation: signal-derived`` (no judgment
    level), and ``level_from_signal`` returns a real level (not None) for each."""
    crit = read_scorecard_block()["dimensions"][_TRACKER_KEY]["criteria"]
    assert set(crit) == {_TC1_KEY, _TC2_KEY}
    for c in crit.values():
        assert c["derivation"] == "signal-derived"
        assert c["signal"]["reader"].startswith("app.quality.signals.")
        assert isinstance(c["evidence_ref"], str) and c["evidence_ref"]


def test_band_ceiling_is_b_disclosed() -> None:
    """FIX-D: the dimension is structurally capped — both criteria cap at ``strong`` (3)
    mechanically (``level_from_signal`` never awards ``uniform``/4). Max = 3+3 = 6/8 = 75 → B.
    This asserts the CEILING is real (so the §6.5 disclosure is honest)."""
    coherent_tc1 = tracker_coherence_signal(_qresult([("ok", "exists")]))
    gating_tc2 = tracker_doc_drift_signal(_wired_monitor(gates_production=True))
    assert level_from_signal(_TC1_KEY, coherent_tc1) == "strong"  # never 'uniform'
    assert level_from_signal(_TC2_KEY, gating_tc2) == "strong"  # never 'uniform'
    # strong→3 each → 6/8 = 75 → Band B (A unreachable).
    assert round(6 / 8 * 100) == 75


# =========================== leak-count reader ================================== #


def test_tracker_leak_count_real_repo_is_two() -> None:
    sig = tracker_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["tracker_leak_count"] == 2


def test_tracker_leak_count_fixture(tmp_path: Path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Governance/Tracker-Coherence Scorecard Leak Registry\n\n"
        "- trk_leak: alpha\n- trk_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- trk_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert tracker_leak_count_signal(p)["tracker_leak_count"] == 2


def test_tracker_leak_count_ignores_other_namespaces(tmp_path: Path) -> None:
    """The ``trk_leak:`` reader must NOT count the other five namespaces."""
    doc = (
        "## Governance/Tracker-Coherence Scorecard Leak Registry\n\n"
        "- trk_leak: only-this\n"
        "- did_leak: not-counted\n- cost_leak: not-counted\n- cov_leak: not-counted\n"
        "- fid_leak: not-counted\n- cap_leak: not-counted\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert tracker_leak_count_signal(p)["tracker_leak_count"] == 1


def test_tracker_leak_count_zero_when_registry_empty(tmp_path: Path) -> None:
    """⚠️ ZERO-LEAK PATH: a registry with NO ``trk_leak:`` line → count 0 — the reader returns a
    clean ``0``, not ``unavailable`` (this is the FIRST dimension that can carry zero leaks)."""
    doc = "## Governance/Tracker-Coherence Scorecard Leak Registry\n\n(no open tracker leaks)\n"
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    sig = tracker_leak_count_signal(p)
    assert sig["status"] == "ok"
    assert sig["tracker_leak_count"] == 0


# =========================== GL-13 cross-dimensional =========================== #


def test_tracker_leaks_aggregate_into_shared_ranked_list() -> None:
    """GL-13: BOTH tracker_coherence GOVERNANCE leaks aggregate into the ONE shared ranked list
    and sort AFTER the paid-walk AND learner-trust blocks (governance lane sorts last)."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    lanes = [e["lane"] for e in ranked]
    dims = {e["dimension"] for e in ranked}
    tc1_slug = "tracker-coherence-status-trackers-degraded-orphan-stories"
    tc2_slug = "tracker-coherence-doc-drift-monitoring-advisory-never-gates"
    assert tc1_slug in slugs and tc2_slug in slugs
    non_gov = [i for i, ln in enumerate(lanes) if ln in ("paid-walk", "learner-trust")]
    assert slugs.index(tc1_slug) > max(non_gov)
    assert slugs.index(tc2_slug) > max(non_gov)
    assert lanes[slugs.index(tc1_slug)] == "governance"
    assert lanes[slugs.index(tc2_slug)] == "governance"
    # SIX dimensions now contribute (cross-dimensional).
    assert dims == {
        _DID_KEY, _COST_KEY, _COVERAGE_KEY, _FIDELITY_KEY, _CAPABILITY_KEY, _TRACKER_KEY,
    }
    # 5 DID + 1 cost + 1 coverage + 1 fidelity + 1 capability + 2 tracker = 11.
    assert len(ranked) == 11


def test_leak_coverage_clean_with_tracker_dimension() -> None:
    """The coverage guard stays clean: tracker_coherence declares open_leaks=2 AND carries a
    ``leaks`` list of length 2, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== ⚠️ ZERO-LEAK-PATH lock-in ========================= #
# This is the FIRST dimension whose open_leaks could legitimately be 0 (if the trackers
# reconciled to CLEAN AND the drift monitor gated). Confirm the shared machinery handles a
# 0-leak dimension cleanly — additively (it ALREADY handles it; these lock it in).


def test_zero_leak_dimension_is_not_a_coverage_gap() -> None:
    """A dimension with ``open_leaks: 0`` + ``leaks: []`` is NOT a coverage gap (a gap is
    ``open_leaks > 0`` AND no leaks list). The 0-leak path must not false-flag."""
    block = {
        "dimensions": {
            _TRACKER_KEY: {
                "label": "Governance / tracker-coherence",
                "open_leaks": 0,
                "leaks": [],
            }
        }
    }
    assert leak_coverage_gaps(block) == []
    block2 = {"dimensions": {_TRACKER_KEY: {"open_leaks": 0}}}  # no leaks key at all
    assert leak_coverage_gaps(block2) == []


def test_zero_leak_dimension_contributes_no_ranked_leaks() -> None:
    """``ranked_project_leaks`` handles a 0-leak dimension (empty ``leaks`` list) — it
    contributes nothing to the shared ranked list, never raises."""
    block = {
        "dimensions": {
            _TRACKER_KEY: {"open_leaks": 0, "leaks": []},
            _DID_KEY: {
                "label": "DID",
                "leaks": [{"rank": 1, "criterion": "C1", "slug": "s1", "lane": "paid-walk"}],
            },
        }
    }
    ranked = ranked_project_leaks(block)
    assert [e["slug"] for e in ranked] == ["s1"]  # only DID contributed; tracker contributed 0


def test_zero_leak_count_reconciles() -> None:
    """The leak-count identity holds at 0: ``open_leaks: 0`` reconciles against a 0 leak-count
    and a ``leaks: []`` list (``0 == 0 == len([])``)."""
    dim = {"open_leaks": 0, "leaks": []}
    assert dim["open_leaks"] == len(dim["leaks"]) == 0


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_tracker_dimension_with_no_code_change() -> None:
    """AC1/AC5: ``render_scorecard_final_report`` picks up tracker_coherence automatically — its
    Band row, its per-criterion trace, its ranked leaks, and its ▬ baseline trend all render with
    NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Governance / tracker-coherence | D |" in out
    assert "tracker-coherence-status-trackers-degraded-orphan-stories" in out
    assert "tracker-coherence-doc-drift-monitoring-advisory-never-gates" in out
    assert "| Governance / tracker-coherence | ▬ baseline |" in out
    tc1_row = "| Governance / tracker-coherence | tracker_divergence_coherence | partial | 2/4 |"
    tc2_row = "| Governance / tracker-coherence | tracker_doc_drift | weak | 1/4 |"
    assert tc1_row in out
    assert tc2_row in out
    assert "/100" not in out  # never a false-precise headline

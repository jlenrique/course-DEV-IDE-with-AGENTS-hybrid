"""Story Q3.1 — capability_honesty signal reader + cross-dimensional integration
(hermetic + real). No live calls, no ``--run-live``.

The capability_honesty dimension is scored by RECONCILING the EXISTING front-door capability
ledger (GL-15 — reuse, no parallel plumbing): the per-component ``CapabilityTier`` in
``app/marcus/lesson_plan/bundle_catalog.py`` (``CAPABILITY_TIERS``), reconciled READ-ONLY
against a bounded curated produced-evidence signal (the recorded DID-Leak-5 evidence). This
module covers:

  * the reconciliation reader against hermetic fixture tiers + produced-evidence (clean /
    lag / overstatement / never-produced-is-honest / unknown-tier) AND the real bundle_catalog;
  * the ISOLATING axis (Q2.3 FT2 lesson): tier HELD, produced-evidence VARIED — proving the
    reader consults the REAL mismatch condition (declared tier vs produced-evidence), NOT the
    raw tier;
  * the reachable close-path (a party-ratified tier → coherent → strong) + read-only (the
    reader NEVER mutates the real registry) + the signal→level derivation;
  * CH2 no-overstatement (judgment-with-evidence);
  * the cross-dimensional GL-13 interleave (the capability governance leak among DID/cost/
    coverage/fidelity) + the coverage guard clean on the real repo;
  * the deterministic projector picking up the new dimension with NO projector change.

The honesty-pin RED-under-seeded proofs (reconciliation-claim, capability leak-count + slug
identity, arithmetic, five-namespace disjointness, the isolating pin) live in
``test_scorecard_honesty_pins.py`` (the registered pins).

**⛔ Governance fence.** This dimension SCORES the honesty of the tiers; it reads
``bundle_catalog`` READ-ONLY and NEVER edits a tier (party-gated governance). The
``test_..._read_only...`` tests assert the reader leaves the real registry byte-identical.
"""

from __future__ import annotations

import builtins
import sys

import pytest

from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _CAPABILITY_KEY, read_scorecard_block
from app.quality.signals import (
    capability_leak_count_signal,
    capability_tier_reconciliation_signal,
    level_from_signal,
)

_CLEAN = {"strong", "uniform"}
_COST_KEY = "cost_efficiency"
_COVERAGE_KEY = "coverage_honesty"
_DID_KEY = "dynamic_intelligence_vs_determinism"
_FIDELITY_KEY = "fidelity_trust"

_KEY = "capability_tier_reconciliation_on"


# =========================== CH1 — tier↔produced reconciliation ================= #


def test_reconciliation_real_repo_flags_workbook_lag_weak() -> None:
    """Real posture: ``bundle_catalog`` tiers workbook ``mechanism_only_never_produced`` while
    a produced artifact demonstrably exists (curated DID-Leak-5 evidence) → ONE lag mismatch →
    ``tiers_match_produced_reality`` False → ``weak`` (the leak). The direction is
    CONSERVATIVE (understating), not an overstatement."""
    sig = capability_tier_reconciliation_signal()
    assert sig["status"] == "ok"
    assert sig["tiers"]["workbook"] == "mechanism_only_never_produced"
    assert len(sig["lag_mismatches"]) == 1
    assert sig["lag_mismatches"][0]["component"] == "workbook"
    assert sig["overstatement_mismatches"] == []
    assert sig["tiers_match_produced_reality"] is False
    assert sig["no_overstatement"] is True
    assert sig["mismatch_direction"] == "conservative-understatement"
    assert level_from_signal(_KEY, sig) == "weak"


def test_reconciliation_curated_evidence_carries_did_leak5_refs() -> None:
    """The BOUNDED curated produced-evidence is the recorded DID-Leak-5 evidence (trial
    ``a940c5eb`` + LO-verified ``8b275e5b``) and the honest tier is proven-on-frozen-lesson —
    NOT blanket proven_wired (off-frozen-lesson stays an open claim)."""
    lag = capability_tier_reconciliation_signal()["lag_mismatches"][0]
    assert lag["honest_tier"] == "proven-on-frozen-lesson"
    refs = " ".join(lag["evidence_refs"])
    assert "a940c5eb" in refs and "8b275e5b" in refs


def test_reconciliation_close_path_reachable_and_read_only() -> None:
    """The reader is NOT a hardcoded verdict and the close-path is REACHABLE + READ-ONLY
    (Q2.1 CE1 / Q2.2 CV1 / Q2.3 FT1 pattern): a SEEDED party-ratified tier that matches
    produced reality → coherent → ``strong``; and calling the reader NEVER mutates the real
    ``CAPABILITY_TIERS`` registry."""
    from app.marcus.lesson_plan.bundle_catalog import CAPABILITY_TIERS

    before = {name: cap.tier for name, cap in CAPABILITY_TIERS.items()}
    off = capability_tier_reconciliation_signal(
        tiers={"workbook": "mechanism_only_never_produced"}
    )
    assert off["tiers_match_produced_reality"] is False
    assert level_from_signal(_KEY, off) == "weak"
    on = capability_tier_reconciliation_signal(tiers={"workbook": "proven_wired"})
    assert on["tiers_match_produced_reality"] is True
    assert level_from_signal(_KEY, on) == "strong"
    # READ-ONLY: no registry mutation across any variant.
    capability_tier_reconciliation_signal()
    assert {name: cap.tier for name, cap in CAPABILITY_TIERS.items()} == before


def test_reconciliation_isolates_evidence_from_raw_tier() -> None:
    """THE ISOLATING axis (Q2.3 FT2 lesson): HOLD the tier ``mechanism_only_never_produced``,
    VARY the produced-evidence. produced=True → lag → weak; produced=False → NO lag (a
    genuinely-never-produced component tiered mechanism_only is HONEST) → strong. A raw-tier-
    only regression (flag mechanism_only regardless of evidence) would flag both and RED here."""
    held = {"workbook": "mechanism_only_never_produced"}
    lag = capability_tier_reconciliation_signal(
        tiers=held, produced_evidence={"workbook": {"produced": True}}
    )
    assert lag["tiers_match_produced_reality"] is False
    assert level_from_signal(_KEY, lag) == "weak"
    honest = capability_tier_reconciliation_signal(
        tiers=held, produced_evidence={"workbook": {"produced": False}}
    )
    assert honest["lag_mismatches"] == []
    assert honest["tiers_match_produced_reality"] is True
    assert level_from_signal(_KEY, honest) == "strong"


def test_reconciliation_flags_overstatement_direction() -> None:
    """The worse OVERSTATING direction IS detected when it occurs: a component tiered
    ``proven_wired`` while curated evidence says it was NEVER produced → an overstatement
    mismatch → ``tiers_match_produced_reality`` False AND ``no_overstatement`` False. (None
    today on the real repo — but the reader is not blind to the believed-green direction.)"""
    sig = capability_tier_reconciliation_signal(
        tiers={"phantom": "proven_wired"},
        produced_evidence={"phantom": {"produced": False}},
    )
    assert len(sig["overstatement_mismatches"]) == 1
    assert sig["no_overstatement"] is False
    assert sig["tiers_match_produced_reality"] is False
    assert sig["mismatch_direction"] == "overstatement"
    assert level_from_signal(_KEY, sig) == "weak"


def test_reconciliation_all_coherent_is_strong() -> None:
    """No lag AND no overstatement → coherent → strong. A produced component tiered proven
    and a never-produced component tiered mechanism_only are BOTH honest."""
    sig = capability_tier_reconciliation_signal(
        tiers={"a": "proven_wired", "b": "mechanism_only_never_produced"},
        produced_evidence={"a": {"produced": True}, "b": {"produced": False}},
    )
    assert sig["lag_mismatches"] == [] and sig["overstatement_mismatches"] == []
    assert sig["tiers_match_produced_reality"] is True
    assert sig["no_overstatement"] is True
    assert sig["mismatch_direction"] == "none"
    assert level_from_signal(_KEY, sig) == "strong"


def test_reconciliation_reads_component_capability_like_objects() -> None:
    """The reader accepts a ``ComponentCapability``-like object (duck-typed ``.tier``) as an
    injected tier value — the shape the REAL ``CAPABILITY_TIERS`` registry carries."""
    from types import SimpleNamespace

    sig = capability_tier_reconciliation_signal(
        tiers={"workbook": SimpleNamespace(tier="mechanism_only_never_produced")},
        produced_evidence={"workbook": {"produced": True}},
    )
    assert sig["tiers"]["workbook"] == "mechanism_only_never_produced"
    assert sig["tiers_match_produced_reality"] is False


def test_reconciliation_shelf_tier_lag_is_flagged() -> None:
    """FIX-1 RED-first: ``CapabilityTier`` is a FOUR-value enum — ``shelf`` ("named but not
    built") ALSO asserts never-produced (strictly further from produced reality than
    ``mechanism_only_never_produced``). A component tiered ``shelf`` with a produced artifact
    → a LAG mismatch → ``tiers_match_produced_reality`` False → ``weak`` (NOT a false-clean
    ``strong``). A three-value classification that only knew ``mechanism_only_never_produced``
    would miss this and false-clean."""
    sig = capability_tier_reconciliation_signal(
        tiers={"widget": "shelf"}, produced_evidence={"widget": {"produced": True}}
    )
    assert sig["reconciled_count"] == 1
    assert len(sig["lag_mismatches"]) == 1
    assert sig["lag_mismatches"][0]["declared_tier"] == "shelf"
    assert sig["tiers_match_produced_reality"] is False
    assert level_from_signal(_KEY, sig) == "weak"


def test_reconciliation_shelf_never_produced_is_honest() -> None:
    """The isolating principle extends to ``shelf``: a genuinely-never-produced component
    tiered ``shelf`` (produced=False) is HONEST → NO lag → coherent → strong (consulted the
    real mismatch condition, not the raw tier)."""
    sig = capability_tier_reconciliation_signal(
        tiers={"widget": "shelf"}, produced_evidence={"widget": {"produced": False}}
    )
    assert sig["lag_mismatches"] == []
    assert sig["tiers_match_produced_reality"] is True
    assert level_from_signal(_KEY, sig) == "strong"


@pytest.mark.parametrize(
    ("tiers", "evidence", "label"),
    [
        ({"workbook": "mechanism_only_never_produced"}, {}, "empty-evidence"),
        (
            {"workbook": None},
            {"workbook": {"produced": True}},
            "all-None-tiers (unreadable)",
        ),
        (
            {"workbook": "proven_wired"},
            {"typo_component": {"produced": True}},
            "absent/typo'd component",
        ),
        (
            {"workbook": "mechanism_only_never_produced"},
            {"workbook": {"produced": "yes"}},
            "non-bool produced",
        ),
    ],
)
def test_reconciliation_nothing_reconciled_is_unavailable(
    tiers: dict, evidence: dict, label: str
) -> None:
    """FIX-3 RED-first (the unifying over-claim-clean fix): when NOTHING is actually reconciled
    (tier readable AND produced a real bool) the reconciliation must read ``unavailable``,
    NEVER ``coherent``/``strong`` — "nothing reconcilable" is UNKNOWN, not clean (CV2/FT2).
    Four cases: empty evidence · all-None (unreadable) tiers · absent/typo'd component ·
    non-bool ``produced``. Before the fix each returned ``status='ok',
    tiers_match_produced_reality=True`` (→ CH1 false-clean strong)."""
    sig = capability_tier_reconciliation_signal(tiers=tiers, produced_evidence=evidence)
    assert sig["status"] == "unavailable", f"{label}: expected unavailable, got {sig}"
    assert sig.get("reconciled_count", 0) == 0
    assert "tiers_match_produced_reality" not in sig  # never certifies clean
    assert level_from_signal(_KEY, sig) == "unavailable"


def test_reconciliation_non_bool_produced_is_surfaced_not_dropped() -> None:
    """FIX-3: a non-bool ``produced`` on a curated entry is SURFACED in ``unreconciled`` (with a
    reason), not silently dropped. Here a real reconciled component coexists with a non-bool
    one, so the signal is still ``ok`` but the malformed entry is visible + uncounted."""
    sig = capability_tier_reconciliation_signal(
        tiers={"a": "proven_wired", "b": "mechanism_only_never_produced"},
        produced_evidence={"a": {"produced": True}, "b": {"produced": None}},
    )
    assert sig["status"] == "ok"
    assert sig["reconciled_count"] == 1  # only 'a' was reconcilable
    reasons = {u["component"]: u["reason"] for u in sig["unreconciled"]}
    assert reasons.get("b") == "produced is not a bool"


def test_reconciliation_non_mapping_tiers_is_unavailable() -> None:
    """A non-mapping injected tier source degrades to ``status='unavailable'`` → ``unavailable``
    level (never a clean or silently-False coherence claim)."""
    sig = capability_tier_reconciliation_signal(tiers=["not", "a", "mapping"])
    assert sig["status"] == "unavailable"
    assert level_from_signal(_KEY, sig) == "unavailable"


def test_reconciliation_empty_tiers_is_unavailable() -> None:
    """An empty tier map (no components to reconcile) degrades to ``unavailable`` — an empty
    ledger is not honestly 'coherent', it is unknown."""
    sig = capability_tier_reconciliation_signal(tiers={})
    assert sig["status"] == "unavailable"
    assert level_from_signal(_KEY, sig) == "unavailable"


def test_reconciliation_status_unavailable_when_bundle_catalog_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-pattern: if ``bundle_catalog`` cannot be imported the reader reports
    ``status='unavailable'`` — never wiring-absent as a clean or silently-coherent posture."""
    monkeypatch.delitem(sys.modules, "app.marcus.lesson_plan.bundle_catalog", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.marcus.lesson_plan.bundle_catalog":
            raise ImportError("seeded: bundle_catalog unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = capability_tier_reconciliation_signal()
    assert sig["status"] == "unavailable"
    assert level_from_signal(_KEY, sig) == "unavailable"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "tiers_match_produced_reality": True}, "strong"),
        ({"status": "ok", "tiers_match_produced_reality": False}, "weak"),
        ({"status": "ok", "tiers_match_produced_reality": None}, "unavailable"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_ch_reconciliation_total(sig: object, expected: str) -> None:
    got = level_from_signal(_KEY, sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


# =========================== CH2 — no-overstatement judgment ==================== #


def test_ch2_no_overstatement_is_judgment_with_evidence() -> None:
    """CH2 is judgment-with-evidence: the reconciliation reader carries the ``no_overstatement``
    fact but ``level_from_signal`` returns ``None`` for the CH2 key (no mechanical clean-level
    award — the §5.6 ``strong`` is an authored judgment over the bounded curated evidence)."""
    sig = capability_tier_reconciliation_signal()
    assert sig["no_overstatement"] is True
    assert level_from_signal("capability_no_overstatement", sig) is None


# =========================== leak-count reader ================================== #


def test_capability_leak_count_real_repo_is_one() -> None:
    sig = capability_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["capability_leak_count"] == 1


def test_capability_leak_count_fixture(tmp_path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Capability-Honesty Scorecard Leak Registry\n\n"
        "- cap_leak: alpha\n- cap_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- cap_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert capability_leak_count_signal(p)["capability_leak_count"] == 2


def test_capability_leak_count_ignores_other_namespaces(tmp_path) -> None:
    """The ``cap_leak:`` reader must NOT count ``did_leak:`` / ``cost_leak:`` / ``cov_leak:``
    / ``fid_leak:`` tags."""
    doc = (
        "## Capability-Honesty Scorecard Leak Registry\n\n"
        "- cap_leak: only-this\n"
        "- did_leak: not-counted\n"
        "- cost_leak: not-counted\n"
        "- cov_leak: not-counted\n"
        "- fid_leak: not-counted\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert capability_leak_count_signal(p)["capability_leak_count"] == 1


# =========================== GL-13 cross-dimensional =========================== #


def test_capability_leak_aggregates_into_shared_ranked_list() -> None:
    """GL-13: the capability_honesty GOVERNANCE leak aggregates into the ONE shared ranked list
    (DID + cost + coverage + fidelity + capability) and sorts AFTER the paid-walk AND
    learner-trust blocks (governance lane sorts last)."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    lanes = [e["lane"] for e in ranked]
    dims = [e["dimension"] for e in ranked]
    cap_slug = "capability-honesty-workbook-tier-lags-produced-reality"
    assert cap_slug in slugs
    cap_idx = slugs.index(cap_slug)
    assert lanes[cap_idx] == "governance"
    # every paid-walk AND learner-trust leak sorts strictly BEFORE the capability governance leak.
    non_gov = [i for i, ln in enumerate(lanes) if ln in ("paid-walk", "learner-trust")]
    assert cap_idx > max(non_gov)
    # FIVE dimensions now contribute (cross-dimensional).
    # Q3.2 added tracker_coherence as a SIXTH contributor (a governance leak).
    assert set(dims) == {
        _DID_KEY, _COST_KEY, _COVERAGE_KEY, _FIDELITY_KEY, _CAPABILITY_KEY, "tracker_coherence",
    }
    assert len(ranked) == 11  # 5 DID + 1 cost + 1 cov + 1 fid + 1 cap + 2 tracker


def test_leak_coverage_clean_with_capability_dimension() -> None:
    """The coverage guard stays clean: capability_honesty declares open_leaks=1 AND carries a
    ``leaks`` list, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_capability_dimension_with_no_code_change() -> None:
    """AC1/AC5: ``render_scorecard_final_report`` picks up capability_honesty automatically —
    its Band row, its per-criterion trace, its ranked leak, and its ▬ baseline trend all
    render with NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Capability-honesty | C |" in out
    assert "capability-honesty-workbook-tier-lags-produced-reality" in out
    assert "| Capability-honesty | ▬ baseline |" in out
    assert "| Capability-honesty | capability_tier_reconciliation_on | weak | 1/4 |" in out
    assert "/100" not in out  # never a false-precise headline

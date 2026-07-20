"""Story Q2.3 — fidelity_trust signal readers + cross-dimensional integration
(hermetic + real). No live calls, no ``--run-live``.

The fidelity_trust dimension is scored from the EXISTING fidelity emitters (GL-15 —
reuse, no parallel plumbing): the semantic-fidelity audit's DEFAULT gating posture
(``SEMANTIC_TRIPWIRE['gates_production']`` — the fence), the Vera fidelity trace's real
Omissions/Inventions/Alterations FAIL condition (``vera._act._hard_fail`` over a trace's
findings + the verdict status), and the audit's WARN-transparency posture
(``mode == 'warn_only'`` + the claim fence). This module covers:

  * the three readers against hermetic fixture ``fidelity-trace.v1`` traces (clean / real
    O/I/A FAIL / empty) AND real repo/constant state;
  * the semantic-fence reader reading the REAL ``SEMANTIC_TRIPWIRE`` constant + the seeded
    on/off close-path (reachable + read-only) + the signal→level derivation;
  * the cross-dimensional GL-13 interleave (fidelity learner-trust leak among DID/cost/
    coverage) + the coverage guard clean on the real repo;
  * the deterministic projector picking up the new dimension with NO projector change.

The honesty-pin RED-under-seeded proofs (gates-claim, fidelity leak-count + slug identity,
arithmetic, four-namespace disjointness) live in ``test_scorecard_honesty_pins.py`` (the
registered pins).

**The Q2.2 CV2 lesson applied to fidelity (most relevant here):** the fidelity-trace
honesty signal MUST consult the REAL O/I/A fail condition — a critical
Omission/Invention/Alteration (``_hard_fail`` → ``HALT-AND-REMEDIATE``) is NEVER a clean
fidelity. That is asserted (not a toothless test).
"""

from __future__ import annotations

import json

import pytest

from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _FIDELITY_KEY, read_scorecard_block
from app.quality.signals import (
    fidelity_audit_honesty_signal,
    fidelity_leak_count_signal,
    fidelity_trace_honesty_signal,
    level_from_signal,
    semantic_fence_gating_signal,
)

_CLEAN = {"strong", "uniform"}
_COST_KEY = "cost_efficiency"
_COVERAGE_KEY = "coverage_honesty"
_DID_KEY = "dynamic_intelligence_vs_determinism"


# --------------------------------------------------------------------------- #
# Hermetic fixture builders — real ``fidelity-trace.v1`` shape (Vera trace).
# --------------------------------------------------------------------------- #
def _finding(category: str, severity: str, desc: str) -> dict[str, str]:
    return {
        "category": category,
        "severity": severity,
        "evidence_anchor": "fixture:trace",
        "description": desc,
    }


def _clean_trace() -> dict:
    """A clean fidelity trace: the advisory O/I/A trio (no hard fail), verdict PROCEED —
    exactly what Vera emits when nothing is detected."""
    return {
        "schema_version": "fidelity-trace.v1",
        "gate_id": "G0",
        "findings": [
            _finding("O", "advisory", "no omissions detected"),
            _finding("I", "advisory", "no inventions detected"),
            _finding("A", "advisory", "no alterations detected"),
        ],
        "verdict": {"status": "PROCEED", "verb": "proceed", "failure_reason": None},
    }


def _fail_trace() -> dict:
    """A REAL fidelity FAIL: a critical Alteration finding → the Vera ``_hard_fail``
    predicate fires → verdict HALT-AND-REMEDIATE. This must NEVER read as clean (CV2)."""
    return {
        "schema_version": "fidelity-trace.v1",
        "gate_id": "G3",
        "findings": [
            _finding("O", "advisory", "no omissions detected"),
            _finding("A", "critical", "narration altered a source figure"),
        ],
        "verdict": {
            "status": "HALT-AND-REMEDIATE",
            "verb": "halt",
            "failure_reason": "narration altered a source figure",
        },
    }


def _warn_trace() -> dict:
    """A WARN-level O/I/A finding (not critical) → the hard-fail predicate does NOT fire,
    verdict PROCEED → still a clean fidelity (the WARN never hard-fails, honest reading)."""
    return {
        "schema_version": "fidelity-trace.v1",
        "gate_id": "G0",
        "findings": [_finding("O", "warning", "extracted text below the word floor")],
        "verdict": {"status": "PROCEED", "verb": "proceed", "failure_reason": None},
    }


def _empty_trace() -> dict:
    """A trace with ZERO findings — cannot certify clean (non-empty guard)."""
    return {"schema_version": "fidelity-trace.v1", "findings": [], "verdict": {"status": "PROCEED"}}


# =========================== FT1 — semantic-fence gating ======================== #


def test_semantic_fence_default_is_warn_only_weak() -> None:
    """Real posture: ``SEMANTIC_TRIPWIRE['gates_production']`` is False → the audit WARNs,
    never gates → ``semantic_fence_gates`` False → ``weak`` (the leak)."""
    sig = semantic_fence_gating_signal()
    assert sig["status"] == "ok"
    assert sig["gates_production"] is False
    assert sig["semantic_fence_gates"] is False
    assert level_from_signal("semantic_fence_gating_on", sig) == "weak"


def test_semantic_fence_close_path_is_reader_reachable() -> None:
    """The reader is NOT a hardcoded ``False`` and the close-path is REACHABLE: an injectable
    tripwire with ``gates_production=False`` → ``weak``; one with ``gates_production=True`` →
    ``strong`` (so closing the leak legitimately earns strong; the pin AGREES rather than
    false-REDs the operator who flips it on)."""
    off = semantic_fence_gating_signal(tripwire={"gates_production": False})
    assert off["semantic_fence_gates"] is False
    assert level_from_signal("semantic_fence_gating_on", off) == "weak"
    on = semantic_fence_gating_signal(tripwire={"gates_production": True})
    assert on["semantic_fence_gates"] is True
    assert level_from_signal("semantic_fence_gating_on", on) == "strong"


def test_semantic_fence_reader_is_read_only_no_constant_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The reader NEVER mutates the ``SEMANTIC_TRIPWIRE`` constant. Any variant leaves the
    real constant byte-identical."""
    from app.specialists._shared.source_fidelity_audit import SEMANTIC_TRIPWIRE

    before = dict(SEMANTIC_TRIPWIRE)
    semantic_fence_gating_signal()
    semantic_fence_gating_signal(tripwire={"gates_production": True})
    semantic_fence_gating_signal(tripwire={"gates_production": False})
    assert dict(SEMANTIC_TRIPWIRE) == before
    assert SEMANTIC_TRIPWIRE["gates_production"] is False  # untouched


def test_semantic_fence_tracks_real_constant(monkeypatch: pytest.MonkeyPatch) -> None:
    """Anti-drift, grounded in the REAL source: the live (tripwire=None) reader tracks the
    REAL ``SEMANTIC_TRIPWIRE['gates_production']`` under ``monkeypatch.setitem`` (auto-
    restored) — flipping the real constant flips the reader (close-path reachable off the
    real source, not a fixture)."""
    from app.specialists._shared.source_fidelity_audit import SEMANTIC_TRIPWIRE

    assert semantic_fence_gating_signal()["semantic_fence_gates"] is False
    monkeypatch.setitem(SEMANTIC_TRIPWIRE, "gates_production", True)
    assert semantic_fence_gating_signal()["semantic_fence_gates"] is True


def test_semantic_fence_nonbool_gates_is_unavailable() -> None:
    """A non-``bool`` ``gates_production`` (unknown posture) is never coerced to a clean or
    false gating claim → ``status='unavailable'`` → ``unavailable`` level."""
    sig = semantic_fence_gating_signal(tripwire={"gates_production": "yes"})
    assert sig["status"] == "unavailable"
    assert level_from_signal("semantic_fence_gating_on", sig) == "unavailable"


def test_semantic_fence_status_unavailable_when_constant_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-4: if ``source_fidelity_audit`` cannot be imported the reader reports
    ``status='unavailable'`` — never wiring-absent as a clean or silently-False posture."""
    import builtins
    import sys

    monkeypatch.delitem(
        sys.modules, "app.specialists._shared.source_fidelity_audit", raising=False
    )
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.specialists._shared.source_fidelity_audit":
            raise ImportError("seeded: source_fidelity_audit unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = semantic_fence_gating_signal()
    assert sig["status"] == "unavailable"


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "semantic_fence_gates": True}, "strong"),
        ({"status": "ok", "semantic_fence_gates": False}, "weak"),
        ({"status": "ok", "semantic_fence_gates": None}, "unavailable"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_ft_semantic_fence_total(sig: object, expected: str) -> None:
    got = level_from_signal("semantic_fence_gating_on", sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


# =========================== FT2 — fidelity-trace honesty ======================= #


def test_trace_honesty_wiring_only_when_no_trace() -> None:
    sig = fidelity_trace_honesty_signal(None)
    assert sig["status"] == "ok"
    assert sig["fidelity_fail_predicate_wired"] is True
    assert sig["trace_present"] is False
    # judgment-with-evidence → no mechanical clean-level award.
    assert level_from_signal("fidelity_trace_honesty", sig) is None


def test_trace_honesty_clean_trace() -> None:
    sig = fidelity_trace_honesty_signal(_clean_trace())
    assert sig["trace_present"] is True
    assert sig["hard_fail_finding"] is None
    assert sig["verdict_halts"] is False
    assert sig["is_clean_fidelity"] is True


def test_trace_honesty_real_oia_fail_is_not_clean() -> None:
    """THE Q2.2 CV2 lesson (most relevant here), ASSERTED: a trace with a REAL critical
    Omission/Invention/Alteration is decided FAIL by the real predicate
    (``vera._act._hard_fail`` → ``HALT-AND-REMEDIATE``) — it must NEVER read as clean
    fidelity. (A toothless test would let a clean-on-fail bug through.)"""
    from app.specialists.vera._act import _hard_fail

    trace = _fail_trace()
    # Sanity: the REAL predicate fires on this trace's findings (a critical A finding).
    assert _hard_fail(trace["findings"]) is not None
    sig = fidelity_trace_honesty_signal(trace)
    assert sig["hard_fail_finding"] is not None  # the reader consults the real predicate
    assert sig["verdict_halts"] is True
    assert sig["oia_finding_count"] >= 1
    assert sig["is_clean_fidelity"] is False  # …so it is NOT a clean fidelity (CV2)


def test_trace_honesty_warn_finding_does_not_hard_fail() -> None:
    """A WARN-level O/I/A finding is honestly NOT a hard fail (only critical hard-fails) —
    the reader agrees with the real predicate and reads it clean (verdict PROCEED)."""
    from app.specialists.vera._act import _hard_fail

    trace = _warn_trace()
    assert _hard_fail(trace["findings"]) is None  # warning severity is not a hard fail
    sig = fidelity_trace_honesty_signal(trace)
    assert sig["hard_fail_finding"] is None
    assert sig["is_clean_fidelity"] is True


def test_trace_honesty_empty_trace_cannot_certify_clean() -> None:
    """A trace with ZERO findings cannot certify clean (non-empty guard) — even with a
    PROCEED verdict, ``is_clean_fidelity`` is False."""
    sig = fidelity_trace_honesty_signal(_empty_trace())
    assert sig["findings_count"] == 0
    assert sig["is_clean_fidelity"] is False


def test_trace_honesty_no_oia_findings_is_not_clean() -> None:
    """FIX-1(a) RED-first: a degenerate trace with findings but ZERO O/I/A entries (e.g. a
    lone ``note``/``info`` finding) + a PROCEED verdict must NOT certify clean — the CV2
    over-claim-clean failure this reader exists to prevent. The clean guard requires
    ``oia_finding_count > 0`` (a genuine Vera fidelity trace emits the O/I/A trio), NOT
    merely ``len(findings) > 0``."""
    trace = {
        "schema_version": "fidelity-trace.v1",
        "findings": [{"category": "note", "severity": "info", "description": "nothing"}],
        "verdict": {"status": "PROCEED", "verb": "proceed", "failure_reason": None},
    }
    sig = fidelity_trace_honesty_signal(trace)
    assert sig["findings_count"] == 1
    assert sig["oia_finding_count"] == 0  # no real O/I/A entry
    assert sig["hard_fail_finding"] is None
    assert sig["verdict_halts"] is False
    assert sig["is_clean_fidelity"] is False  # …so it CANNOT certify clean (FIX-1a)


def test_trace_honesty_hard_fail_alone_drives_not_clean_independent_of_verdict() -> None:
    """FIX-1(b) — the ISOLATING pin on the story's OWN central thesis (the Q2.2 CV2 lesson).
    A trace with a critical Omission/Invention/Alteration finding but a NON-HALT (PROCEED)
    verdict: ``verdict_halts`` is False, yet ``is_clean_fidelity`` must STILL be False —
    proving the REAL ``_hard_fail`` predicate ALONE drives the not-clean verdict, independent
    of the verdict status. A regressed impl that dropped the ``_hard_fail`` term and trusted
    only ``verdict.status`` (the exact CV2 anti-pattern) would return clean here and this
    test would RED it."""
    from app.specialists.vera._act import _hard_fail

    trace = {
        "schema_version": "fidelity-trace.v1",
        "findings": [_finding("A", "critical", "narration altered a source figure")],
        # Deliberately NON-halt verdict — decoupled from the critical finding.
        "verdict": {"status": "PROCEED", "verb": "proceed", "failure_reason": None},
    }
    assert _hard_fail(trace["findings"]) is not None  # the real predicate fires
    sig = fidelity_trace_honesty_signal(trace)
    assert sig["verdict_halts"] is False  # verdict says PROCEED (not halt)…
    assert sig["hard_fail_finding"] is not None  # …but the real predicate fired…
    assert sig["is_clean_fidelity"] is False  # …so it is NOT clean — _hard_fail drives it


def test_trace_honesty_non_dict_finding_does_not_mask_real_fail() -> None:
    """FIX-2 RED-first: a non-dict entry positioned BEFORE a genuine critical O/I/A finding
    must not mask the fail. The raw list is dict-filtered before ``_hard_fail`` (which does
    ``finding.get(...)`` → would AttributeError on a non-dict → caught → ``unavailable``,
    suppressing the real fail). After the fix: the critical A is still detected, ``status``
    stays ``ok``, and the trace is NOT clean."""
    trace = {
        "schema_version": "fidelity-trace.v1",
        "findings": [
            "junk-non-dict-entry",  # a non-dict finding BEFORE the real fail
            _finding("A", "critical", "narration altered a source figure"),
        ],
        "verdict": {"status": "HALT-AND-REMEDIATE", "verb": "halt", "failure_reason": "x"},
    }
    sig = fidelity_trace_honesty_signal(trace)
    assert sig["status"] == "ok"  # not masked to unavailable by the non-dict
    assert sig["hard_fail_finding"] is not None  # the real critical A is still detected
    assert sig["oia_finding_count"] == 1
    assert sig["is_clean_fidelity"] is False


@pytest.mark.parametrize(
    "foreign",
    [
        {"findings": [], "verdict": {"status": "PROCEED"}},  # missing schema_version
        {
            "schema_version": "some-other-artifact.v9",  # foreign schema
            "findings": [{"category": "O", "severity": "advisory", "description": "x"}],
            "verdict": {"status": "PROCEED"},
        },
    ],
)
def test_trace_honesty_foreign_schema_is_unavailable_never_clean(foreign: dict) -> None:
    """FIX-3 RED-first: a dict with ``findings``/``verdict`` keys but a missing / foreign
    ``schema_version`` (a wrong file / foreign artifact) degrades to ``status='unavailable'``
    — it can NEVER reach ``is_clean_fidelity=True``. Only a genuine ``fidelity-trace.v1`` Vera
    trace may certify clean."""
    sig = fidelity_trace_honesty_signal(foreign)
    assert sig["status"] == "unavailable"
    assert "is_clean_fidelity" not in sig  # never certifies clean off a foreign artifact


def test_fidelity_mirrored_vera_constants_match_source() -> None:
    """FIX-4 anti-drift: the hand-mirrored Vera constants in ``app/quality/signals.py`` are
    tied to Vera's REAL values, so a future Vera rename reds THIS test rather than silently
    making the reader mis-count O/I/A or leave ``verdict_halts`` permanently False. Mirrors
    the Q2.2 ``_ENV_TRUTHY`` anti-drift discipline."""
    import inspect

    import app.specialists.vera._act as vera_act
    from app.quality.signals import (
        _FIDELITY_HALT_STATUS,
        _FIDELITY_TRACE_SCHEMA,
        _OIA_CATEGORIES,
    )

    # O/I/A category set tied to Vera's real OIA constant (direct).
    assert frozenset(vera_act.OIA) == _OIA_CATEGORIES
    # The halt status + schema tag are the exact strings Vera's act() emits (source-tied).
    act_src = inspect.getsource(vera_act.act)
    assert f'"{_FIDELITY_HALT_STATUS}"' in act_src, (
        "Vera verdict halt status renamed — update _FIDELITY_HALT_STATUS in signals.py"
    )
    assert f'"{_FIDELITY_TRACE_SCHEMA}"' in act_src, (
        "Vera trace schema_version renamed — update _FIDELITY_TRACE_SCHEMA in signals.py"
    )


def test_trace_honesty_reads_plain_json_dict_and_string() -> None:
    """A trace read as PLAIN data (dict) AND as a JSON-CONTENT ``str`` (not a path) — no
    app import at app.quality module scope; both read the same real trace (Q2.2 FIX-4:
    a JSON-content string is not silently misread as 'no trace')."""
    as_dict = fidelity_trace_honesty_signal(_fail_trace())
    as_str = fidelity_trace_honesty_signal(json.dumps(_fail_trace()))
    assert as_dict["is_clean_fidelity"] is False
    assert as_str["trace_present"] is True and as_str["is_clean_fidelity"] is False


def test_trace_honesty_reads_path(tmp_path) -> None:
    p = tmp_path / "trace.json"
    p.write_text(json.dumps(_clean_trace()), encoding="utf-8")
    sig = fidelity_trace_honesty_signal(str(p))
    assert sig["trace_present"] is True and sig["is_clean_fidelity"] is True


def test_trace_honesty_status_unavailable_when_predicate_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-4: if ``vera._act`` cannot be imported the reader reports
    ``status='unavailable'`` + ``fidelity_fail_predicate_wired=False`` — never wiring-absent
    as clean."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "app.specialists.vera._act", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.specialists.vera._act":
            raise ImportError("seeded: vera._act unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = fidelity_trace_honesty_signal(None)
    assert sig["status"] == "unavailable"
    assert sig["fidelity_fail_predicate_wired"] is False


# =========================== FT3 — audit honesty (WARN transparency) ============ #


def test_audit_honesty_labels_warn_only_with_claim_fence() -> None:
    sig = fidelity_audit_honesty_signal()
    assert sig["status"] == "ok"
    assert sig["mode"] == "warn_only"
    assert sig["labels_warn_only"] is True
    assert sig["has_claim_fence"] is True
    assert sig["advisory_transparency"] is True
    assert sig["gates_production"] is False  # honest self-labelling is NOT a gate (FT1)
    # judgment-with-evidence → no mechanical clean-level award.
    assert level_from_signal("fidelity_audit_honesty", sig) is None


def test_audit_honesty_injectable_tripwire() -> None:
    """A seeded tripwire missing the claim fence honestly reads ``advisory_transparency``
    False (a warn_only with no scoping fence is not the honest advisory posture)."""
    sig = fidelity_audit_honesty_signal(tripwire={"mode": "warn_only"})
    assert sig["labels_warn_only"] is True
    assert sig["has_claim_fence"] is False
    assert sig["advisory_transparency"] is False


def test_audit_honesty_status_unavailable_when_constant_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins
    import sys

    monkeypatch.delitem(
        sys.modules, "app.specialists._shared.source_fidelity_audit", raising=False
    )
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.specialists._shared.source_fidelity_audit":
            raise ImportError("seeded: source_fidelity_audit unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    assert fidelity_audit_honesty_signal()["status"] == "unavailable"


# =========================== leak-count reader ================================== #


def test_fidelity_leak_count_real_repo_is_one() -> None:
    sig = fidelity_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["fidelity_leak_count"] == 1


def test_fidelity_leak_count_fixture(tmp_path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Fidelity-Trust Scorecard Leak Registry\n\n"
        "- fid_leak: alpha\n- fid_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- fid_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert fidelity_leak_count_signal(p)["fidelity_leak_count"] == 2


def test_fidelity_leak_count_ignores_other_namespaces(tmp_path) -> None:
    """The ``fid_leak:`` reader must NOT count ``did_leak:`` / ``cost_leak:`` / ``cov_leak:``
    tags."""
    doc = (
        "## Fidelity-Trust Scorecard Leak Registry\n\n"
        "- fid_leak: only-this\n"
        "- did_leak: not-counted\n"
        "- cost_leak: not-counted\n"
        "- cov_leak: not-counted\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert fidelity_leak_count_signal(p)["fidelity_leak_count"] == 1


# =========================== GL-13 cross-dimensional =========================== #


def test_fidelity_leak_aggregates_into_shared_ranked_list() -> None:
    """GL-13: the fidelity_trust learner-trust leak aggregates into the ONE shared ranked
    list (DID + cost + coverage + fidelity) and sorts AFTER the contiguous paid-walk
    block."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    lanes = [e["lane"] for e in ranked]
    dims = [e["dimension"] for e in ranked]
    fid_slug = "fidelity-trust-semantic-fence-warn-only-never-gates"
    assert fid_slug in slugs
    fid_idx = slugs.index(fid_slug)
    assert lanes[fid_idx] == "learner-trust"
    # every paid-walk leak sorts strictly BEFORE the fidelity learner-trust leak.
    paid_block = [i for i, ln in enumerate(lanes) if ln == "paid-walk"]
    assert paid_block == list(range(len(paid_block)))  # contiguous at front
    assert fid_idx > max(paid_block)
    # FIVE dimensions now contribute (cross-dimensional; Q3.1 added capability_honesty).
    assert set(dims) == {
        _DID_KEY,
        _COST_KEY,
        _COVERAGE_KEY,
        _FIDELITY_KEY,
        "capability_honesty",
    }
    assert len(ranked) == 9  # 5 DID + 1 cost + 1 coverage + 1 fidelity + 1 capability


def test_leak_coverage_clean_with_fidelity_dimension() -> None:
    """The coverage guard stays clean: fidelity_trust declares open_leaks=1 AND carries a
    ``leaks`` list, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_fidelity_dimension_with_no_code_change() -> None:
    """AC1/AC5: ``render_scorecard_final_report`` picks up fidelity_trust automatically —
    its Band row, its per-criterion trace, its ranked leak, and its ▬ baseline trend all
    render with NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Fidelity-trust | C |" in out
    assert "fidelity-trust-semantic-fence-warn-only-never-gates" in out
    assert "| Fidelity-trust | ▬ baseline |" in out
    assert "| Fidelity-trust | semantic_fence_gating_on | weak | 1/4 |" in out
    assert "/100" not in out  # never a false-precise headline

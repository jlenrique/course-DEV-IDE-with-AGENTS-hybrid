"""Story Q2.2 — coverage_honesty signal readers + cross-dimensional integration
(hermetic + real). No live calls, no ``--run-live``.

The coverage_honesty dimension is scored from the EXISTING coverage emitters (GL-15 —
reuse, no parallel plumbing): the coverage-gate DEFAULT posture (``coverage_gate_active`` /
``MARCUS_COVERAGE_GATE_ACTIVE``), the receipt-honesty / vacuous distinction
(``evaluate_vacuous_receipt`` + ``COVERAGE_VACUOUS_TAG`` + the ``CoverageReceipt`` model),
and the narration-obligation BLOCK term (``evaluate_coverage_gate`` +
``narration_obligation_unmet``). This module covers:

  * the three readers against hermetic fixture ``CoverageReceipt``s (PASS / FAIL /
    PASS-vacuous / narration-obligation-unmet / empty / all-excluded) AND real repo/env
    state;
  * the coverage-fence reader env-INDEPENDENCE + read-only + the seeded on/off anti-drift
    (monkeypatch ``MARCUS_COVERAGE_GATE_ACTIVE``) + the signal→level derivation;
  * the cross-dimensional GL-13 interleave (coverage learner-trust leak among DID/cost) +
    the coverage guard clean on the real repo;
  * the deterministic projector picking up the new dimension with NO projector change.

The honesty-pin RED-under-seeded proofs (coverage-fence-claim, coverage leak-count + slug
identity, arithmetic, three-namespace disjointness) live in
``test_scorecard_honesty_pins.py`` (the registered pins).
"""

from __future__ import annotations

import json

import pytest

from app.marcus.lesson_plan.coverage_gate import (
    COVERAGE_VACUOUS_TAG,
    evaluate_coverage_gate,
)
from app.marcus.lesson_plan.coverage_receipt import CoverageReceipt, CoverageReceiptRow
from app.quality.report import (
    leak_coverage_gaps,
    ranked_project_leaks,
    render_scorecard_final_report,
)
from app.quality.scorecard import _COVERAGE_KEY, _DID_KEY, read_scorecard_block
from app.quality.signals import (
    coverage_fence_default_signal,
    coverage_leak_count_signal,
    coverage_narration_obligation_signal,
    coverage_receipt_honesty_signal,
    level_from_signal,
)

_COVERAGE_ENV = "MARCUS_COVERAGE_GATE_ACTIVE"
_CLEAN = {"strong", "uniform"}


# --------------------------------------------------------------------------- #
# Hermetic fixture builders (build REAL models — strict validation is the point).
# --------------------------------------------------------------------------- #
def _row(
    *,
    spid: str,
    coverage_status: str,
    must_cover: bool,
    anchor_resolved: bool = True,
    verbatim_required: bool = False,
    verbatim_absent: bool = False,
    narration_obligation_unmet: bool = False,
    planned_on_slide: bool = False,
    planned_in_narration: bool = False,
    intents: tuple[str, ...] = ("gist_on_slide",),
) -> CoverageReceiptRow:
    return CoverageReceiptRow(
        source_point_id=spid,
        component_id="c1",
        slide_key="Slide 1",
        human_label="Slide 1 / note",
        intent_set=intents,
        verbatim_required=verbatim_required,
        coverage_status=coverage_status,
        containment_verdict=None,
        vouch_level="not_assessed",
        anchor_resolved=anchor_resolved,
        verbatim_absent=verbatim_absent,
        narration_obligation_unmet=narration_obligation_unmet,
        planned_on_slide=planned_on_slide,
        planned_in_narration=planned_in_narration,
        must_cover=must_cover,
        segmentation="assertion_level",
    )


def _receipt(rows: tuple[CoverageReceiptRow, ...]) -> CoverageReceipt:
    return CoverageReceipt(segmentation="assertion_level", rows=rows)


def _pass_receipt() -> CoverageReceipt:
    """A clean PASS: a must-cover point covered on BOTH surfaces (a real join)."""
    return _receipt(
        (
            _row(
                spid="p-covered",
                coverage_status="both",
                must_cover=True,
                planned_on_slide=True,
                planned_in_narration=True,
                intents=("gist_on_slide", "detail_in_narration"),
            ),
        )
    )


def _fail_receipt() -> CoverageReceipt:
    """A FAIL (blocking) that is NOT vacuous: one covered join + one must-cover MISSING
    point with no planned surface (the deterministic must-cover hole)."""
    return _receipt(
        (
            _row(
                spid="p-covered",
                coverage_status="covered_in_narration",
                must_cover=False,
                planned_in_narration=True,
            ),
            _row(
                spid="p-missing",
                coverage_status="missing",
                must_cover=True,
                anchor_resolved=False,
                verbatim_required=True,
                intents=("detail_in_narration",),
            ),
        )
    )


def _vacuous_receipt() -> CoverageReceipt:
    """A PASS-vacuous: rows exist but ZERO join (every span missed its own surfaces), and
    NO point is must_cover — the false-PASS the must-cover gate alone is blind to."""
    return _receipt(
        (
            _row(spid="p-a", coverage_status="missing", must_cover=False),
            _row(spid="p-b", coverage_status="missing", must_cover=False),
        )
    )


def _narration_unmet_receipt() -> CoverageReceipt:
    """A must-cover detail_in_narration point carried ONLY on the slide → narration
    obligation UNMET (an independent BLOCK term); the row still joins (not vacuous)."""
    return _receipt(
        (
            _row(
                spid="p-slide-only",
                coverage_status="covered_on_slide",
                must_cover=True,
                narration_obligation_unmet=True,
                planned_on_slide=True,
                intents=("gist_on_slide", "detail_in_narration"),
            ),
        )
    )


def _excluded_receipt() -> CoverageReceipt:
    """An all-deliberately-excluded receipt: legitimate nothing-to-cover (NOT vacuous)."""
    return _receipt(
        (
            CoverageReceiptRow(
                source_point_id="p-excl",
                component_id="c1",
                slide_key="Slide 1",
                human_label="Slide 1 / note",
                intent_set=("deliberately_excluded",),
                verbatim_required=False,
                coverage_status="deliberately_excluded",
                containment_verdict=None,
                vouch_level="not_assessed",
                anchor_resolved=True,
                must_cover=False,
                segmentation="assertion_level",
            ),
        )
    )


# =========================== CV1 — coverage-fence default ======================= #


def test_coverage_fence_default_is_opt_in_weak(monkeypatch: pytest.MonkeyPatch) -> None:
    """Real production-preset posture: MARCUS_COVERAGE_GATE_ACTIVE unset →
    ``coverage_gate_active()==False`` → ``default_coverage_enforced`` False → ``weak``."""
    monkeypatch.delenv(_COVERAGE_ENV, raising=False)
    sig = coverage_fence_default_signal()
    assert sig["status"] == "ok"
    assert sig["default_coverage_enforced"] is False
    assert level_from_signal("coverage_fence_default_on", sig) == "weak"


def test_coverage_fence_close_path_is_reader_reachable() -> None:
    """The reader is NOT a hardcoded constant and the close-path is REACHABLE: an
    injectable clean env → ``weak`` (preset default), an env carrying the gate ON →
    ``strong`` (so closing the leak legitimately earns strong; the pin AGREES rather than
    false-REDs the operator who wires it on)."""
    off = coverage_fence_default_signal(env={})  # preset-default posture: off → weak
    assert off["default_coverage_enforced"] is False
    assert level_from_signal("coverage_fence_default_on", off) == "weak"
    on = coverage_fence_default_signal(env={_COVERAGE_ENV: "1"})  # gate wired on
    assert on["default_coverage_enforced"] is True
    assert level_from_signal("coverage_fence_default_on", on) == "strong"


def test_coverage_fence_reader_is_read_only_no_env_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The reader NEVER mutates ``os.environ`` (env-independent injectable pattern). Any
    variant leaves the ambient env byte-identical."""
    import os

    monkeypatch.setenv(_COVERAGE_ENV, "1")
    before = dict(os.environ)
    coverage_fence_default_signal()
    coverage_fence_default_signal(env={})
    coverage_fence_default_signal(env={_COVERAGE_ENV: "1"})
    assert dict(os.environ) == before
    assert os.environ[_COVERAGE_ENV] == "1"  # untouched


def test_coverage_fence_tracks_real_gate_on_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Anti-drift, env-independent: the live (env=None) reader tracks the REAL
    ``coverage_gate_active()`` under monkeypatch on/off."""
    from app.marcus.orchestrator.coverage_gate_wiring import coverage_gate_active

    monkeypatch.delenv(_COVERAGE_ENV, raising=False)
    assert coverage_gate_active() is False
    assert coverage_fence_default_signal()["default_coverage_enforced"] is False
    for truthy in ("1", "true", "yes", "on"):
        monkeypatch.setenv(_COVERAGE_ENV, truthy)
        assert coverage_gate_active() is True
        assert coverage_fence_default_signal()["default_coverage_enforced"] is True


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "default_coverage_enforced": True}, "strong"),
        ({"status": "ok", "default_coverage_enforced": False}, "weak"),
        ({"status": "ok", "default_coverage_enforced": None}, "unavailable"),
        ({"status": "unavailable"}, "unavailable"),
        ("garbage", "unavailable"),
        ({}, "unavailable"),
    ],
)
def test_level_cv_coverage_fence_total(sig: object, expected: str) -> None:
    got = level_from_signal("coverage_fence_default_on", sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


# =========================== CV2 — receipt honesty ============================== #


def test_receipt_honesty_wiring_only_when_no_receipt() -> None:
    sig = coverage_receipt_honesty_signal(None)
    assert sig["status"] == "ok"
    assert sig["vacuous_guard_wired"] is True
    assert sig["vacuous_tag"] == COVERAGE_VACUOUS_TAG
    assert sig["receipt_present"] is False
    # judgment-with-evidence → no mechanical clean-level award.
    assert level_from_signal("coverage_receipt_honesty", sig) is None


def test_receipt_honesty_clean_pass() -> None:
    sig = coverage_receipt_honesty_signal(_pass_receipt())
    assert sig["is_vacuous"] is False
    assert sig["joined_row_count"] == 1
    assert sig["vacuous_block_reason"] is None
    assert sig["gate_blocks"] is False  # a real PASS: the gate does not block
    assert sig["is_clean_pass"] is True


def test_receipt_honesty_flags_vacuous_pass() -> None:
    """A vacuous receipt (rows-but-zero-joined) is honestly NOT a clean pass — even though
    NO point is must_cover (the must-cover gate alone is blind to it)."""
    rec = _vacuous_receipt()
    assert evaluate_coverage_gate(rec) == ()  # must-cover gate is silent...
    sig = coverage_receipt_honesty_signal(rec)
    assert sig["is_vacuous"] is True  # ...but the vacuous guard is not
    assert sig["joined_row_count"] == 0
    assert sig["vacuous_block_reason"] is not None
    assert sig["is_clean_pass"] is False


def test_receipt_honesty_fail_receipt_is_not_clean() -> None:
    """FIX-1: a receipt the must-cover gate BLOCKS is a real FAIL — NEVER a clean pass,
    even when the vacuous guard is silent (a covered row makes joined>0, non-vacuous). The
    vacuous guard alone is blind to this; ``is_clean_pass`` must consult
    ``evaluate_coverage_gate``. (Toothless before the fix: the old field wrongly read
    True.)"""
    rec = _fail_receipt()
    assert len(evaluate_coverage_gate(rec)) == 1  # the must-cover hole blocks
    sig = coverage_receipt_honesty_signal(rec)
    assert sig["joined_row_count"] == 1  # the one covered row joined → not vacuous
    assert sig["is_vacuous"] is False
    assert sig["gate_blocks"] is True  # the must-cover gate BLOCKS this receipt
    assert sig["is_clean_pass"] is False  # …so it is NOT a clean pass (FIX-1)


def test_receipt_honesty_empty_when_content_exists_is_not_clean() -> None:
    """FIX-3: a present-but-EMPTY receipt against note-bearing content is NOT a clean pass
    (a non-empty-structure guard) — while a legitimately-empty receipt (no content) is."""
    empty = _receipt(())
    legit = coverage_receipt_honesty_signal(empty, note_bearing_content_exists=False)
    assert legit["vacuous_block_reason"] is None  # legitimately empty → pass
    blocked = coverage_receipt_honesty_signal(empty, note_bearing_content_exists=True)
    assert blocked["vacuous_block_reason"] is not None  # empty-when-content → NOT a pass
    assert blocked["is_clean_pass"] is False


def test_receipt_honesty_all_excluded_is_legitimate_pass() -> None:
    sig = coverage_receipt_honesty_signal(_excluded_receipt())
    assert sig["all_deliberately_excluded"] is True
    assert sig["is_vacuous"] is False
    assert sig["vacuous_block_reason"] is None  # legitimate nothing-to-cover


def test_receipt_honesty_reads_plain_json_dict() -> None:
    """A receipt read as PLAIN data (dict) — no app import at app.quality module scope;
    the reader rehydrates via a deferred import."""
    payload = json.loads(json.dumps(_pass_receipt().model_dump(mode="json")))
    sig = coverage_receipt_honesty_signal(payload)
    assert sig["receipt_present"] is True and sig["is_clean_pass"] is True


def test_receipt_honesty_status_unavailable_when_guard_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-4: if ``coverage_gate`` cannot be imported the reader reports
    ``status='unavailable'`` + ``vacuous_guard_wired=False`` — never wiring-absent as ok."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "app.marcus.lesson_plan.coverage_gate", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.marcus.lesson_plan.coverage_gate":
            raise ImportError("seeded: coverage_gate unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = coverage_receipt_honesty_signal(None)
    assert sig["status"] == "unavailable"
    assert sig["vacuous_guard_wired"] is False


# =========================== CV3 — narration obligation ========================= #


def test_narration_obligation_wiring_fact() -> None:
    sig = coverage_narration_obligation_signal(None)
    assert sig["status"] == "ok"
    assert sig["narration_obligation_gate_wired"] is True
    assert sig["receipt_present"] is False
    assert level_from_signal("coverage_narration_obligation", sig) is None


def test_narration_obligation_blocks_slide_only_must_cover() -> None:
    """A must-cover detail_in_narration point carried only on the slide is an UNMET
    narration obligation → an independent BLOCK term (FIX-2)."""
    rec = _narration_unmet_receipt()
    sig = coverage_narration_obligation_signal(rec)
    assert sig["narration_obligation_unmet_rows"] == 1
    assert sig["blocking_rows"] == 1
    assert sig["blocking_narration_obligation_rows"] == 1
    # the gate agrees: exactly one blocking row, and it is the narration-unmet one.
    assert len(evaluate_coverage_gate(rec)) == 1


def test_narration_obligation_quiet_on_clean_receipt() -> None:
    sig = coverage_narration_obligation_signal(_pass_receipt())
    assert sig["narration_obligation_unmet_rows"] == 0
    assert sig["blocking_rows"] == 0


def test_narration_obligation_status_unavailable_when_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-4: an unimportable gate degrades to ``status='unavailable'``."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "app.marcus.lesson_plan.coverage_gate", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "app.marcus.lesson_plan.coverage_gate":
            raise ImportError("seeded: coverage_gate unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = coverage_narration_obligation_signal(None)
    assert sig["status"] == "unavailable"
    assert sig["narration_obligation_gate_wired"] is False


# =========================== leak-count reader ================================== #


def test_coverage_leak_count_real_repo_is_one() -> None:
    sig = coverage_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["coverage_leak_count"] == 1


def test_coverage_leak_count_fixture(tmp_path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Coverage-Honesty Scorecard Leak Registry\n\n"
        "- cov_leak: alpha\n- cov_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- cov_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert coverage_leak_count_signal(p)["coverage_leak_count"] == 2


def test_coverage_leak_count_ignores_other_namespaces(tmp_path) -> None:
    """The ``cov_leak:`` reader must NOT count ``did_leak:`` / ``cost_leak:`` tags."""
    doc = (
        "## Coverage-Honesty Scorecard Leak Registry\n\n"
        "- cov_leak: only-this\n"
        "- did_leak: not-counted\n"
        "- cost_leak: not-counted\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert coverage_leak_count_signal(p)["coverage_leak_count"] == 1


# =========================== GL-13 cross-dimensional =========================== #


def test_coverage_leak_aggregates_into_shared_ranked_list() -> None:
    """GL-13: the coverage_honesty learner-trust leak aggregates into the ONE shared
    ranked list (DID + cost + coverage) and sorts AFTER the contiguous paid-walk block."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    lanes = [e["lane"] for e in ranked]
    dims = [e["dimension"] for e in ranked]
    cov_slug = "coverage-honesty-gate-opt-in-default-off"
    assert cov_slug in slugs
    cov_idx = slugs.index(cov_slug)
    assert lanes[cov_idx] == "learner-trust"
    # every paid-walk leak sorts strictly BEFORE the coverage learner-trust leak.
    paid_block = [i for i, ln in enumerate(lanes) if ln == "paid-walk"]
    assert paid_block == list(range(len(paid_block)))  # contiguous at front
    assert cov_idx > max(paid_block)
    # THREE dimensions now contribute (cross-dimensional, not DID/cost-only).
    assert set(dims) == {_DID_KEY, "cost_efficiency", _COVERAGE_KEY}


def test_leak_coverage_clean_with_coverage_dimension() -> None:
    """The coverage guard stays clean: coverage_honesty declares open_leaks=1 AND carries
    a ``leaks`` list, so it is registered on the shared ranked list (no gap)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_coverage_dimension_with_no_code_change() -> None:
    """AC5: ``render_scorecard_final_report`` picks up coverage_honesty automatically —
    its Band row, its per-criterion trace, its ranked leak, and its ▬ baseline trend all
    render with NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"coverage": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Coverage-honesty | C |" in out
    assert "coverage-honesty-gate-opt-in-default-off" in out
    assert "| Coverage-honesty | ▬ baseline |" in out
    assert "| Coverage-honesty | coverage_fence_default_on | weak | 1/4 |" in out
    assert "/100" not in out  # never a false-precise headline


# =========================== review-fix RED-first proofs ======================= #


@pytest.mark.parametrize("bad_env", [["not", "a", "mapping"], {_COVERAGE_ENV: 1}])
def test_coverage_fence_injectable_env_is_fail_soft(bad_env: object) -> None:
    """FIX-2 RED-first: the injectable-env branch NEVER raises (the never-raises contract).
    A non-Mapping env (a list → ``.get`` AttributeError) and a non-str env value
    (``{KEY: 1}`` → a malformed env mapping) both degrade to ``status='unavailable'`` — no
    escaping AttributeError, and never a false-clean posture."""
    sig = coverage_fence_default_signal(env=bad_env)  # must not raise
    assert sig["status"] == "unavailable"
    assert "default_coverage_enforced" not in sig
    assert level_from_signal("coverage_fence_default_on", sig) == "unavailable"


def test_coverage_fence_injectable_env_str_values_still_work() -> None:
    """The str-typed happy path is unchanged: a clean mapping → weak, a wired-on str → strong."""
    assert coverage_fence_default_signal(env={})["default_coverage_enforced"] is False
    on = coverage_fence_default_signal(env={_COVERAGE_ENV: "1"})
    assert on["default_coverage_enforced"] is True


@pytest.mark.parametrize("token", ["1", "true", "yes", "on", "TRUE", "On"])
def test_coverage_fence_injectable_truthy_vocab_matches_real_env_true(token: str) -> None:
    """FIX-5 anti-drift: the injectable-env truthy resolution agrees with the REAL gate's
    ``_env_true`` for every token in the shared vocabulary — so a future vocabulary change
    to the real gate cannot silently drift the injectable reading."""
    import os

    from app.marcus.orchestrator.coverage_gate_wiring import (
        COVERAGE_GATE_ACTIVE_ENV,
        _env_true,
    )

    # Route the token through the REAL gate (via os.environ) to get the ground truth...
    saved = os.environ.get(COVERAGE_GATE_ACTIVE_ENV)
    try:
        os.environ[COVERAGE_GATE_ACTIVE_ENV] = token
        real = _env_true(COVERAGE_GATE_ACTIVE_ENV)
    finally:
        if saved is None:
            os.environ.pop(COVERAGE_GATE_ACTIVE_ENV, None)
        else:
            os.environ[COVERAGE_GATE_ACTIVE_ENV] = saved
    # ...and the injectable-env reader must agree (read-only, no ambient dependence).
    injected = coverage_fence_default_signal(env={_COVERAGE_ENV: token})
    assert injected["default_coverage_enforced"] is real is True


def test_narration_obligation_gate_wired_checks_real_predicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FIX-3 RED-first: ``narration_obligation_gate_wired`` EXERCISES the real
    ``_is_blocking`` predicate, not mere model-field presence. Monkeypatch ``_is_blocking``
    to a version that DROPS the ``narration_obligation_unmet`` term (keeping the model
    field) → the reader flips ``gate_wired`` to False (a false wiring claim is caught)."""
    import app.marcus.lesson_plan.coverage_gate as cg

    def _predicate_without_narration_term(row) -> bool:
        if not row.must_cover:
            return False
        no_planned = not (row.planned_on_slide or row.planned_in_narration)
        return (row.coverage_status == "missing" and no_planned) or row.verbatim_absent

    # Sanity: the REAL predicate reports wired.
    assert coverage_narration_obligation_signal(None)["narration_obligation_gate_wired"] is True
    monkeypatch.setattr(cg, "_is_blocking", _predicate_without_narration_term)
    sig = coverage_narration_obligation_signal(None)
    assert sig["narration_obligation_gate_wired"] is False  # dropped term → caught


def test_receipt_honesty_reads_json_content_string() -> None:
    """FIX-4: a receipt passed as a JSON-CONTENT ``str`` (not a filesystem path) is read as
    a real receipt — NOT silently misread as 'no receipt' via an OSError."""
    text = json.dumps(_pass_receipt().model_dump(mode="json"))
    sig = coverage_receipt_honesty_signal(text)
    assert sig["receipt_present"] is True
    assert sig["is_clean_pass"] is True

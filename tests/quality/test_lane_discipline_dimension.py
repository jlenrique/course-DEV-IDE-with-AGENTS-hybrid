"""Story Q3.3 — lane_discipline signal reader + cross-dimensional integration (hermetic + real).

The lane_discipline dimension SCORES the already-CI-enforced lane isolation from the LIVE
import-linter result via the SHIPPED ``importlinter.api`` (GL-16 — NOT the ``lint-imports`` CLI on
PATH). LD1 is ``signal-derived``:

  * LD1 (``import_linter_lane_signal``) — runs the ``pyproject.toml [tool.importlinter]`` contracts
    programmatically (``read_user_options`` + ``create_report``) and reads the REAL kept/broken
    RESULT: 0 broken → ``strong`` (18/0 today); broken > 0 → ``weak`` (a real forbidden-import /
    lane-isolation regression). It keys off the REAL broken-count, NOT the DECLARED contract count.

The read is DETERMINISTIC (import-linter breaks ONLY on a real import-graph regression — a
legitimate persisted-level signal, unlike Q3.2's volatile git-drift), BOUNDED (the app/ graph build
is ~seconds, guarded), and FAIL-SOFT (importlinter unavailable / config missing / run error /
nothing-checked → ``unavailable``, NEVER clean).

This module covers: the reader against the REAL import-linter (18/0) + hermetic seeded fixtures; the
GL-16 shipped-dep path (NOT the CLI — no subprocess / no ``lint_imports`` wrapper at read time); the
consult-real-result / nothing-checked→unavailable discipline; the isolating pin (declared-count vs
real-result); determinism; the signal→level derivation; the cross-dimensional GL-13 interleave; the
⚠️ ZERO-LEAK-PATH lock-in (the SECOND dimension to carry 0 leaks); and the deterministic projector
picking up the 7th dimension with NO projector change. The honesty-pin RED-under-seeded proofs live
in ``test_scorecard_honesty_pins``.

**⛔ READ-ONLY.** This dimension SCORES the lane discipline; it CONSUMES the import-linter contracts
read-only and NEVER edits a contract or a lane-matrix / taxonomy doc. No live-network / paid calls.
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
from app.quality.scorecard import _LANE_KEY, read_scorecard_block
from app.quality.signals import (
    import_linter_lane_signal,
    lane_leak_count_signal,
    level_from_signal,
)

_CLEAN = {"strong", "uniform"}
_LD1_KEY = "lane_discipline_import_linter"
_DID_KEY = "dynamic_intelligence_vs_determinism"
_COST_KEY = "cost_efficiency"
_COVERAGE_KEY = "coverage_honesty"
_FIDELITY_KEY = "fidelity_trust"
_CAPABILITY_KEY = "capability_honesty"
_TRACKER_KEY = "tracker_coherence"


def _fake_report(*, kept: Any, broken: Any, could_not_run: bool = False) -> SimpleNamespace:
    """A hermetic ``importlinter`` ``Report``-like object carrying the count attributes the
    reader reads — proves the object path (a real Report or a fake) without running the linter."""
    return SimpleNamespace(kept_count=kept, broken_count=broken, could_not_run=could_not_run)


# =========================== LD1 — the LIVE import-linter reader (real) ========= #


def test_ld1_real_repo_is_clean_strong() -> None:
    """Real posture: running the ``pyproject.toml [tool.importlinter]`` contracts via the SHIPPED
    ``importlinter.api`` yields 18 kept / 0 broken today → ``lane_discipline_clean`` True →
    ``strong``. This is the honest baseline (the CI-enforced lane isolation holds)."""
    sig = import_linter_lane_signal()
    assert sig["status"] == "ok"
    assert sig["broken_count"] == 0
    assert sig["kept_count"] >= 1
    assert sig["contracts_total"] == sig["kept_count"] + sig["broken_count"]
    assert sig["lane_discipline_clean"] is True
    assert level_from_signal(_LD1_KEY, sig) == "strong"


def test_ld1_real_repo_honest_invariant_is_zero_broken() -> None:
    """FIX-G: pin the HONEST INVARIANT (``broken_count == 0`` — no forbidden import), NOT the
    declared count. A legitimate 19th lane contract (still clean, 19/0) leaves discipline unchanged
    and must NOT red this test — so we assert ``broken == 0`` (the "consult-real-result, not
    declared-count" principle applied to the test itself), with ``kept`` merely informational."""
    sig = import_linter_lane_signal()
    assert sig["broken_count"] == 0  # the honest invariant — no lane regression
    assert sig["kept_count"] >= 1  # informational: at least the declared contracts ran


def test_ld1_via_shipped_dep_not_the_cli_no_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    """GL-16 (the point): the reader reads the result via the SHIPPED ``importlinter.api``
    (``read_user_options`` + ``create_report``), NOT the ``lint-imports`` CLI on PATH. Monkeypatch
    ``subprocess.run`` to RAISE — the live reader is UNAFFECTED (still ok / strong), proving it
    does NOT shell out to the CLI. (import-linter builds the graph in-process via grimp — no
    subprocess.)"""
    import subprocess

    def _boom(*args, **kwargs):
        raise AssertionError("lane_discipline must not shell out to the lint-imports CLI (GL-16)")

    monkeypatch.setattr(subprocess, "run", _boom)
    sig = import_linter_lane_signal()  # in-process importlinter.api read — no subprocess
    assert sig["status"] == "ok"
    assert level_from_signal(_LD1_KEY, sig) == "strong"


def test_ld1_does_not_route_through_lint_imports_cli_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GL-16: even the in-process CLI wrapper ``use_cases.lint_imports`` is NOT used — monkeypatch
    it to raise and the live reader still works (it calls ``create_report`` directly)."""
    from importlinter.api import use_cases

    def _boom(*args, **kwargs):
        raise AssertionError("the reader must not call the lint_imports CLI wrapper (GL-16)")

    monkeypatch.setattr(use_cases, "lint_imports", _boom)
    sig = import_linter_lane_signal()
    assert sig["status"] == "ok"
    assert level_from_signal(_LD1_KEY, sig) == "strong"


def test_ld1_is_deterministic_across_runs() -> None:
    """Determinism: two live reads yield the SAME kept/broken (import-linter breaks only on a real
    import-graph regression — it does not flap per-commit / on wall-clock time)."""
    a = import_linter_lane_signal()
    b = import_linter_lane_signal()
    assert (a["kept_count"], a["broken_count"]) == (b["kept_count"], b["broken_count"])
    assert level_from_signal(_LD1_KEY, a) == level_from_signal(_LD1_KEY, b) == "strong"


# =========================== LD1 — seeded fixtures (broken / unavailable) ======= #


@pytest.mark.parametrize(
    ("report", "expected_level"),
    [
        ({"kept": 18, "broken": 0}, "strong"),  # clean → strong
        ({"kept": 17, "broken": 1}, "weak"),  # one broken → weak (a real regression)
        ({"kept": 15, "broken": 3}, "weak"),  # several broken → weak
        ({"kept": 0, "broken": 18}, "weak"),  # all broken → weak
    ],
)
def test_ld1_broken_count_drives_level(report: dict[str, Any], expected_level: str) -> None:
    """The level derives from the REAL broken-count: 0 → strong; broken > 0 → weak. Seeded via a
    hermetic report mapping (no live run) — the level logic is exercised in isolation."""
    sig = import_linter_lane_signal(report)
    assert sig["status"] == "ok"
    assert level_from_signal(_LD1_KEY, sig) == expected_level
    if expected_level != "strong":
        assert level_from_signal(_LD1_KEY, sig) not in _CLEAN


def test_ld1_accepts_report_object_path() -> None:
    """The reader accepts a real ``importlinter`` ``Report``-like object (``.kept_count`` /
    ``.broken_count``) as well as a mapping — a broken fake object → weak, a clean one → strong."""
    clean = import_linter_lane_signal(_fake_report(kept=18, broken=0))
    dirty = import_linter_lane_signal(_fake_report(kept=17, broken=1))
    assert level_from_signal(_LD1_KEY, clean) == "strong"
    assert level_from_signal(_LD1_KEY, dirty) == "weak"


def test_ld1_isolating_declared_count_vs_real_result() -> None:
    """The isolating pin (Q2.3 FT2 lesson): SAME total contract count (18), only the RESULT
    differs — a declared-count reader would say strong for both, but the real reader consults the
    kept/broken RESULT and drops the broken one to weak."""
    clean = import_linter_lane_signal({"kept": 18, "broken": 0})
    broken = import_linter_lane_signal({"kept": 15, "broken": 3})
    assert clean["contracts_total"] == broken["contracts_total"] == 18
    assert level_from_signal(_LD1_KEY, clean) == "strong"
    assert level_from_signal(_LD1_KEY, broken) == "weak"


@pytest.mark.parametrize(
    ("report", "label"),
    [
        ({"kept": 18, "broken": 0, "could_not_run": True}, "could_not_run"),
        ({"kept": 0, "broken": 0}, "nothing-checked"),
        ({"kept": 18, "broken": True}, "bool-broken-malformed"),
        ({"kept": True, "broken": 0}, "bool-kept-malformed"),
        ({"kept": 18, "broken": -1}, "negative-broken"),
        ({"kept": "eighteen", "broken": 0}, "non-int-kept"),
        ({"kept": 18}, "missing-broken"),
    ],
)
def test_ld1_nothing_checked_or_malformed_is_unavailable(report: dict, label: str) -> None:
    """Consult-real-result / nothing-checked→unavailable: a could_not_run report, a
    nothing-evaluated (0/0) report, or a malformed count degrades to ``unavailable`` — NEVER a
    false-clean. 'we could not actually run the linter' is UNKNOWN, never clean."""
    sig = import_linter_lane_signal(report)
    assert sig["status"] == "unavailable", f"{label}: expected unavailable, got {sig}"
    assert level_from_signal(_LD1_KEY, sig) == "unavailable"


def test_ld1_status_unavailable_when_importlinter_unimportable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If ``importlinter.api`` cannot be imported / raises, the reader reports
    ``status='unavailable'`` — never wiring-absent as a clean or silently-strong posture."""
    import builtins
    import sys

    monkeypatch.delitem(sys.modules, "importlinter.api", raising=False)
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "importlinter.api" or name.startswith("importlinter.application"):
            raise ImportError("seeded: importlinter unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    sig = import_linter_lane_signal()  # report=None → live path, which is now blocked
    assert sig["status"] == "unavailable"
    assert level_from_signal(_LD1_KEY, sig) == "unavailable"


# =========================== signal→level totals ============================== #


@pytest.mark.parametrize(
    ("sig", "expected"),
    [
        ({"status": "ok", "kept_count": 18, "broken_count": 0}, "strong"),
        ({"status": "ok", "kept_count": 17, "broken_count": 1}, "weak"),
        ({"status": "ok", "kept_count": 0, "broken_count": 0}, "unavailable"),  # nothing checked
        ({"status": "ok", "kept_count": 18, "broken_count": True}, "unavailable"),
        ({"status": "ok", "kept_count": 18}, "unavailable"),  # missing broken
        ({"status": "unavailable"}, "unavailable"),
        ({}, "unavailable"),
        ("garbage", "unavailable"),
    ],
)
def test_ld1_level_totals(sig: Any, expected: str) -> None:
    """LD1 returns a real level for every signal and never awards a clean level on a non-ok /
    malformed / nothing-checked signal."""
    got = level_from_signal(_LD1_KEY, sig)
    assert got == expected
    if expected != "strong":
        assert got not in _CLEAN


def test_band_ceiling_is_b() -> None:
    """The single signal-derived criterion caps at ``strong`` (3) mechanically — ``level_from_
    signal`` never awards ``uniform``/4. Max = 3/4 = 75 → Band B. A is structurally unreachable."""
    clean = import_linter_lane_signal({"kept": 18, "broken": 0})
    assert level_from_signal(_LD1_KEY, clean) == "strong"  # never 'uniform'
    assert round(3 / 4 * 100) == 75  # → Band B (A unreachable)


def test_ld1_criterion_is_signal_derived_in_the_block() -> None:
    """LD1 carries ``derivation: signal-derived`` with a real reader + evidence_ref, and
    ``level_from_signal`` returns a real level (not None)."""
    crit = read_scorecard_block()["dimensions"][_LANE_KEY]["criteria"]
    assert set(crit) == {_LD1_KEY}
    c = crit[_LD1_KEY]
    assert c["derivation"] == "signal-derived"
    assert c["signal"]["reader"] == "app.quality.signals.import_linter_lane_signal"
    assert isinstance(c["evidence_ref"], str) and c["evidence_ref"]
    assert level_from_signal(_LD1_KEY, import_linter_lane_signal()) is not None


# =========================== lane leak-count reader (zero-leak) =============== #


def test_lane_leak_count_real_repo_is_one() -> None:
    """The real repo carries 1 ``lane_leak:`` tag — the coverage-completeness-UNVERIFIED gap
    (declared-clean ≠ verified-clean-coverage). The reader returns a clean ``1``."""
    sig = lane_leak_count_signal()
    assert sig["status"] == "ok"
    assert sig["lane_leak_count"] == 1


def test_lane_leak_count_fixture(tmp_path: Path) -> None:
    doc = (
        "# Deferred Inventory (fixture)\n\n"
        "## Lane-Discipline Scorecard Leak Registry\n\n"
        "- lane_leak: alpha\n- lane_leak: beta\n\n"
        "## Closed Entries — Archived\n\n- lane_leak: archived-must-not-count\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert lane_leak_count_signal(p)["lane_leak_count"] == 2


def test_lane_leak_count_ignores_other_namespaces(tmp_path: Path) -> None:
    """The ``lane_leak:`` reader must NOT count the other six namespaces."""
    doc = (
        "## Lane-Discipline Scorecard Leak Registry\n\n"
        "- lane_leak: only-this\n"
        "- did_leak: nope\n- cost_leak: nope\n- cov_leak: nope\n"
        "- fid_leak: nope\n- cap_leak: nope\n- trk_leak: nope\n"
    )
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    assert lane_leak_count_signal(p)["lane_leak_count"] == 1


def test_lane_leak_count_zero_when_registry_empty(tmp_path: Path) -> None:
    """⚠️ ZERO-LEAK PATH: a registry with NO ``lane_leak:`` line → count 0 — a clean ``0``, not
    ``unavailable`` (this is the SECOND dimension that legitimately carries zero leaks)."""
    doc = "## Lane-Discipline Scorecard Leak Registry\n\nZero open lane leaks (18/0 clean).\n"
    p = tmp_path / "inv.md"
    p.write_text(doc, encoding="utf-8")
    sig = lane_leak_count_signal(p)
    assert sig["status"] == "ok"
    assert sig["lane_leak_count"] == 0


def test_lane_leak_count_unavailable_on_unreadable_file(tmp_path: Path) -> None:
    """Fail-soft: an unreadable inventory path → ``{"status": "unavailable", "lane_leak_count":
    None}`` (never a fabricated 0)."""
    missing = tmp_path / "does-not-exist.md"
    sig = lane_leak_count_signal(missing)
    assert sig["status"] == "unavailable"
    assert sig["lane_leak_count"] is None


# =========================== GL-13 cross-dimensional (zero-leak) =============== #


def test_lane_leak_aggregates_into_shared_ranked_list() -> None:
    """GL-13: lane_discipline's ONE governance leak (coverage-completeness UNVERIFIED) aggregates
    into the ONE shared ranked list and sorts AFTER the paid-walk AND learner-trust blocks
    (governance lane sorts last). SEVEN dimensions now contribute; the cross-dimensional total is
    12 (5 DID + 1 cost + 1 cov + 1 fid + 1 cap + 2 tracker + 1 lane)."""
    block = read_scorecard_block()
    ranked = ranked_project_leaks(block)
    slugs = [e["slug"] for e in ranked]
    lanes = [e["lane"] for e in ranked]
    dims = {e["dimension"] for e in ranked}
    lane_slug = "lane-discipline-lane-matrix-contract-coverage-unverified"
    assert lane_slug in slugs
    non_gov = [i for i, ln in enumerate(lanes) if ln in ("paid-walk", "learner-trust")]
    assert slugs.index(lane_slug) > max(non_gov)  # governance sorts after paid-walk/learner-trust
    assert lanes[slugs.index(lane_slug)] == "governance"
    assert dims == {
        _DID_KEY, _COST_KEY, _COVERAGE_KEY, _FIDELITY_KEY, _CAPABILITY_KEY, _TRACKER_KEY, _LANE_KEY,
        "calibration",
    }
    assert len(ranked) == 13  # + Q3.4 calibration's one learner-trust leak (the 8th, final dim)


def test_leak_coverage_clean_with_lane_dimension() -> None:
    """The coverage guard stays clean: lane_discipline declares ``open_leaks: 1`` AND carries a
    ``leaks`` list of length 1, so it is registered on the shared ranked list (no gap — a gap is
    ``open_leaks > 0`` AND no leaks list)."""
    assert leak_coverage_gaps(read_scorecard_block()) == []


# =========================== ⚠️ ZERO-LEAK-PATH lock-in (machinery, synthetic) === #
# The live lane_discipline dimension carries ONE leak (coverage-completeness unverified), so it is
# not itself a live 0-leak example — but the 0-leak PATH must stay locked in as MACHINERY (a future
# dimension, or lane_discipline once the coverage-verifier lands, could be 0-leak). These use
# SYNTHETIC blocks so the path is tested regardless of the live dimension's leak count.


def test_zero_leak_dimension_is_not_a_coverage_gap_synthetic() -> None:
    block = {
        "dimensions": {
            _LANE_KEY: {"label": "Lane-discipline / scope-fidelity", "open_leaks": 0, "leaks": []}
        }
    }
    assert leak_coverage_gaps(block) == []
    block2 = {"dimensions": {_LANE_KEY: {"open_leaks": 0}}}  # no leaks key at all
    assert leak_coverage_gaps(block2) == []


def test_zero_leak_count_identity_synthetic(tmp_path: Path) -> None:
    """The leak-count identity holds at 0 (the machinery): a synthetic ``open_leaks: 0`` + ``leaks:
    []`` reconciles, and the reader over an EMPTY synthetic registry returns a clean ``0``."""
    dim = {"open_leaks": 0, "leaks": []}
    assert dim["open_leaks"] == len(dim["leaks"]) == 0
    empty = tmp_path / "inv.md"
    empty.write_text("## Lane-Discipline Scorecard Leak Registry\n\n(none)\n", encoding="utf-8")
    assert lane_leak_count_signal(empty)["lane_leak_count"] == 0


def test_live_lane_leak_count_identity_reconciles_at_one() -> None:
    """The live dimension's identity holds at 1: ``open_leaks`` == ``len(leaks)`` ==
    ``lane_leak_count_signal()`` == 1 (the coverage-completeness gap)."""
    dim = read_scorecard_block()["dimensions"][_LANE_KEY]
    count = lane_leak_count_signal()["lane_leak_count"]
    assert dim["open_leaks"] == len(dim["leaks"]) == count == 1


# =========================== projector picks it up (no code change) ============= #


def test_projector_renders_lane_dimension_with_no_code_change() -> None:
    """AC1/AC5: ``render_scorecard_final_report`` picks up lane_discipline automatically — its Band
    row, its per-criterion trace, its coverage-completeness leak on the ranked list, and its ▬
    baseline trend all render with NO projector change."""
    block = read_scorecard_block()
    fence = {"cost_posture": "exact", "fences_enabled": {"fidelity": False}}
    out = render_scorecard_final_report(block=block, history=None, fence_state=fence)
    assert "| Lane-discipline / scope-fidelity | B |" in out
    assert "| Lane-discipline / scope-fidelity | ▬ baseline |" in out
    ld1_row = "| Lane-discipline / scope-fidelity | lane_discipline_import_linter | strong | 3/4 |"
    assert ld1_row in out
    assert "lane-discipline-lane-matrix-contract-coverage-unverified" in out  # leak on ranked list
    assert "/100" not in out  # never a false-precise headline


# =========================== FIX-A/E/F/C — robustness proofs ==================== #


def test_ld1_no_console_spinner_leaks_at_read_time(capsys: pytest.CaptureFixture) -> None:
    """FIX-A: ``create_report`` renders a rich ``console.status`` + transient ``Live`` progress bar
    during the multi-second build; a session-ramp / retro scorecard read must NOT flash a spinner.
    The reader wraps the build in ``redirect_stdout``/``redirect_stderr`` + ``console.quiet`` — so
    NOTHING reaches the real terminal. RED/verify: capture stdout/stderr around the live read →
    empty (no spinner text leaks)."""
    capsys.readouterr()  # clear any prior capture
    sig = import_linter_lane_signal()  # the REAL live build
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == "", (
        f"console side-effects leaked at read time: out={captured.out!r} err={captured.err!r}"
    )
    # the read still succeeded (suppression did not break the build).
    assert sig["status"] == "ok" and level_from_signal(_LD1_KEY, sig) == "strong"


def test_ld1_bounded_returns_unavailable_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """FIX-E: the reader's try/except catches raises but NOT a hang; a stuck ``create_report`` must
    not block indefinitely. RED-first: shrink the watchdog bound + make ``create_report`` sleep
    beyond it → the reader returns ``unavailable`` WITHIN the bound (not after the sleep), never
    hanging. (Portable on Windows: a worker-thread watchdog — ``signal.alarm`` is POSIX-only.)"""
    import time

    from importlinter.api import use_cases

    import app.quality.signals as signals_mod

    def _slow(*a, **k):
        # Sleep past the (shrunk) watchdog, then return a BENIGN object (no real build, no console
        # I/O) so the abandoned daemon cannot later flash a spinner into a subsequent test.
        time.sleep(1.5)
        return _fake_report(kept=18, broken=0)

    monkeypatch.setattr(signals_mod, "_IMPORTLINTER_TIMEOUT_S", 0.3)
    monkeypatch.setattr(use_cases, "create_report", _slow)
    t0 = time.time()
    sig = import_linter_lane_signal()
    elapsed = time.time() - t0
    assert sig["status"] == "unavailable"
    assert level_from_signal(_LD1_KEY, sig) == "unavailable"
    assert elapsed < 1.2, f"reader did not return within the watchdog bound (took {elapsed:.2f}s)"


def test_ld1_never_raises_on_hostile_report() -> None:
    """FIX-F: on the injected-report path, an attribute access that raises a NON-AttributeError (a
    report object with a raising ``.kept_count`` property) must NOT propagate — the reader returns
    ``unavailable`` (matching the live-block guarantee), never raises."""

    class _Hostile:
        @property
        def kept_count(self) -> int:
            raise RuntimeError("seeded: hostile report property")

        broken_count = 0

    sig = import_linter_lane_signal(_Hostile())  # must not raise
    assert sig["status"] == "unavailable"
    assert level_from_signal(_LD1_KEY, sig) == "unavailable"


def test_importlinter_register_seam_available() -> None:
    """FIX-C anti-drift: LD1 depends on the internal ``importlinter.application.use_cases.
    _register_contract_types`` (no public path registers contract types — ``configure()`` only sets
    up settings). This test fails LOUD if that seam disappears/moves in a future ``importlinter``
    2.x, so a dep upgrade reds THIS test (a clear signal) rather than silently degrading LD1 to
    ``unavailable`` while the doc/history hard-claim ``strong``."""
    from importlinter.api import use_cases
    from importlinter.application.use_cases import _register_contract_types

    assert callable(_register_contract_types)
    # and the public read path is intact too.
    assert callable(use_cases.read_user_options)
    assert callable(use_cases.create_report)

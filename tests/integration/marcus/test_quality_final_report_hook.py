"""Story Q4.2 — production_runner run-end ``quality-final-report.md`` hook.

WIRING pins for ``production_runner._emit_quality_final_report`` (the seam that
renders the already-built, already-tested Q1.4b projector at genuine terminal
completion). Hermetic + deterministic — no live calls (mirrors
``test_run_summary_fence_state.py``'s direct-emit discipline). The walk-driven
AC2 legs use the offline ``_RecordingAdapter`` + custom-manifest harness borrowed
from ``test_production_runner_resume_continues_execution.py``.

AC map:
  * AC1/AC5 — hermetic byte-match: the written ``.md`` is byte-identical to a
    direct ``render_scorecard_final_report(...)`` on the same inputs (healthy AND
    degraded-every-leaf fence shapes), reusing the goldens in
    ``tests/quality/test_scorecard_final_report.py`` (no parallel truth).
  * AC2 (QLW-3) — two-walk / terminal-only / exactly-once: BOTH completion blocks
    emit once; the G1 start-walk pause NEVER emits; no double-emit over one trial.
  * AC3 (QLW-8) — fail-soft: absent scorecard / corrupt+missing run dir / degraded
    fence render honest markers; a raising projector is swallowed and the walk
    completes normally.
  * AC4 (QLW-10) — idempotent / rewind-safe overwrite (byte-identical, single file).
  * AC6 (QLW-9) — no Band better than the committed block's worst posture
    (open_leaks>0 surfaces the leaks, never an invented clean posture).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import yaml

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict
from app.quality.history import history_path
from app.quality.report import render_scorecard_final_report
from app.quality.scorecard import read_scorecard_block

# REUSE the existing golden corpus — do NOT mint a parallel truth (AC5).
from tests.quality.test_scorecard_final_report import (
    _FIXTURE_BLOCK,
    _FIXTURE_FENCE,
    _FIXTURE_GOLDEN,
)

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")
REPORT_NAME = "quality-final-report.md"

#: The real ``production_runner._build_fence_state`` degraded emit shape (no
#: ``status`` key; every leaf ``unavailable``/``undetected``) — the projector
#: collapses it to a single honest marker (FIX-3).
_DEGRADED_FENCE: dict = {
    "fences_enabled": {
        "fidelity": "unavailable",
        "coverage": "unavailable",
        "udac": "unavailable",
    },
    "silent_bypass_events": "undetected",
    "hil_allowlist_empty": "unavailable",
    "pack_hash_binding": "unavailable",
    "conversation_chain_digest": "unavailable",
    "cost_posture": "unavailable",
}


def _write_run_summary(run_dir: Path, fence_state) -> Path:
    """Write a synthetic ``run_summary.yaml`` carrying ``fence_state`` exactly as
    the real ``_emit_run_summary_yaml`` does (``yaml.safe_dump`` of the payload),
    so the hook reads the run's OWN fence_state back (QLW-6)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "run_summary.yaml"
    payload = {"terminal_gate": "G4", "fence_state": fence_state}
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8", newline="\n")
    return path


# --------------------------------------------------------------------------- #
# AC1 / AC5 — hermetic byte-match (the hook adds/drops nothing).
# --------------------------------------------------------------------------- #
def test_bytematch_real_block_healthy_fence(tmp_path: Path) -> None:
    """AC5: the written .md is byte-identical to a direct render on the SAME
    inputs — real committed block + real history + the healthy fence read back
    from run_summary.yaml."""
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    expected = render_scorecard_final_report(
        block=read_scorecard_block(), history=history_path(), fence_state=_FIXTURE_FENCE
    )
    assert written == expected


def test_bytematch_real_block_degraded_fence(tmp_path: Path) -> None:
    """AC5: byte-match also holds for the degraded every-leaf fence shape."""
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _DEGRADED_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    expected = render_scorecard_final_report(
        block=read_scorecard_block(), history=history_path(), fence_state=_DEGRADED_FENCE
    )
    assert written == expected
    assert "_this run: fence_state unavailable_" in written


def test_bytematch_fixture_golden(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """AC5: reusing the pinned ``_FIXTURE_GOLDEN`` literal directly — inject the
    fixture block + empty history + fixture fence and assert the hook reproduces
    the exact golden (proves the hook is a transparent pass-through)."""
    empty_hist = tmp_path / "hist.jsonl"
    empty_hist.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "app.quality.scorecard.read_scorecard_block", lambda *a, **k: _FIXTURE_BLOCK
    )
    monkeypatch.setattr("app.quality.history.history_path", lambda: empty_hist)
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert written == _FIXTURE_GOLDEN


# --------------------------------------------------------------------------- #
# AC4 — idempotent / rewind-safe overwrite.
# --------------------------------------------------------------------------- #
def test_idempotent_overwrite_byte_identical(tmp_path: Path) -> None:
    """AC4/QLW-10: two emits over the same trial dir → byte-identical, single
    file, no double-append."""
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    first = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    second = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert first == second
    assert sorted(p.name for p in run_dir.glob("quality-final-report*.md")) == [REPORT_NAME]


# --------------------------------------------------------------------------- #
# FIX 1 (Edge finding) — atomic write: no truncated file may read as complete.
# --------------------------------------------------------------------------- #
def test_successful_emit_leaves_no_tmp_file(tmp_path: Path) -> None:
    """FIX-1: after a SUCCESSFUL emit the run dir holds EXACTLY
    ``quality-final-report.md`` and NO leftover ``.md.tmp`` staging file (the
    atomic write cleans up after itself)."""
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    assert (run_dir / REPORT_NAME).is_file()
    assert list(run_dir.glob("*.md.tmp")) == []
    assert sorted(p.name for p in run_dir.glob("quality-final-report*")) == [REPORT_NAME]


def test_midwrite_failure_leaves_prior_good_report_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FIX-1: a mid-write interruption must (a) be swallowed — the helper NEVER
    propagates (fail-soft preserved), AND (b) leave a PRE-EXISTING good
    ``quality-final-report.md`` from a prior emit fully INTACT (never truncated).

    The interruption is modelled faithfully on what a real ``write_text`` does:
    open-truncate the destination, then die mid-write. Under a direct
    ``target.write_text`` this destroys the good report (the very bug — a
    truncated file that reads as complete feeds the R2 witness). Under the atomic
    write the destructive write lands on a ``.md.tmp`` staging path, so the target
    is only ever replaced by a fully-written temp and survives byte-for-byte."""
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    # First emit lands a known-good report.
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    good = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert good  # sanity: a real report landed

    # Model the truncate-then-die: whatever path the content write targets is
    # first truncated to empty (as write_text's "w" open does) and then the write
    # dies mid-stream. Old code targets the report itself → corruption; the atomic
    # write targets the temp → the report is untouched.
    real_write_text = Path.write_text

    def _truncate_then_die(self: Path, *_a, **_k):
        self.write_bytes(b"")  # emulate open("w") truncation before the crash
        raise OSError("seeded mid-write interruption")

    monkeypatch.setattr(Path, "write_text", _truncate_then_die)
    # Must NOT propagate (fail-soft).
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    monkeypatch.setattr(Path, "write_text", real_write_text)
    # The prior good report survives byte-for-byte (never truncated).
    assert (run_dir / REPORT_NAME).read_text(encoding="utf-8") == good
    # No orphaned staging file left behind either.
    assert list(run_dir.glob("*.md.tmp")) == []


# --------------------------------------------------------------------------- #
# FIX 2 (Blind finding) — docstring honesty: don't overstate rewind determinism.
# --------------------------------------------------------------------------- #
def test_docstring_does_not_overstate_rewind_determinism() -> None:
    """FIX-2: the ``_emit_quality_final_report`` docstring must NOT claim a rewind
    is byte-identical across time (it is not — a later rewind reads the grown
    append-only trend ledger, which can change the rendered trend arrow). It must
    carry the honest framing instead. No behaviour change — framing only."""
    doc = (production_runner._emit_quality_final_report.__doc__ or "").lower()
    # Honest framing present.
    assert "not guaranteed byte-identical across time" in doc
    assert "trend ledger" in doc
    # The overstated, unqualified "rewind-safe" determinism claim is gone.
    assert "rewind-safe (qlw-10)" not in doc


# --------------------------------------------------------------------------- #
# AC3 — fail-soft (QLW-8). The walk is NEVER perturbed; markers stay honest.
# --------------------------------------------------------------------------- #
def test_failsoft_absent_scorecard_renders_honest_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.quality.scorecard.read_scorecard_block", lambda *a, **k: None)
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert "_quality scorecard unavailable_" in written
    assert "| Fence enabled — fidelity | true |" in written  # fence section intact


def test_failsoft_corrupt_run_summary_renders_fence_marker(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    rs = run_dir / "run_summary.yaml"
    rs.write_text("{not: valid: yaml: [", encoding="utf-8")
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert "_this run: fence_state unavailable_" in written


def test_failsoft_missing_run_summary_never_raises(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=run_dir / "run_summary.yaml"
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert "_this run: fence_state unavailable_" in written


def test_failsoft_degraded_every_leaf_fence(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _DEGRADED_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert "_this run: fence_state unavailable_" in written


def test_failsoft_projector_raise_is_swallowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A raising projector must be exception-swallowed (mirrors
    ``_emit_operator_surface``) — the hook returns normally, never raises."""

    def _boom(**_kwargs):
        raise RuntimeError("seeded projector failure")

    monkeypatch.setattr("app.quality.report.render_scorecard_final_report", _boom)
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    # Must NOT raise (the whole point of the fail-soft wrapper).
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )


# --------------------------------------------------------------------------- #
# AC6 (QLW-9) — no Band better than the committed block's worst posture.
# --------------------------------------------------------------------------- #
def test_no_band_better_than_committed_open_leaks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A committed block with ``open_leaks>0`` cannot render a clean/higher
    posture — the ranked leaks surface and the committed Band is preserved."""
    block = {
        "dimensions": {
            "d": {
                "label": "D",
                "band": "C",
                "band_note": "n",
                "open_leaks": 2,
                "criteria": {},
                "leaks": [
                    {"rank": 1, "criterion": "X", "slug": "s1", "lane": "paid-walk"},
                    {"rank": 2, "criterion": "Y", "slug": "s2", "lane": "governance"},
                ],
            }
        }
    }
    monkeypatch.setattr("app.quality.scorecard.read_scorecard_block", lambda *a, **k: block)
    empty_hist = tmp_path / "h.jsonl"
    empty_hist.write_text("", encoding="utf-8")
    monkeypatch.setattr("app.quality.history.history_path", lambda: empty_hist)
    run_dir = tmp_path / str(TRIAL_ID)
    rs = _write_run_summary(run_dir, _FIXTURE_FENCE)
    production_runner._emit_quality_final_report(
        trial_id=TRIAL_ID, runs_root=tmp_path, run_summary_path=rs
    )
    written = (run_dir / REPORT_NAME).read_text(encoding="utf-8")
    assert "| D | C | n |" in written  # committed Band preserved, not inflated
    assert "| 1 | D | X | paid-walk | s1 |" in written  # open leaks surfaced
    assert "| 2 | D | Y | governance | s2 |" in written


# --------------------------------------------------------------------------- #
# AC2 (QLW-3) — two-walk / terminal-only / exactly-once (walk-driven, offline).
# --------------------------------------------------------------------------- #
class _RecordingAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict,
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict | None = None,
        projection_map: dict | None = None,
    ) -> ProductionEnvelope:
        del dependency_map, base_state, runner_supplied_payload, projection_map
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
                node_id=node_id,
            )
        )
        return updated


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


@pytest.fixture
def adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    """Offline walk harness (mirrors the gate-pause-resume starvation test): fake
    dispatch adapter + a green preflight stub + a no-op cost recorder so the walk
    runs hermetically with no live keys/services."""
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _RecordingAdapter)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(
        production_runner,
        "_run_start_preflight_gate",
        lambda *_a, **_k: SimpleNamespace(all_green=True, blocking_items=lambda: []),
    )
    monkeypatch.setattr(
        production_runner,
        "_record_cost",
        lambda **k: k["runs_root"] / str(k["trial_id"]) / "cost-report.json",
    )


@pytest.fixture
def emit_spy(monkeypatch: pytest.MonkeyPatch) -> list:
    """Call-through spy over the real hook — counts invocations per trial."""
    calls: list = []
    real = production_runner._emit_quality_final_report

    def _wrapper(**kwargs):
        calls.append(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(production_runner, "_emit_quality_final_report", _wrapper)
    return calls


def _gate_manifest(path: Path, *, gate_id: str) -> Path:
    path.write_text(
        f"""schema_version: "1.0"
lane: "run_graph"
entrypoint: "01"
frozen_graph_version: "v42"
nodes:
  - id: "01"
    specialist_id: "texas"
  - id: "02"
    specialist_id: "marcus"
    gate: true
    gate_code: "{gate_id}"
  - id: "03"
    specialist_id: "irene"
edges:
  - from: "__start__"
    to: "01"
  - from: "01"
    to: "02"
  - from: "02"
    to: "03"
  - from: "03"
    to: "__end__"
""",
        encoding="utf-8",
    )
    return path


def _no_gate_manifest(path: Path) -> Path:
    path.write_text(
        """schema_version: "1.0"
lane: "run_graph"
entrypoint: "01"
frozen_graph_version: "v42"
nodes:
  - id: "01"
    specialist_id: "texas"
  - id: "03"
    specialist_id: "irene"
edges:
  - from: "__start__"
    to: "01"
  - from: "01"
    to: "03"
  - from: "03"
    to: "__end__"
""",
        encoding="utf-8",
    )
    return path


def _approve_verdict(tmp_path: Path, trial_id: UUID, gate_id: str) -> OperatorVerdict:
    import json

    payload = json.loads(
        (tmp_path / str(trial_id) / f"decision-card-{gate_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return OperatorVerdict(
        trial_id=trial_id,
        verb="approve",
        gate_id=gate_id,
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=payload["digest"],
    )


def test_start_walk_completion_emits_once(tmp_path: Path, adapter, emit_spy) -> None:
    """The START node walk (``run_production_trial`` completion block) emits the
    report exactly once at genuine terminal completion."""
    trial_id = uuid4()
    env = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_no_gate_manifest(tmp_path / "m.yaml"),
        max_specialist_calls=5,
    )
    assert env.status == "completed"
    assert (tmp_path / str(trial_id) / REPORT_NAME).is_file()
    assert len(emit_spy) == 1


def test_g1_start_walk_pause_never_emits(tmp_path: Path, adapter, emit_spy) -> None:
    """QLW-3: the G1 start-walk PAUSE must NEVER write a final report."""
    trial_id = uuid4()
    env = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_gate_manifest(tmp_path / "m.yaml", gate_id="G1"),
        max_specialist_calls=1,
    )
    assert env.status == "paused-at-gate"
    assert not (tmp_path / str(trial_id) / REPORT_NAME).exists()
    assert emit_spy == []


def test_continue_walk_completion_emits_exactly_once_not_at_pause(
    tmp_path: Path, adapter, emit_spy
) -> None:
    """QLW-3: the CONTINUE node walk (``_continue_production_walk`` completion
    block) emits once at terminal completion; the preceding G1 pause emitted
    nothing → exactly-once over the whole trial, and no double-emit."""
    trial_id = uuid4()
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_gate_manifest(tmp_path / "m.yaml", gate_id="G1"),
        max_specialist_calls=1,
    )
    assert emit_spy == []  # nothing emitted at the start-walk G1 pause
    env = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_approve_verdict(tmp_path, trial_id, "G1"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )
    assert env.status == "completed"
    assert (tmp_path / str(trial_id) / REPORT_NAME).is_file()
    assert len(emit_spy) == 1  # emitted ONCE, only at the continue-walk completion


def test_walk_completes_even_when_report_emit_raises(
    tmp_path: Path, adapter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC3/QLW-8: a failure inside the report render must NOT perturb the walk —
    the run still reaches ``completed``."""

    def _boom(**_kwargs):
        raise RuntimeError("seeded projector failure")

    monkeypatch.setattr("app.quality.report.render_scorecard_final_report", _boom)
    trial_id = uuid4()
    env = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_no_gate_manifest(tmp_path / "m.yaml"),
        max_specialist_calls=5,
    )
    assert env.status == "completed"

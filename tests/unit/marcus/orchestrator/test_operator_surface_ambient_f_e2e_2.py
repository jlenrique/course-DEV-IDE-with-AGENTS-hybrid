"""Witness tests for the ambient operator-surface wiring (F-E2E-2).

The live E2E party review (epic-35 story-35.7) found that during the walk the
assembler emitted identity/envelope/next_action/steps/decision_card but NEVER
``health``/``specialists``/``modalities``/``trace`` — so the HUD's health strip
(FR9), specialist chips (FR7), modality chips (FR10), and state-trace well (FR8)
were EMPTY mid-run, and the witness-mode lifecycle invariant
("status=in-flight requires the health section") fired on every in-flight emit.

These tests cover the fix at two altitudes:

* the assembler's new ``update_ambient`` section API (health/specialists/
  modalities/trace in one non-progress merge-write); and
* the ``production_runner`` ambient builders + ``_refresh_operator_surface_ambient``
  wrapper, driven directly with a STUB run state (a full walk fixture is far too
  heavy for a unit test — driving the section APIs + wrapper with a stub run
  state exercises exactly the emission wiring F-E2E-2 changed).
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

from app.marcus.orchestrator import production_runner as pr
from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler
from app.models.runtime.operator_surface import (
    HealthTile,
    OperatorSurfaceProjection,
    SpecialistEntry,
    read_operator_surface_lenient,
)

OPERATOR_SURFACE_LOGGER = "app.models.runtime.operator_surface"
HEALTH_WITNESS_MSG = "requires the health section"


# --------------------------------------------------------------------------
# Fixtures / helpers
# --------------------------------------------------------------------------


class _StubEnvelope:
    """Minimal envelope stand-in exposing the fields emit() reads."""

    def __init__(
        self,
        trial_id: UUID,
        status: str,
        *,
        paused_gate: str | None = None,
        paused_error_tag: str | None = None,
        waiting_batch_id: str | None = None,
        completed_at: datetime | None = None,
        corpus_path: str = "lesson-alpha",
        preset: str = "production",
        operator_id: str = "operator_cli",
    ) -> None:
        self.trial_id = trial_id
        self.status = status
        self.paused_gate = paused_gate
        self.paused_error_tag = paused_error_tag
        self.waiting_batch_id = waiting_batch_id
        self.completed_at = completed_at
        self.corpus_path = corpus_path
        self.preset = preset
        self.operator_id = operator_id

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "trial_id": str(self.trial_id),
                "status": self.status,
                "paused_gate": self.paused_gate,
                "paused_error_tag": self.paused_error_tag,
                "waiting_batch_id": self.waiting_batch_id,
                "completed_at": self.completed_at.isoformat()
                if self.completed_at
                else None,
            },
            indent=indent,
            sort_keys=True,
        )


def _assembler(tmp_path: Path, trial_id: UUID) -> OperatorSurfaceAssembler:
    return OperatorSurfaceAssembler(
        trial_id, tmp_path, hud_config_path=tmp_path / "no-such-hud-config.yaml"
    )


def _read(assembler: OperatorSurfaceAssembler) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient(assembler.projection_path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def _read_path(path: Path) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient(path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def _now() -> datetime:
    return datetime.now(UTC)


def _contribution(
    specialist_id: str,
    *,
    node_id: str,
    model_used: str,
    cost_usd: float,
) -> SimpleNamespace:
    return SimpleNamespace(
        specialist_id=specialist_id,
        node_id=node_id,
        model_used=model_used,
        cost_usd=cost_usd,
    )


def _run_state(
    *,
    contributions: list[SimpleNamespace] | None = None,
    llm_execution_mode: str | None = "inline",
) -> SimpleNamespace:
    return SimpleNamespace(
        llm_execution_mode=llm_execution_mode,
        production_envelope=SimpleNamespace(
            contributions=tuple(contributions or [])
        ),
    )


# --------------------------------------------------------------------------
# Assembler: update_ambient section API
# --------------------------------------------------------------------------


def test_update_ambient_populates_all_four_sections(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))

    ok = asm.update_ambient(
        health_tiles=[
            HealthTile(as_of=_now(), label="run cost", value=0.12, unit="USD"),
        ],
        specialist_roster=[
            SpecialistEntry(name="texas", status="contributed", current_node="04"),
        ],
        modalities={"llm_execution_mode": "batch", "styleguide": "hil-2026-apc"},
        trace_event=("node-enter", "04"),
    )
    assert ok is True

    proj = _read(asm)
    assert proj.health is not None and proj.health.tiles[0].label == "run cost"
    assert proj.specialists is not None and proj.specialists.roster[0].name == "texas"
    assert proj.modalities is not None
    assert proj.modalities.llm_execution_mode == "batch"
    assert proj.modalities.styleguide == "hil-2026-apc"
    assert proj.trace is not None and proj.trace.events[-1].event == "node-enter"


def test_update_ambient_is_not_a_progress_event(tmp_path: Path) -> None:
    """Ambient refreshes bump seq but NEVER progress_seq (AD-10)."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    before = _read(asm)

    asm.update_ambient(
        health_tiles=[HealthTile(as_of=_now(), label="run cost", value=0.0)]
    )
    after = _read(asm)
    assert after.seq == before.seq + 1
    assert after.progress_seq == before.progress_seq


def test_update_ambient_none_arg_leaves_section_untouched(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.update_ambient(
        specialist_roster=[SpecialistEntry(name="gary", status="contributed")]
    )
    # a later refresh that omits specialists must preserve the prior roster
    asm.update_ambient(
        health_tiles=[HealthTile(as_of=_now(), label="run cost", value=0.0)]
    )
    proj = _read(asm)
    assert proj.specialists is not None
    assert proj.specialists.roster[0].name == "gary"
    assert proj.health is not None


def test_update_ambient_empty_roster_writes_present_but_empty(tmp_path: Path) -> None:
    """An explicit empty roster still writes the section (present-but-empty), not null."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.update_ambient(specialist_roster=[])
    proj = _read(asm)
    assert proj.specialists is not None
    assert proj.specialists.roster == []


def test_update_ambient_all_none_is_a_noop(tmp_path: Path) -> None:
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.update_ambient() is False


def test_update_ambient_never_raises_on_bad_tile(tmp_path: Path) -> None:
    """Amendment 8: a malformed tile is swallowed, never raised into the walk."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "in-flight"))
    # value must be float|str; a dict is invalid -> validate raises -> swallowed
    assert asm.update_ambient(health_tiles=[{"as_of": _now(), "label": "x", "value": {}}]) is False


# --------------------------------------------------------------------------
# The witness-mode lifecycle warning is cleared once health is present
# --------------------------------------------------------------------------


def test_in_flight_without_health_fires_witness_warning(
    tmp_path: Path, caplog
) -> None:
    """Baseline: an in-flight projection with NO health section warns (the defect)."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    with caplog.at_level(logging.WARNING, logger=OPERATOR_SURFACE_LOGGER):
        asm.emit(_StubEnvelope(tid, "in-flight"))
    assert HEALTH_WITNESS_MSG in caplog.text


def test_ambient_health_at_registered_clears_in_flight_witness_warning(
    tmp_path: Path, caplog
) -> None:
    """Production order: ambient sets health at REGISTERED (exempt), so the
    subsequent in-flight emit inherits health and never warns about it. (Reading
    a prior in-flight-WITHOUT-health projection re-logs the warning, which is why
    the fix places the ambient refresh before the in-flight transition.)"""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    asm.emit(_StubEnvelope(tid, "registered"))
    asm.update_ambient(
        health_tiles=[HealthTile(as_of=_now(), label="run cost", value=0.0)]
    )
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=OPERATOR_SURFACE_LOGGER):
        asm.emit(_StubEnvelope(tid, "in-flight"))
    proj = _read(asm)
    assert proj.envelope.status == "in-flight"
    assert proj.health is not None  # inherited across the transition
    assert HEALTH_WITNESS_MSG not in caplog.text


def test_health_preserved_across_pause_clears_paused_witness_warning(
    tmp_path: Path, caplog
) -> None:
    """Once ambient sets health, a later paused-at-gate emit preserves it (no warn)."""
    tid = uuid4()
    asm = _assembler(tmp_path, tid)
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "decision-card-G1.json").write_text(
        json.dumps({"card": {"gate_focus": "trial_open"}}), encoding="utf-8"
    )
    asm.emit(_StubEnvelope(tid, "in-flight"))
    asm.update_ambient(
        health_tiles=[HealthTile(as_of=_now(), label="run cost", value=0.0)]
    )
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=OPERATOR_SURFACE_LOGGER):
        asm.emit(_StubEnvelope(tid, "paused-at-gate", paused_gate="G1"))
    proj = _read(asm)
    assert proj.health is not None  # preserved by read-merge-write
    assert HEALTH_WITNESS_MSG not in caplog.text


# --------------------------------------------------------------------------
# production_runner ambient builders (data sourcing)
# --------------------------------------------------------------------------


def test_specialist_roster_aggregates_contributions() -> None:
    run_state = _run_state(
        contributions=[
            _contribution("texas", node_id="04", model_used="gpt-5", cost_usd=0.10),
            _contribution("texas", node_id="06", model_used="gpt-5", cost_usd=0.05),
            _contribution("gary", node_id="07", model_used="gpt-5-mini", cost_usd=0.20),
        ]
    )
    roster = pr._operator_surface_specialist_roster(run_state)
    by_name = {e.name: e for e in roster}
    assert set(by_name) == {"texas", "gary"}
    # cost summed; current_node/model from the most recent contribution
    assert abs(by_name["texas"].cost_usd - 0.15) < 1e-9
    assert by_name["texas"].current_node == "06"
    assert by_name["gary"].model == "gpt-5-mini"


def test_specialist_roster_empty_when_no_contributions() -> None:
    assert pr._operator_surface_specialist_roster(_run_state()) == []


def test_health_tiles_live_cost_and_unknown_platform(tmp_path: Path) -> None:
    tid = uuid4()
    run_state = _run_state(
        contributions=[
            _contribution("texas", node_id="04", model_used="gpt-5", cost_usd=0.30),
        ]
    )
    tiles = pr._operator_surface_health_tiles(tid, tmp_path, run_state)
    labels = {t.label: t for t in tiles}
    assert "run cost" in labels
    assert abs(float(labels["run cost"].value) - 0.30) < 1e-9
    # zero-lie: platform quota is not cheaply known mid-walk -> unknown, never green
    assert labels["openai quota"].confidence == "unknown"
    assert labels["openai quota"].threshold_state == "unknown"
    assert labels["openai quota"].value == "unknown"


def test_health_tiles_prefer_persisted_cost_report(tmp_path: Path) -> None:
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "cost-report.json").write_text(
        json.dumps({"total_cost_usd": 1.2345}), encoding="utf-8"
    )
    tiles = pr._operator_surface_health_tiles(tid, tmp_path, _run_state())
    labels = {t.label: t for t in tiles}
    assert abs(float(labels["run cost"].value) - 1.2345) < 1e-6


def test_modalities_from_run_state_and_directive(tmp_path: Path) -> None:
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "directive.yaml").write_text(
        "gamma_settings:\n"
        "  - styleguide: hil-2026-apc-crossroads-classic\n"
        "styleguide_picker_provenance:\n"
        "  source: operator-pinned\n",
        encoding="utf-8",
    )
    # detective disposition receipt on disk
    pr.research_detective_gate.write_disposition(run_dir, "approve")

    mod = pr._operator_surface_modalities(
        tid, tmp_path, _run_state(llm_execution_mode="batch")
    )
    assert mod is not None
    assert mod["llm_execution_mode"] == "batch"
    assert mod["styleguide"] == "hil-2026-apc-crossroads-classic"
    assert mod["styleguide_provenance"] == "operator-pinned"
    assert mod["detective_disposition"] == "approve"


def test_modalities_none_when_nothing_resolvable(tmp_path: Path) -> None:
    tid = uuid4()
    mod = pr._operator_surface_modalities(
        tid, tmp_path, _run_state(llm_execution_mode=None)
    )
    assert mod is None


# --------------------------------------------------------------------------
# The _refresh_operator_surface_ambient wrapper (end-to-end emission wiring)
# --------------------------------------------------------------------------


def test_refresh_wrapper_populates_projection_and_clears_warning(
    tmp_path: Path, caplog
) -> None:
    """Drive the walk's ambient wrapper directly with a stub run state.

    Mirrors the production order (F-E2E-2 fix): the wrapper runs at REGISTERED
    (before the in-flight persist), so all four sections land while the
    lifecycle invariant is exempt, and the subsequent in-flight emit inherits a
    present health section and never warns about it.
    """
    tid = uuid4()
    # establish a registered projection first (require_prev=True for section writes)
    _assembler(tmp_path, tid).emit(_StubEnvelope(tid, "registered"))

    run_state = _run_state(
        contributions=[
            _contribution("texas", node_id="04", model_used="gpt-5", cost_usd=0.10),
        ],
        llm_execution_mode="inline",
    )
    pr._refresh_operator_surface_ambient(
        tid, tmp_path, run_state, trace_event=("walk-start", "starting")
    )

    proj = _read_path(tmp_path / str(tid) / "operator-surface.json")
    assert proj.health is not None and proj.health.tiles
    assert proj.specialists is not None and proj.specialists.roster[0].name == "texas"
    assert proj.modalities is not None
    assert proj.modalities.llm_execution_mode == "inline"
    assert proj.trace is not None and proj.trace.events[-1].event == "walk-start"

    # transitioning to in-flight must not re-raise the health witness warning
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger=OPERATOR_SURFACE_LOGGER):
        _assembler(tmp_path, tid).emit(_StubEnvelope(tid, "in-flight"))
    assert _read_path(tmp_path / str(tid) / "operator-surface.json").health is not None
    assert HEALTH_WITNESS_MSG not in caplog.text


def test_refresh_wrapper_never_raises_without_prior_projection(tmp_path: Path) -> None:
    """No prior projection -> section write is a no-op; the wrapper never raises."""
    tid = uuid4()
    # nothing on disk; require_prev=True means the write is skipped, not fatal
    pr._refresh_operator_surface_ambient(tid, tmp_path, _run_state())
    assert not (tmp_path / str(tid) / "operator-surface.json").exists()


def test_refresh_wrapper_never_raises_on_malformed_artifacts(tmp_path: Path) -> None:
    """F-E2E-2 review S1: garbage cost-report.json / directive.yaml on disk must
    NOT raise into the paid walk (builder-level amendment-8 pin) — health falls
    back to the live cost sum; styleguide is omitted; the walk proceeds."""
    tid = uuid4()
    run_dir = tmp_path / str(tid)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "cost-report.json").write_text("{ this is not json", encoding="utf-8")
    (run_dir / "directive.yaml").write_text("::: not: [valid", encoding="utf-8")
    _assembler(tmp_path, tid).emit(_StubEnvelope(tid, "registered"))

    run_state = _run_state(
        contributions=[
            _contribution("texas", node_id="04", model_used="gpt-5", cost_usd=0.10),
        ]
    )
    # must not raise despite both artifacts being garbage
    pr._refresh_operator_surface_ambient(tid, tmp_path, run_state)

    proj = _read_path(run_dir / "operator-surface.json")
    assert proj.health is not None and proj.health.tiles  # live-sum fallback
    assert proj.specialists is not None and proj.specialists.roster

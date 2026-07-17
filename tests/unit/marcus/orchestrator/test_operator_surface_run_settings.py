"""Run-settings standing readout — resolver + emission wiring (Story 42.3).

Covers the assembler-side of the 16-toggle standing readout:

* ``resolve_run_settings`` maps each of the 16 canonical toggles to its resolved
  display value from env / directive.yaml / run_summary.yaml / the prior
  projection (AC-1) — env-absent toggles resolve to an explicit ``off`` default,
  never a missing key (AC-3);
* the section is emitted through the SAME ``update_ambient`` merge-write both
  walks call, so the readout is present after any ambient refresh (AC-2/4,
  two-walk trap) and the assembler stays the sole writer;
* a double-emit on identical inputs yields an identical section modulo ``as_of``
  (AC-3 determinism).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from app.marcus.orchestrator.operator_surface_assembler import (
    OperatorSurfaceAssembler,
    resolve_run_settings,
)
from app.models.runtime.operator_surface import (
    RUN_SETTINGS_TOGGLES,
    HealthTile,
    OperatorSurfaceProjection,
    read_operator_surface_lenient,
)

_ENV_TOGGLES = (
    "MARCUS_G0_DISPATCH_LIVE",
    "MARCUS_RESEARCH_DISPATCH_LIVE",
    "MARCUS_RESEARCH_DETECTIVE_LIVE",
    "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE",
    "MARCUS_DECK_ENRICHMENT_ACTIVE",
    "MARCUS_UDAC_ACTIVE",
    "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE",
    "MARCUS_TRIAL_BUDGET_USD",
)


def _now() -> datetime:
    return datetime.now(UTC)


def _clear_toggle_env(monkeypatch) -> None:
    for name in _ENV_TOGGLES:
        monkeypatch.delenv(name, raising=False)


class _StubEnvelope:
    """Minimal envelope stand-in exposing the fields ``emit()`` reads."""

    def __init__(self, trial_id: UUID, status: str, *, preset: str = "production") -> None:
        self.trial_id = trial_id
        self.status = status
        self.paused_gate = None
        self.paused_error_tag = None
        self.waiting_batch_id = None
        self.completed_at = None
        self.corpus_path = "lesson-alpha"
        self.preset = preset
        self.operator_id = "operator_cli"

    def model_dump_json(self, indent: int = 2) -> str:
        return json.dumps(
            {"trial_id": str(self.trial_id), "status": self.status},
            indent=indent,
            sort_keys=True,
        )


def _write_directive(run_dir: Path, **body) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    import yaml

    (run_dir / "directive.yaml").write_text(yaml.safe_dump(body), encoding="utf-8")


def _write_run_summary(run_dir: Path, selection: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    import yaml

    (run_dir / "run_summary.yaml").write_text(
        yaml.safe_dump({"component_selection": selection}), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# resolve_run_settings — each toggle resolves to the right value (AC-1/3)
# ---------------------------------------------------------------------------


def test_resolver_maps_every_toggle_to_its_source(tmp_path: Path) -> None:
    _write_directive(
        tmp_path,
        preset="explore",
        encounter_mode="recorded",
        llm_execution_mode="batch",
        voice_direction="expressive",
        coverage_gate="strict",
        gamma_settings=[{"styleguide": "slot-A"}, {"styleguide": "slot-B"}],
    )
    _write_run_summary(tmp_path, {"deck": True, "motion": False, "workbook": True})
    env = {
        "MARCUS_G0_DISPATCH_LIVE": "1",
        "MARCUS_RESEARCH_DISPATCH_LIVE": "true",
        "MARCUS_RESEARCH_DETECTIVE_LIVE": "on",
        "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE": "yes",
        "MARCUS_DECK_ENRICHMENT_ACTIVE": "0",  # explicitly off
        # MARCUS_UDAC_ACTIVE absent → resolves off, not a missing key
        "MARCUS_TRIAL_BUDGET_USD": "7.50",
    }

    section = resolve_run_settings(tmp_path, prev=None, now=_now(), env=env)

    assert section.component_deck == "on"
    assert section.component_motion == "off"
    assert section.component_workbook == "on"
    assert section.preset == "explore"  # directive (no prev)
    assert section.encounter_mode == "recorded"
    assert section.llm_execution_mode == "batch"  # directive (no prev)
    assert section.g0_dispatch_live == "on"
    assert section.research_dispatch_live == "on"
    assert section.research_detective_live == "on"
    assert section.narration_figure_fidelity_active == "on"
    assert section.voice_direction == "expressive"  # directive value wins
    assert section.deck_enrichment_active == "off"
    assert section.udac_active == "off"  # env-absent → explicit off (AC-3)
    assert section.coverage_gate == "strict"
    assert section.trial_budget_usd == "7.50"
    assert section.treatment_slots == "slot-A, slot-B"


def test_resolver_env_absent_toggles_are_off_never_missing(tmp_path: Path) -> None:
    """AC-3: with an empty env + no artifacts, every field is present + explicit."""
    section = resolve_run_settings(tmp_path, prev=None, now=_now(), env={})
    dumped = section.model_dump(mode="json")
    for field, _label in RUN_SETTINGS_TOGGLES:
        assert field in dumped, f"{field} missing from the resolved readout"
        assert dumped[field] not in (None, ""), f"{field} resolved to a blank/None"
    # the six pure env flags default to off; free-form settings to unset
    assert section.g0_dispatch_live == "off"
    assert section.udac_active == "off"
    assert section.trial_budget_usd == "unset"
    assert section.preset == "unset"
    assert section.treatment_slots == "unset"


def test_resolver_prefers_prev_surface_for_preset_and_llm_mode(tmp_path: Path) -> None:
    """preset + llm_execution_mode are run_state-sourced; the resolver reads the
    values already projected onto the prior surface rather than run_state."""
    asm = OperatorSurfaceAssembler(
        uuid4(), tmp_path, hud_config_path=tmp_path / "none.yaml"
    )
    tid = asm.trial_id
    asm.emit(_StubEnvelope(UUID(str(tid)), "in-flight", preset="explore"))
    asm.update_ambient(modalities={"llm_execution_mode": "batch"})
    prev = read_operator_surface_lenient(asm.projection_path.read_bytes())
    assert isinstance(prev, OperatorSurfaceProjection)

    section = resolve_run_settings(asm.run_dir, prev=prev, now=_now(), env={})
    assert section.preset == "explore"  # from prev.identity, not the directive
    assert section.llm_execution_mode == "batch"  # from prev.modalities


def test_resolver_is_deterministic_modulo_as_of(tmp_path: Path) -> None:
    _write_run_summary(tmp_path, {"deck": True, "motion": True, "workbook": False})
    env = {"MARCUS_UDAC_ACTIVE": "1"}
    a = resolve_run_settings(tmp_path, prev=None, now=_now(), env=env).model_dump(
        mode="json"
    )
    b = resolve_run_settings(tmp_path, prev=None, now=_now(), env=env).model_dump(
        mode="json"
    )
    a.pop("as_of")
    b.pop("as_of")
    assert a == b


# ---------------------------------------------------------------------------
# Emission wiring — sole writer, both-walks path, double-emit determinism
# ---------------------------------------------------------------------------


def _read(asm: OperatorSurfaceAssembler) -> OperatorSurfaceProjection:
    parsed = read_operator_surface_lenient(asm.projection_path.read_bytes())
    assert isinstance(parsed, OperatorSurfaceProjection), parsed
    return parsed


def test_update_ambient_emits_run_settings_through_sole_writer(
    tmp_path: Path, monkeypatch
) -> None:
    """AC-2/4: the readout is written by the assembler (sole writer) through the
    same ambient merge-write both walks call."""
    _clear_toggle_env(monkeypatch)
    monkeypatch.setenv("MARCUS_G0_DISPATCH_LIVE", "1")
    tid = uuid4()
    asm = OperatorSurfaceAssembler(tid, tmp_path, hud_config_path=tmp_path / "none.yaml")
    asm.emit(_StubEnvelope(tid, "in-flight"))
    # a bare pre-42.3 emit carries no run_settings yet
    assert _read(asm).run_settings is None

    ok = asm.update_ambient(
        health_tiles=[HealthTile(as_of=_now(), label="run cost", value=0.0)]
    )
    assert ok is True
    proj = _read(asm)
    assert proj.run_settings is not None
    assert proj.run_settings.g0_dispatch_live == "on"
    assert proj.run_settings.udac_active == "off"


def test_update_ambient_all_none_still_a_noop(tmp_path: Path) -> None:
    """The run-settings readout rides real refreshes only — an all-None call
    stays a no-op (does not spuriously write), preserving the existing contract."""
    tid = uuid4()
    asm = OperatorSurfaceAssembler(tid, tmp_path, hud_config_path=tmp_path / "none.yaml")
    asm.emit(_StubEnvelope(tid, "in-flight"))
    assert asm.update_ambient() is False


def test_double_emit_run_settings_is_identical_modulo_as_of(
    tmp_path: Path, monkeypatch
) -> None:
    """AC-3: two ambient refreshes on identical run state → identical readout."""
    _clear_toggle_env(monkeypatch)
    monkeypatch.setenv("MARCUS_UDAC_ACTIVE", "on")
    tid = uuid4()
    asm = OperatorSurfaceAssembler(tid, tmp_path, hud_config_path=tmp_path / "none.yaml")
    asm.emit(_StubEnvelope(tid, "in-flight"))

    asm.update_ambient(health_tiles=[HealthTile(as_of=_now(), label="c", value=0.0)])
    first = _read(asm).run_settings.model_dump(mode="json")
    asm.update_ambient(health_tiles=[HealthTile(as_of=_now(), label="c", value=0.0)])
    second = _read(asm).run_settings.model_dump(mode="json")
    first.pop("as_of")
    second.pop("as_of")
    assert first == second
    assert first["udac_active"] == "on"

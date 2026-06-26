"""S5 — threading the front-door selection through start_trial into the run.

Covers:
  * start_trial threads a chosen ``ComponentSelection`` into run_production_trial
    (and onto RunState), so the composer + both walks honor it.
  * a B1 (deck-only) run freezes a graph that EXCLUDES motion (07E).
  * the default/no-selection path stays byte-identical to today (production_default).
  * the run-summary helper binds the COMPOSED graph (no raw-manifest leak) for a
    non-default selection, while the default selection keeps the raw-file binding.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
from pathlib import Path
from uuid import UUID

import yaml

from app.gates.resume_api import clear_resume_registry
from app.marcus.cli import trial as trial_mod
from app.marcus.cli.trial import start_trial
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.component_selection import ComponentSelection

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")

_REAL_SHAPED_OUTPUTS: dict[str, dict] = {
    "irene_pass1": {
        "lesson_plan": {
            "plan_units": [
                {
                    "unit_id": "PU-1",
                    "title": "Unit",
                    "learning_objective": "Objective",
                    "scope_decision": "in-scope",
                }
            ]
        }
    },
    "cd": {"cd_directive": {"experience_profile": "text-led"}},
}


class _FakeAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        node_id: str | None = None,
        **_,
    ) -> ProductionEnvelope:
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=_REAL_SHAPED_OUTPUTS.get(
                    specialist_id, {"specialist_id": specialist_id}
                ),
                model_used="gpt-5-nano",
                cost_usd=0.0,
                node_id=node_id,
            )
        )
        return updated


def _setup(monkeypatch) -> None:
    clear_resume_registry()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)


def _raw_manifest_sha256() -> str:
    return hashlib.sha256(
        production_runner.DEFAULT_MANIFEST_PATH.read_bytes()
    ).hexdigest()


# ---------------------------------------------------------------------------
# 1. start_trial threads the chosen selection into run_production_trial
# ---------------------------------------------------------------------------


def test_start_trial_threads_selection_into_runner(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    def _spy(**kwargs):
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")  # short-circuit; we only assert threading

    monkeypatch.setattr(trial_mod, "_load_env_if_available", lambda: None)
    monkeypatch.setattr(trial_mod, "run_production_trial", _spy)

    selection = ComponentSelection(deck=True, motion=False, workbook=False)
    try:
        start_trial(
            preset="production",
            input_path=CORPUS,
            operator_id="operator_test",
            allow_offline_cost_report=True,
            runs_root=tmp_path,
            component_selection=selection,
        )
    except RuntimeError as exc:
        assert "stop-after-capture" in str(exc)
    assert captured["component_selection"] == selection


def test_start_trial_default_threads_none_preserving_today(
    tmp_path: Path, monkeypatch
) -> None:
    captured: dict[str, object] = {}

    def _spy(**kwargs):
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr(trial_mod, "_load_env_if_available", lambda: None)
    monkeypatch.setattr(trial_mod, "run_production_trial", _spy)

    with contextlib.suppress(RuntimeError):
        start_trial(
            preset="production",
            input_path=CORPUS,
            operator_id="operator_test",
            allow_offline_cost_report=True,
            runs_root=tmp_path,
        )
    # No selection supplied -> None passed through; runner defaults to
    # production_default (today's full graph) downstream.
    assert captured["component_selection"] is None


# ---------------------------------------------------------------------------
# 2. A B1 deck-only run freezes a graph that excludes motion + persists selection
# ---------------------------------------------------------------------------


def test_b1_deck_only_run_excludes_motion_and_persists_selection(
    tmp_path: Path, monkeypatch
) -> None:
    _setup(monkeypatch)
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    checkpoint = json.loads(
        (tmp_path / str(TRIAL_ID) / "checkpoint.json").read_text(encoding="utf-8")
    )
    assert checkpoint["run_state"]["component_selection"] == {
        "deck": True,
        "motion": False,
        "workbook": False,
    }
    # The frozen composed graph for deck-only excludes the motion nodes (07D/E/F).
    from app.manifest import load
    from app.marcus.lesson_plan.composition import compose_manifest

    composed = compose_manifest(
        load(production_runner.DEFAULT_MANIFEST_PATH),
        ComponentSelection(deck=True, motion=False, workbook=False),
    )
    node_ids = {n.id for n in composed.nodes}
    assert "07E" not in node_ids
    assert "07D" not in node_ids
    assert "07F" not in node_ids


# ---------------------------------------------------------------------------
# 3. run-summary helper: composed binding for non-default; raw binding for default
# ---------------------------------------------------------------------------


def test_run_summary_pack_hash_binds_composed_graph_for_b1(
    tmp_path: Path, monkeypatch
) -> None:
    _setup(monkeypatch)
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    payload = yaml.safe_load(
        (tmp_path / str(TRIAL_ID) / "run_summary.yaml").read_text(encoding="utf-8")
    )
    # No raw-manifest leak: a deck-only run must NOT bind the full raw manifest.
    assert payload["pack_hash_binding"] != _raw_manifest_sha256()
    assert len(payload["pack_hash_binding"]) == 64


def test_run_summary_pack_hash_default_is_byte_identical_to_raw(
    tmp_path: Path, monkeypatch
) -> None:
    _setup(monkeypatch)
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
        # default: no selection -> production_default (deck+motion) -> raw binding
    )
    payload = yaml.safe_load(
        (tmp_path / str(TRIAL_ID) / "run_summary.yaml").read_text(encoding="utf-8")
    )
    assert payload["pack_hash_binding"] == _raw_manifest_sha256()

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import yaml

from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        **_,
    ) -> ProductionEnvelope:
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={"specialist_id": specialist_id},
                model_used="gpt-5-nano",
                cost_usd=0.0,
            )
        )
        return updated


def _linear_manifest(tmp_path: Path) -> Path:
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": "texas",
        "frozen_graph_version": "v42",
        "nodes": [
            {
                "id": "texas",
                "label": "texas",
                "specialist_id": "texas",
                "scaffold_node": "act",
                "model_config_ref": None,
                "gate": False,
                "hud_tracked": True,
                "pack_version": "test",
                "rationale": "test",
            }
        ],
        "edges": [{"from": "__start__", "to": "texas"}, {"from": "texas", "to": "__end__"}],
    }
    path = tmp_path / "linear-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_clean_trial_run_summary_populated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_linear_manifest(tmp_path),
        pause_at_gates=False,
    )

    payload = yaml.safe_load((tmp_path / str(TRIAL_ID) / "run_summary.yaml").read_text())
    assert payload["terminal_gate"] == "G4"
    assert payload["silent_bypass_events"] == 0
    # 12 = 11-roster + irene_pass1 adopted as distinct canonical id
    # (Trial-3 attempt-3 fix 2026-06-11; SPECIALIST_ALIASES already targeted it).
    assert payload["specialist_roster_count"] == 12
    assert len(payload["pack_hash_binding"]) == 64
    assert len(payload["conversation_chain_digest"]) == 64


def test_paused_at_g1_run_summary_records_paused_state(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    payload = yaml.safe_load((tmp_path / str(TRIAL_ID) / "run_summary.yaml").read_text())
    assert payload["terminal_gate"] == "G1"
    assert payload["langsmith_trace_id"] == str(TRIAL_ID)


def test_nonzero_silent_bypass_events_logs_debug_warning(tmp_path: Path, caplog) -> None:
    caplog.set_level("DEBUG", logger=production_runner.__name__)
    manifest = _linear_manifest(tmp_path)
    production_runner._emit_run_summary_yaml(
        trial_id=TRIAL_ID,
        terminal_gate="G1",
        runs_root=tmp_path,
        manifest_path=manifest,
        langsmith_trace_id=None,
        silent_bypass_events=1,
    )

    assert "silent_bypass_events expected 0" in caplog.text

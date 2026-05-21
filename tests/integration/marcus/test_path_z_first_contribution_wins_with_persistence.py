from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

import yaml

from app.marcus.orchestrator import conversation_persistence, production_runner
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal
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


def _proposal() -> PreFillProposal:
    return PreFillProposal(
        decision="confirm",
        directive="accept-as-is",
        rationale="The first contribution is complete enough for approval.",
        confidence=0.9,
        confidence_signals=("first-contribution",),
    )


def _manifest(tmp_path: Path) -> Path:
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": "texas-1",
        "frozen_graph_version": "v42",
        "nodes": [
            {
                "id": "texas-1",
                "label": "texas-1",
                "specialist_id": "texas",
                "scaffold_node": "act",
                "model_config_ref": None,
                "gate": False,
                "hud_tracked": True,
                "pack_version": "test",
                "rationale": "test",
            },
            {
                "id": "texas-2",
                "label": "texas-2",
                "specialist_id": "texas",
                "scaffold_node": "act",
                "model_config_ref": None,
                "gate": False,
                "hud_tracked": True,
                "pack_version": "test",
                "rationale": "test",
            },
            {
                "id": "gate-g1",
                "label": "gate-g1",
                "specialist_id": None,
                "scaffold_node": None,
                "model_config_ref": None,
                "gate": True,
                "gate_code": "G1",
                "hud_tracked": False,
                "pack_version": "test",
                "rationale": "test",
            },
        ],
        "edges": [
            {"from": "__start__", "to": "texas-1"},
            {"from": "texas-1", "to": "texas-2"},
            {"from": "texas-2", "to": "gate-g1"},
            {"from": "gate-g1", "to": "__end__"},
        ],
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_duplicate_specialist_is_skipped_and_no_second_turn_json(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    caplog.set_level(logging.INFO, logger=production_runner.__name__)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-live-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    monkeypatch.setattr(
        production_runner.pre_gate_marcus,
        "invoke_pre_gate_marcus",
        lambda **_: _proposal(),
    )
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    (run_dir / "directive.yaml").write_text("trial: test\n", encoding="utf-8")

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path),
        max_specialist_calls=2,
    )

    turns = list((run_dir / "conversation" / "G1").glob("*.json"))
    assert len(turns) == 1
    assert "Path Z first-contribution-wins contract" in caplog.text


def test_chain_integrity_preserved_across_duplicate_skip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-live-test")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _FakeAdapter)
    monkeypatch.setattr(
        production_runner.pre_gate_marcus,
        "invoke_pre_gate_marcus",
        lambda **_: _proposal(),
    )
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    (run_dir / "directive.yaml").write_text("trial: test\n", encoding="utf-8")

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path),
        max_specialist_calls=2,
    )

    assert conversation_persistence.verify_chain(str(TRIAL_ID), tmp_path) is True

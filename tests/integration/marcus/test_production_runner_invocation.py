from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import yaml

from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.last_input_payload: dict[str, object] | None = None
        self.last_interrupts = [{"gate_id": "fake-specialist-gate"}]

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
    ) -> ProductionEnvelope:
        del base_state
        input_payload: dict[str, object] = {}
        for input_key, upstream_id in dependency_map.items():
            contribution = envelope.get_contribution(upstream_id)
            assert contribution is not None
            input_payload[input_key] = contribution.output
        self.last_input_payload = input_payload
        self.calls.append(
            {
                "specialist_id": specialist_id,
                "dependency_map": dependency_map,
                "input_payload": input_payload,
            }
        )
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={
                    "specialist_id": specialist_id,
                    "received": input_payload,
                    "usage": {"input_tokens": 120, "output_tokens": 30},
                },
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
                node_id=node_id,
            )
        )
        return updated


def _install_fake_adapter(monkeypatch) -> _FakeAdapter:
    adapter = _FakeAdapter()
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)
    return adapter


def _write_linear_manifest(tmp_path: Path, nodes: list[dict[str, object]]) -> Path:
    node_ids = [str(node["id"]) for node in nodes]
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": node_ids[0],
        "frozen_graph_version": "v42",
        "nodes": [
            {
                "id": node["id"],
                "label": node["id"],
                "specialist_id": node["specialist_id"],
                "scaffold_node": "act",
                "model_config_ref": None,
                "gate": False,
                "hud_tracked": True,
                "pack_version": "test",
                "rationale": "test manifest node",
                **(
                    {"dependencies": node["dependencies"]}
                    if "dependencies" in node
                    else {}
                ),
            }
            for node in nodes
        ],
        "edges": [
            {"from": "__start__", "to": node_ids[0]},
            *[
                {"from": left, "to": right}
                for left, right in zip(node_ids, node_ids[1:], strict=False)
            ],
            {"from": node_ids[-1], "to": "__end__"},
        ],
    }
    path = tmp_path / "linear-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_trial_registers_then_transitions_to_paused_gate(tmp_path: Path, monkeypatch) -> None:
    statuses: list[str] = []
    real_persist = production_runner._persist_envelope

    def capture(envelope, runs_root):
        statuses.append(envelope.status)
        return real_persist(envelope, runs_root)

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    _install_fake_adapter(monkeypatch)
    monkeypatch.setattr(production_runner, "_persist_envelope", capture)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    assert statuses[:2] == ["registered", "in-flight"]
    assert envelope.status == "paused-at-gate"
    assert envelope.paused_gate == "G1"
    assert (tmp_path / str(TRIAL_ID) / "run.json").exists()


def test_at_least_one_specialist_node_fires_and_writes_trace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    adapter = _install_fake_adapter(monkeypatch)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    trace = json.loads((tmp_path / str(TRIAL_ID) / "trace-fixture.json").read_text())
    assert envelope.production_clone_launch_evidence is True
    assert envelope.production_envelope is not None
    assert [item.specialist_id for item in envelope.production_envelope.contributions] == [
        "texas"
    ]
    assert adapter.calls[0]["specialist_id"] == "texas"
    assert trace["root"]["extra"]["metadata"]["trial_id"] == str(TRIAL_ID)
    assert trace["root"]["child_runs"][0]["extra"]["metadata"]["specialist_id"] == "texas"


def test_downstream_specialist_input_is_constructed_from_prior_contribution(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    adapter = _install_fake_adapter(monkeypatch)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_write_linear_manifest(
            tmp_path,
            [
                {"id": "02", "specialist_id": "texas", "dependencies": {}},
                {
                    "id": "04A",
                    "specialist_id": "irene",
                    "dependencies": {"upstream_output": "texas"},
                },
                {
                    "id": "4.75",
                    "specialist_id": "cd",
                    "dependencies": {"source_bundle": "texas"},
                },
            ],
        ),
        max_specialist_calls=3,
        pause_at_gates=False,
    )

    assert envelope.production_envelope is not None
    assert [item["specialist_id"] for item in adapter.calls[:3]] == [
        "texas",
        "irene",
        "cd",
    ]
    cd_call = adapter.calls[2]
    texas = envelope.production_envelope.get_contribution("texas")
    assert texas is not None
    assert cd_call["dependency_map"] == {"source_bundle": "texas"}
    assert cd_call["input_payload"] == {"source_bundle": texas.output}


def test_gate_node_pauses_with_registered_decision_card(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    _install_fake_adapter(monkeypatch)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
    )

    card_path = tmp_path / str(TRIAL_ID) / "decision-card-G1.json"
    payload = json.loads(card_path.read_text())
    assert envelope.status == "paused-at-gate"
    assert payload["card"]["gate_id"] == "G1"
    assert len(payload["digest"]) == 64


def test_dependency_map_fallback_isolated_contract() -> None:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    assert (
        production_runner._default_dependency_map_for(
            specialist_id="texas",
            production_envelope=envelope,
        )
        == {}
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="texas",
            output={"source": "bundle"},
            model_used="gpt-5-nano",
            cost_usd=0.0,
        )
    )

    assert production_runner._default_dependency_map_for(
        specialist_id="cd",
        production_envelope=envelope,
    ) == {"source_bundle": "texas"}
    assert production_runner._default_dependency_map_for(
        specialist_id="irene",
        production_envelope=envelope,
    ) == {"upstream_output": "texas"}


def test_multi_node_specialist_contributes_at_each_node(
    tmp_path: Path,
    monkeypatch,
) -> None:
    # S2 (SCP 2026-06-11): per-node keying — texas at §02 AND §03 produces
    # two distinct contributions; the retired per-specialist Path-Z skip
    # silently dropped the second job (irene_pass1 §05/§05B class).
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    adapter = _install_fake_adapter(monkeypatch)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_write_linear_manifest(
            tmp_path,
            [
                {"id": "02", "specialist_id": "texas", "dependencies": {}},
                {"id": "03", "specialist_id": "texas"},
                {
                    "id": "04A",
                    "specialist_id": "irene",
                    "dependencies": {"upstream_output": "texas"},
                },
            ],
        ),
        max_specialist_calls=3,
        pause_at_gates=False,
    )

    assert envelope.production_envelope is not None
    texas_rows = [
        item
        for item in envelope.production_envelope.contributions
        if item.specialist_id == "texas"
    ]
    assert [row.node_id for row in texas_rows] == ["02", "03"]
    assert [item["specialist_id"] for item in adapter.calls].count("texas") == 2
    assert [item.specialist_id for item in envelope.production_envelope.contributions].count(
        "irene"
    ) == 1

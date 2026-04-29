from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.manifest.schema import NodeSpec
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution

TRIAL_ID = UUID("22345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _FakeAdapter:
    def __init__(self, *, omit_first_contribution: bool = False) -> None:
        self.calls: list[dict[str, object]] = []
        self.omit_first_contribution = omit_first_contribution

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
    ) -> ProductionEnvelope:
        del base_state
        input_payload: dict[str, object] = {}
        for input_key, upstream_id in dependency_map.items():
            contribution = envelope.get_contribution(upstream_id)
            assert contribution is not None
            input_payload[input_key] = contribution.output
        self.calls.append(
            {
                "specialist_id": specialist_id,
                "dependency_map": dependency_map,
                "input_payload": input_payload,
            }
        )
        if self.omit_first_contribution and len(self.calls) == 1:
            return envelope
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={
                    "specialist_id": specialist_id,
                    "received": input_payload,
                    "usage": {"input_tokens": 100, "output_tokens": 25},
                },
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
            )
        )
        return updated


def _install_fake_adapter(monkeypatch, adapter: _FakeAdapter | None = None) -> _FakeAdapter:
    instance = adapter or _FakeAdapter()
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: instance)
    return instance


def _enable_live_path(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")


def _write_manifest(tmp_path: Path, nodes: list[dict[str, object]]) -> Path:
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
    path = tmp_path / "pipeline-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_manifest_declared_precedence(tmp_path: Path, monkeypatch) -> None:
    _enable_live_path(monkeypatch)
    adapter = _install_fake_adapter(monkeypatch)
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "02", "specialist_id": "texas", "dependencies": {}},
            {
                "id": "04A",
                "specialist_id": "irene",
                "dependencies": {"declared_input": "texas"},
            },
        ],
    )

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path / "runs",
        manifest_path=manifest_path,
        max_specialist_calls=2,
    )

    assert adapter.calls[1]["dependency_map"] == {"declared_input": "texas"}


def test_fallback_on_empty_dependencies_field(tmp_path: Path, monkeypatch) -> None:
    _enable_live_path(monkeypatch)
    adapter = _install_fake_adapter(monkeypatch)
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "02", "specialist_id": "texas", "dependencies": {}},
            {"id": "04A", "specialist_id": "irene", "dependencies": {}},
        ],
    )

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path / "runs",
        manifest_path=manifest_path,
        max_specialist_calls=2,
    )

    assert adapter.calls[1]["dependency_map"] == {"upstream_output": "texas"}


def test_fallback_on_missing_dependencies_field(tmp_path: Path, monkeypatch) -> None:
    _enable_live_path(monkeypatch)
    adapter = _install_fake_adapter(monkeypatch)
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "02", "specialist_id": "texas", "dependencies": {}},
            {"id": "04A", "specialist_id": "irene"},
        ],
    )

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path / "runs",
        manifest_path=manifest_path,
        max_specialist_calls=2,
    )

    assert adapter.calls[1]["dependency_map"] == {"upstream_output": "texas"}


def test_manifest_dependencies_accept_visible_alias_specialist_ids(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _enable_live_path(monkeypatch)
    adapter = _install_fake_adapter(monkeypatch)
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "07B", "specialist_id": "quinn-r", "dependencies": {}},
            {
                "id": "07E",
                "specialist_id": "kira",
                "dependencies": {"upstream_output": "quinn-r"},
            },
        ],
    )

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path / "runs",
        manifest_path=manifest_path,
        max_specialist_calls=2,
    )

    assert adapter.calls[0]["specialist_id"] == "quinn_r"
    assert adapter.calls[1]["dependency_map"] == {"upstream_output": "quinn_r"}


def test_missing_upstream_dependency_fails_loud(tmp_path: Path, monkeypatch) -> None:
    _enable_live_path(monkeypatch)
    _install_fake_adapter(monkeypatch)
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "02", "specialist_id": "texas", "dependencies": {}},
            {
                "id": "04A",
                "specialist_id": "irene",
                "dependencies": {"source_bundle": "phantom-specialist"},
            },
        ],
    )

    with pytest.raises(
        production_runner.MissingUpstreamContributionError,
        match="phantom-specialist.*source_bundle",
    ) as exc_info:
        production_runner.run_production_trial(
            CORPUS,
            "production",
            "operator_test",
            trial_id=TRIAL_ID,
            runs_root=tmp_path / "runs",
            manifest_path=manifest_path,
            max_specialist_calls=2,
        )

    assert exc_info.value.specialist_id == "phantom-specialist"
    assert exc_info.value.downstream_input_key == "source_bundle"


def test_upstream_ran_but_no_contribution_fails_loud(tmp_path: Path, monkeypatch) -> None:
    _enable_live_path(monkeypatch)
    _install_fake_adapter(monkeypatch, _FakeAdapter(omit_first_contribution=True))
    manifest_path = _write_manifest(
        tmp_path,
        [
            {"id": "02", "specialist_id": "texas", "dependencies": {}},
            {
                "id": "04A",
                "specialist_id": "irene",
                "dependencies": {"upstream_output": "texas"},
            },
        ],
    )

    with pytest.raises(
        production_runner.MissingUpstreamContributionError,
        match="texas.*upstream_output",
    ) as exc_info:
        production_runner.run_production_trial(
            CORPUS,
            "production",
            "operator_test",
            trial_id=TRIAL_ID,
            runs_root=tmp_path / "runs",
            manifest_path=manifest_path,
            max_specialist_calls=2,
        )

    assert exc_info.value.specialist_id == "texas"
    assert exc_info.value.downstream_input_key == "upstream_output"


def test_fallback_path_unchanged_for_undeclared_existing_manifest_node(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _enable_live_path(monkeypatch)
    adapter = _install_fake_adapter(monkeypatch)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_write_manifest(
            tmp_path,
            [
                {"id": "02", "specialist_id": "texas", "dependencies": {}},
                {"id": "04A", "specialist_id": "irene"},
                {"id": "4.75", "specialist_id": "cd"},
                {"id": "07", "specialist_id": "gary"},
            ],
        ),
        max_specialist_calls=4,
        pause_at_gates=False,
    )

    assert [call["specialist_id"] for call in adapter.calls[:4]] == [
        "texas",
        "irene",
        "cd",
        "gary",
    ]
    assert adapter.calls[3]["dependency_map"] == {"upstream_output": "cd"}
    assert envelope.production_envelope is not None
    assert [item.specialist_id for item in envelope.production_envelope.contributions] == [
        "texas",
        "irene",
        "cd",
        "gary",
    ]


def test_resolve_dependency_map_prefers_declared_map() -> None:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="texas",
            output={"source": "bundle"},
            model_used="gpt-5-nano",
            cost_usd=0.0,
        )
    )
    node = NodeSpec(
        id="4.75",
        specialist_id="cd",
        dependencies={"source_bundle": "texas"},
    )

    assert production_runner._resolve_dependency_map(
        node=node,
        specialist_id="cd",
        production_envelope=envelope,
    ) == {"source_bundle": "texas"}

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.gates.errors import GateError
from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.models.runtime import ProductionEnvelope, SpecialistContribution
from app.models.state.operator_verdict import OperatorVerdict

CORPUS = Path("tests/fixtures/trial_corpus/README.md")


class _RecordingAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict[str, object] | None = None,
        projection_map: dict[str, str] | None = None,
    ) -> ProductionEnvelope:
        del projection_map
        cache_prefix = None
        if base_state is not None and base_state.cache_state is not None:
            cache_prefix = base_state.cache_state.cache_prefix
        self.calls.append(
            {
                "specialist_id": specialist_id,
                "dependency_map": dependency_map,
                "cache_prefix": cache_prefix,
                "runner_supplied_payload": runner_supplied_payload,
            }
        )
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output={
                    "specialist_id": specialist_id,
                    "received_edit": json.loads(cache_prefix) if cache_prefix else None,
                    "usage": {"input_tokens": 100, "output_tokens": 25},
                },
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
def adapter(monkeypatch) -> _RecordingAdapter:
    instance = _RecordingAdapter()
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: instance)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    return instance


def _manifest(path: Path, *, gate_id: str) -> Path:
    path.write_text(
        f"""
schema_version: "1.0"
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
""".lstrip(),
        encoding="utf-8",
    )
    return path


def _manifest_with_resume_specialists(
    path: Path,
    *,
    gate_id: str,
    after_gate: list[str],
) -> Path:
    nodes = [
        '  - id: "01"',
        '    specialist_id: "irene"',
        '  - id: "02"',
        '    specialist_id: "marcus"',
        "    gate: true",
        f'    gate_code: "{gate_id}"',
    ]
    edges = [
        '  - from: "__start__"',
        '    to: "01"',
        '  - from: "01"',
        '    to: "02"',
    ]
    previous = "02"
    for offset, specialist_id in enumerate(after_gate, start=3):
        node_id = f"{offset:02d}"
        nodes.extend([f'  - id: "{node_id}"', f'    specialist_id: "{specialist_id}"'])
        edges.extend([f'  - from: "{previous}"', f'    to: "{node_id}"'])
        previous = node_id
    edges.extend([f'  - from: "{previous}"', '    to: "__end__"'])
    path.write_text(
        "\n".join(
            [
                'schema_version: "1.0"',
                'lane: "run_graph"',
                'entrypoint: "01"',
                'frozen_graph_version: "v42"',
                "nodes:",
                *nodes,
                "edges:",
                *edges,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _decision_payload(tmp_path: Path, trial_id: UUID, gate_id: str) -> dict[str, object]:
    return json.loads(
        (tmp_path / str(trial_id) / f"decision-card-{gate_id}.json").read_text(
            encoding="utf-8"
        )
    )


def _verdict(
    tmp_path: Path,
    *,
    trial_id: UUID,
    gate_id: str,
    verb: str,
    **overrides,
) -> OperatorVerdict:
    payload = _decision_payload(tmp_path, trial_id, gate_id)
    return OperatorVerdict(
        trial_id=trial_id,
        verb=verb,
        gate_id=gate_id,
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=overrides.pop("digest", payload["digest"]),
        **overrides,
    )


def test_pause_at_g1_verdict_continues_execution_to_completion(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path / "manifest.yaml", gate_id="G1"),
        max_specialist_calls=1,
    )

    envelope = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(tmp_path, trial_id=trial_id, gate_id="G1", verb="approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    assert envelope.status == "completed"
    assert envelope.paused_gate is None
    assert [item.specialist_id for item in envelope.production_envelope.contributions] == [
        "texas",
        "irene",
    ]
    assert [item["specialist_id"] for item in adapter.calls] == ["texas", "irene"]
    assert envelope.production_clone_launch_evidence is True


def test_pause_at_g2c_edit_verdict_is_marshaled_to_post_gate_state(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path / "manifest-g2c.yaml", gate_id="G2C"),
        max_specialist_calls=1,
    )
    edit_payload = {"slide_count": 3, "tone": "concise"}

    envelope = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(
            tmp_path,
            trial_id=trial_id,
            gate_id="G2C",
            verb="edit",
            edit_payload=edit_payload,
        ),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    assert envelope.status == "completed"
    assert json.loads(adapter.calls[-1]["cache_prefix"]) == edit_payload
    irene = envelope.production_envelope.get_contribution("irene")
    assert irene is not None
    assert irene.output["received_edit"] == edit_payload


def test_verdict_validation_failure_leaves_checkpoint_and_trial_paused(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path / "manifest-validation.yaml", gate_id="G1"),
        max_specialist_calls=1,
    )
    checkpoint_before = (tmp_path / str(trial_id) / "checkpoint.json").read_text(
        encoding="utf-8"
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        production_runner.resume_production_trial(
            trial_id=trial_id,
            verdict=_verdict(
                tmp_path,
                trial_id=trial_id,
                gate_id="G1",
                verb="approve",
                digest="b" * 64,
            ),
            runs_root=tmp_path,
            max_specialist_calls=1,
        )

    persisted = json.loads((tmp_path / str(trial_id) / "run.json").read_text())
    assert persisted["status"] == "paused-at-gate"
    assert (tmp_path / str(trial_id) / "checkpoint.json").read_text(
        encoding="utf-8"
    ) == checkpoint_before
    assert not (tmp_path / str(trial_id) / "resume-command.json").exists()
    assert [item["specialist_id"] for item in adapter.calls] == ["texas"]


def test_gate_checkpoint_persists_directive_path_for_resume(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir()
    directive = run_dir / "directive.yaml"
    directive.write_text("run_id: T1\ngamma_settings: []\n", encoding="utf-8")

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path / "manifest-directive.yaml", gate_id="G1"),
        max_specialist_calls=1,
        directive_path=directive,
    )

    del adapter
    checkpoint = json.loads((run_dir / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["runner"]["directive_path"] == directive.as_posix()
    assert checkpoint["runner"]["bundle_dir"] == (run_dir / "bundle").as_posix()


def test_resume_reconstructs_canonical_directive_path_for_texas_and_gary(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir()
    directive = run_dir / "directive.yaml"
    directive.write_text(
        "\n".join(
            [
                "run_id: T1",
                "gamma_settings:",
                "  - variant_id: A",
                "    image_style: photographic",
                "  - variant_id: B",
                "    image_style: diagrammatic",
                "",
            ]
        ),
        encoding="utf-8",
    )

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest_with_resume_specialists(
            tmp_path / "manifest-resume-directive.yaml",
            gate_id="G1",
            after_gate=["texas", "gary"],
        ),
        max_specialist_calls=1,
        directive_path=directive,
    )
    checkpoint_path = run_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint["runner"].pop("directive_path", None)
    checkpoint["runner"].pop("bundle_dir", None)
    checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")

    envelope = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(tmp_path, trial_id=trial_id, gate_id="G1", verb="approve"),
        runs_root=tmp_path,
        max_specialist_calls=2,
    )

    assert envelope.status == "completed"
    texas_payload = next(
        item["runner_supplied_payload"]
        for item in adapter.calls
        if item["specialist_id"] == "texas"
    )
    assert texas_payload == {
        "directive_path": directive.as_posix(),
        "bundle_dir": (run_dir / "bundle").as_posix(),
    }
    gary_payload = next(
        item["runner_supplied_payload"]
        for item in adapter.calls
        if item["specialist_id"] == "gary"
    )
    # Canonical-arc S3 (D1/D4, F-205 pin EXTENSION — never weakened): the
    # parity-context keys joined the exact-payload pin. No cd contribution /
    # trial-start.json in this harness ⇒ honest None; the directive digest
    # attests the SAME bytes the gamma_settings parse read.
    assert gary_payload == {
        "export_dir": (run_dir / "exports" / "gary").as_posix(),
        "gamma_settings": [
            {"variant_id": "A", "image_style": "photographic"},
            {"variant_id": "B", "image_style": "diagrammatic"},
        ],
        "cd_styleguide_resolution": None,
        "directive_digest": hashlib.sha256(directive.read_bytes()).hexdigest(),
        "trial_start_directive_digest": None,
    }


def test_resume_without_gamma_settings_preserves_gary_legacy_payload(
    tmp_path: Path,
    adapter: _RecordingAdapter,
) -> None:
    trial_id = uuid4()
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir()
    directive = run_dir / "directive.yaml"
    directive.write_text("run_id: T1\n", encoding="utf-8")

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest_with_resume_specialists(
            tmp_path / "manifest-resume-legacy.yaml",
            gate_id="G1",
            after_gate=["gary"],
        ),
        max_specialist_calls=1,
        directive_path=directive,
    )

    envelope = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(tmp_path, trial_id=trial_id, gate_id="G1", verb="approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    assert envelope.status == "completed"
    gary_payload = next(
        item["runner_supplied_payload"]
        for item in adapter.calls
        if item["specialist_id"] == "gary"
    )
    # Canonical-arc S3 (D1/D4, F-205 pin EXTENSION — never weakened): the
    # legacy payload still carries NO gamma_settings key; the parity-context
    # keys are present with honest None (cd/trial-start absent) plus the
    # digest of the settings-less directive bytes.
    assert gary_payload == {
        "export_dir": (run_dir / "exports" / "gary").as_posix(),
        "cd_styleguide_resolution": None,
        "directive_digest": hashlib.sha256(directive.read_bytes()).hexdigest(),
        "trial_start_directive_digest": None,
    }

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import yaml

from app.marcus.orchestrator import workbook_wiring
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.specialist_model_config import SpecialistModelConfig
from app.specialists.dispatch_errors import SpecialistDispatchError


def _empty_envelope() -> ProductionEnvelope:
    return ProductionEnvelope(trial_id=uuid4())


def test_default_band_executes_exact_truthful_stubs_in_order() -> None:
    envelope = _empty_envelope()
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=envelope
        )

    assert [(item.node_id, item.specialist_id) for item in envelope.contributions] == [
        ("07W.1", "workbook_brief_stub"),
        ("07W.2", "ask_a_enrichment"),
        ("07W.3", "workbook_review_stub"),
        ("07W.4", "ask_b_hot_topics"),
    ]
    assert all(
        item.model_used == "deterministic-workbook-band-stub"
        for item in envelope.contributions
    )
    assert envelope.contributions[0].output == {
        "stub_status": "not_yet_wired",
        "brief_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }
    assert envelope.contributions[1].output == {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_a_not_yet_wired"],
    }
    assert envelope.contributions[2].output == {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }
    assert envelope.contributions[3].output == {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_b_not_yet_wired"],
    }


def test_factory_is_not_called_when_exact_coordinate_exists() -> None:
    calls: list[str] = []

    def spy(node_id: str, envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"spy": True}

    factories: dict[str, Callable[[str, ProductionEnvelope], dict[str, object]]] = {
        "07W.1": spy
    }
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=_empty_envelope(), factories=factories
    )
    repeated = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=envelope, factories=factories
    )
    assert calls == ["07W.1"]
    assert repeated is envelope


def test_partial_resume_only_calls_missing_nodes() -> None:
    calls: list[str] = []

    def spy(node_id: str, envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"node": node_id}

    factories = dict.fromkeys(workbook_wiring.WORKBOOK_BAND_NODE_IDS, spy)
    envelope = workbook_wiring.run_workbook_band_node(
        node_id="07W.1", production_envelope=_empty_envelope(), factories=factories
    )
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=envelope, factories=factories
        )
    assert calls == list(workbook_wiring.WORKBOOK_BAND_NODE_IDS)


def test_serialized_partial_resume_only_invokes_missing_factories() -> None:
    calls: list[str] = []

    def spy(node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
        calls.append(node_id)
        return {"node": node_id}

    factories = dict.fromkeys(workbook_wiring.WORKBOOK_BAND_NODE_IDS, spy)
    envelope = _empty_envelope()
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS[:2]:
        envelope = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=envelope, factories=factories
        )
    reloaded = ProductionEnvelope.model_validate_json(envelope.model_dump_json())
    calls.clear()
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        reloaded = workbook_wiring.run_workbook_band_node(
            node_id=node_id, production_envelope=reloaded, factories=factories
        )
    assert calls == ["07W.3", "07W.4"]


@pytest.mark.parametrize(
    ("factory", "tag"),
    [
        (lambda _n, _e: (_ for _ in ()).throw(RuntimeError("boom")),
         "workbook.band.factory-failed"),
        (lambda _n, _e: ["not-a-dict"], "workbook.band.invalid-output"),
        (lambda _n, _e: {"bad": object()}, "workbook.band.invalid-output"),
    ],
)
def test_factory_failures_are_tagged(factory: object, tag: str) -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1",
            production_envelope=_empty_envelope(),
            factories={"07W.1": factory},  # type: ignore[dict-item]
        )
    assert caught.value.tag == tag


def test_invalid_context_is_tagged() -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.1", production_envelope=object()  # type: ignore[arg-type]
        )
    assert caught.value.tag == "workbook.band.invalid-context"


def test_unknown_node_is_tagged() -> None:
    with pytest.raises(SpecialistDispatchError) as caught:
        workbook_wiring.run_workbook_band_node(
            node_id="07W.9", production_envelope=_empty_envelope()
        )
    assert caught.value.tag == "workbook.band.unknown-node"


def test_manifest_band_and_model_config_are_pinned() -> None:
    raw = yaml.safe_load(Path("state/config/pipeline-manifest.yaml").read_text("utf-8"))
    nodes = {node["id"]: node for node in raw["nodes"]}
    order = [node["id"] for node in raw["nodes"]]
    assert order[-5:] == ["07W.1", "07W.2", "07W.3", "07W.4", "07W"]
    expected_after = {
        "07W.1": "15", "07W.2": "07W.1", "07W.3": "07W.2",
        "07W.4": "07W.3", "07W": "07W.4",
    }
    for node_id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
        node = nodes[node_id]
        assert node["specialist_id"] is None
        assert node["gate"] is False
        assert node["hud_tracked"] is False
        assert node["sub_phase_of"] == "07W"
        assert node["insertion_after"] == expected_after[node_id]
    config = SpecialistModelConfig.model_validate(
        yaml.safe_load(
            Path("app/marcus/orchestrator/workbook_writer_model_config.yaml").read_text(
                "utf-8"
            )
        )
    )
    assert config.model_dump() == {
        "specialist_id": "workbook_writer",
        "default_model": "gpt-5",
        "per_node_overrides": {},
        "temperature_default": 0.2,
    }
    config_ref = "app/marcus/orchestrator/workbook_writer_model_config.yaml"
    assert nodes["07W.1"]["model_config_ref"] == config_ref
    assert nodes["07W.3"]["model_config_ref"] == config_ref
    assert nodes["07W.2"]["model_config_ref"] is None
    assert nodes["07W.4"]["model_config_ref"] is None
    assert nodes["07W"]["model_config_ref"] is None


@pytest.mark.parametrize(
    ("offline_after_g1", "failure_tag"),
    [
        (False, None),
        (True, None),
        (True, "workbook.band.invalid-context"),
        (True, "workbook.band.unknown-node"),
    ],
)
def test_real_start_then_continuation_reaches_band_in_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    offline_after_g1: bool,
    failure_tag: str | None,
) -> None:
    """Behavioral two-walk proof: pre-band pause, then one real resume walk."""
    from app.gates.resume_api import clear_resume_registry
    from app.marcus.orchestrator import production_runner
    from app.models.state.component_selection import ComponentSelection
    from app.models.state.operator_verdict import OperatorVerdict

    trial_id = UUID("72345678-1234-4234-8234-123456789abc")
    calls: list[str] = []
    real_hook = workbook_wiring.run_workbook_band_node

    class _Adapter:
        def invoke_specialist(
            self,
            *,
            specialist_id: str,
            envelope: ProductionEnvelope,
            cost_usd: float = 0.0,
            node_id: str | None = None,
            **_kwargs: object,
        ) -> ProductionEnvelope:
            updated = envelope.model_copy(deep=True)
            outputs = {
                "irene_pass1": {"lesson_plan": {"plan_units": [{"unit_id": "u1"}]}},
                "cd": {"cd_directive": {"experience_profile": "text-led"}},
            }
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=specialist_id,
                    output=outputs.get(specialist_id, {"specialist_id": specialist_id}),
                    model_used="gpt-5-nano",
                    cost_usd=cost_usd,
                    node_id=node_id,
                )
            )
            return updated

    def _spy(**kwargs: object) -> ProductionEnvelope:
        calls.append(str(kwargs["node_id"]))
        if failure_tag == "workbook.band.invalid-context":
            return real_hook(
                node_id=str(kwargs["node_id"]),
                production_envelope=object(),  # type: ignore[arg-type]
            )
        if failure_tag == "workbook.band.unknown-node":
            return real_hook(
                node_id="07W.9",
                production_envelope=kwargs["production_envelope"],  # type: ignore[arg-type]
            )
        return real_hook(**kwargs)  # type: ignore[arg-type]

    clear_resume_registry()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "0")
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)
    monkeypatch.setattr(production_runner, "production_gate_ids", lambda _m: {"G1"})
    monkeypatch.setattr(production_runner, "_record_cost", lambda **_kwargs: None)
    monkeypatch.setattr(
        production_runner,
        "_run_start_preflight_gate",
        lambda *_args, **_kwargs: SimpleNamespace(
            all_green=True, blocking_items=lambda: []
        ),
    )
    monkeypatch.setattr(workbook_wiring, "run_workbook_band_node", _spy)

    started = production_runner.run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=100,
        component_selection=ComponentSelection(
            deck=True, motion=True, workbook=True
        ),
        hud="off",
    )
    assert started.paused_gate == "G1"
    assert calls == []

    card_payload = json.loads(
        (tmp_path / str(trial_id) / "decision-card-G1.json").read_text("utf-8")
    )
    verdict = OperatorVerdict(
        trial_id=trial_id,
        verb="approve",
        gate_id="G1",
        card_id=UUID(card_payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=card_payload["digest"],
    )
    # The start walk must be a genuine gated walk. Once G1 is accepted, switch
    # only the persisted continuation harness to offline traversal so later
    # unrelated production gates do not prevent this continuation reaching the
    # terminal band. The band hook itself is required to ignore this flag.
    checkpoint_path = tmp_path / str(trial_id) / "checkpoint.json"
    if offline_after_g1:
        checkpoint = json.loads(checkpoint_path.read_text("utf-8"))
        checkpoint["runner"]["allow_offline_cost_report"] = True
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2) + "\n", "utf-8")
    resumed = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=verdict,
        runs_root=tmp_path,
        max_specialist_calls=100,
    )
    for _ in range(12):
        if resumed.status != "paused-at-gate":
            break
        gate_id = resumed.paused_gate
        assert gate_id is not None
        payload = json.loads(
            (tmp_path / str(trial_id) / f"decision-card-{gate_id}.json").read_text(
                "utf-8"
            )
        )
        resumed = production_runner.resume_production_trial(
            trial_id=trial_id,
            verdict=OperatorVerdict(
                trial_id=trial_id,
                verb="approve",
                gate_id=gate_id,
                card_id=UUID(payload["card"]["card_id"]),
                operator_id="operator_test",
                decision_card_digest=payload["digest"],
            ),
            runs_root=tmp_path,
            max_specialist_calls=100,
        )
    if failure_tag is not None:
        assert resumed.status == "paused-at-error"
        assert calls == ["07W.1"]
        error_pause = json.loads(
            (tmp_path / str(trial_id) / "error-pause.json").read_text("utf-8")
        )
        assert error_pause["node_id"] == "07W.1"
        assert error_pause["tag"] == failure_tag
        assert resumed.production_envelope.get_contribution(
            workbook_wiring.WORKBOOK_BRIEF_SPECIALIST_ID, node_id="07W.1"
        ) is None
        return
    assert resumed.status == "completed", resumed.model_dump(mode="json")
    assert calls == list(workbook_wiring.WORKBOOK_BAND_NODE_IDS)
    for node_id, specialist_id in workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS.items():
        assert resumed.production_envelope.get_contribution(
            specialist_id, node_id=node_id
        ) is not None

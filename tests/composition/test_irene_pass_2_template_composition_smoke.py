from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene.graph import build_irene_graph


class _IreneFakeChat:
    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        joined = "\n".join(str(message.get("content", "")) for message in messages)
        assert "schema/irene_pass_2_authoring.v1.schema.json" in joined
        return SimpleNamespace(
            content=json.dumps(
                {
                    # id-integrity gate: narration segments carry a usable ``id``
                    # (the shared join keys narration text on ``id``); an id-less
                    # segment fails loud by design (the 40f3a90a collapse).
                    "narration_script": [
                        {"id": "seg-01", "segment_id": "seg-01", "text": "Pass 2 narration."}
                    ],
                    # dp-v1.1: deltas must join the grounded roster or the act
                    # raises Pass2GroundingError (cycle-4 confabulation kill).
                    "segment_manifest_deltas": [
                        {
                            "segment_id": "seg-01",
                            "bridge_type": "none",
                            "visual_references": [{"perception_source": "s1"}],
                        }
                    ],
                }
            ),
            usage_metadata={"input_tokens": 20, "output_tokens": 10},
        )


def _fake_make_chat_model(specialist_id: str, **kwargs: object) -> SimpleNamespace:
    del kwargs
    return SimpleNamespace(
        chat=_IreneFakeChat(),
        entry=ModelResolutionEntry(
            level="per_specialist",
            requested=None,
            resolved="gpt-5-nano",
            reason=f"composition fixture {specialist_id}",
            timestamp=datetime.now(UTC),
            cache_prefix_hash="d" * 64,
        ),
    )


def test_irene_pass_2_template_composition_smoke(monkeypatch, tmp_path) -> None:
    from tests.specialists.irene.conftest import make_grounded_pass2_payload

    monkeypatch.setattr("app.specialists.irene.graph.make_chat_model", _fake_make_chat_model)
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    payload = make_grounded_pass2_payload(
        tmp_path,
        pass_phase="pass-2",
        composition_mode="composed",
        authoring_schema="schema/irene_pass_2_authoring.v1.schema.json",
    )
    base_state = RunState(
        run_id=trial_id,
        graph_version="v42",
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True, separators=(",", ":"))
        ),
    )
    adapter = ProductionDispatchAdapter(graph_builders={"irene": build_irene_graph})

    envelope = adapter.invoke_specialist(
        specialist_id="irene",
        envelope=ProductionEnvelope(trial_id=trial_id),
        dependency_map={},
        cost_usd=0.0,
        base_state=base_state,
    )

    contribution = envelope.get_contribution("irene")
    assert contribution is not None
    assert contribution.output["narration_script"][0]["segment_id"] == "seg-01"
    assert contribution.output["segment_manifest_deltas"][0]["bridge_type"] == "none"
    assert contribution.specialist_id == "irene"
    assert adapter.last_interrupts

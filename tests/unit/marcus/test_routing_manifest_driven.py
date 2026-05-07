from __future__ import annotations

from pathlib import Path

from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from app.marcus.orchestrator.routing import route_step


def _manifest() -> PipelineManifest:
    return PipelineManifest.model_validate(
        {
            "schema_version": "0.1-test",
            "lane": "run_graph",
            "entrypoint": "01",
            "frozen_graph_version": "v-test",
            "nodes": [
                NodeSpec(id="01", specialist_id="alpha"),
                NodeSpec(id="02", specialist_id="beta"),
                NodeSpec(id="03", specialist_id="gamma"),
            ],
            "edges": [
                EdgeSpec.model_validate(
                    {
                        "from": "__start__",
                        "to": "01",
                        "decision_card_schema": "app.models.decision_cards.g1:G1Card",
                    }
                ),
                EdgeSpec.model_validate(
                    {
                        "from": "01",
                        "to": "02",
                        "decision_card_schema": "app.models.decision_cards.g2c:G2CCard",
                    }
                ),
                EdgeSpec.model_validate({"from": "02", "to": "03"}),
            ],
        }
    )


def test_routing_reads_manifest_specialist_id() -> None:
    manifest = _manifest()

    decision_start = route_step(current_node=None, manifest=manifest)
    decision_mid = route_step(current_node="01", manifest=manifest)

    assert decision_start.target_specialist == "alpha"
    assert decision_mid.target_specialist == "beta"
    assert decision_start.decision_card_schema == "app.models.decision_cards.g1:G1Card"
    assert decision_mid.decision_card_schema == "app.models.decision_cards.g2c:G2CCard"


def test_routing_has_no_inline_specialist_selection() -> None:
    source = Path("marcus/orchestrator/routing.py").read_text(encoding="utf-8").lower()
    for forbidden in ("irene", "kira", "texas", "gary", "vera", "quinn-r"):
        assert forbidden not in source

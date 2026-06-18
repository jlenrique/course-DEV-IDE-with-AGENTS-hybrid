from __future__ import annotations

from pathlib import Path

import pytest

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
    # Path repointed 2026-06-18 (Arc-1a code review): the module lives at
    # app/marcus/orchestrator/routing.py post-Slab-1; the prior relative
    # "marcus/orchestrator/routing.py" FileNotFound'd, leaving the guard inert.
    source_path = (
        Path(__file__).resolve().parents[3]
        / "app"
        / "marcus"
        / "orchestrator"
        / "routing.py"
    )
    source = source_path.read_text(encoding="utf-8").lower()
    for forbidden in ("irene", "kira", "texas", "gary", "vera", "quinn-r"):
        assert forbidden not in source


def _folded_gate_manifest() -> PipelineManifest:
    """01 (alpha) -> [content-free folded gate G] -> 02 (beta). The gate node
    has no specialist_id and a fold_with, so it is a pass-through the router
    must skip (Arc-1a, 2026-06-18)."""
    return PipelineManifest.model_validate(
        {
            "schema_version": "0.1-test",
            "lane": "run_graph",
            "entrypoint": "01",
            "frozen_graph_version": "v-test",
            "nodes": [
                NodeSpec(id="01", specialist_id="alpha"),
                NodeSpec(id="G", specialist_id=None, gate=True, gate_code="G2B", fold_with="G2C"),
                NodeSpec(id="02", specialist_id="beta"),
            ],
            "edges": [
                EdgeSpec.model_validate({"from": "__start__", "to": "01"}),
                EdgeSpec.model_validate({"from": "01", "to": "G"}),
                EdgeSpec.model_validate({"from": "G", "to": "02"}),
                EdgeSpec.model_validate({"from": "02", "to": "__end__"}),
            ],
        }
    )


def test_routing_skips_content_free_folded_gate() -> None:
    """A woken-gate split puts a content-free folded gate node between two
    specialists; route_step transparently skips it to the next specialist and
    preserves `origin` as the real prior node (not the skipped gate)."""
    manifest = _folded_gate_manifest()

    decision = route_step(current_node="01", manifest=manifest)

    assert decision.next_node_id == "02"
    assert decision.target_specialist == "beta"
    assert decision.current_node_id == "01"  # origin preserved, gate transparent


def test_routing_raises_on_content_free_cycle() -> None:
    """A cycle through content-free nodes must raise loudly, not loop forever
    (the `visited` guard in route_step)."""
    manifest = PipelineManifest.model_validate(
        {
            "schema_version": "0.1-test",
            "lane": "run_graph",
            "entrypoint": "01",
            "frozen_graph_version": "v-test",
            "nodes": [
                NodeSpec(id="01", specialist_id="alpha"),
                NodeSpec(id="GA", specialist_id=None, gate=True, gate_code="GX", fold_with="G2C"),
                NodeSpec(id="GB", specialist_id=None, gate=True, gate_code="GY", fold_with="G2C"),
            ],
            "edges": [
                EdgeSpec.model_validate({"from": "__start__", "to": "01"}),
                EdgeSpec.model_validate({"from": "01", "to": "GA"}),
                EdgeSpec.model_validate({"from": "GA", "to": "GB"}),
                EdgeSpec.model_validate({"from": "GB", "to": "GA"}),
            ],
        }
    )

    with pytest.raises(ValueError, match="cycle through content-free nodes"):
        route_step(current_node="01", manifest=manifest)

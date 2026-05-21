from __future__ import annotations

import inspect
import json

import pytest

from app.specialists.texas.retrieval_dispatch import dispatch_retrieval
from app.specialists.tracy import _act as tracy_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestTracyToTexasChain(ChainTestBase):
    upstream_specialist = "tracy"
    downstream_specialist = "texas"
    gate_id = "G2"
    cassette_path = "tests/fixtures/composition/tracy-to-texas"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_retrieval_intent_shape_is_texas_compatible(self) -> None:
        intent = tracy_act.parse_retrieval_intents(
            json.dumps(
                {
                    "retrieval_intents": [
                        {
                            "intent": "Find evidence for worked examples.",
                            "provider_hints": [
                                {"provider": "scite", "params": {"mode": "search"}}
                            ],
                            "acceptance_criteria": {
                                "mechanical": {"min_results": 2},
                                "provider_scored": {
                                    "authority_tier_min": "peer-reviewed"
                                },
                                "semantic_deferred": "Tracy screens for lesson fit.",
                            },
                        }
                    ]
                }
            )
        )[0]
        assert set(intent["acceptance_criteria"]) == {
            "mechanical",
            "provider_scored",
            "semantic_deferred",
        }
        ready_or_stub = set(tracy_act.available_retrieval_provider_ids())
        assert {hint["provider"] for hint in intent["provider_hints"]} <= ready_or_stub

    def test_texas_dispatch_signature_accepts_directive_and_bundle_paths(self) -> None:
        signature = inspect.signature(dispatch_retrieval)
        assert {"directive_path", "bundle_dir"} <= set(signature.parameters)
        receipt = dispatch_retrieval(directive_path=None, bundle_dir=None)
        assert receipt["status"] == "mocked"

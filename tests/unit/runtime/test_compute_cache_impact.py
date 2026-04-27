from __future__ import annotations

import pytest

from app.runtime.override_api import compute_cache_impact
from tests.unit.runtime._helpers import TRIAL_ID, register_sample_run_state


@pytest.mark.parametrize(
    ("node_id", "minimum_nodes"),
    [
        ("05", {"05"}),
        ("04", {"04", "05"}),
        ("01", {"01", "02", "04"}),
    ],
)
def test_compute_cache_impact_reports_affected_nodes(
    node_id: str,
    minimum_nodes: set[str],
) -> None:
    register_sample_run_state()
    impact = compute_cache_impact(TRIAL_ID, node_id, "gpt-5-mini")
    assert minimum_nodes.issubset(set(impact["affected_nodes"]))
    assert impact["cache_state_delta"]["before"] == "healthy"
    assert impact["cache_state_delta"]["after"] == "mixed"


def test_compute_cache_impact_uses_leaf_cost_delta() -> None:
    register_sample_run_state()
    impact = compute_cache_impact(TRIAL_ID, "05", "gpt-5-nano")
    assert impact["current_model"] == "gpt-5"
    assert impact["estimated_cost_delta_usd"] == 0.0

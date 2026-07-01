"""Leg-2 (concierge-production-substrate): kira (07E) continuation-walk isolation.

OFFLINE integration pin for the real invariant the Leg-2 decouple protects:

    kira on the CONTINUATION walk receives the UNCONDITIONAL run-scoped
    ``bundle_path`` via ``runner_supplied_payload``; it passes the 07E
    dispatch-adapter COLLISION GUARD (07E projects only ``motion_plan``, NOT
    ``bundle_path``); and it lands in kira's ``cache_state.cache_prefix`` — so
    kira roots its motion/ receipts + .mp4s under ``runs_root/<trial_id>`` and
    NEVER the process-global ``runs/kira-motion``.

This is exercised at the dispatch-adapter level (``build_specialist_state``) —
the seam where 07E's REAL ``dependency_projections`` (loaded from
``state/config/pipeline-manifest.yaml``) and the runner-supplied
``{"bundle_path": ...}`` meet the collision guard and cache-prefix builder. No
Kling / network call occurs: ``build_specialist_state`` never compiles or
invokes kira's graph.

Why the adapter level (not a full continuation-walk drive): the task's
preferred shape. The full walk would require a live/stubbed kira graph + a
resumable checkpoint; the adapter seam is the SMALLEST test that genuinely
exercises (a) the real 07E projection_map, (b) the collision guard accepting an
unconditional ``bundle_path`` alongside the projected ``motion_plan``, and
(c) ``bundle_path`` reaching the constructed cache_state — which is exactly the
three-part invariant under review.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.manifest.loader import load as load_manifest
from app.marcus.orchestrator.dispatch_adapter import (
    ProductionDispatchAdapter,
    ProductionDispatchAdapterError,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)

TRIAL_ID = UUID("11111111-2222-4222-8222-333333333333")
MANIFEST_PATH = Path("state/config/pipeline-manifest.yaml")


def _motion_plan_contribution() -> SpecialistContribution:
    """A realistic 07D.5 motion_planner contribution the 07E projection reads."""
    output = {
        "motion_plan": {
            "slides": [
                {"slide_key": "B2", "provider": "kling-v1-6", "prompt": "text2video"}
            ]
        }
    }
    return SpecialistContribution(
        specialist_id="motion_planner",
        contributed_at=datetime.now(UTC),
        output=output,
        cost_usd=0.0,
        model_used="deterministic",
        output_digest=compute_output_digest(output),
    )


def _node_07e_projection_map() -> dict[str, object]:
    """Load node 07E's REAL dependency_projections from the shipped manifest."""
    manifest = load_manifest(MANIFEST_PATH)
    node = next(n for n in manifest.nodes if n.id == "07E")
    assert node.specialist_id == "kira"
    assert node.dependency_projections is not None
    return node.dependency_projections


def test_07e_real_projection_does_not_declare_bundle_path() -> None:
    """The invariant that makes an UNCONDITIONAL bundle_path safe: 07E's real
    projection delivers only ``motion_plan`` — it does NOT claim ``bundle_path``,
    so a runner-supplied ``bundle_path`` cannot collide with it."""
    projection_map = _node_07e_projection_map()
    assert "motion_plan" in projection_map
    assert "bundle_path" not in projection_map


def test_continuation_bundle_path_reaches_kira_cache_state_offline() -> None:
    """Happy path: real 07E projection_map + runner-supplied run-scoped
    bundle_path → NO ProductionDispatchAdapterError, and BOTH the projected
    ``motion_plan`` and the run-scoped ``bundle_path`` land in kira's
    cache_state.cache_prefix (never the global runs/kira-motion)."""
    adapter = ProductionDispatchAdapter()
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(_motion_plan_contribution())

    runs_root = Path("/tmp/runs-root")
    expected_bundle = (runs_root / str(TRIAL_ID)).as_posix()

    # No exception == the collision guard accepted the unconditional bundle_path
    # against the real 07E projection.
    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={},
        runner_supplied_payload={"bundle_path": expected_bundle},
        projection_map=_node_07e_projection_map(),
    )

    assert state.cache_state is not None
    payload = json.loads(state.cache_state.cache_prefix)
    # (a) run-scoped bundle_path reached kira's cache_prefix ...
    assert payload["bundle_path"] == expected_bundle
    assert "runs/kira-motion" not in payload["bundle_path"]
    # (b) ... alongside the projected motion_plan from 07D.5 (both delivered, no
    #     mechanism shadowed the other).
    assert payload["motion_plan"] == {
        "slides": [{"slide_key": "B2", "provider": "kling-v1-6", "prompt": "text2video"}]
    }


def test_bundle_path_collision_with_projection_refuses_loudly() -> None:
    """Teeth for the collision guard: IF 07E ever projected a ``bundle_path``
    key (i.e. the runner seam and a projection both delivered it), the adapter
    MUST refuse loudly rather than silently shadow one. This proves the guard is
    real — and is exactly the RED condition ('if bundle_path collided') the
    happy-path test relies on NOT holding for the real 07E projection."""
    adapter = ProductionDispatchAdapter()
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    # A producer whose output carries a bundle_path key, projected onto the
    # consumer input key 'bundle_path' — a synthetic collision.
    colliding_output = {"bundle_path": "/tmp/runs-root/from-projection"}
    envelope.add_contribution(
        SpecialistContribution(
            specialist_id="motion_planner",
            contributed_at=datetime.now(UTC),
            output=colliding_output,
            cost_usd=0.0,
            model_used="deterministic",
            output_digest=compute_output_digest(colliding_output),
        )
    )
    colliding_projection = {
        "bundle_path": {"from": "motion_planner", "key": "bundle_path"}
    }

    with pytest.raises(ProductionDispatchAdapterError):
        adapter.build_specialist_state(
            envelope=envelope,
            dependency_map={},
            runner_supplied_payload={"bundle_path": "/tmp/runs-root/from-runner"},
            projection_map=colliding_projection,
        )

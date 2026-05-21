"""Runner-level threading test for directive_path → Texas (Story 7a.1, AC-7.1-D)."""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist
from app.models.runtime.production_envelope import ProductionEnvelope


def test_runner_payload_only_for_texas(tmp_path: Path) -> None:
    """Only Texas receives runner_supplied_payload; other specialists get None."""
    directive = tmp_path / "directive.yaml"
    directive.write_text("run_id: T1\nsources: []\n", encoding="utf-8")
    bundle = tmp_path / "bundle"
    bundle.mkdir()

    payload = _runner_payload_for_specialist(
        specialist_id="texas", directive_path=directive, bundle_dir=bundle
    )
    assert payload == {
        "directive_path": directive.as_posix(),
        "bundle_dir": bundle.as_posix(),
    }

    other = _runner_payload_for_specialist(
        specialist_id="irene", directive_path=directive, bundle_dir=bundle
    )
    assert other is None


def test_runner_payload_none_when_directive_path_absent(tmp_path: Path) -> None:
    """If directive composition didn't run, Texas still gets None."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    payload = _runner_payload_for_specialist(
        specialist_id="texas", directive_path=None, bundle_dir=bundle
    )
    assert payload is None


def test_runner_payload_uses_posix_paths_on_windows_inputs(tmp_path: Path) -> None:
    """Windows-portability: payload values are POSIX-form (W-R6)."""
    directive = tmp_path / "subdir" / "directive.yaml"
    directive.parent.mkdir(parents=True)
    directive.write_text("run_id: T1\nsources: []\n", encoding="utf-8")
    bundle = tmp_path / "subdir" / "bundle"
    bundle.mkdir()

    payload = _runner_payload_for_specialist(
        specialist_id="texas", directive_path=directive, bundle_dir=bundle
    )
    assert payload is not None
    assert "\\" not in payload["directive_path"]
    assert "\\" not in payload["bundle_dir"]


def test_dispatch_adapter_merges_runner_supplied_payload(tmp_path: Path) -> None:
    """build_specialist_state merges runner_supplied_payload into cache_prefix JSON."""
    from uuid import uuid4

    trial_id = uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    adapter = ProductionDispatchAdapter(graph_builders={})

    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={},
        runner_supplied_payload={
            "directive_path": "state/runs/abc/directive.yaml",
            "bundle_dir": "state/runs/abc/bundle",
        },
    )
    assert state.cache_state is not None
    payload = json.loads(state.cache_state.cache_prefix)
    assert payload["directive_path"] == "state/runs/abc/directive.yaml"
    assert payload["bundle_dir"] == "state/runs/abc/bundle"


def test_dispatch_adapter_runner_payload_wins_on_collision(tmp_path: Path) -> None:
    """runner_supplied_payload wins over dependency_map keys on collision (documented)."""
    from uuid import uuid4

    from app.models.runtime.production_envelope import SpecialistContribution

    trial_id = uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    contribution = SpecialistContribution.from_output(
        specialist_id="upstream",
        output={"key1": "from-dependency"},
        model_used="test-model",
        cost_usd=0.0,
    )
    envelope.add_contribution(contribution)

    adapter = ProductionDispatchAdapter(graph_builders={})
    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={"key1": "upstream"},
        runner_supplied_payload={"key1": "from-runner"},
    )
    assert state.cache_state is not None
    payload = json.loads(state.cache_state.cache_prefix)
    assert payload["key1"] == "from-runner"


def test_dispatch_adapter_no_runner_payload_preserves_existing_behavior(
    tmp_path: Path,
) -> None:
    """Backward compatibility: omitting runner_supplied_payload behaves as Slab 6.0.

    _payload_from_dependencies maps {input_key: contribution.output}, so a
    dependency_map ``{"only_key": "upstream"}`` against an upstream contribution
    whose output is ``{"only_key": "only_value"}`` produces a nested payload of
    ``{"only_key": {"only_key": "only_value"}}``. The test pins this existing
    Slab 6.0 behavior so the additive runner_supplied_payload kwarg cannot
    silently change it.
    """
    from uuid import uuid4

    from app.models.runtime.production_envelope import SpecialistContribution

    trial_id = uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    contribution = SpecialistContribution.from_output(
        specialist_id="upstream",
        output={"only_key": "only_value"},
        model_used="test-model",
        cost_usd=0.0,
    )
    envelope.add_contribution(contribution)

    adapter = ProductionDispatchAdapter(graph_builders={})
    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={"only_key": "upstream"},
    )
    assert state.cache_state is not None
    payload = json.loads(state.cache_state.cache_prefix)
    # Slab 6.0 behavior: {input_key: <upstream contribution output dict>}
    assert payload == {"only_key": {"only_key": "only_value"}}

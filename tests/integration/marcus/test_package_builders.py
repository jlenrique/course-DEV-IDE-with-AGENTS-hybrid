"""S3 ratchets — §06 package builder + Gary/Quinn-R seam threading.

Ratchet-B (Murat): the lesson-plan → slide-briefs boundary, tested against
the REAL irene_pass1 lesson plan + cd directive from frozen trial 50b7d353
(input-side golden data is legitimate fixture use; output-side substitution
is not). Plus the runner-seam contracts that deliver the package to Gary
and Gary's slide rows to Quinn-R in their declared vocabularies.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.orchestrator import package_builders, production_runner
from app.marcus.orchestrator.package_builders import (
    BuilderInputError,
    build_gary_briefs,
    run_builder_node,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.specialists.gary.payload_contract import (
    CONSUMED_PAYLOAD_KEYS as GARY_KEYS,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
LEGACY_ENVELOPE_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "integration" / "marcus" / "legacy_envelope_50b7d353.json"
)
TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


def _fixture_outputs() -> tuple[dict, dict]:
    raw = json.loads(LEGACY_ENVELOPE_FIXTURE.read_text(encoding="utf-8-sig"))
    by_id = {c["specialist_id"]: c["output"] for c in raw["contributions"]}
    return by_id["irene_pass1"]["lesson_plan"], by_id["cd"]["cd_directive"]


def _scope(unit: dict) -> object:
    decision = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    return decision


def _in_scope_units(lesson_plan: dict) -> list[dict]:
    return [u for u in lesson_plan["plan_units"] if _scope(u) != "out-of-scope"]


def _contribution(specialist_id: str, output: dict, node_id: str | None = None):
    return SpecialistContribution.from_output(
        specialist_id=specialist_id,
        output=output,
        model_used="gpt-5-nano",
        node_id=node_id,
    )


def test_build_gary_briefs_from_real_trial_fixture() -> None:
    lesson_plan, cd_directive = _fixture_outputs()
    package = build_gary_briefs(lesson_plan, cd_directive)
    # Vocabulary lockstep: builder output ⊆ gary's declared contract.
    assert set(package) <= GARY_KEYS
    slides = package["slides"]
    # The REAL attempt-4 plan ratified 10 units with 2 out-of-scope; the
    # builder briefs exactly the in-scope set.
    in_scope = _in_scope_units(lesson_plan)
    assert len(slides) == len(in_scope)
    assert 0 < len(slides) < len(lesson_plan["plan_units"])
    assert [s["slide_id"] for s in slides] == [
        f"slide-{i:02d}" for i in range(1, len(slides) + 1)
    ]
    # Traceable provenance: every brief points back at its plan unit.
    unit_ids = {str(u["unit_id"]) for u in lesson_plan["plan_units"]}
    assert {s["source_ref"] for s in slides} <= unit_ids
    assert all(s["prompt"] for s in slides)
    assert package["prompt"]
    assert "Experience profile: text-led" in package["additional_instructions"]


def test_build_gary_briefs_fails_loud_on_malformed_inputs() -> None:
    lesson_plan, cd_directive = _fixture_outputs()
    with pytest.raises(BuilderInputError) as excinfo:
        build_gary_briefs({}, cd_directive)
    assert excinfo.value.tag == "builder.gary.lesson-plan-shape"
    with pytest.raises(BuilderInputError) as excinfo:
        build_gary_briefs(lesson_plan, {})
    assert excinfo.value.tag == "builder.gary.cd-directive-shape"


def test_build_gary_briefs_excludes_ratified_out_of_scope_units() -> None:
    lesson_plan, cd_directive = _fixture_outputs()
    baseline = len(_in_scope_units(lesson_plan))
    pruned = json.loads(json.dumps(lesson_plan))
    first_in_scope = next(
        u for u in pruned["plan_units"] if _scope(u) != "out-of-scope"
    )
    first_in_scope["scope_decision"] = "out-of-scope"
    package = build_gary_briefs(pruned, cd_directive)
    assert len(package["slides"]) == baseline - 1


def test_run_builder_node_emits_first_class_contribution_and_is_idempotent() -> None:
    lesson_plan, cd_directive = _fixture_outputs()
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        _contribution("irene_pass1", {"lesson_plan": lesson_plan}, node_id="04A")
    )
    envelope.add_contribution(
        _contribution("cd", {"cd_directive": cd_directive}, node_id="4.75")
    )
    updated = run_builder_node(node_id="06", production_envelope=envelope)
    package = updated.get_contribution("package_builder", node_id="06")
    assert package is not None
    assert package.model_used == package_builders.BUILDER_MODEL_MARKER
    assert set(package.output) <= GARY_KEYS
    # Idempotent per node (resume-safe; mirrors walker skip rule).
    again = run_builder_node(node_id="06", production_envelope=updated)
    assert len(again.contributions) == len(updated.contributions)


def test_run_builder_node_fails_loud_on_missing_upstream() -> None:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    with pytest.raises(BuilderInputError) as excinfo:
        run_builder_node(node_id="06", production_envelope=envelope)
    assert excinfo.value.tag == "builder.gary.upstream-missing"


def test_runner_payload_for_gary_is_runner_context_only(tmp_path: Path) -> None:
    # S4: content keys flow via manifest projections; the seam carries ONLY
    # runner context (export_dir under the run dir).
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="gary",
        directive_path=None,
        bundle_dir=None,
        runs_root=tmp_path,
        trial_id=TRIAL_ID,
    )
    assert payload == {
        "export_dir": (tmp_path / str(TRIAL_ID) / "exports" / "gary").as_posix()
    }
    assert set(payload) <= GARY_KEYS


def test_projection_resolves_package_keys_for_gary(tmp_path: Path) -> None:
    # The adapter projects §06 package keys into gary's payload per the
    # manifest dependency_projections (Winston: projection, not spread).
    from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter

    lesson_plan, cd_directive = _fixture_outputs()
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        _contribution("irene_pass1", {"lesson_plan": lesson_plan}, node_id="04A")
    )
    envelope.add_contribution(
        _contribution("cd", {"cd_directive": cd_directive}, node_id="4.75")
    )
    envelope = run_builder_node(node_id="06", production_envelope=envelope)
    adapter = ProductionDispatchAdapter(graph_builders={})
    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={},
        projection_map={
            "slides": {"from": "package_builder", "key": "slides"},
            "prompt": {"from": "package_builder", "key": "prompt"},
            "additional_instructions": {
                "from": "package_builder",
                "key": "additional_instructions",
            },
        },
        runner_supplied_payload={
            "export_dir": (tmp_path / str(TRIAL_ID) / "exports" / "gary").as_posix()
        },
    )
    payload = json.loads(state.cache_state.cache_prefix)
    assert set(payload) <= GARY_KEYS
    assert payload["slides"]
    assert payload["prompt"]
    assert payload["export_dir"].endswith("exports/gary")


def test_projection_missing_producer_refuses(tmp_path: Path) -> None:
    from app.marcus.orchestrator.dispatch_adapter import (
        ProductionDispatchAdapter,
        ProductionDispatchAdapterError,
    )

    adapter = ProductionDispatchAdapter(graph_builders={})
    with pytest.raises(ProductionDispatchAdapterError, match="no contribution"):
        adapter.build_specialist_state(
            envelope=ProductionEnvelope(trial_id=TRIAL_ID),
            dependency_map={},
            projection_map={"slides": {"from": "package_builder", "key": "slides"}},
        )


def test_spread_key_roster_is_exactly_pinned() -> None:
    # Amelia b.2 (party review 2026-06-12): the seam spreads the package at
    # top level, so a NEW builder field is a deliberate two-file contract
    # change (builder + gary contract), never a silent addition.
    lesson_plan, cd_directive = _fixture_outputs()
    package = build_gary_briefs(lesson_plan, cd_directive)
    assert set(package) == {"slides", "prompt", "additional_instructions"}


def test_seam_collision_with_dependency_keys_refuses() -> None:
    # Amelia b.1: runner-keys-win silent precedence is retired — a key
    # delivered by BOTH the dependency map and the runner seam refuses loud.
    from app.marcus.orchestrator.dispatch_adapter import (
        ProductionDispatchAdapter,
        ProductionDispatchAdapterError,
    )

    adapter = ProductionDispatchAdapter(graph_builders={})
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        _contribution("gary", {"gary_slide_output": []}, node_id="07")
    )
    with pytest.raises(ProductionDispatchAdapterError, match="collides"):
        adapter.build_specialist_state(
            envelope=envelope,
            dependency_map={"slides": "gary"},
            runner_supplied_payload={"slides": ["seam-delivered"]},
        )


def test_seam_carries_runner_context_only_post_projection() -> None:
    # Winston S3-A executed: projection LANDED at S4, the bridge spread was
    # removed by deliberately rewriting this tombstone. The seam must never
    # again deliver content keys — slides/prompt flow through the manifest.
    import inspect

    source = inspect.getsource(production_runner._runner_payload_for_specialist)
    assert "manifest-edge-key-projection-s4" in source  # history stays cited
    assert '"slides"' not in source.replace("``slides``", ""), (
        "the seam must not deliver content keys; projections own them"
    )


def test_manifest_declares_projection_edges() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml").read_text(
            encoding="utf-8"
        )
    )
    nodes = {node["id"]: node for node in manifest["nodes"]}
    assert manifest["data_plane_vocabulary_version"] == "dp-v1"
    gary_projections = nodes["07"]["dependency_projections"]
    assert set(gary_projections) == {"slides", "prompt", "additional_instructions"}
    assert all(p["from"] == "package_builder" for p in gary_projections.values())
    quinn_projections = nodes["07B"]["dependency_projections"]
    assert quinn_projections == {"slides": {"from": "gary", "key": "gary_slide_output"}}


def test_runner_payload_for_quinn_r_is_gate_context_only() -> None:
    # S4: gary_slide_output reaches quinn_r via the 07B manifest projection;
    # the seam carries only the gate context.
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="quinn_r",
        directive_path=None,
        bundle_dir=None,
        gate_code="G2B",
    )
    assert payload == {"gate_id": "G2B"}


def test_projection_resolves_gary_rows_for_quinn_r() -> None:
    from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter

    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    rows = [{"slide_id": "slide-01", "card_number": 1, "file_path": "exports/s1.png"}]
    envelope.add_contribution(
        _contribution("gary", {"gary_slide_output": rows}, node_id="07")
    )
    adapter = ProductionDispatchAdapter(graph_builders={})
    state = adapter.build_specialist_state(
        envelope=envelope,
        dependency_map={},
        projection_map={"slides": {"from": "gary", "key": "gary_slide_output"}},
        runner_supplied_payload={"gate_id": "G2B"},
    )
    payload = json.loads(state.cache_state.cache_prefix)
    assert payload == {"gate_id": "G2B", "slides": rows}


class _RecordingFakeAdapter:
    """Real-shaped fake: emits fixture-derived outputs and records seams."""

    def __init__(self) -> None:
        lesson_plan, cd_directive = _fixture_outputs()
        self._outputs = {
            "irene_pass1": {"lesson_plan": lesson_plan},
            "cd": {"cd_directive": cd_directive},
            "gary": {"gary_slide_output": [{"slide_id": "slide-01"}], "status": "complete"},
        }
        self.runner_payloads: dict[str, dict | None] = {}
        self.projection_maps: dict[str, dict | None] = {}

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        runner_supplied_payload: dict | None = None,
        node_id: str | None = None,
        projection_map: dict | None = None,
        **_,
    ) -> ProductionEnvelope:
        self.runner_payloads[specialist_id] = runner_supplied_payload
        self.projection_maps[specialist_id] = (
            {
                key: dict(spec)
                if isinstance(spec, dict)
                else spec.model_dump(by_alias=True)
                for key, spec in projection_map.items()
            }
            if projection_map
            else None
        )
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=self._outputs.get(specialist_id, {"specialist_id": specialist_id}),
                model_used="gpt-5-nano",
                node_id=node_id,
            )
        )
        return updated


def _manifest(tmp_path: Path) -> Path:
    nodes = [
        {"id": "04A", "specialist_id": "irene-pass1"},
        {"id": "4.75", "specialist_id": "cd"},
        {"id": "06", "specialist_id": "marcus", "label": "Pre-Dispatch Package Build"},
        {
            "id": "07",
            "specialist_id": "gary",
            "dependency_projections": {
                "slides": {"from": "package_builder", "key": "slides"},
                "prompt": {"from": "package_builder", "key": "prompt"},
                "additional_instructions": {
                    "from": "package_builder",
                    "key": "additional_instructions",
                },
            },
        },
    ]
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": "04A",
        "frozen_graph_version": "v42",
        "nodes": [
            {
                "label": node["id"],
                "scaffold_node": "act",
                "model_config_ref": None,
                "gate": False,
                "hud_tracked": True,
                "pack_version": "test",
                "rationale": "test",
                **node,
            }
            for node in nodes
        ],
        "edges": [
            {"from": "__start__", "to": "04A"},
            {"from": "04A", "to": "4.75"},
            {"from": "4.75", "to": "06"},
            {"from": "06", "to": "07"},
            {"from": "07", "to": "__end__"},
        ],
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def test_walker_builds_package_at_06_and_threads_briefs_to_gary(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    caplog.set_level(logging.INFO, logger=production_runner.__name__)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    adapter = _RecordingFakeAdapter()
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", lambda: adapter
    )
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir()
    (run_dir / "directive.yaml").write_text("trial: test\n", encoding="utf-8")

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path),
        max_specialist_calls=4,
        pause_at_gates=False,
    )

    production_envelope = envelope.production_envelope
    assert production_envelope is not None
    package = production_envelope.get_contribution("package_builder", node_id="06")
    assert package is not None, "§06 must emit a first-class contribution"
    gary_payload = adapter.runner_payloads.get("gary")
    assert gary_payload is not None
    assert set(gary_payload) == {"export_dir"}, "seam carries runner context only"
    assert gary_payload["export_dir"].endswith("exports/gary")
    # Content keys travel via the manifest projection (S4).
    gary_projections = adapter.projection_maps.get("gary")
    assert gary_projections is not None
    assert set(gary_projections) == {"slides", "prompt", "additional_instructions"}

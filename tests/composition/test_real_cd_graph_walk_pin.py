"""Canonical-arc S1 D5 — F-103 closure: the real-CD-graph-in-walk pin.

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s1-cd-styleguide-resolution-emission.md`
(RED-6, AC-4 dispatch-path witness / F-102 rider; AC-5 both-walks + persisted
survival).

The `_FakeAdapter` canned-cd shim is replaced by the REAL 9-node CD graph
(fake LLM per the `tests/composition/test_texas_to_cd_chain.py` pattern)
driven through the REAL production dispatch adapter inside a REAL runner walk.

Anti-vacuity (SOP-002, binding): the projection is obtained through
`_runner_payload_for_specialist` — the harness NEVER hand-feeds
`runner_supplied_payload`. The hybrid adapter only RECORDS what the runner's
shared `_dispatch_specialist_at_node` computed, then forwards it verbatim to
the real `ProductionDispatchAdapter` for the cd node.

AC-5 witness-gap note honored: BOTH walk cases assert on the RE-LOADED
envelope (persist -> read run.json from disk), not in-memory walker state.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.gates.resume_api import clear_resume_registry
from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.state.operator_verdict import OperatorVerdict
from app.specialists.cd.graph import build_cd_graph
from tests.composition.composed_specialist_chain_harness import fake_make_chat_model

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")
DEFAULT_GUIDE = "hil-2026-apc-crossroads-classic"

_LESSON_PLAN = {
    "plan_units": [
        {
            "unit_id": "PU-1",
            "title": "Unit",
            "learning_objective": "Objective",
            "scope_decision": "in-scope",
        }
    ]
}


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a — flip-robustness pin (D-migrate-canonical, pin OFF).

    The default-manifest continuation walk (``_run_continuation_walk``) and the
    ceremony-started walk first-pause at G1 before node 4.75 on the dormant path.
    Pinning ``MARCUS_G0_ENRICHMENT_ACTIVE`` OFF explicitly keeps that true under the
    3b default flip; the CD-resolution subject is orthogonal to G0-enrichment, and
    the custom ``_walk_manifest`` start-walk tests are unaffected. Explicit ``"0"``
    survives the code-default flip.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


class _HybridRealCdAdapter:
    """Canned for every specialist EXCEPT cd, which runs the REAL compiled
    9-node CD graph through the REAL ProductionDispatchAdapter."""

    def __init__(self, bundle_dir: Path) -> None:
        self._real = ProductionDispatchAdapter(graph_builders={"cd": build_cd_graph})
        self._canned_outputs: dict[str, dict] = {
            "texas": {
                "specialist_id": "texas",
                "status": "complete",
                "bundle_reference": str(bundle_dir),
            },
            "irene_pass1": {"lesson_plan": _LESSON_PLAN},
            "gary": {
                "gary_slide_output": [{"slide_id": "slide-01"}],
                "status": "complete",
            },
        }
        # Anti-vacuity witness: whatever the RUNNER computed via
        # _runner_payload_for_specialist for the cd node (never hand-fed).
        self.cd_runner_supplied_payload: dict | None = None
        self.cd_dispatched = False
        self.last_interrupts = None

    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],
        cost_usd: float,
        base_state=None,
        node_id: str | None = None,
        runner_supplied_payload: dict | None = None,
        projection_map: dict | None = None,
    ) -> ProductionEnvelope:
        if specialist_id == "cd":
            self.cd_dispatched = True
            self.cd_runner_supplied_payload = runner_supplied_payload
            updated = self._real.invoke_specialist(
                specialist_id="cd",
                envelope=envelope,
                dependency_map=dependency_map,
                cost_usd=cost_usd,
                base_state=base_state,
                node_id=node_id,
                runner_supplied_payload=runner_supplied_payload,
                projection_map=projection_map,
            )
            # F-102: interrupts land write-only; the walk continues regardless.
            self.last_interrupts = self._real.last_interrupts
            return updated
        del projection_map
        updated = envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=self._canned_outputs.get(
                    specialist_id, {"specialist_id": specialist_id}
                ),
                model_used="gpt-5-nano",
                cost_usd=cost_usd,
                node_id=node_id,
            )
        )
        return updated


def _fake_cd_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.specialists.cd.graph.make_chat_model", fake_make_chat_model
    )
    monkeypatch.setattr("app.specialists.cd.graph.assert_sanctum_lock", lambda: None)


def _seed_run_dir_with_picked_directive(runs_root: Path) -> tuple[Path, Path]:
    """Run dir + a REAL picker-patched directive at the canonical location."""
    from app.marcus.orchestrator.styleguide_picker import write_pick_to_directive

    run_dir = runs_root / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    directive = run_dir / "directive.yaml"
    directive.write_text(
        yaml.safe_dump({"run_id": str(TRIAL_ID), "sources": []}, sort_keys=False),
        encoding="utf-8",
    )
    write_pick_to_directive(directive, {"A": DEFAULT_GUIDE})
    bundle = run_dir / "cd-source-bundle"
    bundle.mkdir(exist_ok=True)
    (bundle / "extracted.md").write_text(
        "# Corpus\n\nReal walk-pin corpus body.", encoding="utf-8"
    )
    return directive, bundle


def _walk_manifest(tmp_path: Path) -> Path:
    nodes = [
        {"id": "02", "specialist_id": "texas", "dependencies": {}},
        {"id": "04A", "specialist_id": "irene-pass1"},
        {"id": "4.75", "specialist_id": "cd", "dependencies": {"source_bundle": "texas"}},
        {"id": "06", "specialist_id": "marcus", "label": "Pre-Dispatch Package Build"},
    ]
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": "02",
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
            {"from": "__start__", "to": "02"},
            {"from": "02", "to": "04A"},
            {"from": "04A", "to": "4.75"},
            {"from": "4.75", "to": "06"},
            {"from": "06", "to": "__end__"},
        ],
    }
    path = tmp_path / "walk-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def _reload_cd_contribution_from_disk(runs_root: Path) -> dict:
    """AC-5 witness-gap: assert on the RE-LOADED persisted envelope."""
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

    persisted = ProductionTrialEnvelope.model_validate_json(
        (runs_root / str(TRIAL_ID) / "run.json").read_text(encoding="utf-8"),
        context={"anomaly_sink": runs_root / str(TRIAL_ID) / "anomalies.jsonl"},
    )
    assert persisted.production_envelope is not None
    contribution = persisted.production_envelope.get_contribution("cd", node_id="4.75")
    assert contribution is not None, "no persisted cd contribution at node 4.75"
    return contribution.output


def _assert_resolution_block(output: dict, *, directive: Path) -> None:
    assert output["cd_directive"]["schema_version"] == "1.0"
    block = output.get("styleguide_resolution")
    assert block is not None, (
        "real CD graph emitted no styleguide_resolution through the production "
        "dispatch path (F-103 open)"
    )
    assert block["status"] == "resolved"
    assert [guide["name"] for guide in block["bound_guides"]] == [DEFAULT_GUIDE]
    assert block["directive_digest"] == hashlib.sha256(
        directive.read_bytes()
    ).hexdigest()
    assert block["layering_manifest"]["composition_rule"] == "source_derived_wins"


# --- RED-6: start walk, real CD graph, real dispatch path (AC-4/D5) ----------


def test_walk_475_with_real_cd_graph_emits_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _fake_cd_llm(monkeypatch)
    directive, bundle = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealCdAdapter(bundle)
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", lambda: adapter
    )

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path),
        max_specialist_calls=8,
        pause_at_gates=False,
        directive_path=directive,
    )

    assert adapter.cd_dispatched, "cd node 4.75 never dispatched in the walk"
    # Anti-vacuity: the projection came from the RUNNER seam, not the harness.
    assert adapter.cd_runner_supplied_payload is not None, (
        "runner supplied no payload for cd — D2 wiring absent"
    )
    assert "directive_projection" in adapter.cd_runner_supplied_payload
    # F-102 rider: cd's gate_decision interrupt landed write-only; the walk
    # continued through 4.75 to §06 without resuming the sub-graph.
    assert adapter.last_interrupts, "cd graph interrupt evidence missing"

    # The §06 builder CONSUMED the real graph's canonicalized output.
    production_envelope = envelope.production_envelope
    assert production_envelope is not None
    package = production_envelope.get_contribution("package_builder", node_id="06")
    assert package is not None, "§06 builder did not run over the real cd output"

    # Persisted survival: assert on the RE-LOADED envelope from disk.
    output = _reload_cd_contribution_from_disk(tmp_path)
    _assert_resolution_block(output, directive=directive)


# --- AC-5: both walks + persisted survival (parametrized) --------------------


def _run_start_walk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directive, bundle = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealCdAdapter(bundle)
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", lambda: adapter
    )
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path),
        max_specialist_calls=8,
        pause_at_gates=False,
        directive_path=directive,
    )
    assert adapter.cd_runner_supplied_payload is not None
    assert "directive_projection" in adapter.cd_runner_supplied_payload
    return directive


def _run_continuation_walk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Default manifest: start walk pauses at G1 BEFORE 4.75; the continuation
    walk (resume) is the one that dispatches cd — pause -> persist -> resume
    -> read from disk."""
    directive, bundle = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealCdAdapter(bundle)
    monkeypatch.setattr(
        production_runner, "ProductionDispatchAdapter", lambda: adapter
    )
    paused = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
        directive_path=directive,
    )
    assert paused.status == "paused-at-gate"
    assert paused.paused_gate == "G1"
    assert not adapter.cd_dispatched, "start walk must stop at G1 before 4.75"

    card_payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text(encoding="utf-8")
    )
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID(card_payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=card_payload["digest"],
    )
    resumed = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=verdict,
        runs_root=tmp_path,
    )
    assert resumed.status == "paused-at-gate"
    assert adapter.cd_dispatched, "continuation walk never dispatched cd at 4.75"
    assert adapter.cd_runner_supplied_payload is not None
    assert "directive_projection" in adapter.cd_runner_supplied_payload
    return directive


@pytest.mark.parametrize("walk", ["start", "continuation"])
def test_both_walks_resolution_block_lands_and_survives_reload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, walk: str
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _fake_cd_llm(monkeypatch)
    if walk == "start":
        directive = _run_start_walk(tmp_path, monkeypatch)
    else:
        directive = _run_continuation_walk(tmp_path, monkeypatch)

    output = _reload_cd_contribution_from_disk(tmp_path)
    _assert_resolution_block(output, directive=directive)


# --- S2 AC-4: walk started THROUGH the ceremony closes the F-404 loop ---------

CEREMONY_PICKED_GUIDE = "hil-2026-apc-crossroads-blueprint"


def test_walk_started_through_ceremony_binds_pick_to_cd_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """S2 AC-4 (spec `canonical-arc-s2-picker-canonical-trial-start.md`): a trial
    started through the INTERACTIVE ceremony (`start_trial` -> injected
    `picker_preflight_fn` -> the REAL `run_picker_preflight`) persists the pick
    via `write_pick_to_directive`, and the walk's REAL CD graph (S1 D5 harness)
    emits `styleguide_resolution.status == "resolved"` with `bound_guides`
    naming exactly the picked guide. Resume makes ZERO input calls (D1)."""
    import hashlib as _hashlib

    from app.marcus.cli import trial as trial_module
    from app.marcus.cli.marcus_spoc import run_picker_preflight
    from app.marcus.cli.trial import start_trial
    from app.marcus.orchestrator.picker_html_emitter import build_selection_code

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "lsv2-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    # Offline witness: the fake key must never reach the live LangSmith API
    # (background multipart POSTs 403 loudly under an armed shell env).
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.setattr(trial_module, "_load_env_if_available", lambda: None)
    _fake_cd_llm(monkeypatch)

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    run_dir = tmp_path / str(TRIAL_ID)
    bundle = run_dir / "cd-source-bundle"
    bundle.mkdir(parents=True)
    (bundle / "extracted.md").write_text(
        "# Corpus\n\nCeremony walk-pin corpus body.", encoding="utf-8"
    )

    def _stub_compose(*, corpus_dir, run_dir, run_id, llm=None, gamma_settings=None):
        del llm, gamma_settings
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "directive.yaml"
        path.write_text(
            yaml.safe_dump(
                {"run_id": str(run_id), "corpus_dir": corpus_dir.as_posix(), "sources": []},
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return path, _hashlib.sha256(path.read_bytes()).hexdigest()

    monkeypatch.setattr(trial_module, "compose_and_write", _stub_compose)
    adapter = _HybridRealCdAdapter(bundle)
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)

    input_calls: list[str] = []
    code = build_selection_code(TRIAL_ID.hex, {"A": CEREMONY_PICKED_GUIDE})
    replies = iter([code, "confirm"])

    def _ceremony_input(prompt: str) -> str:
        input_calls.append(prompt)
        return next(replies)

    def _fake_publish(**kwargs):
        return {
            "publish_url": "https://x.github.io/p/index.html",
            "run_tag": kwargs["run_tag"],
            "style_count": 8,
        }

    def _preflight(**kwargs):
        return run_picker_preflight(
            input_fn=_ceremony_input,
            print_fn=lambda _m: None,
            publish_fn=_fake_publish,
            **kwargs,
        )

    start_trial(
        preset="production",
        input_path=corpus,
        operator_id="operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        auto_confirm_directive=False,
        confirm_fn=lambda **_k: "confirmed",
        picker_preflight_fn=_preflight,
        picker_events_path=tmp_path / "picks.jsonl",
        max_specialist_calls=12,
    )

    directive = run_dir / "directive.yaml"
    loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
    settings = {row["variant_id"]: row["styleguide"] for row in loaded["gamma_settings"]}
    assert settings == {"A": CEREMONY_PICKED_GUIDE}
    pick_bytes = directive.read_bytes()
    assert len(input_calls) == 2, "the ceremony is exactly paste + confirm"
    assert not adapter.cd_dispatched, "start walk must pause at G1 before 4.75"

    # D1: resume NEVER re-prompts — any input call below fails the test.
    monkeypatch.setattr(
        "builtins.input",
        lambda *_a: pytest.fail("resume must never prompt (D1 witness)"),
    )
    card_payload = json.loads(
        (run_dir / "decision-card-G1.json").read_text(encoding="utf-8")
    )
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID(card_payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=card_payload["digest"],
    )
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID, verdict=verdict, runs_root=tmp_path
    )
    assert adapter.cd_dispatched, "continuation walk never dispatched cd at 4.75"
    # P15: the former `len(input_calls) == 2` re-assert here was DEAD — the
    # ceremony's input_fn is only wired into the START preflight and cannot be
    # reached on resume; the monkeypatched builtins.input (pytest.fail above)
    # is the real zero-prompt witness for the resume leg.
    # AC-2: the pick survives resume byte-identically in the directive.
    assert directive.read_bytes() == pick_bytes

    output = _reload_cd_contribution_from_disk(tmp_path)
    block = output.get("styleguide_resolution")
    assert block is not None
    assert block["status"] == "resolved"
    assert [guide["name"] for guide in block["bound_guides"]] == [CEREMONY_PICKED_GUIDE]
    assert block["directive_digest"] == _hashlib.sha256(pick_bytes).hexdigest()

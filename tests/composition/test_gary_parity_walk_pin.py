"""Canonical-arc S3 — both-walks Gary parity receipts (AC-5) + F-802 legacy
clean-dispatch witness (AC-6) + the F-801 walk-level non-null-digest witness (AC-3).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`
(RED-first plan #4). Pattern: the S1/S2 walk-pin harness
(`tests/composition/test_real_cd_graph_walk_pin.py`) — REAL gary graph driven
through the REAL production dispatch adapter at the SHARED dispatch site
(`_dispatch_specialist_at_node`), offline Gamma client, canned upstream
specialists. Both walk cases assert on the RE-LOADED persisted envelope
(run.json from disk), not in-memory walker state.

F-805 fence honored: the harness drives the slides/`generate_gamma_variants`
path (§06 projections deliver ``slides``/``prompt``), exactly as production
§07 always does.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any
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
from app.specialists.cd.graph import _styleguide_resolution_from_projection
from app.specialists.gary import _act as gary_act
from app.specialists.gary.graph import build_gary_graph
from tests.composition.composed_specialist_chain_harness import fake_make_chat_model

TRIAL_ID = UUID("87654321-4321-4234-8321-cba987654321")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")
PICKED_GUIDE = "hil-2026-apc-crossroads-classic"

_LESSON_PLAN = {
    "plan_units": [
        {
            "unit_id": "PU-1",
            # NB: the title must NOT contain "parity" — it becomes export
            # artifact filenames, which would false-trip the no-sidecar scan.
            "title": "Shadow Probe Unit",
            "learning_objective": "Objective",
            "scope_decision": "in-scope",
        }
    ]
}
_CD_DIRECTIVE = {
    "schema_version": "1.0",
    "experience_profile": "overview_first",
    "slide_mode_proportions": {"static": 1.0},
    "narration_profile_controls": {"pace": "measured"},
    "creative_rationale": "gary parity walk-pin fixture",
}


@pytest.fixture(autouse=True)
def _clear_registry():
    clear_resume_registry()
    yield
    clear_resume_registry()


class _OfflineGammaClient:
    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        del limit
        return [{"id": "njim9kuhfnljvaa", "name": "2026 HIL APC Tejal"}]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        del input_text, kwargs
        return {
            "generation_id": "gen-walk-pin",
            "exportUrl": "https://example.invalid/export.zip",
        }


class _HybridRealGaryAdapter:
    """Canned for every specialist EXCEPT gary, which runs the REAL 9-node
    gary graph through the REAL ProductionDispatchAdapter. Records what the
    runner's shared `_dispatch_specialist_at_node` computed for gary (never
    hand-fed — SOP-002 anti-vacuity discipline)."""

    def __init__(self, cd_output: dict[str, Any]) -> None:
        self._real = ProductionDispatchAdapter(graph_builders={"gary": build_gary_graph})
        self._canned_outputs: dict[str, dict[str, Any]] = {
            "irene_pass1": {"lesson_plan": _LESSON_PLAN},
            "cd": cd_output,
        }
        self.gary_runner_supplied_payload: dict | None = None
        self.gary_dispatch_count = 0
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
        if specialist_id == "gary":
            self.gary_dispatch_count += 1
            self.gary_runner_supplied_payload = runner_supplied_payload
            updated = self._real.invoke_specialist(
                specialist_id="gary",
                envelope=envelope,
                dependency_map=dependency_map,
                cost_usd=cost_usd,
                base_state=base_state,
                node_id=node_id,
                runner_supplied_payload=runner_supplied_payload,
                projection_map=projection_map,
            )
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


def _fake_gary_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    # Offline witness: the fake key must never reach the live LangSmith API
    # (background multipart POSTs 403 loudly under an armed shell env).
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.setattr("app.specialists.gary.graph.make_chat_model", fake_make_chat_model)
    monkeypatch.setattr(gary_act, "GammaClient", _OfflineGammaClient)
    zpath = tmp_path / "gamma-export.zip"
    with zipfile.ZipFile(zpath, "w") as archive:
        # §06 briefs one slide titled after the lesson-plan unit; the export
        # title-matcher needs >= 2 distinctive tokens to bind bijectively.
        archive.writestr("1_Shadow-Probe-Unit.png", b"bytes::unit-slide")
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )


def _seed_run_dir_with_picked_directive(runs_root: Path) -> Path:
    from app.marcus.orchestrator.styleguide_picker import write_pick_to_directive

    run_dir = runs_root / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    directive = run_dir / "directive.yaml"
    directive.write_text(
        yaml.safe_dump({"run_id": str(TRIAL_ID), "sources": []}, sort_keys=False),
        encoding="utf-8",
    )
    write_pick_to_directive(directive, {"A": PICKED_GUIDE})
    return directive


def _canned_cd_output(directive: Path, *, legacy: bool = False) -> dict[str, Any]:
    """The canned cd contribution: cd_directive always (the §06 builder's
    fail-loud input); S3's block only on the non-legacy shape — computed by
    the REAL committed emission over the SAME picked directive bytes."""
    output: dict[str, Any] = {"cd_directive": dict(_CD_DIRECTIVE)}
    if not legacy:
        loaded = yaml.safe_load(directive.read_text(encoding="utf-8"))
        output["styleguide_resolution"] = _styleguide_resolution_from_projection(
            {
                "gamma_settings": loaded.get("gamma_settings"),
                "directive_digest": hashlib.sha256(directive.read_bytes()).hexdigest(),
            }
        )
    return output


def _walk_manifest(
    tmp_path: Path, *, with_gate: bool, gate_after_07: bool = False
) -> Path:
    nodes: list[dict[str, Any]] = [{"id": "04A", "specialist_id": "irene-pass1"}]
    if with_gate:
        nodes.append(
            {"id": "04G", "specialist_id": "vera", "gate": True, "gate_code": "G1"}
        )
    nodes.extend(
        [
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
    )
    if gate_after_07:
        # T11 P7 harness shape: a gate AFTER §07 so the start walk executes
        # gary (receipt persisted) and the resume walks a run whose §07
        # already carries a receipt.
        nodes.append(
            {"id": "07G", "specialist_id": "vera", "gate": True, "gate_code": "G1"}
        )
    ids = [node["id"] for node in nodes]
    manifest = {
        "schema_version": "test",
        "pack_version": "test",
        "generator_ref": "tests",
        "lane": "run_graph",
        "entrypoint": ids[0],
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
            {"from": "__start__", "to": ids[0]},
            *({"from": a, "to": b} for a, b in zip(ids, ids[1:], strict=False)),
            {"from": ids[-1], "to": "__end__"},
        ],
    }
    path = tmp_path / "walk-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return path


def _reload_contribution_from_disk(
    runs_root: Path, specialist_id: str, node_id: str
) -> dict:
    """AC-5 witness-gap discipline: assert on the RE-LOADED persisted envelope."""
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

    persisted = ProductionTrialEnvelope.model_validate_json(
        (runs_root / str(TRIAL_ID) / "run.json").read_text(encoding="utf-8"),
        context={"anomaly_sink": runs_root / str(TRIAL_ID) / "anomalies.jsonl"},
    )
    assert persisted.production_envelope is not None
    contribution = persisted.production_envelope.get_contribution(
        specialist_id, node_id=node_id
    )
    assert contribution is not None, f"no persisted {specialist_id} contribution"
    return contribution.output


def _assert_no_parity_sidecar(run_dir: Path) -> None:
    # AC-5: the receipt's ONLY home is the contribution (provenance in the
    # carrier) — never a shadow store / sidecar file.
    strays = [p for p in run_dir.rglob("*parity*") if p.is_file()]
    assert strays == [], f"parity receipt leaked into a sidecar store: {strays}"


# --- AC-5: start walk ------------------------------------------------------------


def test_start_walk_gary_contribution_carries_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_gary_offline(tmp_path, monkeypatch)
    directive = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealGaryAdapter(_canned_cd_output(directive))
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)

    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path, with_gate=False),
        max_specialist_calls=8,
        pause_at_gates=False,
        directive_path=directive,
    )

    assert adapter.gary_dispatch_count == 1
    payload = adapter.gary_runner_supplied_payload
    assert payload is not None, "runner supplied no gary payload — D1/D4 wiring absent"
    # Anti-vacuity: the parity context came through the RUNNER seam.
    assert payload["cd_styleguide_resolution"] is not None
    assert payload["directive_digest"] == hashlib.sha256(
        directive.read_bytes()
    ).hexdigest()
    # No trial-start attestation on this harness start walk ⇒ honest None.
    assert payload["trial_start_directive_digest"] is None

    output = _reload_contribution_from_disk(tmp_path, "gary", "07")
    receipt = output["styleguide_parity"]
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["clock_eligible"] is True
    assert receipt["trial_start_directive_digest"] is None
    _assert_no_parity_sidecar(tmp_path / str(TRIAL_ID))


# --- AC-5 continuation walk + AC-3 F-801 non-null walk witness ---------------------


def test_continuation_walk_receipt_with_real_trial_start_attestation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_gary_offline(tmp_path, monkeypatch)
    directive = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealGaryAdapter(_canned_cd_output(directive))
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)
    run_dir = tmp_path / str(TRIAL_ID)

    paused = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path, with_gate=True),
        max_specialist_calls=8,
        directive_path=directive,
    )
    assert paused.status == "paused-at-gate"
    assert paused.paused_gate == "G1"
    assert adapter.gary_dispatch_count == 0, "start walk must pause before §07"

    # F-801: a REAL trial-start.json lands on disk between the start walk and
    # the continuation walk (production timing: `start_trial` writes it at
    # trial.py:536 after the paused start returns).
    directive_digest = hashlib.sha256(directive.read_bytes()).hexdigest()
    (run_dir / "trial-start.json").write_text(
        json.dumps({"directive_digest": directive_digest, "status": "paused-at-gate"})
        + "\n",
        encoding="utf-8",
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
    assert adapter.gary_dispatch_count == 1, "continuation walk never dispatched gary"

    output = _reload_contribution_from_disk(tmp_path, "gary", "07")
    receipt = output["styleguide_parity"]
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["clock_eligible"] is True
    # AC-3 F-801 sub-witness (mandatory): the three-way check is provably
    # three-way — the receipt's trial-start digest is NON-null and equal to
    # the on-disk trial-start.json attestation.
    assert receipt["trial_start_directive_digest"] == directive_digest
    assert receipt["cd_directive_digest"] == directive_digest
    assert receipt["gary_directive_digest"] == directive_digest
    _assert_no_parity_sidecar(run_dir)


# --- T11 P7: resume of a receipted run never re-audits or rewrites the receipt ------


def test_resume_of_receipted_run_never_reaudits_or_rewrites(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-5 "never re-audit" teeth: resume a run whose §07 ALREADY carries a
    persisted receipt (gate after §07) — gary_dispatch_count stays 1 and the
    persisted receipt is byte-unchanged through the resume."""
    _fake_gary_offline(tmp_path, monkeypatch)
    directive = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealGaryAdapter(_canned_cd_output(directive))
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)
    run_dir = tmp_path / str(TRIAL_ID)

    paused = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path, with_gate=False, gate_after_07=True),
        max_specialist_calls=8,
        directive_path=directive,
    )
    assert paused.status == "paused-at-gate"
    assert adapter.gary_dispatch_count == 1, "§07 must execute BEFORE the post-07 gate"
    receipt_before = json.dumps(
        _reload_contribution_from_disk(tmp_path, "gary", "07")["styleguide_parity"],
        sort_keys=True,
        ensure_ascii=True,
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

    assert adapter.gary_dispatch_count == 1, (
        "resume of a receipted run must NOT re-dispatch/re-audit §07"
    )
    receipt_after = json.dumps(
        _reload_contribution_from_disk(tmp_path, "gary", "07")["styleguide_parity"],
        sort_keys=True,
        ensure_ascii=True,
    )
    assert receipt_after == receipt_before, (
        "the persisted receipt must be byte-unchanged through the resume"
    )
    _assert_no_parity_sidecar(run_dir)


# --- AC-6 F-802: legacy envelope dispatches §07 CLEANLY -----------------------------


def test_legacy_pre_s3_envelope_dispatches_gary_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A cd/package_builder contribution set that PREDATES S1/S3 (no
    # styleguide_resolution anywhere) must reach §07 without a raise —
    # rewind-recovered golden bundles must not false-fail (W5-morph, §7).
    _fake_gary_offline(tmp_path, monkeypatch)
    directive = _seed_run_dir_with_picked_directive(tmp_path)
    adapter = _HybridRealGaryAdapter(_canned_cd_output(directive, legacy=True))
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)

    envelope = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        manifest_path=_walk_manifest(tmp_path, with_gate=False),
        max_specialist_calls=8,
        pause_at_gates=False,
        directive_path=directive,
    )
    assert envelope.status != "error-paused", "legacy envelope must NOT false-fail"
    assert adapter.gary_dispatch_count == 1
    assert adapter.gary_runner_supplied_payload is not None
    assert adapter.gary_runner_supplied_payload["cd_styleguide_resolution"] is None

    output = _reload_contribution_from_disk(tmp_path, "gary", "07")
    receipt = output["styleguide_parity"]
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-envelope-absent-legacy"
    assert receipt["clock_eligible"] is False

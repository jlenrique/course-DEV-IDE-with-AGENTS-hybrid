"""Hermetic tests for the Ask-B hot-topics demand resolver (38.2 AC 1).

The closed Ask-B loss→status lattice under test (a NEW design — Ask-A's
skeleton-digest-coupled map does not transfer):

    workbook_brief_absent       → unavailable
    workbook_brief_legacy_stub  → unavailable
    promise_vows_unavailable    → unavailable
    scene_identity_absent       → READY with recorded scope loss (W-3/A-1)

Corrupt/forged/mismatched authority raises ``ResearchDemandShapeError``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from app.marcus.lesson_plan.prework_artifact import (
    read_workbook_brief,
    workbook_brief_contribution_receipt,
)
from app.marcus.lesson_plan.research_demand import (
    AskBHotTopicsDemandV1,
    ResearchDemandShapeError,
    resolve_hot_topics_demand,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

LEGACY_RUN = Path(
    "_bmad-output/implementation-artifacts/evidence/"
    "prework-36-4-fresh-input-380ecd47/run"
)


def _canonical_digest(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_envelope(
    run_dir: Path, contributions: list[tuple[str, str, dict[str, Any]]]
) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=tuple(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=output,
                model_used="fixture",
                node_id=node_id,
                provenance="fixture",
            )
            for specialist_id, node_id, output in contributions
        ),
        fixture_run=True,
    )
    started = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="ask-b-hermetic",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _install_brief(run_dir: Path, mutate=None) -> dict[str, Any]:
    """Install a digest-consistent brief + matching contribution receipt."""
    raw = json.loads(
        (LEGACY_RUN / "workbook-brief.v1.json").read_text(encoding="utf-8")
    )
    if mutate is not None:
        mutate(raw["payload"])
    raw["payload_digest"] = _canonical_digest(raw["payload"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "workbook-brief.v1.json").write_text(
        json.dumps(raw, indent=2) + "\n", encoding="utf-8"
    )
    artifact = read_workbook_brief(run_dir)
    receipt = workbook_brief_contribution_receipt(artifact)
    _write_envelope(run_dir, [("workbook_brief", "07W.1", receipt)])
    return raw


def _degrade_scene(payload: dict[str, Any]) -> None:
    payload["pre_work"]["scene"] = {
        "status": "degraded",
        "text": None,
        "source_refs": payload["pre_work"]["scene"]["source_refs"],
        "known_losses": ["scene_seed_unavailable"],
        "marker": "prework_semantics_not_authored",
        "lesson_type": None,
        "archetype": None,
    }
    payload["pre_work"]["provenance"]["known_losses"] = ["scene_seed_unavailable"]
    payload["known_losses"] = ["scene_seed_unavailable"]
    payload["scene_receipt"]["gate"]["failures"] = ["scene_seed_unavailable"]
    payload["writer_receipts"][0]["calls"] = 0


def _degrade_promise(payload: dict[str, Any]) -> None:
    payload["pre_work"]["promise"] = {
        "status": "degraded",
        "vows": [],
        "known_losses": ["promise_objectives_unratified"],
        "marker": "prework_semantics_not_authored",
    }
    payload["pre_work"]["provenance"]["known_losses"] = [
        "promise_objectives_unratified"
    ]
    payload["known_losses"] = ["promise_objectives_unratified"]
    payload["promise_receipt"]["gate"]["failures"] = ["promise_objectives_unratified"]
    payload["writer_receipts"][1]["calls"] = 0


def test_real_authored_brief_yields_ready_demand_with_bound_scene() -> None:
    """The frozen 36-4 lineage (scene+promise authored) is READY for Ask-B.

    NOTE: this brief carries a NULL deep-dive skeleton — Ask-B is ready
    anyway because it binds Promise vows + Scene, never the skeleton
    (narrower than Ask-A by design; Ask-A calls this run legacy-null).
    """
    artifact = read_workbook_brief(LEGACY_RUN)
    demand = resolve_hot_topics_demand(LEGACY_RUN)
    assert demand.status == "ready"
    assert demand.known_losses == ()
    assert demand.workbook_brief_payload_digest == artifact.payload_digest
    assert [
        (ability.ability_id, ability.text) for ability in demand.abilities
    ] == [
        (vow.objective_id, vow.text)
        for vow in artifact.payload.pre_work.promise.vows
    ]
    scene = artifact.payload.pre_work.scene
    assert demand.scene_text == scene.text
    assert demand.scene_digest == _canonical_digest(scene.model_dump(mode="json"))
    assert demand.demand_digest.startswith("sha256:")
    # Stable on re-resolution (same digest witnessed).
    assert resolve_hot_topics_demand(LEGACY_RUN) == demand


def test_missing_brief_is_honest_absent_demand(tmp_path: Path) -> None:
    demand = resolve_hot_topics_demand(tmp_path)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("workbook_brief_absent",)
    assert demand.workbook_brief_payload_digest is None
    assert demand.abilities == ()
    assert demand.scene_digest is None and demand.scene_text is None


def test_scene_absent_brief_is_ready_with_recorded_scope_loss(tmp_path: Path) -> None:
    """W-3/A-1 DECIDED: no scene → ready WITH loss, never a blocking retryable."""
    _install_brief(tmp_path, _degrade_scene)
    demand = resolve_hot_topics_demand(tmp_path)
    assert demand.status == "ready"
    assert demand.known_losses == ("scene_identity_absent",)
    assert demand.scene_digest is None and demand.scene_text is None
    assert demand.abilities  # vows still bind


def test_promise_not_authored_is_unavailable(tmp_path: Path) -> None:
    _install_brief(tmp_path, _degrade_promise)
    demand = resolve_hot_topics_demand(tmp_path)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("promise_vows_unavailable",)
    assert demand.workbook_brief_payload_digest is not None
    assert demand.abilities == ()


def test_legacy_stub_contribution_is_unavailable(tmp_path: Path) -> None:
    _write_envelope(
        tmp_path, [("workbook_brief_stub", "07W.1", {"stub": True})]
    )
    demand = resolve_hot_topics_demand(tmp_path)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("workbook_brief_legacy_stub",)
    assert demand.workbook_brief_payload_digest is not None


def test_contribution_receipt_mismatch_fails_loud(tmp_path: Path) -> None:
    _install_brief(tmp_path)
    _write_envelope(
        tmp_path, [("workbook_brief", "07W.1", {"forged": "receipt"})]
    )
    with pytest.raises(ResearchDemandShapeError, match="contribution/sidecar"):
        resolve_hot_topics_demand(tmp_path)


def test_coordinate_collision_fails_loud(tmp_path: Path) -> None:
    _install_brief(tmp_path)
    artifact = read_workbook_brief(tmp_path)
    receipt = workbook_brief_contribution_receipt(artifact)
    _write_envelope(
        tmp_path,
        [
            ("workbook_brief", "07W.1", receipt),
            ("intruder", "07W.1", {"x": 1}),
        ],
    )
    with pytest.raises(ResearchDemandShapeError, match="collision"):
        resolve_hot_topics_demand(tmp_path)


def test_brief_sidecar_without_contribution_fails_loud(tmp_path: Path) -> None:
    _install_brief(tmp_path)
    _write_envelope(tmp_path, [])
    with pytest.raises(ResearchDemandShapeError, match="no exact contribution"):
        resolve_hot_topics_demand(tmp_path)


def test_brief_symlink_is_corruption_not_honest_absence(tmp_path: Path) -> None:
    brief = tmp_path / "workbook-brief.v1.json"
    try:
        brief.symlink_to(tmp_path / "missing-workbook-brief.json")
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")
    with pytest.raises(ResearchDemandShapeError, match="symlink"):
        resolve_hot_topics_demand(tmp_path)


def test_duplicate_vow_objective_ids_fail_loud(tmp_path: Path) -> None:
    def duplicate_vows(payload: dict[str, Any]) -> None:
        vow = payload["pre_work"]["promise"]["vows"][0]
        payload["pre_work"]["promise"]["vows"] = [vow, dict(vow)]

    _install_brief(tmp_path, duplicate_vows)
    with pytest.raises(ResearchDemandShapeError, match="duplicate Promise vow"):
        resolve_hot_topics_demand(tmp_path)


def _raw_demand(**overrides: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "schema_version": "ask-b-hot-topics-demand.v1",
        "status": "ready",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        "workbook_brief_payload_digest": "sha256:" + "1" * 64,
        "abilities": [{"ability_id": "LO-1", "text": "I can act."}],
        "scene_digest": "sha256:" + "2" * 64,
        "scene_text": "A clinic hits workflow friction.",
        "known_losses": [],
    }
    raw.update(overrides)
    raw["demand_digest"] = _canonical_digest(
        {k: v for k, v in raw.items() if k != "demand_digest"}
    )
    return raw


def test_constructed_demand_rejects_forged_digest() -> None:
    raw = _raw_demand()
    raw["demand_digest"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="digest mismatch"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_ready_demand_rejects_blocking_loss() -> None:
    raw = _raw_demand(known_losses=["promise_vows_unavailable"])
    with pytest.raises(ValueError, match="scene_identity_absent"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_ready_demand_rejects_scene_loss_with_bound_scene() -> None:
    raw = _raw_demand(known_losses=["scene_identity_absent"])
    with pytest.raises(ValueError, match="mirror"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_ready_demand_rejects_unpaired_scene_fields() -> None:
    raw = _raw_demand(scene_text=None)
    with pytest.raises(ValueError, match="together"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_ready_demand_rejects_duplicate_ability_ids() -> None:
    raw = _raw_demand(
        abilities=[
            {"ability_id": "LO-1", "text": "I can act."},
            {"ability_id": "LO-1", "text": "I can act twice."},
        ]
    )
    with pytest.raises(ValueError, match="unique vow objective"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_non_ready_demand_rejects_payload_or_extra_losses() -> None:
    raw = _raw_demand(
        status="unavailable",
        known_losses=["workbook_brief_absent", "promise_vows_unavailable"],
        workbook_brief_payload_digest=None,
        scene_digest=None,
        scene_text=None,
        abilities=[],
    )
    with pytest.raises(ValueError, match="exactly one blocking loss"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


@pytest.mark.parametrize("bad_text", ["I can\nact.", "I can\ract.", "I can act."])
def test_constructed_ready_demand_rejects_line_control_vow_text(bad_text: str) -> None:
    """38-2 T4 R5a (B6/E7): vow text carrying \\r/\\n (or unicode line
    separators) is rejected AT the demand contract, so the wiring seam types
    it ``ask-b.demand-invalid`` instead of crashing at query build. Trailing
    whitespace stays contract-legal (see the companion scope test)."""
    raw = _raw_demand(abilities=[{"ability_id": "LO-1", "text": bad_text}])
    with pytest.raises(ValueError, match="line-control"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_constructed_ready_demand_accepts_trailing_space_vow_text() -> None:
    """38-2 T4 R5c (B6): trailing-space vow text is contract-legal upstream
    (PromiseVow NonBlankStr) and must stay legal here — the canonical query
    collapses it downstream."""
    raw = _raw_demand(abilities=[{"ability_id": "LO-1", "text": "I can act. "}])
    demand = AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)
    assert demand.abilities[0].text == "I can act. "


def test_constructed_non_ready_demand_rejects_ready_only_scene_loss() -> None:
    raw = _raw_demand(
        status="unavailable",
        known_losses=["scene_identity_absent"],
        workbook_brief_payload_digest="sha256:" + "3" * 64,
        scene_digest=None,
        scene_text=None,
        abilities=[],
    )
    with pytest.raises(ValueError, match="blocking loss"):
        AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.marcus.lesson_plan.deep_dive_from_run import (
    DeepDiveAuthorityInvalidError,
    build_deep_dive_request,
)
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.prework_artifact import (
    read_workbook_brief,
    workbook_brief_contribution_receipt,
)
from app.marcus.lesson_plan.prework_projection import PromiseProjection, PromiseVow
from app.marcus.lesson_plan.research_demand import (
    AskAResearchDemandV1,
    ResearchDemandShapeError,
    resolve_enrichment_demand,
)
from app.marcus.lesson_plan.research_packet import (
    ASK_A_ENRICHMENT_NODE_ID,
    ASK_A_ENRICHMENT_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
    ASK_B_HOT_TOPICS_SPECIALIST_ID,
)
from app.marcus.orchestrator import workbook_wiring

LEGACY_RUN = Path(
    "_bmad-output/implementation-artifacts/evidence/"
    "prework-36-4-fresh-input-380ecd47/run"
)


def _write_authority(run_dir: Path, course_root: Path) -> None:
    exports = run_dir / "exports"
    exports.mkdir(parents=True)
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        "segments:\n"
        "  - segment_id: seg-01\n"
        "    slide_id: slide-01\n"
        "    narration_text: The workflow symptom is visible.\n"
        "  - segment_id: seg-02\n"
        "    slide_id: slide-02\n"
        "    narration_text: Use two stages to organize the work.\n",
        encoding="utf-8",
    )
    slides = course_root / "slides"
    slides.mkdir(parents=True)
    (slides / "slide-1-symptom.md").write_text(
        "# Symptom\n\n- **Narration (Speaker Notes):** "
        '"The workflow symptom is visible, but causal analysis adds depth."\n',
        encoding="utf-8",
    )
    (slides / "slide-2-method.md").write_text(
        "# Method\n\n- **Narration (Speaker Notes):** "
        '"Use two stages to organize the work."\n',
        encoding="utf-8",
    )


def test_real_pre_38_3a_null_fixture_retains_digest_and_projects_typed_loss() -> None:
    artifact = read_workbook_brief(LEGACY_RUN)
    raw = json.loads((LEGACY_RUN / "workbook-brief.v1.json").read_text("utf-8"))
    assert artifact.payload.deep_dive_skeleton is None
    assert artifact.payload.deep_dive_writer_receipt is None
    assert artifact.payload_digest == raw["payload_digest"]
    assert workbook_brief_contribution_receipt(artifact) == {
        "artifact_path": "workbook-brief.v1.json",
        "payload_digest": artifact.payload_digest,
        "schema_version": "workbook-brief.v1",
        "status_summary": {"scene": "authored", "promise": "authored"},
        "warning_summary": list(artifact.payload.warnings),
        "loss_summary": [],
        "node_id": "07W.1",
        "specialist_id": "workbook_brief",
    }

    demand = resolve_enrichment_demand(LEGACY_RUN)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("workbook_brief_legacy_null",)
    assert demand.workbook_brief_payload_digest == artifact.payload_digest
    assert demand.abilities == demand.bold_terms == demand.source_claim_refs == ()


def test_immediate_baseline_null_digest_with_empty_introduced_terms_still_reads(
    tmp_path: Path,
) -> None:
    raw = json.loads((LEGACY_RUN / "workbook-brief.v1.json").read_text("utf-8"))
    raw["payload"]["scene_receipt"]["introduced_terms"] = []
    canonical = json.dumps(
        raw["payload"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    raw["payload_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    (tmp_path / "workbook-brief.v1.json").write_text(
        json.dumps(raw, indent=2) + "\n", encoding="utf-8"
    )
    artifact = read_workbook_brief(tmp_path)
    assert artifact.payload_digest == raw["payload_digest"]


def test_missing_brief_is_honest_absent_demand(tmp_path: Path) -> None:
    demand = resolve_enrichment_demand(tmp_path)
    assert demand.status == "unavailable"
    assert demand.known_losses == ("workbook_brief_absent",)
    assert demand.workbook_brief_payload_digest is None
    assert demand.demand_digest.startswith("sha256:")


def test_broken_brief_symlink_is_corruption_not_honest_absence(tmp_path: Path) -> None:
    brief = tmp_path / "workbook-brief.v1.json"
    try:
        brief.symlink_to(tmp_path / "missing-workbook-brief.json")
    except OSError as exc:
        pytest.skip(f"host cannot create symlinks: {exc}")
    with pytest.raises(ResearchDemandShapeError, match="symlink"):
        resolve_enrichment_demand(tmp_path)


def test_request_adapter_is_ordered_and_admits_only_real_note_delta(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    promise = PromiseProjection(
        status="authored",
        vows=(
            PromiseVow(objective_id="LO-1", text="I can distinguish symptom from cause."),
            PromiseVow(objective_id="LO-2", text="I can choose a first move."),
        ),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert tuple(span.span_id for span in request.source_spans) == (
        "vo:seg-01",
        "vo:seg-02",
        "delta:slide-01",
    )
    assert tuple(claim.claim_id for claim in request.source_claims) == (
        "claim:vo:seg-01",
        "claim:vo:seg-02",
        "claim:delta:slide-01",
    )
    assert request.abilities == (
        DeepDiveAbilityInput(
            ability_id="LO-1", text="I can distinguish symptom from cause."
        ),
        DeepDiveAbilityInput(ability_id="LO-2", text="I can choose a first move."),
    )
    assert request.source_spans[-1].text.endswith("adds depth.\"")
    assert not request.source_spans[-1].text.startswith("**")


def test_request_adapter_rejects_duplicate_ids_without_search(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    manifest = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    manifest.write_text(
        manifest.read_text("utf-8").replace("segment_id: seg-02", "segment_id: seg-01"),
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="duplicate"):
        build_deep_dive_request(run_dir, course_root, promise)


@pytest.mark.parametrize("segment_id", [" seg-01", "seg/01", "seg#01", "seg~01"])
def test_request_adapter_rejects_ambiguous_segment_reference_tokens(
    tmp_path: Path, segment_id: str
) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    manifest = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    manifest.write_text(
        manifest.read_text("utf-8").replace(
            "segment_id: seg-01", f"segment_id: {json.dumps(segment_id)}"
        ),
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="segment_id"):
        build_deep_dive_request(run_dir, course_root, promise)


def test_request_adapter_treats_absent_or_blank_note_as_zero_delta(
    tmp_path: Path,
) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    (course_root / "slides/slide-1-symptom.md").write_text(
        "# Symptom\n\n- **Narration (Speaker Notes):**\n"
        "- **On-screen text:** must not become narration authority\n",
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert tuple(span.span_id for span in request.source_spans) == (
        "vo:seg-01",
        "vo:seg-02",
    )
    assert all("On-screen" not in span.text for span in request.source_spans)


def test_request_adapter_preserves_multiline_note_and_rejects_duplicate_field(
    tmp_path: Path,
) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    slide = course_root / "slides/slide-1-symptom.md"
    slide.write_bytes(
        b"# Symptom\r\n\r\n- **Narration (Speaker Notes):**\r\n"
        b"Added source-supported detail.\r\n"
        b"Reason: managers lack authority.\r\n"
        b"https://example.test/source: detail\r\n"
        b"- **On-screen text:** ignored\r\n"
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert request.source_spans[-1].text == (
        "\r\nAdded source-supported detail.\r\n"
        "Reason: managers lack authority.\r\n"
        "https://example.test/source: detail"
    )
    slide.write_text(
        "- **Narration (Speaker Notes):** first\n"
        "- **Narration (Speaker Notes):** second\n",
        encoding="utf-8",
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="duplicate speaker-note"):
        build_deep_dive_request(run_dir, course_root, promise)


def test_request_adapter_rejects_duplicate_yaml_mapping_keys(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    manifest = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    manifest.write_text(
        manifest.read_text("utf-8").replace(
            "  - segment_id: seg-01\n",
            "  - segment_id: overwritten\n    segment_id: seg-01\n",
        ),
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="invalid"):
        build_deep_dive_request(run_dir, course_root, promise)


def test_request_adapter_rejects_duplicate_canonical_slide_ids(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    manifest = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    manifest.write_text(
        manifest.read_text("utf-8").replace("slide_id: slide-02", "slide_id: slide-1"),
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="canonical slide_id"):
        build_deep_dive_request(run_dir, course_root, promise)


@pytest.mark.parametrize("authority", ["manifest", "slide"])
def test_request_adapter_rejects_symlinked_authority(
    tmp_path: Path, authority: str
) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    if authority == "manifest":
        target = run_dir / "external-manifest.yaml"
        target.write_text(
            (run_dir / "exports/segment-manifest-storyboard-b.yaml").read_text("utf-8"),
            encoding="utf-8",
        )
        link = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    else:
        target = course_root / "external-slide.md"
        target.write_text("- **Narration (Speaker Notes):** external", encoding="utf-8")
        link = course_root / "slides/slide-1-symptom.md"
    link.unlink()
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable on this host")
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="symlink"):
        build_deep_dive_request(run_dir, course_root, promise)


def test_constructed_non_ready_demand_rejects_wrong_status_loss_pair(
    tmp_path: Path,
) -> None:
    raw = resolve_enrichment_demand(tmp_path).model_dump(mode="json")
    raw["status"] = "degraded"
    unsigned = {key: value for key, value in raw.items() if key != "demand_digest"}
    canonical = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    raw["demand_digest"] = "sha256:" + hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    with pytest.raises(ValueError, match="status/loss"):
        AskAResearchDemandV1.model_validate_json(json.dumps(raw), strict=True)


@pytest.mark.parametrize(
    "source_ref",
    ["", " ", " claim:vo:seg-01", "claim:vo:seg-01 ", "claim:vo:seg-01\nforged"],
)
def test_constructed_ready_demand_rejects_ambiguous_source_claim_refs(
    source_ref: str,
) -> None:
    raw = {
        "schema_version": "ask-a-research-demand.v1",
        "status": "ready",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        "workbook_brief_payload_digest": "sha256:" + "1" * 64,
        "skeleton_authority_digest": "sha256:" + "2" * 64,
        "skeleton_candidate_digest": "sha256:" + "3" * 64,
        "abilities": [{"ability_id": "LO-1", "text": "I can act."}],
        "bold_terms": [{"term": "workflow"}],
        "source_claim_refs": [source_ref],
        "known_losses": [],
    }
    raw["demand_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(
            raw,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    with pytest.raises(ValueError, match="source claim refs"):
        AskAResearchDemandV1.model_validate_json(json.dumps(raw), strict=True)


def test_request_adapter_translates_unbounded_slide_ordinal(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    manifest = run_dir / "exports/segment-manifest-storyboard-b.yaml"
    manifest.write_text(
        manifest.read_text("utf-8").replace("slide_id: slide-01", "slide_id: slide-" + "9" * 5000),
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    with pytest.raises(DeepDiveAuthorityInvalidError, match="invalid slide_id"):
        build_deep_dive_request(run_dir, course_root, promise)


@pytest.mark.parametrize(
    "field_header",
    [
        "Answer",
        "On-screen text",
        "References",
        "Summary Text",
        "Prompt to Generate Image",
        "Learning Objective",
        "The Core Message",
    ],
)
def test_unbolded_slide_fields_do_not_enter_speaker_note_authority(
    tmp_path: Path, field_header: str
) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    (course_root / "slides/slide-1-symptom.md").write_text(
        "Narration (Speaker Notes): Added source-supported detail.\n"
        f"{field_header}: forbidden display copy\n",
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert request.source_spans[-1].text == "Added source-supported detail."
    assert all("forbidden display copy" not in span.text for span in request.source_spans)


def test_bold_answer_field_does_not_enter_speaker_note_authority(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    (course_root / "slides/slide-1-symptom.md").write_text(
        "Narration (Speaker Notes): Added source-supported detail.\n"
        "**Answer:** forbidden assessment answer\n",
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert request.source_spans[-1].text == "Added source-supported detail."
    assert all(
        "forbidden assessment answer" not in span.text for span in request.source_spans
    )


def test_colon_bearing_narration_prose_is_not_a_slide_field_boundary(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    (course_root / "slides/slide-1-symptom.md").write_text(
        "Narration (Speaker Notes): Added source-supported detail.\n"
        "Consider the following question:\n"
        "This is the core assessment: keep both narration lines.\n"
        "**Reason:** bold colon-bearing narration also remains.\n"
        "\u2022 **References:** forbidden display metadata\n",
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    note = request.source_spans[-1].text
    assert "Consider the following question:" in note
    assert "This is the core assessment:" in note
    assert "**Reason:**" in note
    assert "forbidden display metadata" not in note


def test_unicode_bullet_can_prefix_exact_speaker_note_header(tmp_path: Path) -> None:
    run_dir, course_root = tmp_path / "run", tmp_path / "course"
    run_dir.mkdir()
    _write_authority(run_dir, course_root)
    (course_root / "slides/slide-1-symptom.md").write_text(
        "\u2022 **Narration (Speaker Notes):** Added source-supported detail.\n",
        encoding="utf-8",
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can act."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(run_dir, course_root, promise)
    assert request.source_spans[-1].text == "Added source-supported detail."


def test_cross_layer_coordinates_remain_exact() -> None:
    # 37.2b: 07W.3 activated at the exact coordinate (legacy stub id retained
    # only for the same-coordinate upgrade walk).
    assert workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS == {
        "07W.1": "workbook_brief",
        ASK_A_ENRICHMENT_NODE_ID: ASK_A_ENRICHMENT_SPECIALIST_ID,
        "07W.3": "workbook_review",
        ASK_B_HOT_TOPICS_NODE_ID: ASK_B_HOT_TOPICS_SPECIALIST_ID,
    }
    assert workbook_wiring.LEGACY_WORKBOOK_REVIEW_SPECIALIST_ID == "workbook_review_stub"

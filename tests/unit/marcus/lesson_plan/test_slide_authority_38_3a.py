from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import uuid4

import pytest
import yaml

from app.marcus.lesson_plan import deep_dive_from_run
from app.marcus.lesson_plan.deep_dive_from_run import (
    DeepDiveAuthorityInvalidError,
    build_deep_dive_request,
)
from app.marcus.lesson_plan.pass1_authority import finalize_plan_authority
from app.marcus.lesson_plan.prework_artifact import WorkbookBriefRuntimeContext
from app.marcus.lesson_plan.prework_projection import PromiseProjection, PromiseVow
from app.marcus.lesson_plan.slide_authority import (
    SLIDE_AUTHORITY_FILENAME,
    SlideAuthorityInvalidError,
    SlideAuthorityPersistenceError,
    SourceSlideInventoryEntryV1,
    WorkbookSlideAuthorityMapV1,
    WorkbookSlideAuthorityRowV1,
    build_slide_authority_map,
    canonical_source_content_digest,
    read_contained_regular_bytes,
    read_slide_authority_map,
    slide_authority_digest,
    write_or_validate_slide_authority_map,
)
from app.marcus.orchestrator import workbook_wiring
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from tests._helpers.pass1_bundle import write_authenticated_slide_bundle_from_course

FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "fixtures"
    / "marcus"
    / "lesson_plan"
    / "slide_authority_13_to_6.json"
)
LIVE_WITNESS = FIXTURE.with_name("slide_authority_live_witness_c8f17a24.json")
SHA = "sha256:" + "1" * 64
EXPECTED_SOURCE_ORDINALS = (1, 2, 2, 2, 3, 3, 3, 3, 4, 5, 5, 5, 6)


def _canonical_source_id(course_root: Path, relative_path: str) -> str:
    text = (course_root / relative_path).read_text(encoding="utf-8")
    return f"{relative_path}|{canonical_source_content_digest(text)}"


def _authenticated_sections(
    course_root: Path,
) -> tuple[Pass1AuthenticatedSourceSection, ...]:
    """Authenticated sections mirroring the on-disk slides (body == raw text).

    The workbook resolver now matches anchors over Texas-authenticated bodies
    instead of the raw slide files; in these unit fixtures the two are identical,
    so building the sections from disk preserves prior resolution behavior while
    exercising the authenticated-source path.
    """
    slides = course_root / "slides"
    sections: list[Pass1AuthenticatedSourceSection] = []
    for path in sorted(slides.iterdir(), key=lambda item: item.name):
        if path.is_symlink() or not path.is_file():
            continue
        if not path.name.startswith("slide-") or not path.name.endswith(".md"):
            continue
        text = path.read_text(encoding="utf-8")
        rel = f"slides/{path.name}"
        sections.append(
            Pass1AuthenticatedSourceSection(
                source_id=f"{rel}|{canonical_source_content_digest(text)}",
                source_content_digest=canonical_source_content_digest(text),
                extracted_content_digest=canonical_extracted_content_digest(text),
                body=text,
            )
        )
    return tuple(sections)


def _fixture(tmp_path: Path) -> tuple[dict[str, object], Path]:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    course_root = tmp_path / "course"
    slides = course_root / "slides"
    slides.mkdir(parents=True)
    for name, text in raw["source_slides"].items():
        (slides / name).write_text(text, encoding="utf-8")
    return raw, course_root


def _build(
    raw: dict[str, object],
    course_root: Path,
    *,
    manifest_digest: str = SHA,
    authorized_source_ids: dict[str, str] | None = None,
):
    if authorized_source_ids is None:
        authorized_source_ids = {}
        for unit, ordinal in zip(
            raw["plan_units"], EXPECTED_SOURCE_ORDINALS, strict=True
        ):
            if unit.get("scope_decision") != "in-scope":
                continue
            matches = [
                _canonical_source_id(course_root, f"slides/{name}")
                for name in raw["source_slides"]
                if name.startswith(f"slide-{ordinal}-")
            ]
            assert len(matches) == 1
            authorized_source_ids[unit["unit_id"]] = matches[0]
    return build_slide_authority_map(
        manifest_segments=raw["manifest_segments"],
        plan_units=raw["plan_units"],
        package_slides=raw["package_slides"],
        authorized_source_ids=authorized_source_ids,
        course_source_root=course_root,
        source_sections=_authenticated_sections(course_root),
        manifest_digest=manifest_digest,
        plan_sidecar_digest="sha256:" + "2" * 64,
        plan_contribution_digest="sha256:" + "3" * 64,
        package_contribution_digest="sha256:" + "4" * 64,
    )


def test_serialized_live_shape_maps_13_final_slides_to_6_sources(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)

    authority = _build(raw, course_root)

    assert [row.source_slide_ordinal for row in authority.rows] == [
        1,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        4,
        5,
        5,
        5,
        6,
    ]
    assert authority.rows[4].unit_id == "u05"
    assert authority.rows[4].source_slide_id == "slide-3"
    assert authority.rows[8].source_slide_id == "slide-4"
    assert authority.rows[9].source_slide_id == "slide-5"
    assert authority.rows[12].source_slide_id == "slide-6"

    live = json.loads(LIVE_WITNESS.read_text(encoding="utf-8"))
    assert live["source_run_id"] == "c8f17a24-9b63-4e10-a5d7-6f2043bc9812"
    assert live["captured_map_digest"] == (
        "sha256:536579300f2d44e9e28e323810570035bfa1693ae7b36db6f90bcaf3b4326c0c"
    )
    assert live["captured_manifest_digest"] == (
        "sha256:cb5d5eb21108f56465f31e1f998964785b212c82e4a8ba9e77afab1b13424aef"
    )
    assert live["captured_source_inventory_digest"] == (
        "sha256:e4187f3b197dfa81dc86600d0f485e48b97485a25292ca137407e4bdebb71b8d"
    )
    live_root = tmp_path / "live-witness-course"
    live_slides = live_root / "slides"
    live_slides.mkdir(parents=True)
    for name, text in live["source_slides"].items():
        (live_slides / name).write_text(text, encoding="utf-8")
    live_authority = _build(live, live_root)
    assert live["expected_fixture_map_digest"] == (
        "sha256:ccc71e7f7129a972b12ab2bc28f163792db58b05a100abfd9fd2971fe85a9b00"
    )
    assert live_authority.map_digest == (
        "sha256:ccc71e7f7129a972b12ab2bc28f163792db58b05a100abfd9fd2971fe85a9b00"
    )
    assert [row.source_slide_ordinal for row in live_authority.rows] == [
        1,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
        4,
        5,
        5,
        5,
        6,
    ]


def test_final_ordinal_never_falls_back_to_same_numbered_source(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    (course_root / "slides" / "slide-7-trap.md").write_text(
        "unrelated source seven", encoding="utf-8"
    )

    authority = _build(raw, course_root)

    row = next(row for row in authority.rows if row.final_slide_id == "slide-07")
    assert row.source_slide_id == "slide-3"
    assert row.source_path == "slides/slide-3-three.md"


def test_missing_or_ambiguous_exact_anchor_fails_closed(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    raw["plan_units"][6]["source_refs"] = ["missing-anchor"]
    with pytest.raises(SlideAuthorityInvalidError, match="exactly one"):
        _build(raw, course_root)

    raw, course_root = _fixture(tmp_path / "ambiguous")
    (course_root / "slides" / "slide-6-six.md").write_text(
        "anchor-source-6-head\nanchor-source-3-b\n", encoding="utf-8"
    )
    with pytest.raises(SlideAuthorityInvalidError, match="exactly one"):
        _build(raw, course_root)


def test_newline_equivalent_duplicate_anchors_fail_closed(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    (course_root / "slides" / "slide-1-one.md").write_text(
        "alpha\nbeta\n", encoding="utf-8"
    )
    raw["plan_units"][0]["source_refs"] = ["alpha\r\nbeta", "alpha\nbeta"]

    with pytest.raises(SlideAuthorityInvalidError, match="duplicate"):
        _build(raw, course_root)


def test_interstitial_must_resolve_to_its_head_source(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    raw["plan_units"][6]["source_refs"] = ["anchor-source-4-head"]

    with pytest.raises(SlideAuthorityInvalidError, match="Pass-1 authority|parent"):
        _build(raw, course_root)


def test_resolved_source_must_equal_pass1_authority(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    baseline = _build(raw, course_root)
    authorized = {
        row.unit_id: _canonical_source_id(course_root, row.source_path)
        for row in baseline.rows
    }
    authorized["u01"] = authorized["u02"]
    with pytest.raises(SlideAuthorityInvalidError, match="Pass-1 authority"):
        _build(raw, course_root, authorized_source_ids=authorized)


def test_source_content_drift_invalidates_pass1_authority(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    baseline = _build(raw, course_root)
    authorized = {
        row.unit_id: _canonical_source_id(course_root, row.source_path)
        for row in baseline.rows
    }
    source = course_root / "slides" / "slide-1-one.md"
    source.write_text(source.read_text(encoding="utf-8") + "\nchanged", encoding="utf-8")

    with pytest.raises(SlideAuthorityInvalidError, match="Pass-1 authority"):
        _build(raw, course_root, authorized_source_ids=authorized)


def test_source_boundary_whitespace_drift_invalidates_pass1_authority(
    tmp_path: Path,
) -> None:
    raw, course_root = _fixture(tmp_path)
    baseline = _build(raw, course_root)
    authorized = {
        row.unit_id: _canonical_source_id(course_root, row.source_path)
        for row in baseline.rows
    }
    source = course_root / "slides" / "slide-1-one.md"
    source.write_text(
        source.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )

    with pytest.raises(SlideAuthorityInvalidError, match="Pass-1 authority"):
        _build(raw, course_root, authorized_source_ids=authorized)


def test_authority_map_is_minted_once_and_revalidated(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    first = write_or_validate_slide_authority_map(run_dir, authority)
    original = first.read_bytes()
    second = write_or_validate_slide_authority_map(run_dir, authority)

    assert first == second
    assert second.read_bytes() == original
    assert read_slide_authority_map(run_dir) == authority


def test_authority_map_flushes_link_and_temporary_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    flushes: list[Path] = []
    monkeypatch.setattr(
        "app.marcus.lesson_plan.slide_authority._fsync_directory",
        lambda path: flushes.append(path),
    )

    write_or_validate_slide_authority_map(run_dir, authority)

    assert flushes == [run_dir, run_dir]


def test_existing_authority_map_is_never_overwritten(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    path = write_or_validate_slide_authority_map(run_dir, authority)
    corrupted = path.read_text(encoding="utf-8").replace(
        '"manifest_digest":"sha256:111', '"manifest_digest":"sha256:999'
    )
    path.write_text(corrupted, encoding="utf-8")
    before = path.read_bytes()

    with pytest.raises(SlideAuthorityInvalidError):
        write_or_validate_slide_authority_map(run_dir, authority)

    assert path.read_bytes() == before


def test_duplicate_key_and_split_brain_fail_closed(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target = run_dir / SLIDE_AUTHORITY_FILENAME
    target.write_text(
        '{"schema_version":"a","schema_version":"b"}', encoding="utf-8"
    )
    with pytest.raises(SlideAuthorityInvalidError):
        read_slide_authority_map(run_dir)
    target.unlink()
    (run_dir / f".{SLIDE_AUTHORITY_FILENAME}.tmp").write_text(
        "partial", encoding="utf-8"
    )
    raw, course_root = _fixture(tmp_path)
    with pytest.raises(SlideAuthorityPersistenceError, match="split-brain"):
        write_or_validate_slide_authority_map(run_dir, _build(raw, course_root))


@pytest.mark.parametrize("malformed", [None, 7, "anchor"])
def test_reader_rejects_malformed_matched_anchor_collection(
    tmp_path: Path, malformed: object
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    path = write_or_validate_slide_authority_map(run_dir, authority)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["rows"][0]["matched_anchors"] = malformed
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SlideAuthorityInvalidError, match="invalid"):
        read_slide_authority_map(run_dir)


def test_map_internal_digests_and_inventory_correspondence_are_revalidated(
    tmp_path: Path,
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    payload = authority.model_dump()
    payload["source_inventory_digest"] = "sha256:" + "9" * 64
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    with pytest.raises(ValueError, match="source inventory digest"):
        WorkbookSlideAuthorityMapV1.model_validate(payload)

    row = authority.rows[0].model_copy(
        update={"source_path": "slides/unlisted.md"}
    )
    payload = authority.model_dump()
    payload["rows"] = (
        row.model_dump(),
        *(item.model_dump() for item in authority.rows[1:]),
    )
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    with pytest.raises(ValueError, match="does not match source inventory"):
        WorkbookSlideAuthorityMapV1.model_validate(payload)


def test_map_rejects_duplicate_units_and_cross_row_parent_drift(tmp_path: Path) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)

    payload = authority.model_dump()
    payload["rows"][1]["unit_id"] = payload["rows"][0]["unit_id"]
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    with pytest.raises(ValueError, match="duplicate plan unit"):
        WorkbookSlideAuthorityMapV1.model_validate(payload)

    payload = authority.model_dump()
    payload["rows"][2]["parent_unit_id"] = "u01"
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    with pytest.raises(ValueError, match="parent.*source|source.*parent"):
        WorkbookSlideAuthorityMapV1.model_validate(payload)

    payload = authority.model_dump()
    payload["rows"][2]["cluster_id"] = "c-u01"
    payload["map_digest"] = slide_authority_digest(payload, exclude_map_digest=True)
    with pytest.raises(ValueError, match="cluster"):
        WorkbookSlideAuthorityMapV1.model_validate(payload)


@pytest.mark.parametrize(
    "decision",
    [None, "", "OUT", {}, {"scope": None}, {"scope": "unknown"}],
)
def test_resolver_rejects_unknown_scope_decisions(
    tmp_path: Path, decision: object
) -> None:
    raw, course_root = _fixture(tmp_path)
    raw["plan_units"][0]["scope_decision"] = decision
    with pytest.raises(SlideAuthorityInvalidError, match="scope_decision"):
        _build(raw, course_root)


def test_contained_reader_rejects_named_path_identity_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target.txt"
    other = tmp_path / "other.txt"
    target.write_text("trusted", encoding="utf-8")
    other.write_text("substituted", encoding="utf-8")
    other_stat = other.stat()
    real_stat = Path.stat

    def swapped_stat(path: Path, *args, **kwargs):
        if path == target and kwargs.get("follow_symlinks") is False:
            return other_stat
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", swapped_stat)
    with pytest.raises(SlideAuthorityInvalidError, match="unsafe, or stale"):
        read_contained_regular_bytes(tmp_path, target, "test carrier")


@pytest.mark.parametrize(
    "model",
    [
        lambda: SourceSlideInventoryEntryV1(
            source_slide_id="slide-1",
            source_slide_ordinal=1,
            source_path="slides/../secret.md",
            source_sha256=SHA,
        ),
        lambda: WorkbookSlideAuthorityRowV1(
            final_slide_id="slide-01",
            unit_id="u01",
            source_slide_id="slide-1",
            source_slide_ordinal=1,
            source_path="slides/../secret.md",
            source_sha256=SHA,
            matched_anchors=("anchor",),
            cluster_id="c-u01",
            cluster_role="head",
        ),
    ],
)
def test_models_reject_source_path_traversal(model) -> None:
    with pytest.raises(ValueError, match="below slides"):
        model()


def test_identifiers_are_not_coerced_and_final_ordinals_are_canonical(
    tmp_path: Path,
) -> None:
    raw, course_root = _fixture(tmp_path)
    raw["package_slides"][0]["source_ref"] = 1
    with pytest.raises(SlideAuthorityInvalidError, match="nonblank string"):
        _build(raw, course_root)

    raw, course_root = _fixture(tmp_path / "canonical")
    raw["manifest_segments"][1]["slide_id"] = "slide-1"
    raw["package_slides"][1]["slide_id"] = "slide-1"
    with pytest.raises(SlideAuthorityInvalidError, match="duplicate final"):
        _build(raw, course_root)


def test_target_temp_coexistence_and_link_failure_use_persistence_taxonomy(
    tmp_path: Path, monkeypatch
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    target = write_or_validate_slide_authority_map(run_dir, authority)
    temporary = run_dir / f".{SLIDE_AUTHORITY_FILENAME}.tmp"
    temporary.write_bytes(target.read_bytes())
    with pytest.raises(SlideAuthorityPersistenceError, match="split-brain"):
        write_or_validate_slide_authority_map(run_dir, authority)
    temporary.unlink()
    target.unlink()

    def denied_link(_source, _target):
        raise PermissionError("denied")

    monkeypatch.setattr("app.marcus.lesson_plan.slide_authority.os.link", denied_link)
    with pytest.raises(SlideAuthorityPersistenceError, match="persistence failed"):
        write_or_validate_slide_authority_map(run_dir, authority)


def test_temporary_cleanup_failure_uses_persistence_taxonomy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    temporary = run_dir / f".{SLIDE_AUTHORITY_FILENAME}.tmp"
    real_unlink = Path.unlink

    def denied_cleanup(path: Path, *args, **kwargs) -> None:
        if path == temporary:
            raise PermissionError("denied")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", denied_cleanup)
    with pytest.raises(SlideAuthorityPersistenceError, match="cleanup failed"):
        write_or_validate_slide_authority_map(run_dir, authority)
    monkeypatch.setattr(Path, "unlink", real_unlink)

    recovered = write_or_validate_slide_authority_map(run_dir, authority)

    assert read_slide_authority_map(run_dir) == authority
    assert recovered.is_file()
    assert not temporary.exists()


def test_deep_dive_keeps_all_vo_and_groups_delta_once_per_source(
    tmp_path: Path, monkeypatch
) -> None:
    raw, course_root = _fixture(tmp_path)
    authority = _build(raw, course_root)
    run_dir = tmp_path / "run"
    exports = run_dir / "exports"
    exports.mkdir(parents=True)
    manifest_path = exports / "segment-manifest-storyboard-b.yaml"
    manifest_path.write_text(
        yaml.safe_dump({"segments": raw["manifest_segments"]}, sort_keys=False),
        encoding="utf-8",
    )
    authority = _build(
        raw,
        course_root,
        manifest_digest="sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can choose."),),
        known_losses=(),
        marker=None,
    )

    original_safe_read = deep_dive_from_run.read_contained_regular_bytes
    source_reads: list[Path] = []

    def tracked_safe_read(root: Path, path: Path, label: str) -> bytes:
        if path.parent == course_root / "slides":
            source_reads.append(path)
        return original_safe_read(root, path, label=label)

    monkeypatch.setattr(
        "app.marcus.lesson_plan.deep_dive_from_run.read_contained_regular_bytes",
        tracked_safe_read,
    )
    request = build_deep_dive_request(
        run_dir, course_root, promise, authority_map=authority
    )

    assert len([span for span in request.source_spans if span.span_id.startswith("vo:")]) == 13
    assert [
        span.span_id
        for span in request.source_spans
        if span.span_id.startswith("delta:")
    ] == [f"delta:slide-{ordinal}" for ordinal in range(1, 7)]
    assert request.slide_authority_map_digest == authority.map_digest
    assert len(source_reads) == 6

    slide_two = course_root / "slides" / "slide-2-two.md"
    slide_two.write_text(
        slide_two.read_text(encoding="utf-8").replace(
            "source note two", "Narration two. Narration three. Narration four."
        ),
        encoding="utf-8",
    )
    aggregate_equal_authority = _build(
        raw,
        course_root,
        manifest_digest="sha256:"
        + hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    )
    aggregate_equal_request = build_deep_dive_request(
        run_dir,
        course_root,
        promise,
        authority_map=aggregate_equal_authority,
    )
    assert "delta:slide-2" not in {
        span.span_id for span in aggregate_equal_request.source_spans
    }


def test_deep_dive_uses_one_manifest_snapshot_and_revalidates_disk_bytes(
    tmp_path: Path,
) -> None:
    raw, course_root = _fixture(tmp_path)
    run_dir = tmp_path / "run"
    exports = run_dir / "exports"
    exports.mkdir(parents=True)
    manifest_path = exports / "segment-manifest-storyboard-b.yaml"
    original = yaml.safe_dump(
        {"segments": raw["manifest_segments"]}, sort_keys=False
    ).encode()
    manifest_path.write_bytes(original)
    authority = _build(
        raw,
        course_root,
        manifest_digest="sha256:" + hashlib.sha256(original).hexdigest(),
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can choose."),),
        known_losses=(),
        marker=None,
    )
    request = build_deep_dive_request(
        run_dir,
        course_root,
        promise,
        authority_map=authority,
        manifest_bytes=original,
    )
    assert request.source_spans[0].text == "Narration one."
    manifest_path.write_bytes(original.replace(b"Narration one", b"Changed words"))
    with pytest.raises(DeepDiveAuthorityInvalidError, match="manifest digest"):
        build_deep_dive_request(
            run_dir, course_root, promise, authority_map=authority
        )


def test_authenticated_marker_anchor_resolves_against_bundle_not_raw_slides(
    tmp_path: Path,
) -> None:
    """Drift-guard: source_refs carrying Texas ``[evidence: src-NNN]`` markers
    must resolve against the authenticated bundle bodies, not the raw slides.

    This reproduces the live 07W.1 ``deep-dive-authority-invalid`` pause: the raw
    slide never contains the marker, so before the fix the workbook resolver
    (reading raw slides) fails ``anchor must match exactly one source slide
    file`` while Irene Pass-1 (reading the authenticated body) resolves it
    cleanly. Reading the same authenticated bodies removes the divergence.
    """
    from app.specialists.source_bundle import read_extracted_source_sections
    from tests._helpers.pass1_bundle import (
        write_authenticated_slide_bundle_from_course,
    )

    run_dir = tmp_path / "run"
    exports = run_dir / "exports"
    exports.mkdir(parents=True)
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump(
            {"segments": [{"slide_id": "slide-01"}]}, sort_keys=False
        ),
        encoding="utf-8",
    )
    course_root = tmp_path / "course"
    slides = course_root / "slides"
    slides.mkdir(parents=True)
    visual_line = (
        "**Visual Format:** Dual-Axis Data Visualization "
        "(Clean, high-contrast chart)."
    )
    raw_slide = f"# Charts\n{visual_line}\n- **Narration (Speaker Notes):** read it\n"
    (slides / "slide-1-charts.md").write_text(raw_slide, encoding="utf-8")

    # The bundle body carries the marker the raw slide lacks.
    write_authenticated_slide_bundle_from_course(
        run_dir,
        course_root,
        marker_lines={"slide-1-charts.md": visual_line},
    )
    marker_anchor = f"{visual_line} [evidence: src-006]"
    assert marker_anchor not in raw_slide  # verbatim in the body, absent from raw

    sections = read_extracted_source_sections(
        {"bundle_reference": str(run_dir / "bundle")}
    )
    assert any(marker_anchor in section.body for section in sections)

    selected_plan = {
        "plan_units": [
            {
                "unit_id": "u01",
                "scope_decision": "in-scope",
                "cluster_id": "c-u01",
                "cluster_role": "head",
                "parent_slide_id": None,
                "source_refs": [marker_anchor],
            }
        ]
    }
    authority_receipt = finalize_plan_authority(
        selected_plan, source_sections=sections
    )
    (run_dir / "irene-pass1.lesson-plan.json").write_text(
        json.dumps(selected_plan), encoding="utf-8"
    )
    (run_dir / "irene-pass1.plan-authority.json").write_text(
        json.dumps(authority_receipt), encoding="utf-8"
    )
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={
                "lesson_plan": selected_plan,
                "plan_authority_receipt": authority_receipt,
            },
            model_used="fixture",
        )
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output={"slides": [{"slide_id": "slide-01", "source_ref": "u01"}]},
            model_used="fixture",
        )
    )
    envelope = ProductionEnvelope.model_validate_json(envelope.model_dump_json())
    context = WorkbookBriefRuntimeContext(
        run_dir=run_dir,
        course_source_root=course_root,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
    )

    authority, _manifest = workbook_wiring._resolve_slide_authority(
        envelope=envelope, runtime_context=context
    )

    assert authority is not None
    row = authority.rows[0]
    assert row.unit_id == "u01"
    assert row.source_slide_id == "slide-1"
    assert row.matched_anchors == (marker_anchor,)


def test_orchestration_mints_map_from_exact_selected_contributions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, course_root = _fixture(tmp_path)
    run_dir = tmp_path / "run"
    exports = run_dir / "exports"
    exports.mkdir(parents=True)
    (exports / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": raw["manifest_segments"]}, sort_keys=False),
        encoding="utf-8",
    )
    selected_plan = {"plan_units": raw["plan_units"]}
    authority_receipt = finalize_plan_authority(
        selected_plan,
        source_sections=tuple(
            (
                f"slides/{name}|{canonical_source_content_digest(text)}",
                text,
            )
            for name, text in raw["source_slides"].items()
        ),
    )
    (run_dir / "irene-pass1.lesson-plan.json").write_text(
        json.dumps(selected_plan), encoding="utf-8"
    )
    receipt_path = run_dir / "irene-pass1.plan-authority.json"
    receipt_path.write_text(json.dumps(authority_receipt), encoding="utf-8")
    write_authenticated_slide_bundle_from_course(run_dir, course_root)
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={
                "lesson_plan": selected_plan,
                "plan_authority_receipt": authority_receipt,
            },
            model_used="fixture",
        )
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output={"slides": raw["package_slides"]},
            model_used="fixture",
        )
    )
    envelope = ProductionEnvelope.model_validate_json(envelope.model_dump_json())
    context = WorkbookBriefRuntimeContext(
        run_dir=run_dir,
        course_source_root=course_root,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
    )

    authority, manifest_bytes = workbook_wiring._resolve_slide_authority(
        envelope=envelope, runtime_context=context
    )

    assert authority is not None
    assert manifest_bytes == (
        exports / "segment-manifest-storyboard-b.yaml"
    ).read_bytes()
    assert read_slide_authority_map(run_dir) == authority
    repeated, repeated_manifest_bytes = workbook_wiring._resolve_slide_authority(
        envelope=envelope, runtime_context=context
    )
    assert repeated == authority
    assert repeated_manifest_bytes == manifest_bytes

    receipt_path.unlink()
    with pytest.raises(SlideAuthorityInvalidError, match="source authority"):
        workbook_wiring._resolve_slide_authority(
            envelope=envelope, runtime_context=context
        )
    receipt_path.write_text(json.dumps(authority_receipt), encoding="utf-8")

    alternate_raw, alternate_root = _fixture(tmp_path / "alternate")
    alternate_source = alternate_root / "slides" / "slide-1-one.md"
    alternate_source.write_text(
        alternate_source.read_text(encoding="utf-8") + "different snapshot\n",
        encoding="utf-8",
    )
    alternate = _build(alternate_raw, alternate_root)
    real_persist = workbook_wiring.write_or_validate_slide_authority_map

    def substitute_after_validation(run_dir: Path, expected):
        path = real_persist(run_dir, expected)
        path.write_text(alternate.model_dump_json(), encoding="utf-8")
        return path

    monkeypatch.setattr(
        workbook_wiring,
        "write_or_validate_slide_authority_map",
        substitute_after_validation,
    )
    resolved, resolved_manifest = workbook_wiring._resolve_slide_authority(
        envelope=envelope, runtime_context=context
    )
    assert resolved == authority
    assert resolved_manifest == manifest_bytes
    assert read_slide_authority_map(run_dir) == alternate
    with pytest.raises(SlideAuthorityInvalidError, match="stale"):
        workbook_wiring._resolve_slide_authority(
            envelope=envelope, runtime_context=context
        )


def test_partial_exact_contribution_authority_fails_closed(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    envelope = ProductionEnvelope(trial_id=uuid4())
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={"lesson_plan": {"plan_units": []}},
            model_used="fixture",
        )
    )
    context = WorkbookBriefRuntimeContext(
        run_dir=run_dir,
        course_source_root=tmp_path,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
    )
    with pytest.raises(SlideAuthorityInvalidError, match="package_builder@06"):
        workbook_wiring._resolve_slide_authority(
            envelope=envelope, runtime_context=context
        )


def test_current_execution_cannot_fall_back_when_both_contributions_are_absent(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "run.json").write_text("{}", encoding="utf-8")
    context = WorkbookBriefRuntimeContext(
        run_dir=run_dir,
        course_source_root=tmp_path,
        encounter_mode="recorded",
        context_origin="new_start",
        writer_execution_mode="offline_stub",
    )
    envelope = ProductionEnvelope(trial_id=uuid4())

    with pytest.raises(SlideAuthorityInvalidError, match="current execution requires"):
        workbook_wiring._resolve_slide_authority(
            envelope=envelope, runtime_context=context
        )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            node_id="05B",
            output={"lesson_plan": {"plan_units": []}},
            model_used="fixture",
        )
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="package_builder",
            node_id="06",
            output={"slides": []},
            model_used="fixture",
        )
    )
    assert workbook_wiring._resolve_slide_authority(
        envelope=envelope,
        runtime_context=context,
        allow_legacy_absence=True,
    ) == (None, None)
    (run_dir / SLIDE_AUTHORITY_FILENAME).write_text("{}", encoding="utf-8")
    with pytest.raises(SlideAuthorityInvalidError, match="pre-map replay conflicts"):
        workbook_wiring._resolve_slide_authority(
            envelope=envelope,
            runtime_context=context,
            allow_legacy_absence=True,
        )

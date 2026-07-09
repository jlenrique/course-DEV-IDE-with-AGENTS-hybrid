from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.course_source.syllabus_metadata import (
    ExtractedSyllabusDocument,
    ModuleMetadataProposal,
    build_module_metadata_proposal,
    build_module_metadata_proposal_from_document,
    load_extracted_document_yaml,
    read_mhtml_syllabus,
)
from scripts.utilities.extract_syllabus_module_metadata import (
    assert_output_outside_course_root,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "course_source" / "syllabi"
HAI_ROOT = (
    REPO_ROOT / "course-content" / "courses" / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
PHS_ROOT = REPO_ROOT / "course-content" / "courses" / "juan-leon-phs-620-teaching-learning-seminar"


def _assert_anchored_text(value: object) -> None:
    assert value is not None
    assert value.source_ref.path
    assert value.source_ref.locator


def test_hai_fixture_proposal_is_source_anchored_and_uses_existing_module_ids() -> None:
    document = load_extracted_document_yaml(FIXTURES / "hai-510-syllabus-extracted.yaml")
    proposal = build_module_metadata_proposal_from_document(
        HAI_ROOT,
        document,
        expected_learning_objective_count=6,
    )

    assert proposal.extraction_status == "verified"
    assert len(proposal.course_learning_objectives) == 6
    assert len(proposal.modules) == 4
    assert {module.slug_status for module in proposal.modules} == {"existing_aligned"}
    assert [module.proposed_slug.value for module in proposal.modules] == [
        "module-01-foundations-of-ai-in-healthcare",
        "module-02-how-llms-work-and-prompt-engineering",
        "module-03-ethics-and-challenges",
        "module-04-agentic-ai",
    ]
    _assert_anchored_text(proposal.course_title)
    _assert_anchored_text(proposal.learner_profile)
    assert all(objective.source_ref.path for objective in proposal.course_learning_objectives)
    assert all(module.source_refs for module in proposal.modules)


def test_phs_fixture_proposal_yields_15_reviewable_module_records() -> None:
    document = load_extracted_document_yaml(FIXTURES / "phs-620-syllabus-extracted.yaml")
    proposal = build_module_metadata_proposal_from_document(
        PHS_ROOT,
        document,
        expected_learning_objective_count=12,
        required_title="Teaching and Learning Seminar",
    )

    assert proposal.extraction_status == "verified"
    assert proposal.course_title is not None
    assert proposal.course_title.value == "Teaching and Learning Seminar"
    assert len(proposal.course_learning_objectives) == 12
    assert len(proposal.modules) == 15
    assert {module.slug_status for module in proposal.modules} == {"synthesized_requires_review"}
    assert proposal.modules[0].proposed_slug is not None
    assert proposal.modules[0].proposed_slug.value.startswith("module-01-")
    assert "-page-" not in proposal.modules[0].proposed_slug.value
    assert all(module.slug_review_note is not None for module in proposal.modules)
    assert all(module.source_bucket_suggestions for module in proposal.modules)


def test_missing_syllabus_row_yields_missing_module_not_invented_metadata() -> None:
    document = load_extracted_document_yaml(FIXTURES / "phs-620-syllabus-extracted.yaml")
    tables = [list(map(tuple, table)) for table in document.tables]
    calendar_index = next(
        index for index, table in enumerate(tables) if table and "Week/ Module" in table[0][0]
    )
    tables[calendar_index] = tables[calendar_index][:-1]
    truncated = ExtractedSyllabusDocument(
        source_path=document.source_path,
        source_format=document.source_format,
        paragraphs=document.paragraphs,
        tables=tuple(tuple(row for row in table) for table in tables),
    )

    proposal = build_module_metadata_proposal_from_document(
        PHS_ROOT,
        truncated,
        expected_learning_objective_count=12,
        required_title="Teaching and Learning Seminar",
    )

    assert len(proposal.modules) == 15
    missing = proposal.modules[-1]
    assert missing.module_id == "module-15"
    assert missing.status == "missing"
    assert missing.title is None
    assert missing.proposed_slug is None


def test_blank_phs_calendar_row_yields_missing_module_not_fallback_title() -> None:
    document = load_extracted_document_yaml(FIXTURES / "phs-620-syllabus-extracted.yaml")
    tables = [list(map(tuple, table)) for table in document.tables]
    calendar_index = next(
        index
        for index, table in enumerate(tables)
        if table and "Week/ Module" in table[0][0]
    )
    row = list(tables[calendar_index][1])
    row[1:] = [""] * (len(row) - 1)
    tables[calendar_index][1] = tuple(row)
    blank_row = ExtractedSyllabusDocument(
        source_path=document.source_path,
        source_format=document.source_format,
        paragraphs=document.paragraphs,
        tables=tuple(tuple(row for row in table) for table in tables),
    )

    proposal = build_module_metadata_proposal_from_document(
        PHS_ROOT,
        blank_row,
        expected_learning_objective_count=12,
        required_title="Teaching and Learning Seminar",
    )

    assert proposal.modules[0].module_id == "module-01"
    assert proposal.modules[0].status == "missing"
    assert proposal.modules[0].title is None


def test_verified_status_requires_expected_learning_objective_count() -> None:
    hai_document = load_extracted_document_yaml(FIXTURES / "hai-510-syllabus-extracted.yaml")
    hai_reduced = ExtractedSyllabusDocument(
        source_path=hai_document.source_path,
        source_format=hai_document.source_format,
        paragraphs=tuple(
            paragraph
            for paragraph in hai_document.paragraphs
            if "Design and prototype an agentic" not in paragraph
        ),
        tables=hai_document.tables,
    )
    hai_proposal = build_module_metadata_proposal_from_document(
        HAI_ROOT,
        hai_reduced,
        expected_learning_objective_count=6,
    )

    assert hai_proposal.extraction_status == "format_unsupported"
    assert "objective count" in hai_proposal.gaps[0].message

    phs_document = load_extracted_document_yaml(FIXTURES / "phs-620-syllabus-extracted.yaml")
    tables = [list(map(tuple, table)) for table in phs_document.tables]
    objective_index = next(
        index
        for index, table in enumerate(tables)
        if table and table[0][0] == "PLO-01"
    )
    tables[objective_index] = tables[objective_index][:1]
    phs_reduced = ExtractedSyllabusDocument(
        source_path=phs_document.source_path,
        source_format=phs_document.source_format,
        paragraphs=phs_document.paragraphs,
        tables=tuple(tuple(row for row in table) for table in tables),
    )
    phs_proposal = build_module_metadata_proposal_from_document(
        PHS_ROOT,
        phs_reduced,
        expected_learning_objective_count=12,
        required_title="Teaching and Learning Seminar",
    )

    assert phs_proposal.extraction_status == "format_unsupported"
    assert "objective count" in phs_proposal.gaps[0].message


def test_verified_status_requires_required_title_sentinel() -> None:
    document = load_extracted_document_yaml(FIXTURES / "phs-620-syllabus-extracted.yaml")
    proposal = build_module_metadata_proposal_from_document(
        PHS_ROOT,
        document,
        expected_learning_objective_count=12,
        required_title="Wrong Title",
    )

    assert proposal.extraction_status == "format_unsupported"
    assert "title" in proposal.gaps[0].message


def test_corrupted_doc_returns_format_unsupported_gap(tmp_path: Path) -> None:
    corrupt = tmp_path / "corrupt.doc"
    corrupt.write_bytes(b"not a MIME MHTML export")

    proposal = build_module_metadata_proposal(
        PHS_ROOT,
        corrupt,
        expected_learning_objective_count=12,
        required_title="Teaching and Learning Seminar",
    )

    assert proposal.extraction_status == "format_unsupported"
    assert len(proposal.gaps) == 1
    assert proposal.gaps[0].kind == "format_unsupported"


def test_mhtml_suspicious_decode_is_rejected(tmp_path: Path) -> None:
    suspicious = tmp_path / "suspicious.doc"
    suspicious.write_text(
        "\n".join(
            [
                "MIME-Version: 1.0",
                'Content-Type: text/html; charset="utf-8"',
                "",
                "<html><body>Teaching and Learning Seminar Ã Ã Ã</body></html>",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="suspicious text"):
        read_mhtml_syllabus(suspicious)


def test_anchor_models_are_frozen_and_non_empty() -> None:
    document = load_extracted_document_yaml(FIXTURES / "hai-510-syllabus-extracted.yaml")
    proposal = build_module_metadata_proposal_from_document(
        HAI_ROOT,
        document,
        expected_learning_objective_count=6,
    )
    assert proposal.course_title is not None

    with pytest.raises(ValidationError):
        proposal.course_title.source_ref.locator = ""  # type: ignore[misc]


def test_missing_module_records_cannot_carry_proposed_fields() -> None:
    with pytest.raises(ValidationError, match="missing module metadata"):
        ModuleMetadataProposal(
            module_id="module-01",
            status="missing",
            slug_status="missing",
            title={
                "value": "Invented",
                "source_ref": {"path": "fixture.yaml", "locator": "row 1"},
            },
        )


def test_extractor_output_fence_rejects_course_container_target(tmp_path: Path) -> None:
    outside = tmp_path / "proposal.yaml"
    assert_output_outside_course_root(PHS_ROOT, outside)

    with pytest.raises(ValueError, match="outside the course container"):
        assert_output_outside_course_root(PHS_ROOT, PHS_ROOT / "proposal.yaml")


def test_syllabus_metadata_app_code_has_no_seed_course_literals() -> None:
    source = (
        REPO_ROOT
        / "app"
        / "marcus"
        / "course_source"
        / "syllabus_metadata.py"
    ).read_text(encoding="utf-8").lower()

    for literal in (
        "hai-510",
        "phs-620",
        "aziz",
        "juan-leon",
        "teaching and learning seminar",
        "generative ai in healthcare",
    ):
        assert literal not in source

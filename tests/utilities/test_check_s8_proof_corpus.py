from __future__ import annotations

from pathlib import Path

import pytest

import scripts.utilities.check_s8_proof_corpus as s8_preflight
from scripts.utilities.check_s8_proof_corpus import evaluate_s8_proof_corpus


def _candidate_root(tmp_path: Path, slug: str = "healthcare-ai-proof") -> Path:
    root = tmp_path / "course-content" / "courses" / slug
    root.mkdir(parents=True)
    return root


def _write_valid_shape(root: Path) -> None:
    (root / "primary.pdf").write_bytes(b"%PDF-1.4\n")
    (root / "slides.pptx").write_bytes(b"pptx-placeholder")
    (root / "slides").mkdir()
    (root / "references").mkdir()
    (root / "assessments").mkdir()
    images = root / "images"
    images.mkdir()
    (images / "diagram.png").write_bytes(b"png-placeholder")
    (root / "references.md").write_text(
        "Evidence: Example Author. Example Paper. doi:10.1001/example.2026.1\n"
        "URL directive: https://example.edu/source\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Candidate\n", encoding="utf-8")
    (root / "urls.txt").write_text("https://example.edu/source\n", encoding="utf-8")


def _write_gap_ledger_shape(root: Path) -> None:
    (root / "slides").mkdir()
    (root / "references").mkdir()
    (root / "assessments").mkdir()
    (root / "README.md").write_text("# Candidate\n", encoding="utf-8")
    (root / "urls.txt").write_text("https://example.edu/source\n", encoding="utf-8")
    (root / "slides" / "summary.md").write_text("Bridge storyboard.\n", encoding="utf-8")
    (root / "assessments" / "quiz.md").write_text("Assessment source.\n", encoding="utf-8")
    (root / "references" / "source-gap-ledger.md").write_text(
        "No PDF, deck, image, or DOI appears in the source section.\n",
        encoding="utf-8",
    )


def _messages(report) -> list[str]:
    return [finding.message for finding in report.findings]


@pytest.fixture(autouse=True)
def _isolate_from_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(s8_preflight, "_repo_root", lambda _path: None)


def test_valid_candidate_requires_operator_attestations(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path)
    _write_valid_shape(root)

    report = evaluate_s8_proof_corpus(root)

    assert not report.ready
    assert any(
        "Operator-named S8 proof corpus is required" in message
        for message in _messages(report)
    )
    assert any("Operator must attest" in message for message in _messages(report))


def test_valid_candidate_passes_with_required_attestations(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path)
    _write_valid_shape(root)

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="healthcare-ai-proof",
        operator_knows_cold=True,
        fresh_to_pipeline=True,
        adequacy_wrinkle="Source includes an intentionally thin learning objective.",
        no_corpus_specific_diffs_acknowledged=True,
    )

    assert report.ready
    assert report.inventory.pdf_count == 1
    assert report.inventory.doc_or_deck_count == 1
    assert report.inventory.image_count == 1
    assert report.inventory.doi_count == 1


def test_source_gap_exception_passes_with_gap_ledger_and_freshness_rationale(
    tmp_path: Path,
) -> None:
    root = _candidate_root(tmp_path, "tejal-c1m1-p4-assessments-bridge")
    _write_gap_ledger_shape(root)

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="tejal-c1m1-p4-assessments-bridge",
        operator_knows_cold=True,
        freshness_exception_rationale="Only Tejal real content is available.",
        adequacy_wrinkle="Assessment-heavy source should pressure-test gaps.",
        no_corpus_specific_diffs_acknowledged=True,
        allow_tejal_exception=True,
        allow_source_gaps=True,
    )

    assert report.ready
    assert report.inventory.pdf_count == 0
    assert any(
        finding.check_id == "source_gap_ledger" and finding.severity == "pass"
        for finding in report.findings
    )
    assert any(
        finding.check_id == "has_pdf" and finding.severity == "warning"
        for finding in report.findings
    )


def test_source_gap_exception_requires_gap_ledger(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path, "tejal-c1m1-p4-assessments-bridge")
    (root / "slides").mkdir()
    (root / "references").mkdir()
    (root / "assessments").mkdir()
    (root / "README.md").write_text("# Candidate\n", encoding="utf-8")
    (root / "urls.txt").write_text("https://example.edu/source\n", encoding="utf-8")

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="tejal-c1m1-p4-assessments-bridge",
        operator_knows_cold=True,
        freshness_exception_rationale="Only Tejal real content is available.",
        adequacy_wrinkle="Assessment-heavy source should pressure-test gaps.",
        no_corpus_specific_diffs_acknowledged=True,
        allow_tejal_exception=True,
        allow_source_gaps=True,
    )

    assert not report.ready
    assert any("no references/*gap*.md ledger" in message for message in _messages(report))


def test_rejects_nested_path_under_course_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(s8_preflight, "_repo_root", lambda _path: tmp_path)
    root = (
        tmp_path
        / "course-content"
        / "courses"
        / "healthcare-ai-proof"
        / "nested"
    )
    root.mkdir(parents=True)
    _write_valid_shape(root)

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="nested",
        operator_knows_cold=True,
        fresh_to_pipeline=True,
        adequacy_wrinkle="Known adequacy wrinkle.",
        no_corpus_specific_diffs_acknowledged=True,
    )

    assert not report.ready
    assert any(
        "course-content/courses/<lesson_slug>" in message
        for message in _messages(report)
    )


def test_rejects_mismatched_operator_slug(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path, "healthcare-ai-proof")
    _write_valid_shape(root)

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="different-proof",
        operator_knows_cold=True,
        fresh_to_pipeline=True,
        adequacy_wrinkle="Known adequacy wrinkle.",
        no_corpus_specific_diffs_acknowledged=True,
    )

    assert not report.ready
    assert any("does not match corpus slug" in message for message in _messages(report))


def test_rejects_tejal_family_without_exception(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path, "tejal-new-proof")
    _write_valid_shape(root)

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="tejal-new-proof",
        operator_knows_cold=True,
        fresh_to_pipeline=True,
        adequacy_wrinkle="Known adequacy wrinkle.",
        no_corpus_specific_diffs_acknowledged=True,
    )

    assert not report.ready
    assert any("Tejal-family corpus requires explicit" in message for message in _messages(report))


def test_rejects_missing_mixed_source_requirements(tmp_path: Path) -> None:
    root = _candidate_root(tmp_path)
    (root / "references.md").write_text(
        "A DOI exists but no mixed source assets: doi:10.1001/example.2026.1\n",
        encoding="utf-8",
    )

    report = evaluate_s8_proof_corpus(
        root,
        operator_named_slug="healthcare-ai-proof",
        operator_knows_cold=True,
        fresh_to_pipeline=True,
        adequacy_wrinkle="Known adequacy wrinkle.",
        no_corpus_specific_diffs_acknowledged=True,
    )

    assert not report.ready
    messages = _messages(report)
    assert any("At least one PDF source is required" in message for message in messages)
    assert any(
        "At least one DOC/DOCX/PPT/PPTX source is required" in message
        for message in messages
    )
    assert any("At least one image source is required" in message for message in messages)

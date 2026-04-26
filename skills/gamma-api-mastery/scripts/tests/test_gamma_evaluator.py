"""Tests for GammaEvaluator with real PDF comparison."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gamma_evaluator import (
    GammaEvaluator,
    detect_added_tokens,
    detect_emojis,
    normalize_text,
    text_similarity,
)


@pytest.fixture
def evaluator() -> GammaEvaluator:
    return GammaEvaluator()


@pytest.fixture
def l1_brief() -> str:
    return (
        "# Exemplar: Two Processes, One Mind\n\n"
        "## Level: L1 (Simple)\n\n"
        "Single slide. The simplest structural pattern — a parallel comparison layout.\n\n"
        "**Title**: Two Processes, One Mind\n\n"
        "**Left column — Clinical Diagnosis:**\n"
        "- History & Physical\n"
        "**Right column — Design Thinking:**\n"
        "- Empathize with users\n"
    )


@pytest.fixture
def l2_brief() -> str:
    return (
        "# Exemplar: Diagnosis = Innovation\n\n"
        "## Level: L2 (Simple-Moderate)\n\n"
        "Single slide. Text-focused explanatory slide with a bold conceptual headline.\n\n"
        "**Title**: Diagnosis = Innovation\n\n"
        "**Body**: Your clinical training has already prepared you.\n"
    )


class TestNormalizeText:
    def test_removes_emojis(self) -> None:
        assert "clinical diagnosis" in normalize_text("🩺 Clinical Diagnosis")

    def test_removes_standalone_numbers(self) -> None:
        result = normalize_text("01 History 02 Physical")
        assert "01" not in result
        assert "history" in result

    def test_lowercases(self) -> None:
        assert normalize_text("Hello World") == "hello world"


class TestDetectAddedTokens:
    def test_finds_added_words(self) -> None:
        source = "Clinical Diagnosis"
        repro = "Clinical Diagnosis with extra words"
        added = detect_added_tokens(source, repro)
        assert "extra" in added
        assert "words" in added

    def test_no_additions(self) -> None:
        source = "Hello world"
        repro = "Hello world"
        assert detect_added_tokens(source, repro) == []


class TestDetectEmojis:
    def test_finds_emojis(self) -> None:
        result = detect_emojis("🩺 Clinical 💡 Design")
        assert len(result) == 2

    def test_no_emojis(self) -> None:
        assert detect_emojis("Plain text") == []


class TestTextSimilarity:
    def test_identical_texts(self) -> None:
        assert text_similarity("Hello world", "Hello world") == 1.0

    def test_similar_texts(self) -> None:
        sim = text_similarity("Hello world foo", "Hello world bar")
        assert 0.5 < sim < 1.0

    def test_different_texts(self) -> None:
        sim = text_similarity("abc def", "xyz uvw")
        assert sim < 0.3


class TestGammaEvaluatorProperties:
    def test_tool_name(self, evaluator: GammaEvaluator) -> None:
        assert evaluator.tool_name == "gamma"


class TestAnalyzeExemplar:
    def test_detects_parallel_layout(self, evaluator: GammaEvaluator, l1_brief: str) -> None:
        result = evaluator.analyze_exemplar(l1_brief, [])
        assert result["layout_pattern"] == "two-column-parallel"

    def test_detects_title_plus_body(self, evaluator: GammaEvaluator, l2_brief: str) -> None:
        result = evaluator.analyze_exemplar(l2_brief, [])
        assert result["layout_pattern"] == "title-plus-body"

    def test_extracts_title(self, evaluator: GammaEvaluator, l1_brief: str) -> None:
        result = evaluator.analyze_exemplar(l1_brief, [])
        assert result["title"] == "Two Processes, One Mind"

    def test_detects_assessment_type(self, evaluator: GammaEvaluator) -> None:
        brief = "Assessment slide. Comprehension check with categorization."
        result = evaluator.analyze_exemplar(brief, [])
        assert result["pedagogical_type"] == "assessment"


class TestDeriveReproductionSpec:
    def test_uses_preserve_mode(self, evaluator: GammaEvaluator) -> None:
        analysis = {"layout_pattern": "two-column-parallel", "word_count": 100}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert spec["text_mode"] == "preserve"

    def test_includes_rich_visual_instructions(self, evaluator: GammaEvaluator) -> None:
        analysis = {"layout_pattern": "two-column-parallel", "word_count": 100}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert "parallel comparison" in spec["additional_instructions"].lower()
        assert "icons" in spec["additional_instructions"].lower() or "accents" in spec["additional_instructions"].lower()

    def test_does_not_suppress_images_for_rich_content(self, evaluator: GammaEvaluator) -> None:
        analysis = {"layout_pattern": "two-column-parallel", "word_count": 100}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert "image_options" not in spec or spec.get("image_options", {}).get("source") != "noImages"

    def test_exports_pdf(self, evaluator: GammaEvaluator) -> None:
        analysis = {"layout_pattern": "title-plus-body", "word_count": 30}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert spec["export_as"] == "pdf"


class TestCompareReproduction:
    def test_failed_reproduction_scores_zero(self, evaluator: GammaEvaluator) -> None:
        result = evaluator.compare_reproduction(
            [], {"status": "error", "error": "API timeout"}, {}
        )
        for dim in result["scores"].values():
            assert dim["score"] == 0

    def test_good_reproduction_scores_high(self, evaluator: GammaEvaluator, tmp_path: Path) -> None:
        # Create a "source" PDF-like text
        source_text = "Two Processes One Mind\nClinical Diagnosis\nDesign Thinking"
        # Create a "reproduction" that matches well
        artifact = tmp_path / "repro.pdf"
        artifact.write_bytes(b"x" * 30000)  # 30KB = visually rich

        output = {
            "status": "completed",
            "output": {"gammaUrl": "https://gamma.app/docs/test"},
            "artifact_path": str(artifact),
            "api_interaction": {
                "parameters": {
                    "num_cards": 1,
                    "additional_instructions": "Two-column parallel comparison",
                    "export_as": "pdf",
                    "format": "presentation",
                }
            },
        }
        analysis = {
            "layout_pattern": "two-column-parallel",
            "pedagogical_type": "content-delivery",
            "title": "Two Processes One Mind",
            "source_text": source_text,
        }

        with patch("gamma_evaluator.extract_pdf_text", return_value=source_text):
            result = evaluator.compare_reproduction([], output, analysis)

        assert result["scores"]["structural_fidelity"]["score"] >= 4
        assert result["scores"]["content_completeness"]["score"] >= 4

    def test_poor_reproduction_scores_low(self, evaluator: GammaEvaluator, tmp_path: Path) -> None:
        artifact = tmp_path / "repro.pdf"
        artifact.write_bytes(b"x" * 5000)  # 5KB = visually sparse

        output = {
            "status": "completed",
            "output": {"gammaUrl": "https://gamma.app/docs/test"},
            "artifact_path": str(artifact),
            "api_interaction": {
                "parameters": {
                    "num_cards": 1,
                    "additional_instructions": "test",
                    "export_as": "pdf",
                    "format": "presentation",
                }
            },
        }
        analysis = {
            "layout_pattern": "two-column-parallel",
            "pedagogical_type": "content-delivery",
            "title": "Two Processes One Mind",
            "source_text": "Two Processes One Mind\nClinical Diagnosis\nDesign Thinking\nHistory Physical",
        }

        with patch("gamma_evaluator.extract_pdf_text", return_value="Something completely different"):
            result = evaluator.compare_reproduction([], output, analysis)

        assert result["scores"]["structural_fidelity"]["score"] <= 3
        assert result["scores"]["content_completeness"]["score"] <= 2

    def test_detects_embellishment(self, evaluator: GammaEvaluator, tmp_path: Path) -> None:
        artifact = tmp_path / "repro.pdf"
        artifact.write_bytes(b"x" * 20000)

        output = {
            "status": "completed",
            "artifact_path": str(artifact),
            "api_interaction": {"parameters": {}},
        }
        analysis = {
            "source_text": "Clinical Diagnosis",
            "title": "Test",
        }

        with patch("gamma_evaluator.extract_pdf_text", return_value="🩺 Clinical Diagnosis with extras"):
            result = evaluator.compare_reproduction([], output, analysis)

        assert result["embellishment"]["detected"] is True
        assert len(result["embellishment"]["emojis"]) > 0


class TestGetCustomRubricWeights:
    def test_l1_weights(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L1")
        assert weights["structural_fidelity"] == "high"
        assert weights["content_completeness"] == "high"

    def test_l4_weights(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L4")
        assert weights["context_alignment"] == "high"
        assert weights["creative_quality"] == "medium"

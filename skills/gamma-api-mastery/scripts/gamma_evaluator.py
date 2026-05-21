"""Gamma-specific exemplar evaluator.

Extends BaseEvaluator from the woodshed skill to provide Gamma-specific
analysis, reproduction, and comparison logic. The evaluator reverse-engineers
source exemplar PDFs to understand their visual structure, then translates
that understanding into Gamma API instructions that recreate the visual intent.
"""

from __future__ import annotations

import importlib.util
import logging
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_gamma_ops_mod = _load_module(
    "gamma_operations",
    str(Path(__file__).resolve().parent / "gamma_operations.py"),
)
download_export = _gamma_ops_mod.download_export
generate_slide = _gamma_ops_mod.generate_slide
execute_generation = _gamma_ops_mod.execute_generation
load_style_guide_gamma = _gamma_ops_mod.load_style_guide_gamma

_woodshed_mod = _load_module(
    "woodshed_base",
    str(_PROJECT_ROOT / "skills" / "woodshed" / "scripts" / "woodshed_base.py"),
)
BaseEvaluator = _woodshed_mod.BaseEvaluator

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text content from a PDF file."""
    try:
        import pymupdf
    except ImportError:
        logger.warning("pymupdf not available; returning empty text")
        return ""
    doc = pymupdf.open(str(pdf_path))
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip extra whitespace, remove emojis."""
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff\U0001f900-\U0001f9ff"
        "\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff"
        "\u2600-\u26ff\u2700-\u27bf]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)
    text = re.sub(r"\b\d{2}\b", "", text)  # remove standalone 2-digit numbers (01-99)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def detect_added_tokens(source_text: str, repro_text: str) -> list[str]:
    """Find tokens in the reproduction that aren't in the source."""
    source_words = set(normalize_text(source_text).split())
    repro_words = normalize_text(repro_text).split()
    added = []
    for word in repro_words:
        if word not in source_words and len(word) > 1:
            added.append(word)
    return list(set(added))


def detect_emojis(text: str) -> list[str]:
    """Find emoji characters in text."""
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff\U0001f900-\U0001f9ff"
        "\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff"
        "\u2600-\u26ff\u2700-\u27bf]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.findall(text)


def text_similarity(source: str, repro: str) -> float:
    """Compute similarity ratio between normalized texts (0.0-1.0)."""
    s = normalize_text(source)
    r = normalize_text(repro)
    return SequenceMatcher(None, s, r).ratio()


VISUAL_INSTRUCTIONS = {
    "two-column-parallel": (
        "Create a visually striking two-column parallel comparison slide. "
        "Each column should have a clear header and a vertical list of process steps below it. "
        "Use clean icons or visual accents for each column header to distinguish the two processes. "
        "Include a unifying conclusion statement at the bottom that connects both sides. "
        "Professional medical education aesthetic — clean, balanced, equal visual weight on both columns."
    ),
    "title-plus-body": (
        "Create a bold, impactful single-focus slide. "
        "The title should be the dominant visual element — large, provocative, attention-grabbing. "
        "The supporting paragraph should be smaller, underneath, providing context. "
        "Clean, minimal layout with strong visual hierarchy. "
        "Professional medical education aesthetic — confident, not cluttered."
    ),
    "three-column-cards": (
        "Create a three-column card layout slide. "
        "Each card should have a heading and a one-line description below it. "
        "All three cards should be visually balanced — equal width, equal visual weight. "
        "Use subtle visual accents or icons for each card header. "
        "Professional medical education aesthetic — scannable, structured, clean."
    ),
    "assessment-interactive": (
        "Create an interactive assessment slide. "
        "The question prompt should be visually prominent at the top. "
        "Answer options or categorization items should be clearly separated below. "
        "This is a pedagogical assessment slide — it should feel like an activity, not a content slide. "
        "Use visual cues that invite engagement — checkboxes, cards, or categorization zones."
    ),
    "narrative-progression": (
        "Create a three-beat progressive narrative slide. "
        "Each beat should convey forward momentum — past to present to future. "
        "The visual layout should show progression — left to right or top to bottom with escalating energy. "
        "This is a STORY with rising energy, not three equal sections. "
        "Professional medical education aesthetic — motivational, forward-looking."
    ),
}

LEVEL_RUBRIC_WEIGHTS: dict[str, dict[str, str]] = {
    "L1": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "high",
        "context_alignment": "medium",
        "creative_quality": "low",
    },
    "L2": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "high",
        "context_alignment": "medium",
        "creative_quality": "low",
    },
    "L3": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "high",
        "context_alignment": "medium",
        "creative_quality": "medium",
    },
    "L4": {
        "structural_fidelity": "high",
        "parameter_accuracy": "medium",
        "content_completeness": "high",
        "context_alignment": "high",
        "creative_quality": "medium",
    },
}


class GammaEvaluator(BaseEvaluator):
    """Gamma-specific evaluator for slide exemplar mastery.

    The evaluator reverse-engineers source exemplar PDFs: extracts text,
    identifies visual structure (columns, cards, progression), and crafts
    Gamma API instructions that communicate the visual INTENT — guiding
    Gamma to recreate the slide's spirit rather than suppressing its
    visual intelligence.
    """

    @property
    def tool_name(self) -> str:
        return "gamma"

    def analyze_exemplar(
        self, brief: str, source_artifacts: list[Path]
    ) -> dict[str, Any]:
        """Extract layout pattern, content structure, and source text from brief and PDF."""
        analysis: dict[str, Any] = {
            "layout_pattern": None,
            "content_sections": [],
            "pedagogical_type": None,
            "title": None,
            "source_text": "",
            "section_count": 0,
            "has_visual_accents": False,
            "word_count": 0,
        }

        # Extract source PDF text if available
        for artifact in source_artifacts:
            if artifact.suffix.lower() == ".pdf":
                analysis["source_text"] = extract_pdf_text(artifact)
                break

        # Detect layout from brief
        layout_markers = {
            "parallel": "two-column-parallel",
            "two-column": "two-column-parallel",
            "comparison": "two-column-parallel",
            "title-plus-body": "title-plus-body",
            "bold headline": "title-plus-body",
            "bold conceptual headline": "title-plus-body",
            "single-focus": "title-plus-body",
            "explanatory slide": "title-plus-body",
            "three-column": "three-column-cards",
            "card layout": "three-column-cards",
            "feature cards": "three-column-cards",
            "assessment": "assessment-interactive",
            "comprehension check": "assessment-interactive",
            "categorization": "assessment-interactive",
            "narrative": "narrative-progression",
            "story arc": "narrative-progression",
            "three-beat": "narrative-progression",
            "progression": "narrative-progression",
        }

        brief_lower = brief.lower()
        for marker, pattern in layout_markers.items():
            if marker in brief_lower:
                analysis["layout_pattern"] = pattern
                break

        # Extract title
        title_match = re.search(r"\*\*Title\*\*:\s*(.+)", brief)
        if title_match:
            analysis["title"] = title_match.group(1).strip()

        # Count content sections
        section_headers = re.findall(
            r"\*\*(?:Section|Beat|Left|Right|Body|Prompt|column)[^*]*\*\*",
            brief, re.IGNORECASE,
        )
        analysis["content_sections"] = section_headers
        analysis["section_count"] = max(len(section_headers), 1)

        # Detect pedagogical type
        ped_markers = {
            "assessment": "assessment",
            "comprehension": "assessment",
            "quiz": "assessment",
            "narrative": "narrative",
            "story": "narrative",
            "motivational": "narrative",
            "comparison": "content-delivery",
            "lecture": "content-delivery",
            "synthesis": "synthesis",
            "conclusion": "synthesis",
        }
        for marker, ped_type in ped_markers.items():
            if marker in brief_lower:
                analysis["pedagogical_type"] = ped_type
                break
        if analysis["pedagogical_type"] is None:
            analysis["pedagogical_type"] = "content-delivery"

        source = analysis["source_text"] or brief
        analysis["word_count"] = len(source.split())

        return analysis

    def derive_reproduction_spec(
        self,
        analysis: dict[str, Any],
        style_guide: dict[str, Any],
    ) -> dict[str, Any]:
        """Reverse-engineer the source into Gamma API parameters.

        Crafts rich additionalInstructions that communicate the visual
        INTENT of the source slide, guiding Gamma to recreate its spirit
        rather than producing bare text.
        """
        layout = analysis.get("layout_pattern", "title-plus-body")
        visual_instruction = VISUAL_INSTRUCTIONS.get(
            layout, VISUAL_INSTRUCTIONS["title-plus-body"]
        )

        # preserve keeps the exact text; additionalInstructions guides
        # visual treatment without suppressing Gamma's design intelligence
        spec: dict[str, Any] = {
            "input_text": "",
            "text_mode": "preserve",
            "format": "presentation",
            "num_cards": 1,
            "additional_instructions": visual_instruction,
            "export_as": "pdf",
        }
        # else: let Gamma choose (default aiGenerated or themeAccent)

        if style_guide.get("theme_id"):
            spec["theme_id"] = style_guide["theme_id"]

        if analysis.get("pedagogical_type") == "assessment" or layout == "title-plus-body":
            spec["text_options"] = {"amount": "brief"}

        return spec

    def execute_reproduction(
        self,
        spec: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute reproduction via GammaClient through gamma_operations."""
        result: dict[str, Any] = {
            "output": None,
            "api_interaction": {},
            "status": "error",
            "error": None,
            "artifact_path": None,
        }

        try:
            params = dict(spec)
            completed = generate_slide(params)
            result["output"] = completed
            result["api_interaction"] = {
                "endpoint": "POST /v1.0/generations",
                "parameters": spec,
                "generation_id": completed.get("generationId", ""),
                "gamma_url": completed.get("gammaUrl", ""),
            }

            export_url = completed.get("exportUrl")
            if export_url:
                artifact_path = download_export(export_url)
                result["artifact_path"] = str(artifact_path)
                result["api_interaction"]["export_url"] = export_url
                result["api_interaction"]["artifact_path"] = str(artifact_path)

            result["status"] = "completed"

        except Exception as exc:
            result["error"] = str(exc)
            logger.error("Reproduction failed: %s", exc)

        return result

    def compare_reproduction(
        self,
        source_artifacts: list[Path],
        reproduction_output: dict[str, Any],
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Compare reproduction against source using real PDF text extraction."""
        scores: dict[str, dict[str, Any]] = {}

        if reproduction_output.get("status") != "completed":
            return {
                "scores": {
                    dim: {"score": 0, "notes": "Reproduction failed"}
                    for dim in [
                        "structural_fidelity", "parameter_accuracy",
                        "content_completeness", "context_alignment",
                        "creative_quality",
                    ]
                },
                "conclusion": f"Reproduction failed: {reproduction_output.get('error', 'unknown')}",
                "embellishment": {"detected": False, "items": []},
            }

        # Extract text from source and reproduction PDFs
        source_text = analysis.get("source_text", "")
        if not source_text:
            for artifact in source_artifacts:
                if artifact.suffix.lower() == ".pdf":
                    source_text = extract_pdf_text(artifact)
                    break

        repro_text = ""
        artifact_path = reproduction_output.get("artifact_path", "")
        if artifact_path and Path(artifact_path).exists():
            repro_text = extract_pdf_text(Path(artifact_path))

        # --- STRUCTURAL FIDELITY: Is the source content present AND is the layout right? ---
        # This measures whether the reproduction CONTAINS the source content
        # (not exact match — Gamma may enhance with sub-descriptions, accents, etc.)
        similarity = text_similarity(source_text, repro_text) if source_text and repro_text else 0.0
        source_lines = [l.strip() for l in source_text.splitlines() if l.strip()]
        repro_lines = [l.strip() for l in repro_text.splitlines() if l.strip()]
        repro_lower = repro_text.lower()

        title = analysis.get("title", "")
        # Handle line breaks in PDF text extraction (title may wrap across lines)
        repro_collapsed = re.sub(r"\s+", " ", repro_text).lower()
        title_present = title.lower() in repro_collapsed if title else True

        # Check source key words/phrases are present in reproduction
        source_key_words = set(normalize_text(source_text).split())
        repro_words_set = set(normalize_text(repro_text).split())
        if source_key_words:
            word_coverage = len(source_key_words & repro_words_set) / len(source_key_words)
        else:
            word_coverage = 0.0

        struct_score = 1
        if not repro_text:
            struct_score = 0
        elif word_coverage >= 0.85 and title_present:
            struct_score = 5
        elif word_coverage >= 0.7 and title_present:
            struct_score = 4
        elif word_coverage >= 0.5 and title_present:
            struct_score = 3
        elif title_present:
            struct_score = 2

        scores["structural_fidelity"] = {
            "score": struct_score,
            "notes": (
                f"Source word coverage: {word_coverage:.0%}. "
                f"Title present: {title_present}. "
                f"Text similarity: {similarity:.2f}. "
                f"Source lines: {len(source_lines)}, Repro lines: {len(repro_lines)}."
            ),
        }

        # --- CONTENT COMPLETENESS: Are all source KEY PHRASES present? ---
        source_norm = normalize_text(source_text)
        repro_norm = normalize_text(repro_text)
        source_key_phrases = [
            normalize_text(line) for line in source_lines
            if len(line.split()) >= 2
        ]

        # Use word-level containment: check if key words from each phrase appear
        phrases_found = 0
        missing_phrases = []
        for phrase in source_key_phrases:
            phrase_words = set(phrase.split())
            if len(phrase_words) <= 1:
                continue
            matched_words = phrase_words & repro_words_set
            if len(matched_words) / len(phrase_words) >= 0.6:
                phrases_found += 1
            else:
                missing_phrases.append(phrase)

        phrase_count = len(source_key_phrases) if source_key_phrases else 1
        phrase_ratio = phrases_found / phrase_count

        completeness_score = 1
        if phrase_ratio >= 0.9:
            completeness_score = 5
        elif phrase_ratio >= 0.7:
            completeness_score = 4
        elif phrase_ratio >= 0.5:
            completeness_score = 3
        elif phrase_ratio >= 0.3:
            completeness_score = 2

        scores["content_completeness"] = {
            "score": completeness_score,
            "notes": (
                f"Key phrases covered: {phrases_found}/{phrase_count} "
                f"({phrase_ratio:.0%}). "
                f"Missing: {missing_phrases[:3] if missing_phrases else 'none'}."
            ),
        }

        # --- PARAMETER ACCURACY: Were the right API params used? ---
        api_params = reproduction_output.get("api_interaction", {}).get("parameters", {})
        param_checks = [
            api_params.get("num_cards") == 1 or api_params.get("numCards") == 1,
            bool(api_params.get("additional_instructions") or api_params.get("additionalInstructions")),
            api_params.get("export_as") == "pdf" or api_params.get("exportAs") == "pdf",
            api_params.get("format") == "presentation",
        ]
        param_score = sum(param_checks) + 1
        scores["parameter_accuracy"] = {
            "score": min(param_score, 5),
            "notes": f"{sum(param_checks)}/4 key parameters correctly set.",
        }

        # --- CONTEXT ALIGNMENT: Does the slide serve the pedagogical purpose? ---
        ped_type = analysis.get("pedagogical_type", "unknown")
        context_score = 3
        if title_present and phrase_ratio >= 0.5:
            context_score = 4
        if title_present and phrase_ratio >= 0.7 and similarity >= 0.5:
            context_score = 5

        scores["context_alignment"] = {
            "score": context_score,
            "notes": f"Pedagogical type: {ped_type}. Title+content alignment: {phrase_ratio:.0%}.",
        }

        # --- CREATIVE QUALITY: Visual richness relative to source ---
        file_size = 0
        if artifact_path and Path(artifact_path).exists():
            file_size = Path(artifact_path).stat().st_size

        # A visually rich Gamma PDF is typically >20KB for a single slide
        # A bare text-only PDF is typically <15KB
        creative_score = 2
        if file_size > 50_000:
            creative_score = 5
        elif file_size > 25_000:
            creative_score = 4
        elif file_size > 15_000:
            creative_score = 3

        scores["creative_quality"] = {
            "score": creative_score,
            "notes": (
                f"File size: {file_size:,} bytes. "
                f"{'Visually rich' if file_size > 25000 else 'Visually sparse — Gamma may need richer instructions'}."
            ),
        }

        # --- EMBELLISHMENT DETECTION ---
        added_tokens = detect_added_tokens(source_text, repro_text)
        emojis_found = detect_emojis(repro_text)

        embellishment = {
            "detected": bool(added_tokens or emojis_found),
            "added_tokens": added_tokens[:10],
            "emojis": emojis_found,
            "severity": "none",
        }
        if emojis_found:
            embellishment["severity"] = "medium"
        if len(added_tokens) > 5:
            embellishment["severity"] = "high"

        # Build conclusion
        conclusion_parts = [
            f"Layout: {analysis.get('layout_pattern', 'unknown')}",
            f"Similarity: {similarity:.2f}",
            f"Content coverage: {phrase_ratio:.0%}",
            f"File size: {file_size:,}B",
            f"Embellishment: {embellishment['severity']}",
        ]
        if missing_phrases:
            conclusion_parts.append(f"Missing: {', '.join(missing_phrases[:3])}")

        return {
            "scores": scores,
            "conclusion": ". ".join(conclusion_parts),
            "embellishment": embellishment,
            "details": {
                "text_similarity": similarity,
                "phrase_coverage": phrase_ratio,
                "source_word_count": len(source_text.split()),
                "repro_word_count": len(repro_text.split()),
                "file_size_bytes": file_size,
            },
        }

    def get_custom_rubric_weights(self, level: str) -> dict[str, str]:
        base_level = re.match(r"L\d+", level)
        if base_level:
            key = base_level.group(0)
            if key in LEVEL_RUBRIC_WEIGHTS:
                return LEVEL_RUBRIC_WEIGHTS[key]
        return super().get_custom_rubric_weights(level)

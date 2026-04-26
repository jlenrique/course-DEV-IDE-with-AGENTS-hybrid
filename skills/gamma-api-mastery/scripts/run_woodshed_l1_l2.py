r"""Woodshed runner for L1 and L2 exemplar faithful reproduction.

Executes the study → reproduce → compare workflow for Gamma exemplars
using the GammaEvaluator. Downloads PDF artifacts and saves full run logs.

Usage:
    .venv\Scripts\python skills/gamma-api-mastery/scripts/run_woodshed_l1_l2.py
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

load_dotenv(_PROJECT_ROOT / ".env")

from gamma_evaluator import GammaEvaluator
from gamma_operations import load_style_guide_gamma

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXEMPLARS_DIR = _PROJECT_ROOT / "resources" / "exemplars" / "gamma"


def run_exemplar(exemplar_id: str, evaluator: GammaEvaluator) -> dict:
    """Run the full woodshed workflow for one exemplar."""
    exemplar_dir = EXEMPLARS_DIR / exemplar_id
    brief_path = exemplar_dir / "brief.md"

    if not brief_path.exists():
        return {"exemplar_id": exemplar_id, "status": "error", "error": "brief.md not found"}

    brief = brief_path.read_text(encoding="utf-8")
    source_dir = exemplar_dir / "source"
    source_artifacts = list(source_dir.iterdir()) if source_dir.exists() else []

    logger.info("=== Studying exemplar: %s ===", exemplar_id)
    analysis = evaluator.analyze_exemplar(brief, source_artifacts)
    logger.info("Layout pattern: %s", analysis.get("layout_pattern"))
    logger.info("Pedagogical type: %s", analysis.get("pedagogical_type"))
    logger.info("Title: %s", analysis.get("title"))

    style_guide = load_style_guide_gamma()
    spec = evaluator.derive_reproduction_spec(analysis, style_guide)

    # Rich input text that communicates the slide's intent and content,
    # giving Gamma the material to create a visually engaging slide.
    # The additionalInstructions (from derive_reproduction_spec) guides
    # the visual layout; the inputText provides the content and context.
    content_sections = {
        "L1-two-processes-one-mind": (
            "Two Processes, One Mind\n\n"
            "This slide compares two parallel processes side by side to show "
            "that clinical diagnosis and design thinking share the same cognitive pattern.\n\n"
            "Clinical Diagnosis process:\n"
            "- History & Physical\n"
            "- Form hypothesis\n"
            "- Order labs & imaging\n"
            "- Iterate until diagnosis\n\n"
            "Design Thinking process:\n"
            "- Empathize with users\n"
            "- Define the problem\n"
            "- Ideate solutions\n"
            "- Prototype & test\n\n"
            "Unifying insight: Both require rapid hypothesis formation, "
            "experimentation, and iteration to find root causes."
        ),
        "L2-diagnosis-innovation": (
            "Diagnosis = Innovation\n\n"
            "A bold, provocative statement that reframes what physicians already do "
            "as innovation.\n\n"
            "Your clinical training has already prepared you to be an innovator. "
            "The process you use every day mirrors the innovation process exactly."
        ),
    }

    spec["input_text"] = content_sections.get(exemplar_id, "")
    if not spec["input_text"]:
        return {"exemplar_id": exemplar_id, "status": "error", "error": "No content mapping"}

    logger.info("=== Reproducing exemplar: %s ===", exemplar_id)
    logger.info("Parameters: numCards=%s, textMode=%s, exportAs=%s",
                spec.get("num_cards"), spec.get("text_mode"), spec.get("export_as"))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    attempt_dir = exemplar_dir / "reproductions" / timestamp
    output_dir = attempt_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    spec_for_api = dict(spec)
    result = evaluator.execute_reproduction(spec_for_api)

    if result.get("artifact_path"):
        src_path = Path(result["artifact_path"])
        if src_path.exists():
            dest_path = output_dir / src_path.name
            dest_path.write_bytes(src_path.read_bytes())
            result["artifact_path"] = str(dest_path)
            logger.info("Artifact saved: %s (%d bytes)", dest_path, dest_path.stat().st_size)

    run_log = {
        "exemplar_id": exemplar_id,
        "timestamp": timestamp,
        "analysis": analysis,
        "reproduction_spec": spec,
        "api_interaction": result.get("api_interaction", {}),
        "status": result.get("status"),
        "error": result.get("error"),
        "artifact_path": result.get("artifact_path"),
    }
    run_log_path = attempt_dir / "run-log.yaml"
    run_log_path.write_text(
        yaml.dump(run_log, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    logger.info("Run log saved: %s", run_log_path)

    logger.info("=== Comparing reproduction: %s ===", exemplar_id)
    comparison = evaluator.compare_reproduction(source_artifacts, result, analysis)

    from skills.woodshed.scripts.woodshed_base import evaluate_pass_fail
    pass_fail = evaluate_pass_fail(comparison["scores"])

    comparison_data = {
        "exemplar_id": exemplar_id,
        "timestamp": timestamp,
        "scores": comparison["scores"],
        "conclusion": comparison["conclusion"],
        "pass_fail": pass_fail,
    }
    comparison_path = attempt_dir / "comparison.yaml"
    comparison_path.write_text(
        yaml.dump(comparison_data, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    logger.info("Comparison saved: %s", comparison_path)
    logger.info("Result: %s — %s", pass_fail["result"], pass_fail["reason"])

    return {
        "exemplar_id": exemplar_id,
        "status": result.get("status"),
        "pass_fail": pass_fail,
        "artifact_path": result.get("artifact_path"),
        "attempt_dir": str(attempt_dir),
        "scores": {k: v["score"] for k, v in comparison["scores"].items()},
    }


def main() -> None:
    evaluator = GammaEvaluator()

    results = []
    for exemplar_id in ["L1-two-processes-one-mind", "L2-diagnosis-innovation"]:
        result = run_exemplar(exemplar_id, evaluator)
        results.append(result)
        logger.info("")

    logger.info("=== WOODSHED SUMMARY ===")
    for r in results:
        status = r.get("pass_fail", {}).get("result", r.get("status", "unknown"))
        logger.info("%s: %s", r["exemplar_id"], status)
        if r.get("scores"):
            for dim, score in r["scores"].items():
                logger.info("  %s: %d/5", dim, score)

    all_passed = all(
        r.get("pass_fail", {}).get("result") in ("pass", "conditional_pass")
        for r in results
    )
    logger.info("\nOverall: %s", "ALL PASSED" if all_passed else "SOME FAILED")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

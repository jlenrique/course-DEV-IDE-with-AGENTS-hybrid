"""Common base classes for the woodshed exemplar mastery system.

The woodshed owns the PROCESS (study, reproduce, compare, reflect, regress).
Each specialist agent's mastery skill owns the EVALUATION INTELLIGENCE
(what constitutes "good" for that artifact type, what API calls to make,
what rubric dimensions to weight).

This module provides:
- BaseEvaluator: abstract base that each mastery skill implements
- WoodshedRunner: orchestrates the workflow using any evaluator
- Shared data structures for run logs, comparisons, catalogs
"""

from __future__ import annotations

import abc
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXEMPLARS_DIR = PROJECT_ROOT / "resources" / "exemplars"

CIRCUIT_BREAKER_DEFAULTS = {
    "max_attempts_per_session": 3,
    "max_total_attempts": 7,
    "max_consecutive_no_improvement": 2,
}

RUBRIC_DIMENSIONS = [
    "structural_fidelity",
    "parameter_accuracy",
    "content_completeness",
    "context_alignment",
    "creative_quality",
]

HIGH_WEIGHT_DIMENSIONS = ["structural_fidelity", "parameter_accuracy"]


class BaseEvaluator(abc.ABC):
    """Abstract base for agent-specific exemplar evaluation.

    Each specialist agent's mastery skill provides a concrete evaluator
    that knows how to analyze, reproduce, and compare artifacts of that
    type. The woodshed runner delegates to the evaluator for all
    tool-specific decisions.
    """

    @property
    @abc.abstractmethod
    def tool_name(self) -> str:
        """Tool identifier (gamma, elevenlabs, canvas, etc.)."""

    @abc.abstractmethod
    def analyze_exemplar(
        self, brief: str, source_artifacts: list[Path]
    ) -> dict[str, Any]:
        """Analyze an exemplar's brief and source to extract key attributes.

        Returns a dict of attributes the agent identified as essential
        for reproduction (layout pattern, content structure, parameter
        choices, etc.). These attributes become the basis for the
        reproduction spec and later comparison.
        """

    @abc.abstractmethod
    def derive_reproduction_spec(
        self,
        analysis: dict[str, Any],
        style_guide: dict[str, Any],
    ) -> dict[str, Any]:
        """Derive the reproduction-spec.yaml from exemplar analysis.

        Combines the analyzed attributes with style guide defaults to
        produce the exact API parameters for reproduction.
        """

    @abc.abstractmethod
    def execute_reproduction(
        self,
        spec: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the reproduction via the tool's API/MCP.

        Returns a dict with:
        - 'output': the produced artifact data (response, URL, file, etc.)
        - 'api_interaction': detailed log of the exact call made
        - 'status': 'completed' | 'error'
        - 'error': error message if status is 'error'
        """

    @abc.abstractmethod
    def compare_reproduction(
        self,
        source_artifacts: list[Path],
        reproduction_output: dict[str, Any],
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Compare a reproduction against the original source.

        Returns rubric scores and a plain-language conclusion. The
        evaluator applies tool-specific comparison logic (e.g., for Gamma:
        slide count, layout pattern, content flow; for ElevenLabs: audio
        duration, voice match, pronunciation accuracy).

        Must return a dict with at minimum:
        - 'scores': dict of dimension_name -> {'score': int, 'notes': str}
        - 'conclusion': str (plain-language summary)
        """

    def get_custom_rubric_weights(self, level: str) -> dict[str, str]:
        """Override rubric dimension weights for this tool/level.

        Returns a dict of dimension_name -> weight ('high', 'medium', 'low').
        Default implementation uses the standard weights. Override in
        subclasses to adjust for tool-specific priorities.
        """
        return {
            "structural_fidelity": "high",
            "parameter_accuracy": "high",
            "content_completeness": "medium",
            "context_alignment": "medium",
            "creative_quality": "low",
        }


def load_catalog(tool: str) -> dict:
    """Load a tool's exemplar catalog."""
    catalog_path = EXEMPLARS_DIR / tool / "_catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"No _catalog.yaml for tool: {tool}")
    return yaml.safe_load(catalog_path.read_text(encoding="utf-8"))


def save_catalog(tool: str, catalog: dict) -> None:
    """Save a tool's exemplar catalog."""
    catalog_path = EXEMPLARS_DIR / tool / "_catalog.yaml"
    catalog_path.write_text(
        yaml.dump(catalog, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def get_exemplar_dir(tool: str, exemplar_id: str) -> Path:
    """Get the directory for a specific exemplar."""
    return EXEMPLARS_DIR / tool / exemplar_id


def count_attempts(tool: str, exemplar_id: str) -> int:
    """Count total reproduction attempts for an exemplar."""
    reproductions_dir = get_exemplar_dir(tool, exemplar_id) / "reproductions"
    if not reproductions_dir.exists():
        return 0
    return sum(1 for d in reproductions_dir.iterdir() if d.is_dir())


def create_attempt_dir(tool: str, exemplar_id: str) -> Path:
    """Create a timestamped attempt directory."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    attempt_dir = (
        get_exemplar_dir(tool, exemplar_id) / "reproductions" / timestamp
    )
    output_dir = attempt_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return attempt_dir


def check_circuit_breaker(
    tool: str,
    exemplar_id: str,
    session_attempt: int,
    catalog: dict | None = None,
) -> dict | None:
    """Check if circuit breaker limits have been reached.

    Returns None if OK to proceed, or a dict describing which limit was hit.
    """
    if catalog is None:
        catalog = load_catalog(tool)

    limits = catalog.get("circuit_breaker", CIRCUIT_BREAKER_DEFAULTS)
    total = count_attempts(tool, exemplar_id)

    if session_attempt > limits.get(
        "max_attempts_per_session",
        CIRCUIT_BREAKER_DEFAULTS["max_attempts_per_session"],
    ):
        return {
            "limit": "max_attempts_per_session",
            "message": "Session attempt limit reached. Stop and produce failure report.",
        }

    max_total = limits.get(
        "max_total_attempts", CIRCUIT_BREAKER_DEFAULTS["max_total_attempts"]
    )
    if total >= max_total:
        return {
            "limit": "max_total_attempts",
            "message": f"Total attempt limit reached ({max_total}). Produce failure report.",
        }

    return None


def evaluate_pass_fail(scores: dict[str, dict]) -> dict:
    """Apply rubric pass/fail rules to scored dimensions."""
    high_scores = [
        scores[d]["score"] for d in HIGH_WEIGHT_DIMENSIONS if d in scores
    ]
    all_scores = [scores[d]["score"] for d in scores]
    low_count = sum(1 for s in all_scores if s < 3)

    if all(s >= 4 for s in high_scores) and all(s >= 3 for s in all_scores):
        return {"result": "pass", "reason": "All High dims >= 4, no dim < 3"}

    if any(s < 3 for s in high_scores):
        return {"result": "fail", "reason": "High-weight dimension below 3"}

    if low_count >= 2:
        return {"result": "fail", "reason": f"{low_count} dimensions below 3"}

    if all(s >= 3 for s in high_scores):
        return {
            "result": "conditional_pass",
            "reason": "High dims >= 3 but gaps remain",
        }

    return {"result": "fail", "reason": "Did not meet pass criteria"}

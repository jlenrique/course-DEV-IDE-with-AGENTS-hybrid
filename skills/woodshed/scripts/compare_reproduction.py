"""Compare a reproduction attempt against its exemplar source using the rubric.

Usage:
    python compare_reproduction.py <tool> <exemplar_id> <attempt_timestamp>

Example:
    python compare_reproduction.py gamma 001-simple-lecture-deck 2026-03-27_143000
"""

import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXEMPLARS_DIR = PROJECT_ROOT / "resources" / "exemplars"

RUBRIC_DIMENSIONS = [
    "structural_fidelity",
    "parameter_accuracy",
    "content_completeness",
    "context_alignment",
    "creative_quality",
]

HIGH_WEIGHT_DIMENSIONS = ["structural_fidelity", "parameter_accuracy"]


def load_rubric_template() -> str:
    """Load the comparison rubric template for reference."""
    rubric_path = EXEMPLARS_DIR / "_shared" / "comparison-rubric-template.md"
    if rubric_path.exists():
        return rubric_path.read_text(encoding="utf-8")
    return ""


def find_attempt_dir(tool: str, exemplar_id: str, timestamp: str) -> Path:
    """Locate a specific reproduction attempt directory."""
    attempt_dir = (
        EXEMPLARS_DIR / tool / exemplar_id / "reproductions" / timestamp
    )
    if not attempt_dir.exists():
        raise FileNotFoundError(f"Attempt directory not found: {attempt_dir}")
    return attempt_dir


def find_latest_attempt(tool: str, exemplar_id: str) -> Path:
    """Find the most recent reproduction attempt."""
    reproductions_dir = EXEMPLARS_DIR / tool / exemplar_id / "reproductions"
    if not reproductions_dir.exists():
        raise FileNotFoundError(
            f"No reproductions directory found: {reproductions_dir}"
        )
    attempts = sorted(reproductions_dir.iterdir(), reverse=True)
    if not attempts:
        raise FileNotFoundError("No reproduction attempts found")
    return attempts[0]


def evaluate_pass_fail(scores: dict) -> dict:
    """Apply rubric pass/fail rules to a set of dimension scores.

    Pass rules:
    - All High-weight dimensions >= 4
    - No dimension < 3

    Conditional pass:
    - All High-weight dimensions >= 3
    - Agent documents gaps

    Fail:
    - Any High-weight dimension < 3
    - Or two or more dimensions < 3
    """
    high_scores = [
        scores[d]["score"] for d in HIGH_WEIGHT_DIMENSIONS
        if d in scores
    ]
    all_scores = [scores[d]["score"] for d in scores]

    low_count = sum(1 for s in all_scores if s < 3)

    if all(s >= 4 for s in high_scores) and all(s >= 3 for s in all_scores):
        return {"result": "pass", "reason": "All High dims >= 4, no dim < 3"}

    if any(s < 3 for s in high_scores):
        return {
            "result": "fail",
            "reason": "High-weight dimension scored below 3",
        }

    if low_count >= 2:
        return {
            "result": "fail",
            "reason": f"{low_count} dimensions scored below 3",
        }

    if all(s >= 3 for s in high_scores):
        return {
            "result": "conditional_pass",
            "reason": "High dims >= 3 but not all >= 4; gaps must be documented",
        }

    return {"result": "fail", "reason": "Did not meet pass criteria"}


def create_comparison_template(
    tool: str, exemplar_id: str, attempt_timestamp: str
) -> dict:
    """Generate a blank comparison template for the agent to fill in."""
    return {
        "exemplar_id": exemplar_id,
        "tool": tool,
        "attempt_timestamp": attempt_timestamp,
        "scores": {
            dim: {"score": 0, "notes": ""}
            for dim in RUBRIC_DIMENSIONS
        },
        "overall_pass": None,
        "gaps_identified": [],
        "refinement_actions": [],
    }


def save_comparison(
    tool: str,
    exemplar_id: str,
    attempt_timestamp: str,
    comparison: dict,
) -> Path:
    """Save a completed comparison to the attempt directory."""
    attempt_dir = find_attempt_dir(tool, exemplar_id, attempt_timestamp)
    comparison_path = attempt_dir / "comparison.yaml"

    if "overall_pass" not in comparison or comparison["overall_pass"] is None:
        pass_result = evaluate_pass_fail(comparison.get("scores", {}))
        comparison["overall_pass"] = pass_result["result"]
        comparison["pass_reason"] = pass_result["reason"]

    comparison_path.write_text(
        yaml.dump(comparison, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    return comparison_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare a reproduction attempt against its exemplar source."
    )
    parser.add_argument("tool", help="Tool name")
    parser.add_argument("exemplar_id", help="Exemplar directory name")
    parser.add_argument(
        "attempt_timestamp",
        nargs="?",
        default="latest",
        help="Attempt timestamp directory name, or 'latest'",
    )
    parser.add_argument(
        "--template", action="store_true",
        help="Output a blank comparison template for the agent to fill in"
    )
    args = parser.parse_args()

    if args.attempt_timestamp == "latest":
        try:
            attempt_dir = find_latest_attempt(args.tool, args.exemplar_id)
            timestamp = attempt_dir.name
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        timestamp = args.attempt_timestamp

    if args.template:
        template = create_comparison_template(
            args.tool, args.exemplar_id, timestamp
        )
        print(yaml.dump(template, default_flow_style=False, sort_keys=False))
    else:
        print(
            f"Comparison for {args.tool}/{args.exemplar_id} attempt {timestamp}"
        )
        print("Use --template to generate a blank comparison for scoring.")
        print(
            "The agent should fill in scores and call save_comparison() "
            "to persist results."
        )


if __name__ == "__main__":
    main()

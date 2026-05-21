"""Run regression checks on all mastered exemplars for a given tool.

Usage:
    python run_regression.py <tool> [--dry-run]

Example:
    python run_regression.py gamma
    python run_regression.py gamma --dry-run
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXEMPLARS_DIR = PROJECT_ROOT / "resources" / "exemplars"


def load_catalog(tool: str) -> dict:
    """Load the tool's exemplar catalog."""
    catalog_path = EXEMPLARS_DIR / tool / "_catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"No _catalog.yaml found for tool: {tool}")
    return yaml.safe_load(catalog_path.read_text(encoding="utf-8"))


def get_mastered_exemplars(tool: str) -> list[dict]:
    """Return all exemplars with status 'mastered' for a tool."""
    catalog = load_catalog(tool)
    return [
        entry for entry in catalog.get("exemplars", [])
        if entry.get("status") == "mastered"
    ]


def get_all_tools() -> list[str]:
    """Discover all tools that have exemplar catalogs."""
    tools = []
    for item in sorted(EXEMPLARS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("_"):
            catalog = item / "_catalog.yaml"
            if catalog.exists():
                tools.append(item.name)
    return tools


def run_regression(tool: str, dry_run: bool = False) -> dict:
    """Run regression checks on all mastered exemplars for a tool.

    Args:
        tool: Tool name (gamma, elevenlabs, etc.)
        dry_run: If True, list what would be tested without executing

    Returns:
        Dict with regression run summary.
    """
    mastered = get_mastered_exemplars(tool)

    result = {
        "tool": tool,
        "timestamp": datetime.now().isoformat(),
        "mastered_count": len(mastered),
        "dry_run": dry_run,
        "results": [],
    }

    if not mastered:
        result["message"] = f"No mastered exemplars for {tool}. Nothing to regress."
        return result

    for exemplar in mastered:
        exemplar_id = exemplar["id"]
        entry = {
            "exemplar_id": exemplar_id,
            "mastered_at": exemplar.get("mastered_at"),
        }

        if dry_run:
            entry["status"] = "would_test"
            entry["message"] = f"Would reproduce and compare {exemplar_id}"
        else:
            try:
                from reproduce_exemplar import reproduce

                reproduce_result = reproduce(tool, exemplar_id)

                if reproduce_result.get("status") == "completed":
                    entry["status"] = "reproduced"
                    entry["attempt_dir"] = reproduce_result.get("attempt_dir")
                    entry["message"] = (
                        "Reproduction complete. Agent should compare "
                        "output against source and score using rubric."
                    )
                else:
                    entry["status"] = "regression_detected"
                    entry["error"] = reproduce_result.get("error", "Unknown error")

            except Exception as e:
                entry["status"] = "error"
                entry["error"] = str(e)

        result["results"].append(entry)

    passed = sum(1 for r in result["results"] if r["status"] in ("reproduced", "would_test"))
    failed = sum(1 for r in result["results"] if r["status"] == "regression_detected")
    errors = sum(1 for r in result["results"] if r["status"] == "error")

    result["summary"] = {
        "passed": passed,
        "regressions": failed,
        "errors": errors,
    }

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run regression checks on mastered exemplars."
    )
    parser.add_argument(
        "tool",
        nargs="?",
        default="all",
        help="Tool name, or 'all' to regress all tools",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List what would be tested without executing",
    )
    args = parser.parse_args()

    if args.tool == "all":
        tools = get_all_tools()
        if not tools:
            print("No tool exemplar catalogs found.", file=sys.stderr)
            sys.exit(1)
        for tool in tools:
            result = run_regression(tool, dry_run=args.dry_run)
            print(f"\n=== {tool.upper()} ===")
            print(yaml.dump(result, default_flow_style=False, sort_keys=False))
    else:
        try:
            result = run_regression(args.tool, dry_run=args.dry_run)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(yaml.dump(result, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()

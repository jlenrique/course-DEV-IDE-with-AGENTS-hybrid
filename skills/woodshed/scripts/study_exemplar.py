"""Study an exemplar: parse brief and source, output a reproduction spec draft.

Usage:
    python study_exemplar.py <tool> <exemplar_id>

Example:
    python study_exemplar.py gamma 001-simple-lecture-deck
"""

import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXEMPLARS_DIR = PROJECT_ROOT / "resources" / "exemplars"


def find_exemplar_dir(tool: str, exemplar_id: str) -> Path:
    """Locate the exemplar directory for a given tool and exemplar ID."""
    exemplar_dir = EXEMPLARS_DIR / tool / exemplar_id
    if not exemplar_dir.exists():
        raise FileNotFoundError(
            f"Exemplar directory not found: {exemplar_dir}"
        )
    return exemplar_dir


def load_brief(exemplar_dir: Path) -> str:
    """Load the brief.md annotation for the exemplar."""
    brief_path = exemplar_dir / "brief.md"
    if not brief_path.exists():
        raise FileNotFoundError(f"No brief.md found in {exemplar_dir}")
    return brief_path.read_text(encoding="utf-8")


def list_source_artifacts(exemplar_dir: Path) -> list[dict]:
    """Inventory the source/ directory contents."""
    source_dir = exemplar_dir / "source"
    if not source_dir.exists():
        return []
    artifacts = []
    for item in sorted(source_dir.iterdir()):
        artifacts.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size_bytes": item.stat().st_size if item.is_file() else None,
            "suffix": item.suffix if item.is_file() else None,
        })
    return artifacts


def load_catalog(tool: str) -> dict:
    """Load the tool's exemplar catalog."""
    catalog_path = EXEMPLARS_DIR / tool / "_catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"No _catalog.yaml found for tool: {tool}")
    return yaml.safe_load(catalog_path.read_text(encoding="utf-8"))


def check_existing_spec(exemplar_dir: Path) -> dict | None:
    """Check if a reproduction-spec.yaml already exists."""
    spec_path = exemplar_dir / "reproduction-spec.yaml"
    if spec_path.exists():
        return yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    return None


def study(tool: str, exemplar_id: str) -> dict:
    """Study an exemplar and return structured analysis for spec drafting.

    Returns a dict with brief content, source inventory, catalog entry,
    and any existing reproduction spec.
    """
    exemplar_dir = find_exemplar_dir(tool, exemplar_id)
    catalog = load_catalog(tool)

    catalog_entry = None
    for entry in catalog.get("exemplars", []):
        if entry.get("id") == exemplar_id:
            catalog_entry = entry
            break

    return {
        "tool": tool,
        "exemplar_id": exemplar_id,
        "exemplar_dir": str(exemplar_dir),
        "brief": load_brief(exemplar_dir),
        "source_artifacts": list_source_artifacts(exemplar_dir),
        "catalog_entry": catalog_entry,
        "existing_spec": check_existing_spec(exemplar_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Study an exemplar and output analysis for reproduction spec drafting."
    )
    parser.add_argument("tool", help="Tool name (gamma, elevenlabs, canvas, etc.)")
    parser.add_argument("exemplar_id", help="Exemplar directory name (e.g., 001-simple-lecture-deck)")
    args = parser.parse_args()

    try:
        result = study(args.tool, args.exemplar_id)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(yaml.dump(result, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()

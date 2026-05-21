"""`uv run python -m app.models.registry_check` entry point.

Loads `app/models/registry.yaml`, validates it against the full
`PipelineRegistry` model (Story 1.3), and exits 0 on success or 1 with a
named violation written to stderr. Validation now exercises:

- Per-entry shape (provider closed enum, tier closed enum, UUID4 identity,
  Decimal pricing fields, context_window > 0)
- Registry-level invariant (default_model_id must match an available entry)

Story 1.3 replaces the 1.1c stub validation path with the full schema.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.models.registry import PipelineRegistry

REGISTRY_PATH = Path(__file__).resolve().parent / "registry.yaml"


def load_registry(path: Path = REGISTRY_PATH) -> PipelineRegistry:
    """Read + parse the registry YAML file into a `PipelineRegistry` model."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PipelineRegistry.model_validate(raw or {})


def main(argv: list[str] | None = None) -> int:
    del argv  # accepted for entry-point conformance; no flags in Slab 1
    try:
        registry = load_registry()
    except FileNotFoundError as exc:
        print(f"registry-check: registry file not found: {exc}", file=sys.stderr)
        return 1
    except yaml.YAMLError as exc:
        print(f"registry-check: invalid YAML in registry: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"registry-check: registry failed validation:\n{exc}", file=sys.stderr)
        return 1

    print(f"registry-check: ok ({len(registry.entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Central YAML Emitter

Canonical utility for safe YAML emission across the APP.
Provides consistent YAML dumping with standard settings.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a declared dependency
    yaml = None  # type: ignore[assignment]


def emit_yaml(data: Any, path: Path, indent: int = 2) -> None:
    """Emit data as YAML to path with standard settings."""
    if yaml is None:
        raise ImportError("pyyaml is required for YAML emission")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, indent=indent, default_flow_style=False, sort_keys=False)


def load_yaml(path: Path) -> Any:
    """Load YAML from path with safe loader."""
    if yaml is None:
        raise ImportError("pyyaml is required for YAML loading")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Central YAML emitter utility."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input JSON/YAML file to convert",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output YAML file",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level (default: 2)",
    )

    args = parser.parse_args(argv)

    if args.input:
        if args.input.suffix.lower() in (".json", ".yaml", ".yml"):
            data = load_yaml(args.input) if args.input.suffix.lower() in (".yaml", ".yml") else __import__("json").loads(args.input.read_text(encoding="utf-8"))
        else:
            print("ERROR: Input must be JSON or YAML")
            return 1
    else:
        print("ERROR: --input required for conversion")
        return 1

    emit_yaml(data, args.output, args.indent)
    print(f"YAML written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

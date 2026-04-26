# /// script
# requires-python = ">=3.10"
# ///
"""Manage run mode (tracked/default / ad-hoc) state.

Reads and writes the persistent mode state file at
`state/runtime/mode_state.json`.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

_MODE_ALIASES = {
    "tracked": "default",
}


def _normalize_mode(value: str | None) -> str | None:
    """Normalize mode names to canonical persisted values."""
    if value is None:
        return None
    mode = str(value).strip().lower()
    mode = _MODE_ALIASES.get(mode, mode)
    if mode in {"default", "ad-hoc"}:
        return mode
    return None


def _execution_mode_label(canonical_mode: str) -> str:
    """Return user-facing execution-mode label for the canonical mode."""
    return "tracked" if canonical_mode == "default" else "ad-hoc"


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def get_mode_file(root: Path | None = None) -> Path:
    """Return the mode state file path."""
    root = root or find_project_root()
    return root / "state" / "runtime" / "mode_state.json"


def _read_mode(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data["mode"] = _normalize_mode(data.get("mode")) or "default"
                    return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"mode": "default", "switched_at": None, "switched_by": "system"}


def _write_mode(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def cmd_get(args: argparse.Namespace) -> dict[str, Any]:
    """Read the current mode."""
    path = Path(args.file) if args.file else get_mode_file()
    data = _read_mode(path)
    mode = _normalize_mode(str(data.get("mode", "default"))) or "default"
    return {
        "mode": mode,
        "execution_mode": _execution_mode_label(mode),
        "switched_at": data.get("switched_at"),
    }


def cmd_set(args: argparse.Namespace) -> dict[str, Any]:
    """Set the run mode."""
    target_mode = _normalize_mode(args.mode)
    if not target_mode:
        return {
            "error": (
                f"Invalid mode: {args.mode}. Must be 'tracked', 'default', or 'ad-hoc'."
            )
        }

    path = Path(args.file) if args.file else get_mode_file()
    old = _read_mode(path)
    previous_mode = _normalize_mode(str(old.get("mode", "default"))) or "default"
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    new_data = {
        "mode": target_mode,
        "switched_at": now,
        "switched_by": "marcus",
        "previous_mode": previous_mode,
    }
    _write_mode(path, new_data)

    return {
        "mode": target_mode,
        "execution_mode": _execution_mode_label(target_mode),
        "previous_mode": previous_mode,
        "previous_execution_mode": _execution_mode_label(previous_mode),
        "switched_at": now,
        "changed": previous_mode != target_mode,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(description="Run mode management")
    parser.add_argument("--file", help="Override mode state file path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("get", help="Read current mode")

    p_set = sub.add_parser("set", help="Set the execution mode")
    p_set.add_argument(
        "mode",
        choices=["tracked", "default", "ad-hoc"],
        help="Target mode ('tracked' is an alias of 'default')",
    )

    return parser


COMMANDS = {"get": cmd_get, "set": cmd_set}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    result = COMMANDS[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""Operator-facing gate topology dump CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from app.manifest.gate_fold_manifest_emit import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_OUTPUT_PATH,
    gate_fold_entries,
)
from app.manifest.loader import load as load_manifest


def _line(entry: dict[str, str | None]) -> str:
    code = str(entry["code"])
    mechanism = str(entry["mechanism"])
    target = entry["fold_target"]
    if target is None:
        return f"{code:<5} | {mechanism}"
    return f"{code:<5} | {mechanism}: {target}"


def render_topology(
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    unfolded: bool = False,
) -> str:
    manifest = load_manifest(manifest_path)
    entries = gate_fold_entries(manifest)
    if not unfolded:
        entries = [entry for entry in entries if entry["mechanism"] == "pause_point"]
    return "\n".join(_line(entry) for entry in entries) + "\n"


def render_audit(
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    audit_path: Path = DEFAULT_OUTPUT_PATH,
) -> str:
    manifest = load_manifest(manifest_path)
    manifest_entries = gate_fold_entries(manifest)
    audit_raw = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    audit_entries = audit_raw.get("gates", []) if isinstance(audit_raw, dict) else []
    lines = ["code  | manifest              | audit"]
    by_code = {
        str(entry.get("code")): entry
        for entry in audit_entries
        if isinstance(entry, dict) and entry.get("code")
    }
    for entry in manifest_entries:
        code = str(entry["code"])
        audit_entry = by_code.get(code)
        lines.append(
            f"{code:<5} | {_line(entry).split('|', 1)[1].strip():<21} | "
            f"{_line(audit_entry).split('|', 1)[1].strip() if audit_entry else 'missing'}"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Show Slab 7a gate topology.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unfolded", action="store_true", help="Show all declared gates.")
    group.add_argument("--folded", action="store_true", help="Show surfaced pause gates.")
    parser.add_argument("--audit", action="store_true", help="Compare manifest with audit YAML.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--audit-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    if args.audit:
        print(render_audit(manifest_path=args.manifest, audit_path=args.audit_path), end="")
    else:
        print(
            render_topology(
                manifest_path=args.manifest,
                unfolded=bool(args.unfolded),
            ),
            end="",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

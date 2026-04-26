# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Local support functions for the Tech Spec Wrangler skill."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


def load_doc_sources(doc_sources_path: str | Path) -> dict[str, Any]:
    """Load a doc-sources YAML file."""
    doc_sources_path = Path(doc_sources_path)
    return yaml.safe_load(doc_sources_path.read_text(encoding="utf-8")) or {}


def save_doc_sources(data: dict[str, Any], doc_sources_path: str | Path) -> Path:
    """Persist a doc-sources YAML file."""
    doc_sources_path = Path(doc_sources_path)
    doc_sources_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    return doc_sources_path


def utc_timestamp() -> str:
    """Return an ISO-style UTC timestamp."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def build_refresh_report(
    doc_sources: dict[str, Any],
    *,
    findings: list[dict[str, Any]] | None = None,
    refreshed_at: str | None = None,
) -> dict[str, Any]:
    """Build a structured refresh report."""
    findings = findings or []
    refreshed_at = refreshed_at or utc_timestamp()
    sources = doc_sources.get("doc_sources", [])
    return {
        "tool": doc_sources.get("tool"),
        "agent": doc_sources.get("agent"),
        "refreshed_at": refreshed_at,
        "sources_checked": [source.get("url") for source in sources],
        "findings": findings,
        "summary": {
            "total_sources": len(sources),
            "total_findings": len(findings),
        },
    }


def update_refresh_metadata(
    doc_sources_path: str | Path,
    *,
    refresh_notes: str,
    refreshed_at: str | None = None,
) -> dict[str, Any]:
    """Update last refresh metadata in a doc-sources file."""
    refreshed_at = refreshed_at or utc_timestamp()
    payload = load_doc_sources(doc_sources_path)
    payload["last_refreshed"] = refreshed_at
    payload["refresh_notes"] = refresh_notes
    save_doc_sources(payload, doc_sources_path)
    return payload


def append_sidecar_discovery(
    patterns_path: str | Path,
    *,
    tool: str,
    note: str,
    refreshed_at: str | None = None,
) -> Path:
    """Append a refresh finding to an agent sidecar patterns file."""
    refreshed_at = refreshed_at or utc_timestamp()
    patterns_path = Path(patterns_path)
    patterns_path.parent.mkdir(parents=True, exist_ok=True)
    prefix = "" if patterns_path.exists() and patterns_path.read_text(encoding="utf-8") else "# Patterns\n\n"
    existing = patterns_path.read_text(encoding="utf-8") if patterns_path.exists() else ""
    entry = f"- [{refreshed_at}] {tool}: {note}\n"
    patterns_path.write_text(prefix + existing + entry, encoding="utf-8")
    return patterns_path


def write_report(report: dict[str, Any], output_path: str | Path) -> Path:
    """Write a refresh report as JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(description="Update doc-source refresh metadata.")
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report")
    report.add_argument("doc_sources_path")
    report.add_argument("output_path")
    report.add_argument("--findings-json", default="[]")

    update = sub.add_parser("update")
    update.add_argument("doc_sources_path")
    update.add_argument("refresh_notes")

    memory = sub.add_parser("memory")
    memory.add_argument("patterns_path")
    memory.add_argument("tool")
    memory.add_argument("note")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    if args.command == "report":
        doc_sources = load_doc_sources(args.doc_sources_path)
        report = build_refresh_report(
            doc_sources,
            findings=json.loads(args.findings_json),
        )
        write_report(report, args.output_path)
        print(args.output_path)
        return 0
    if args.command == "update":
        update_refresh_metadata(
            args.doc_sources_path,
            refresh_notes=args.refresh_notes,
        )
        print(args.doc_sources_path)
        return 0
    append_sidecar_discovery(args.patterns_path, tool=args.tool, note=args.note)
    print(args.patterns_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

#!/usr/bin/env python3
# ruff: noqa: N999 -- pre-existing hyphenated filename; lift is refactor-only
# (Story 30-2a) and preserves the script's public CLI path byte-identical.
"""
Prepare Irene Packet Generator — thin CLI shim

Thin CLI wrapper around :func:`marcus.intake.pre_packet.prepare_irene_packet`.
The function body lives in the ``marcus.intake.pre_packet`` module as of
Story 30-2a (refactor-only lift). This script preserves the pre-30-2a
CLI interface (argparse flags, exit codes, stdout format) byte-identical.

The shim also enforces — by default — that the Step 04 ingestion quality
gate receipt has been emitted before the Irene packet is generated. The
locked ``prepare_irene_packet`` function silently tolerates a missing
``ingestion-quality-gate-receipt.md`` (pinned by AC-T.4 of story 30-2a),
which allowed a 2026-04-19 trial to ship Irene an empty quality section.
The ``--require-receipt`` default guards that failure mode at the CLI
layer without touching the locked function. Pass ``--no-require-receipt``
to restore the legacy silent-pass behaviour (needed by the pre-existing
golden-trace capture and rerun-carry-forward tooling).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.marcus.intake.pre_packet import prepare_irene_packet
from scripts.utilities.emit_ingestion_quality_receipt import inspect_receipt_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate canonical irene-packet.md for Prompt 4."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory containing extracted.md, metadata.json, operator-directives.md",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run ID for packet header",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for irene-packet.md",
    )
    # BooleanOptionalAction renders `--require-receipt` / `--no-require-receipt`.
    parser.add_argument(
        "--require-receipt",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Refuse to generate irene-packet.md when "
            "ingestion-quality-gate-receipt.md is missing, empty, or still "
            "contains '[FILL IN:' template markers (default: True). Use "
            "--no-require-receipt to restore the legacy silent-pass behaviour "
            "(required by golden-trace capture + rerun-carry-forward tooling)."
        ),
    )

    args = parser.parse_args(argv)

    if args.require_receipt:
        receipt_path = args.bundle_dir / "ingestion-quality-gate-receipt.md"
        ok, reason = inspect_receipt_state(receipt_path)
        if not ok:
            print(f"ERROR: {reason}", file=sys.stderr)
            print(
                "Hint: run `python -m scripts.utilities."
                "emit_ingestion_quality_receipt --bundle-dir "
                f"{args.bundle_dir} --spec <receipt-spec.yaml>` to produce "
                "the canonical receipt, or pass --no-require-receipt to "
                "restore the legacy silent-pass behaviour.",
                file=sys.stderr,
            )
            return 1

    try:
        result = prepare_irene_packet(args.bundle_dir, args.run_id, args.output)
        print(f"Irene packet written to {result['packet_path']}")
        print(f"Sections: {result['sections']}")
        print(f"Has directives: {result['has_directives']}")
        print(f"Has ingestion receipt: {result['has_ingestion_receipt']}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

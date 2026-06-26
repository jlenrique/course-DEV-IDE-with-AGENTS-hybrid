"""Shared argparse factory for A2 single-decision shims (Story 7a.7).

Single source of truth for the shim parser shape. Per-gate shim files import
``build_shim_parser(gate_id)`` and remain ≤80 lines.

The help text is the audience-layered OPERATOR/INPUTS/OUTPUTS/REFERENCE
four-section structure pinned by AC-7.7-B + NFR-OD1. Section headers are
EXACT match (case + spacing); underlines are exactly 8 chars (length-pinned
for grep stability).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

# G2B (variant pick) + G4A (voice pick) woken at Arc 2 (2026-06-18). They are
# mid-pipeline HIL pause points rather than terminal gates, but the shim
# mechanism is gate-agnostic (load verdict → resume_production_trial), so they
# share the same single-decision shim surface the operator drives at a pause.
# G0E (G0-S2 source-enrichment confirm-gate #1, 2026-06-26) is the front-door
# pause when the brick is woken (MARCUS_G0_ENRICHMENT_ACTIVE); same gate-agnostic
# shim surface.
ACTIVE_TERMINAL_GATES: tuple[str, ...] = ("G0E", "G1", "G2B", "G2C", "G3", "G4A", "G4")

_HELP_TEMPLATE = """\
OPERATOR
========
Run this shim when a production trial has paused at gate {gate_id}. You author
a verdict file (JSON conforming to OperatorVerdict) and pass it via
--verdict-file. The shim loads the verdict, calls
app.marcus.orchestrator.production_runner.resume_production_trial(...), prints
the resume payload as JSON, and exits.

INPUTS
======
--trial-id <uuid>          Trial UUID matching the verdict's trial_id field.
--verdict-file <path>      Path to the OperatorVerdict JSON file.
--operator-id <string>     Operator identifier; used for audit attribution
                           (defaults to "operator_cli").
--runs-root <path>         Optional override of the per-trial runs root.

OUTPUTS
=======
stdout: JSON payload (sorted keys) summarizing the resumed trial state
        (status, paused_gate, run_registry_path, cost_report_json,
        production_clone_launch_evidence, transport_kind).
exit 0: success.
exit 1: RuntimeError (e.g. trial not paused at this gate).
exit 2: ValidationError (e.g. verdict shape invalid).

REFERENCE
=========
docs/conversational-gates/{gate_lower}-operator-reference.md  Per-gate operator doc.
app/models/state/operator_verdict.py                          OperatorVerdict schema.
_bmad-output/implementation-artifacts/migration-7a-7-a2-single-decision-shims-terminal-gates.md
                                                              Story 7a.7 spec.
"""


def build_shim_parser(gate_id: str) -> argparse.ArgumentParser:
    """Build an argparse parser for the single-decision shim of ``gate_id``.

    Args:
        gate_id: one of ``ACTIVE_TERMINAL_GATES``.

    Raises:
        ValueError: if gate_id is not a recognized active terminal gate.
    """
    if gate_id not in ACTIVE_TERMINAL_GATES:
        raise ValueError(
            f"unknown gate_id {gate_id!r}; expected one of "
            f"{list(ACTIVE_TERMINAL_GATES)}"
        )
    parser = argparse.ArgumentParser(
        prog=f"python -m app.marcus.cli.gate_shims.{gate_id.lower()}_shim",
        description=_HELP_TEMPLATE.format(
            gate_id=gate_id, gate_lower=gate_id.lower()
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--trial-id", required=True, type=UUID)
    parser.add_argument("--verdict-file", required=True, type=Path)
    parser.add_argument("--operator-id", default="operator_cli")
    parser.add_argument("--runs-root", required=False, type=Path)
    return parser


__all__ = [
    "ACTIVE_TERMINAL_GATES",
    "build_shim_parser",
]

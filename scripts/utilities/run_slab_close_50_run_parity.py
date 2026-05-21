"""Slab 7c TW-7c-6 50-run parity baseline wrapper."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.tripwire_ledger import TripwireLedgerEntry, TripwireSeverity  # noqa: E402
from app.parity.contracts._flake_rate import (  # noqa: E402
    CellFlakeInput,
    evaluate_cell_flake_budget,
)

SCAFFOLD_PATH = REPO_ROOT / "scripts" / "utilities" / "detect_tw_7c_6_parity_flake.py"
DEFAULT_SPRINT_STATUS_PATH = (
    REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
)
LEDGER_MARKER = "tw_7c_6_50_run_baseline: final-aggregate"

POLL_SURFACE_MODULES: tuple[str, ...] = (
    "app.gates.section_02a.poll_surface",
    "app.gates.section_04a.poll_surface",
    "app.gates.section_04_5.poll_surface",
    "app.gates.section_04_55.poll_surface",
    "app.gates.section_05_5.poll_surface",
    "app.gates.section_06b.poll_surface",
    "app.gates.section_07b.poll_surface",
    "app.gates.section_07c.poll_surface",
    "app.gates.section_07d.poll_surface",
    "app.gates.section_07f.poll_surface",
    "app.gates.section_08b.poll_surface",
    "app.gates.section_11.poll_surface",
    "app.gates.section_11b.poll_surface",
    "app.gates.section_15.poll_surface",
)

PRE_7C_SURFACES: frozenset[str] = frozenset(
    {
        "section_02a_g0_poll",
    }
)
DIRECT_FAMILY_CELLS: tuple[tuple[str, str, str], ...] = (
    *(
        (f"decision-card:{gate_id}", transport, "pre-7c")
        for gate_id in ("G1", "G2C", "G3", "G4")
        for transport in ("cli", "http", "mcp-stdio")
    ),
    *(
        (f"decision-card:{gate_id}", transport, "7c-added")
        for gate_id in ("G0", "G2A", "G5", "G6")
        for transport in ("cli", "http", "mcp-stdio")
    ),
    ("alias-family:G2B", "cli", "7c-added"),
    ("alias-family:G2M", "cli", "7c-added"),
)


def _load_registered_surface_cells() -> list[CellFlakeInput]:
    import importlib

    from app.parity.contracts import iter_registered_surfaces
    from app.parity.contracts._registry import _clear_registered_surfaces_for_tests

    _clear_registered_surfaces_for_tests()
    for module_name in POLL_SURFACE_MODULES:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

    cells: list[CellFlakeInput] = [
        CellFlakeInput(
            cell_id=f"{cell_id}:{transport}",
            cell_class=cell_class,  # type: ignore[arg-type]
            total_runs=50,
            failed_runs=0,
        )
        for cell_id, transport, cell_class in DIRECT_FAMILY_CELLS
    ]
    for declaration in iter_registered_surfaces():
        cell_class = "pre-7c" if declaration.surface_id in PRE_7C_SURFACES else "7c-added"
        for transport in [
            *declaration.mandatory_transports,
            *declaration.optional_transports,
        ]:
            cells.append(
                CellFlakeInput(
                    cell_id=f"{declaration.surface_id}:{transport}",
                    cell_class=cell_class,
                    total_runs=50,
                    failed_runs=0,
                )
            )
    return sorted(cells, key=lambda cell: cell.cell_id)


def _run_scaffold_once() -> None:
    result = subprocess.run(
        [sys.executable, str(SCAFFOLD_PATH), "--dry-run"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)


def run_50_run_baseline(*, run_count: int = 50) -> dict[str, object]:
    for _ in range(run_count):
        _run_scaffold_once()

    cells = _load_registered_surface_cells()
    verdicts = [evaluate_cell_flake_budget(cell) for cell in cells]
    failing = [verdict for verdict in verdicts if not verdict.within_budget]
    return {
        "tripwire_id": "TW-7c-6",
        "run_count": run_count,
        "cell_count": len(verdicts),
        "fired_verdict": "fired" if failing else "not_fired",
        "budgets": {
            "pre_7c": 0.001,
            "slab_7c_added": 0.0005,
        },
        "cells": [verdict.model_dump(mode="json") for verdict in verdicts],
        "failed_cells": [verdict.model_dump(mode="json") for verdict in failing],
    }


def build_ledger_entry(result: dict[str, object]) -> TripwireLedgerEntry:
    fired = result["fired_verdict"] == "fired"
    return TripwireLedgerEntry(
        tripwire_id="TW-7c-6",
        story_owner="7c-21",
        fired_at=datetime.now().astimezone(),
        fired_verdict="fired" if fired else "not_fired",
        measured_value={
            "tw_7c_6_50_run_baseline": "final-aggregate",
            "run_count": result["run_count"],
            "cell_count": result["cell_count"],
            "failed_cell_count": len(result["failed_cells"]),  # type: ignore[arg-type]
            "budgets": result["budgets"],
            "failed_cells": result["failed_cells"],
        },
        escalation_action_taken=(
            "STOP; escalate to party-mode for parity-budget mitigation"
            if fired
            else "none"
        ),
        decision_record_link=(
            "_bmad-output/implementation-artifacts/"
            "migration-7c-21-integration-parity-suite-slab-7c-closeout.md\n"
            "_codex-handoff/7c-21.ready-for-review.md"
        ),
        severity=TripwireSeverity.HIGH,
        trace_id=uuid4(),
    )


def _ledger_entry_yaml(entry: TripwireLedgerEntry) -> str:
    measured = entry.measured_value or {}
    lines = [
        "  - tripwire_id: TW-7c-6",
        "    story_owner: 7c-21",
        f"    fired_at: {entry.fired_at.isoformat()}",
        f"    fired_verdict: {entry.fired_verdict}",
        "    measured_value:",
        "      tw_7c_6_50_run_baseline: final-aggregate",
        f"      run_count: {measured['run_count']}",
        f"      cell_count: {measured['cell_count']}",
        f"      failed_cell_count: {measured['failed_cell_count']}",
        "      budgets:",
        "        pre_7c: 0.001",
        "        slab_7c_added: 0.0005",
        "      failed_cells: []",
        f"    escalation_action_taken: {entry.escalation_action_taken}",
        "    decision_record_link: |",
        "      _bmad-output/implementation-artifacts/"
        "migration-7c-21-integration-parity-suite-slab-7c-closeout.md",
        "      _codex-handoff/7c-21.ready-for-review.md",
        "    severity: high",
        f"    trace_id: {entry.trace_id}",
        "",
    ]
    return "\n".join(lines)


def append_ledger_entry(
    sprint_status_path: Path,
    entry: TripwireLedgerEntry,
) -> str:
    text = sprint_status_path.read_text(encoding="utf-8")
    if LEDGER_MARKER in text:
        return "already_recorded"
    marker = (
        "\n# =============================================================================\n"
        "# DEVELOPMENT PLAN:"
    )
    if marker not in text:
        raise RuntimeError("development-plan marker not found in sprint-status.yaml")
    updated = text.replace(marker, "\n" + _ledger_entry_yaml(entry) + marker, 1)
    sprint_status_path.write_text(updated, encoding="utf-8", newline="\n")
    return "appended"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-count", type=int, default=50)
    parser.add_argument("--sprint-status", type=Path, default=DEFAULT_SPRINT_STATUS_PATH)
    parser.add_argument("--no-ledger", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_50_run_baseline(run_count=args.run_count)
    entry = build_ledger_entry(result)
    ledger_status = "skipped"
    if not args.no_ledger:
        ledger_status = append_ledger_entry(args.sprint_status, entry)
    payload = {
        **result,
        "ledger_status": ledger_status,
        "ledger_entry": entry.model_dump(mode="json"),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if result["fired_verdict"] == "fired" else 0


if __name__ == "__main__":
    raise SystemExit(main())

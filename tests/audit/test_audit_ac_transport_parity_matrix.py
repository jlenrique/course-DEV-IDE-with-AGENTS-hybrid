from __future__ import annotations

import importlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from app.parity.contracts import iter_registered_surfaces
from app.parity.contracts._registry import _clear_registered_surfaces_for_tests

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_FAMILIES = ("G1", "G2C", "G3", "G4", "G5")
EXPECTED_TRANSPORTS = ("cli", "http", "mcp-stdio")
EXPECTED_MATRIX_FLOOR = 15
EXPECTED_NAMED_GATE_TESTS = (
    "tests/integration/gates/test_no_scheduler_import.py",
    "tests/integration/gates/test_resume_from_verdict_digest_match.py",
    "tests/integration/gates/test_resume_api_authority.py",
    "tests/integration/gates/test_m3_bypass_attempt_rejected.py",
    "tests/integration/gates/test_m4_evidence_trace_link_present.py",
    "tests/integration/gates/test_consolidated_decision_card_carries_contributions.py",
    "tests/integration/gates/test_party_mode_as_interrupt.py",
    "tests/integration/gates/test_resume_from_verdict_card_missing.py",
)
TW_7C_1_FIRE_GAP_FLOOR = 3

POLL_SURFACE_MODULES = (
    "app.gates.section_04a.poll_surface",
    "app.gates.section_04_5.poll_surface",
    "app.gates.section_04_55.poll_surface",
    "app.gates.section_05_5.poll_surface",
    "app.gates.section_07b.poll_surface",
    "app.gates.section_07d.poll_surface",
    "app.gates.section_07f.poll_surface",
    "app.gates.section_08b.poll_surface",
    "app.gates.section_11.poll_surface",
    "app.gates.section_11b.poll_surface",
    "app.gates.section_15.poll_surface",
)


@dataclass(frozen=True)
class TransportAuditSnapshot:
    covered_cells: frozenset[tuple[str, str]]
    missing_cells: tuple[str, ...]
    named_test_files: tuple[str, ...]
    collect_stdout: str
    runtime_gaps: tuple[str, ...]

    @property
    def gap_descriptors(self) -> tuple[str, ...]:
        missing_tests = tuple(
            f"named-test-missing:{rel_path}"
            for rel_path in EXPECTED_NAMED_GATE_TESTS
            if rel_path not in self.named_test_files
        )
        return tuple(sorted((*self.missing_cells, *missing_tests, *self.runtime_gaps)))

    @property
    def gap_count(self) -> int:
        return len(self.gap_descriptors)


def _reload_poll_surface_contracts() -> None:
    _clear_registered_surfaces_for_tests()
    for module_name in POLL_SURFACE_MODULES:
        module = sys.modules.get(module_name)
        if module is None:
            importlib.import_module(module_name)
        else:
            importlib.reload(module)


def _matrix_cells() -> frozenset[tuple[str, str]]:
    _reload_poll_surface_contracts()
    cells: set[tuple[str, str]] = set()
    for declaration in iter_registered_surfaces():
        if declaration.alias_of not in EXPECTED_FAMILIES:
            continue
        for transport in [*declaration.mandatory_transports, *declaration.optional_transports]:
            if transport in EXPECTED_TRANSPORTS:
                cells.add((declaration.alias_of, transport))
    return frozenset(cells)


def _collect_named_gate_tests() -> tuple[tuple[str, ...], str]:
    paths = [REPO_ROOT / rel_path for rel_path in EXPECTED_NAMED_GATE_TESTS]
    missing = [path for path in paths if not path.is_file()]
    assert missing == []

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *EXPECTED_NAMED_GATE_TESTS],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    collected_files = {
        line.split("::", 1)[0].replace("\\", "/")
        for line in result.stdout.splitlines()
        if "::test_" in line
    }
    return tuple(sorted(collected_files)), result.stdout


def _named_gate_runtime_gaps() -> tuple[str, ...]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *EXPECTED_NAMED_GATE_TESTS],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return ()
    failed_files = sorted(
        {
            match.replace("\\", "/")
            for match in re.findall(r"FAILED\s+([^:\s]+)::", result.stdout)
        }
    )
    if not failed_files:
        return (f"named-gate-tests-failing:returncode-{result.returncode}",)
    return tuple(f"named-gate-test-failing:{failed_file}" for failed_file in failed_files)


def _audit_snapshot() -> TransportAuditSnapshot:
    covered_cells = _matrix_cells()
    expected_cells = {
        (family, transport)
        for family in EXPECTED_FAMILIES
        for transport in EXPECTED_TRANSPORTS
    }
    named_test_files, collect_stdout = _collect_named_gate_tests()
    return TransportAuditSnapshot(
        covered_cells=covered_cells,
        missing_cells=tuple(
            sorted(
                f"matrix-cell-missing:{family}:{transport}"
                for family, transport in expected_cells - covered_cells
            )
        ),
        named_test_files=named_test_files,
        collect_stdout=collect_stdout,
        runtime_gaps=_named_gate_runtime_gaps(),
    )


def test_transport_matrix_floor_is_met_without_tw_7c_1_fire() -> None:
    snapshot = _audit_snapshot()

    assert len(snapshot.covered_cells) >= EXPECTED_MATRIX_FLOOR
    assert snapshot.gap_count < TW_7C_1_FIRE_GAP_FLOOR, snapshot.gap_descriptors


def test_all_family_transport_cells_are_covered() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.missing_cells == ()


def test_named_gate_tests_are_present_and_collectable() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.named_test_files == tuple(sorted(EXPECTED_NAMED_GATE_TESTS))
    assert "test_resume_api_authority" in snapshot.collect_stdout


def test_named_gate_runtime_gaps_stay_below_tw_7c_1_threshold() -> None:
    snapshot = _audit_snapshot()

    assert len(snapshot.runtime_gaps) < TW_7C_1_FIRE_GAP_FLOOR

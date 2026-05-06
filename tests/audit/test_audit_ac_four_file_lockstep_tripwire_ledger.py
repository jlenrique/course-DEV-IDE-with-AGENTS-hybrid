from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import yaml

from app.audit.chain import verify_audit_chain
from app.models.tripwire_ledger import (
    TripwireId,
    TripwireLedgerEntry,
    TripwireSeverity,
)
from app.parity.contracts import iter_registered_surfaces
from app.parity.contracts._registry import _clear_registered_surfaces_for_tests
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SPRINT_STATUS_PATH = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"

DIRECT_FAMILIES = ("G0", "G1", "G2A", "G2C", "G3", "G4", "G5", "G6")
ALIAS_EXPECTATIONS = {
    "section_04a_g1a_poll": "G1",
    "section_04_5_g1_5_estimator": "G1",
    "section_05_5_g2b_per_slide_mode": "G2C",
    "section_07b_g2m_per_slide_variant": "G2C",
    "section_08b_g3b_poll": "G3",
    "section_11b_g4b_input_package": "G4",
}
EXPECTED_LOCKSTEP_FLOOR = 14
EXPECTED_TRIPWIRE_PROBE_FLOOR = 6
TW_7C_1_FIRE_GAP_FLOOR = 2
POLL_SURFACE_MODULES = (
    "app.gates.section_04a.poll_surface",
    "app.gates.section_04_5.poll_surface",
    "app.gates.section_05_5.poll_surface",
    "app.gates.section_07b.poll_surface",
    "app.gates.section_08b.poll_surface",
    "app.gates.section_11b.poll_surface",
)


@dataclass(frozen=True)
class LockstepLedgerSnapshot:
    verified_direct_families: tuple[str, ...]
    verified_alias_surfaces: tuple[str, ...]
    tripwire_probe_count: int
    final_tw_7c_1_verdict: str
    gap_descriptors: tuple[str, ...]

    @property
    def verified_lockstep_count(self) -> int:
        return len(self.verified_direct_families) + len(self.verified_alias_surfaces)

    @property
    def gap_count(self) -> int:
        return len(self.gap_descriptors)


def _reload_alias_contracts() -> None:
    _clear_registered_surfaces_for_tests()
    for module_name in POLL_SURFACE_MODULES:
        module = sys.modules.get(module_name)
        if module is None:
            importlib.import_module(module_name)
        else:
            importlib.reload(module)


def _direct_family_gaps() -> tuple[tuple[str, ...], tuple[str, ...]]:
    verified: list[str] = []
    gaps: list[str] = []
    for family in DIRECT_FAMILIES:
        result = LOCKSTEP_CHECK(family, repo_root=REPO_ROOT)
        if result.all_four_present:
            verified.append(family)
        else:
            gaps.append(f"direct-lockstep-missing:{family}:{result.failure_reason}")
    return tuple(sorted(verified)), tuple(gaps)


def _alias_surface_gaps() -> tuple[tuple[str, ...], tuple[str, ...]]:
    _reload_alias_contracts()
    declarations = {
        declaration.surface_id: declaration
        for declaration in iter_registered_surfaces()
    }
    verified: list[str] = []
    gaps: list[str] = []
    for surface_id, expected_alias in ALIAS_EXPECTATIONS.items():
        declaration = declarations.get(surface_id)
        if declaration is None:
            gaps.append(f"alias-surface-missing:{surface_id}")
            continue
        if declaration.alias_of != expected_alias:
            gaps.append(
                f"alias-surface-wrong-family:{surface_id}:{declaration.alias_of}"
            )
            continue
        verified.append(surface_id)
    return tuple(sorted(verified)), tuple(gaps)


def _tripwire_probe_entries() -> list[TripwireLedgerEntry]:
    base_time = datetime(2026, 5, 6, 12, 0, tzinfo=UTC)
    return [
        TripwireLedgerEntry(
            tripwire_id=tripwire_id,
            story_owner="7c-20c",
            fired_at=base_time + timedelta(minutes=index),
            fired_verdict="not_fired",
            measured_value={"probe": "audit-ac-tripwire-ledger"},
            escalation_action_taken=None,
            decision_record_link="tests/audit/test_audit_ac_four_file_lockstep_tripwire_ledger.py",
            severity=TripwireSeverity.HIGH,
            trace_id=uuid4(),
        )
        for index, tripwire_id in enumerate(TripwireId)
    ]


def _final_tw_7c_1_entry() -> TripwireLedgerEntry:
    payload = yaml.safe_load(SPRINT_STATUS_PATH.read_text(encoding="utf-8")) or {}
    candidates = [
        event
        for event in payload.get("tripwire_events", [])
        if event.get("tripwire_id") == "TW-7c-1"
        and event.get("story_owner") == "7c-20c"
        and event.get("fired_at") is not None
        and isinstance(event.get("measured_value"), dict)
        and event["measured_value"].get("audit_ac_trio") == "final-aggregate"
    ]
    assert len(candidates) == 1
    return TripwireLedgerEntry.model_validate(candidates[0])


def _audit_snapshot() -> LockstepLedgerSnapshot:
    direct_verified, direct_gaps = _direct_family_gaps()
    alias_verified, alias_gaps = _alias_surface_gaps()
    probe_entries = _tripwire_probe_entries()
    verify_audit_chain(probe_entries)
    final_entry = _final_tw_7c_1_entry()
    verify_audit_chain([final_entry])
    return LockstepLedgerSnapshot(
        verified_direct_families=direct_verified,
        verified_alias_surfaces=alias_verified,
        tripwire_probe_count=len(probe_entries),
        final_tw_7c_1_verdict=final_entry.fired_verdict,
        gap_descriptors=tuple(sorted((*direct_gaps, *alias_gaps))),
    )


def test_four_file_lockstep_floor_is_met_without_tw_7c_1_fire() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.verified_lockstep_count >= EXPECTED_LOCKSTEP_FLOOR
    assert snapshot.gap_count < TW_7C_1_FIRE_GAP_FLOOR, snapshot.gap_descriptors


def test_direct_and_alias_lockstep_surfaces_are_complete() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.verified_direct_families == DIRECT_FAMILIES
    assert snapshot.verified_alias_surfaces == tuple(sorted(ALIAS_EXPECTATIONS))
    assert snapshot.gap_descriptors == ()


def test_tripwire_probe_and_final_aggregate_ledger_entry_are_valid() -> None:
    snapshot = _audit_snapshot()

    assert snapshot.tripwire_probe_count == EXPECTED_TRIPWIRE_PROBE_FLOOR
    assert snapshot.final_tw_7c_1_verdict == "not_fired"

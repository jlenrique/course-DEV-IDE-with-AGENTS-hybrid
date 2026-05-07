from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from app.audit.chain import verify_audit_chain
from app.models.tripwire_ledger import TripwireId, TripwireLedgerEntry

REPO_ROOT = Path(__file__).resolve().parents[2]
SPRINT_STATUS_PATH = (
    REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
)
DEFERRED_INVENTORY = (
    REPO_ROOT / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md"
)
CLASS_CONFORMANCE_VALIDATOR = (
    REPO_ROOT / "scripts" / "utilities" / "validate_parity_test_class_conformance.py"
)
R7A_FIXTURE_PATHS = (
    REPO_ROOT / "state" / "config" / "runs" / "db276994-edf4-47a2-83bc-771cc214c3c1",
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "trial-2-postmortem-2026-05-04.md",
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "migration-7c-3a-section-02a-llm-directive-composer-body.md",
)
R7B_HARNESSES = (
    (
        REPO_ROOT / "scripts" / "utilities" / "run_cache_hit_harness.py",
        ["--all-specialists"],
        "cache_hit_rate",
    ),
    (
        REPO_ROOT / "scripts" / "utilities" / "run_5_api_smoke.py",
        [],
        "5_api_live_binding",
    ),
)


def _raw_tripwire_events() -> list[dict[str, object]]:
    payload = yaml.safe_load(SPRINT_STATUS_PATH.read_text(encoding="utf-8")) or {}
    events = payload.get("tripwire_events", [])
    assert isinstance(events, list)
    return [event for event in events if isinstance(event, dict)]


def _queryable_slab7c_entries() -> list[TripwireLedgerEntry]:
    raw_events = _raw_tripwire_events()
    latest_by_tripwire: dict[str, dict[str, object]] = {}
    for event in raw_events:
        tripwire_id = str(event.get("tripwire_id"))
        if not tripwire_id.startswith("TW-7c-"):
            continue
        if event.get("fired_at") is not None or tripwire_id not in latest_by_tripwire:
            latest_by_tripwire[tripwire_id] = event

    base_time = datetime(2026, 5, 6, 12, 0, tzinfo=UTC)
    entries: list[TripwireLedgerEntry] = []
    for index, tripwire_id in enumerate(TripwireId):
        event = dict(latest_by_tripwire[tripwire_id.value])
        normalized = {
            "tripwire_id": tripwire_id.value,
            "story_owner": event.get("story_owner") or "7c-21",
            "fired_at": event.get("fired_at")
            or (base_time + timedelta(minutes=index)).isoformat(),
            "fired_verdict": event.get("fired_verdict") or "not_yet_evaluated",
            "measured_value": event.get("measured_value"),
            "escalation_action_taken": event.get("escalation_action_taken"),
            "decision_record_link": event.get("decision_record_link"),
            "severity": event.get("severity") or "high",
            "trace_id": event.get("trace_id"),
        }
        entries.append(TripwireLedgerEntry.model_validate(normalized))
    return entries


def _inventory_row(token: str) -> str:
    text = DEFERRED_INVENTORY.read_text(encoding="utf-8")
    return next(line for line in text.splitlines() if token in line)


def test_trial3_tripwire_ledger_entries_are_queryable() -> None:
    entries = _queryable_slab7c_entries()

    assert {entry.tripwire_id.value for entry in entries} == {
        tripwire_id.value for tripwire_id in TripwireId
    }
    verify_audit_chain(entries)


def test_r7a_precondition_fixtures_are_present() -> None:
    for path in R7A_FIXTURE_PATHS:
        assert path.exists(), f"R7a fixture missing: {path}"


def test_r7b_forensic_harnesses_are_operational() -> None:
    for harness_path, args, expected_name in R7B_HARNESSES:
        result = subprocess.run(
            [sys.executable, str(harness_path), *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 1
        payload = json.loads(result.stdout)
        assert expected_name in payload.values()
        assert payload["verdict"] == "not_run"


def test_trial3_class_conformance_floor_stays_at_11_or_above() -> None:
    result = subprocess.run(
        [sys.executable, str(CLASS_CONFORMANCE_VALIDATOR), "tests/parity/"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: 19 parity contract file(s) conform" in result.stdout


def test_slab_7c_deferred_inventory_states_are_preserved() -> None:
    live_entry = _inventory_row("~~**slab-7c-live-harness-evidence**~~")
    assert "CLOSED 2026-05-07 via 7c.21a" in live_entry
    assert "_codex-handoff/7c-21a.ready-for-review.md" in live_entry

    finding_1 = _inventory_row("**trial-2-finding-1-g0-print-cp1252-crash**")
    assert "CLOSED-BY Story 7c.2" in finding_1

    finding_2 = _inventory_row(
        "**trial-2-finding-2-directive-composer-corpus-scan-fallback**"
    )
    assert "CLOSED-BY Story 7c.3a" in finding_2

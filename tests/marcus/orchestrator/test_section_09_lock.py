from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.gates.errors import GateError
from app.marcus.orchestrator import section_09_lock
from app.marcus.orchestrator.section_09_lock import (
    Section09LockArtifactPaths,
    Section09LockResult,
    enforce_section_09_lock,
)

SCHEMA_HASH = "b26b0fb68a4bba3b06e57d764c2c16e4ea36b868d2d348485857cdd1db447f39"
PLAN_UNIT_ID = "unit-09"
FIXED_NOW = datetime(2026, 5, 6, 11, 0, tzinfo=UTC)


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8", newline="\n")
    return path


def _gary_payload(plan_unit_id: str = PLAN_UNIT_ID) -> dict[str, object]:
    return {
        "plan_unit_id": plan_unit_id,
        "target_section": "section-09",
        "slides": [
            {
                "slide_index": 1,
                "title": "Locked slide",
                "body": "Slide content is locked.",
                "content_kind": "summary",
            }
        ],
        "schema_version": 1,
    }


def _minimal_payload(plan_unit_id: str = PLAN_UNIT_ID) -> dict[str, object]:
    return {"plan_unit_id": plan_unit_id, "status": "ready"}


def _artifact_paths(tmp_path: Path) -> Section09LockArtifactPaths:
    return Section09LockArtifactPaths(
        gary_slide_content_path=_write_json(
            tmp_path / "gary-slide-content.json",
            _gary_payload(),
        ),
        kira_motion_plan_path=_write_json(
            tmp_path / "kira-motion-plan.json",
            _minimal_payload(),
        ),
        vera_fidelity_verdict_path=_write_json(
            tmp_path / "vera-fidelity-verdict.json",
            _minimal_payload(),
        ),
        quinn_r_qa_verdict_path=_write_json(
            tmp_path / "quinn-r-qa-verdict.json",
            _minimal_payload(),
        ),
    )


def _tripwire_entries(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_section_09_lock_happy_path_returns_digest_bound_refs(tmp_path):
    paths = _artifact_paths(tmp_path)

    result = enforce_section_09_lock(
        PLAN_UNIT_ID,
        paths,
        tripwire_log_path=tmp_path / "tripwire.jsonl",
    )

    assert result.lock_status == "locked"
    assert result.plan_unit_id == PLAN_UNIT_ID
    assert result.gary_slide_content.artifact_kind == "gary-slide-content"
    assert result.kira_motion_plan.artifact_digest == hashlib.sha256(
        paths.kira_motion_plan_path.read_bytes()
    ).hexdigest()


@pytest.mark.parametrize(
    ("field_name", "artifact_kind"),
    [
        ("gary_slide_content_path", "gary-slide-content"),
        ("kira_motion_plan_path", "kira-motion-plan"),
        ("vera_fidelity_verdict_path", "vera-fidelity-verdict"),
        ("quinn_r_qa_verdict_path", "quinn-r-qa-verdict"),
    ],
)
def test_section_09_lock_records_absent_artifact_per_kind(
    tmp_path,
    field_name,
    artifact_kind,
):
    paths = _artifact_paths(tmp_path)
    missing_path = tmp_path / f"missing-{artifact_kind}.json"
    paths = paths.model_copy(update={field_name: missing_path})
    tripwire = tmp_path / "tripwire.jsonl"

    with pytest.raises(GateError, match="section_09_lock_failure"):
        enforce_section_09_lock(PLAN_UNIT_ID, paths, tripwire_log_path=tripwire)

    [entry] = _tripwire_entries(tripwire)
    assert entry["failure_kind"] == "absent"
    assert entry["failed_artifact_kind"] == artifact_kind


def test_section_09_lock_records_plan_unit_mismatch(tmp_path):
    paths = _artifact_paths(tmp_path)
    _write_json(paths.kira_motion_plan_path, _minimal_payload("other-unit"))
    tripwire = tmp_path / "tripwire.jsonl"

    with pytest.raises(GateError, match="section_09_lock_failure"):
        enforce_section_09_lock(PLAN_UNIT_ID, paths, tripwire_log_path=tripwire)

    [entry] = _tripwire_entries(tripwire)
    assert entry["failure_kind"] == "plan_unit_id_mismatch"


def test_section_09_lock_records_validation_error(tmp_path):
    paths = _artifact_paths(tmp_path)
    invalid = _gary_payload()
    invalid["slides"] = [{**invalid["slides"][0], "slide_index": 0}]  # type: ignore[index]
    _write_json(paths.gary_slide_content_path, invalid)
    tripwire = tmp_path / "tripwire.jsonl"

    with pytest.raises(GateError, match="section_09_lock_failure"):
        enforce_section_09_lock(PLAN_UNIT_ID, paths, tripwire_log_path=tripwire)

    [entry] = _tripwire_entries(tripwire)
    assert entry["failure_kind"] == "validation_error"


def test_section_09_lock_records_parse_error(tmp_path):
    paths = _artifact_paths(tmp_path)
    paths.vera_fidelity_verdict_path.write_text("{", encoding="utf-8", newline="\n")
    tripwire = tmp_path / "tripwire.jsonl"

    with pytest.raises(GateError, match="section_09_lock_failure"):
        enforce_section_09_lock(PLAN_UNIT_ID, paths, tripwire_log_path=tripwire)

    [entry] = _tripwire_entries(tripwire)
    assert entry["failure_kind"] == "parse_error"


def test_section_09_tripwire_line_is_deterministic_when_clock_is_fixed(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(section_09_lock, "_now_utc", lambda: FIXED_NOW)
    tripwire_a = tmp_path / "tripwire-a.jsonl"
    tripwire_b = tmp_path / "tripwire-b.jsonl"
    for tripwire in (tripwire_a, tripwire_b):
        paths = _artifact_paths(tmp_path / tripwire.stem)
        paths = paths.model_copy(
            update={"kira_motion_plan_path": tmp_path / "missing.json"}
        )
        with pytest.raises(GateError):
            enforce_section_09_lock(PLAN_UNIT_ID, paths, tripwire_log_path=tripwire)

    assert tripwire_a.read_bytes() == tripwire_b.read_bytes()


def test_section_09_lock_result_schema_hash_is_stable():
    schema = json.dumps(Section09LockResult.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH

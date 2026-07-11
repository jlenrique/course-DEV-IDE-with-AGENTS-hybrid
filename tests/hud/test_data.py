"""Unit tests for the explicit-path projection reader (Story 35.4; app/hud/data.py)."""

from __future__ import annotations

from app.hud.data import (
    PROJECTION_FILENAME,
    projection_etag,
    read_operator_surface,
    read_snapshot,
)
from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    Unrecognized,
)
from tests.hud._helpers import (
    build_registered_projection,
    write_projection,
    write_projection_file,
)


def test_absent_file_returns_none(run_dir) -> None:
    assert read_operator_surface(run_dir) is None
    assert read_snapshot(run_dir) is None


def test_valid_projection_parses_to_model(run_dir, bound_trial_id) -> None:
    write_projection(run_dir, build_registered_projection(trial_id=bound_trial_id, seq=4))
    result = read_operator_surface(run_dir)
    assert isinstance(result, OperatorSurfaceProjection)
    assert result.seq == 4
    assert result.identity.trial_id == bound_trial_id


def test_garbage_file_returns_unrecognized(run_dir) -> None:
    write_projection_file(run_dir, b"not json at all {{{")
    result = read_operator_surface(run_dir)
    assert isinstance(result, Unrecognized)


def test_snapshot_carries_raw_bytes_and_mtime(run_dir, bound_trial_id) -> None:
    raw = b'{"schema_version": "v1"}'  # unknown-status garbage-ish; still raw-preserved
    write_projection_file(run_dir, raw)
    snap = read_snapshot(run_dir)
    assert snap is not None
    assert snap.raw == raw
    assert snap.mtime_ns > 0
    # schema_version v1 but no valid envelope -> Unrecognized
    assert isinstance(snap.parsed, Unrecognized)


def test_projection_etag_uses_schema_version_and_seq(bound_trial_id) -> None:
    proj = build_registered_projection(trial_id=bound_trial_id, seq=9)
    assert projection_etag(proj) == "v1:9"


def test_projection_etag_unrecognized_uses_mtime(bound_trial_id) -> None:
    unrec = Unrecognized(reason="x", raw_value=None)
    assert projection_etag(unrec, mtime_ns=1234) == "unrecognized:1234"
    assert projection_etag(None, mtime_ns=None) == "unrecognized:0"


def test_reader_uses_explicit_filename(run_dir, bound_trial_id) -> None:
    path = write_projection(
        run_dir, build_registered_projection(trial_id=bound_trial_id)
    )
    assert path.name == PROJECTION_FILENAME

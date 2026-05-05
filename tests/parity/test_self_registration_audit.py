from __future__ import annotations

import json

from app.parity.contracts._audit import main, run_self_registration_audit
from app.parity.contracts._declaration import SurfaceTransportDeclaration
from app.parity.contracts._registry import (
    _clear_registered_surfaces_for_tests,
    register_surface,
)
from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests


def _clear_registries() -> None:
    _clear_registered_surfaces_for_tests()
    _clear_sanctum_alignments_for_tests()


def test_audit_empty_registries_floor_zero_passes(tmp_path):
    _clear_registries()
    result = run_self_registration_audit(
        declared_floor=0,
        manifest_path=tmp_path / "manifest.json",
        discovery_roots=(),
        include_reference_surface=False,
    )

    assert result.audit_status == "PASS"
    assert result.surface_cardinality == 0


def test_audit_empty_registries_floor_one_fails(tmp_path):
    _clear_registries()
    result = run_self_registration_audit(
        declared_floor=1,
        manifest_path=tmp_path / "manifest.json",
        discovery_roots=(),
        include_reference_surface=False,
    )

    assert result.audit_status == "FAIL"
    assert result.failure_reason


def test_audit_reflects_synthetic_surface_registration(tmp_path):
    _clear_registries()
    register_surface(
        SurfaceTransportDeclaration(surface_id="surface_a", mandatory_transports=["cli"])
    )

    result = run_self_registration_audit(
        declared_floor=1,
        manifest_path=tmp_path / "manifest.json",
        discovery_roots=(),
        include_reference_surface=False,
    )

    assert result.audit_status == "PASS"
    assert result.surface_cardinality == 1


def test_cli_exit_code_passes_for_floor_zero(tmp_path, capsys):
    _clear_registries()
    exit_code = main(
        [
            "--declared-floor",
            "0",
            "--manifest-path",
            (tmp_path / "manifest.json").as_posix(),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["audit_status"] == "PASS"


def test_cli_exit_code_fails_when_floor_not_met(tmp_path, capsys):
    _clear_registries()
    exit_code = main(
        [
            "--declared-floor",
            "99",
            "--manifest-path",
            (tmp_path / "manifest.json").as_posix(),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["audit_status"] == "FAIL"

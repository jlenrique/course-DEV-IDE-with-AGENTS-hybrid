from __future__ import annotations

import json

from app.parity.contracts import run_self_registration_audit
from app.parity.contracts._registry import _clear_registered_surfaces_for_tests

DISCOVERY_ROOTS = (
    "app.gates",
    "app.composers",
    "tests.integration.transport_parity",
    "tests.integration.transports",
)

EXPECTED_SURFACES = {
    "reference_7c0b_scaffold",
    "fastapi_mcp_parity",
    "mcp_stdio_smoke",
    "mcp_subprocess_hygiene",
    "transport_parity",
    "override_transport_parity",
    "cli_gate_decide",
    "http_gate_endpoint",
    "mcp_gate_decide_tool",
}


def test_transport_parity_dsl_self_registration_floor(tmp_path) -> None:
    _clear_registered_surfaces_for_tests()
    manifest_path = tmp_path / "manifest.json"
    result = run_self_registration_audit(
        declared_floor=9,
        manifest_path=manifest_path,
        discovery_roots=DISCOVERY_ROOTS,
    )

    assert result.audit_status == "PASS"
    assert result.surface_cardinality >= 9
    assert result.sanctum_cardinality == 0

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    surface_ids = {surface["surface_id"] for surface in payload["surfaces"]}
    assert EXPECTED_SURFACES.issubset(surface_ids)

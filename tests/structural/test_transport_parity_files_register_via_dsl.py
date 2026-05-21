from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from app.parity.contracts import iter_registered_surfaces
from app.parity.contracts._registry import _clear_registered_surfaces_for_tests

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    "tests/integration/transport_parity/test_fastapi_mcp_parity.py": {
        "module": "tests.integration.transport_parity.test_fastapi_mcp_parity",
        "surface_id": "fastapi_mcp_parity",
        "mandatory_transports": ["http", "mcp-stdio"],
    },
    "tests/integration/transport_parity/test_mcp_stdio_smoke.py": {
        "module": "tests.integration.transport_parity.test_mcp_stdio_smoke",
        "surface_id": "mcp_stdio_smoke",
        "mandatory_transports": ["mcp-stdio"],
    },
    "tests/integration/transport_parity/test_mcp_subprocess_hygiene.py": {
        "module": "tests.integration.transport_parity.test_mcp_subprocess_hygiene",
        "surface_id": "mcp_subprocess_hygiene",
        "mandatory_transports": ["mcp-subprocess"],
    },
    "tests/integration/transports/test_transport_parity.py": {
        "module": "tests.integration.transports.test_transport_parity",
        "surface_id": "transport_parity",
        "mandatory_transports": ["cli", "http", "mcp-stdio"],
    },
    "tests/integration/transports/test_override_transport_parity.py": {
        "module": "tests.integration.transports.test_override_transport_parity",
        "surface_id": "override_transport_parity",
        "mandatory_transports": ["cli", "http", "mcp-stdio"],
    },
    "tests/integration/transports/test_cli_gate_decide.py": {
        "module": "tests.integration.transports.test_cli_gate_decide",
        "surface_id": "cli_gate_decide",
        "mandatory_transports": ["cli"],
    },
    "tests/integration/transports/test_http_gate_endpoint.py": {
        "module": "tests.integration.transports.test_http_gate_endpoint",
        "surface_id": "http_gate_endpoint",
        "mandatory_transports": ["http"],
    },
    "tests/integration/transports/test_mcp_gate_decide_tool.py": {
        "module": "tests.integration.transports.test_mcp_gate_decide_tool",
        "surface_id": "mcp_gate_decide_tool",
        "mandatory_transports": ["mcp-stdio"],
    },
}


def _parity_contract_decorators(path: Path) -> list[ast.Call]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    decorators: list[ast.Call] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.ClassDef):
            continue
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and ast.unparse(decorator.func) == "parity_contract":
                decorators.append(decorator)
    return decorators


@pytest.mark.parametrize(("relative_path", "expected"), TARGETS.items())
def test_transport_parity_file_has_exactly_one_module_level_contract(
    relative_path: str,
    expected: dict[str, object],
) -> None:
    decorators = _parity_contract_decorators(REPO_ROOT / relative_path)
    assert len(decorators) == 1
    keywords = {keyword.arg: ast.literal_eval(keyword.value) for keyword in decorators[0].keywords}
    assert keywords["surface_id"] == expected["surface_id"]
    assert keywords["mandatory_transports"] == expected["mandatory_transports"]
    assert keywords["mandatory_transports"]


def test_transport_parity_files_register_expected_surfaces() -> None:
    _clear_registered_surfaces_for_tests()
    for expected in TARGETS.values():
        importlib.import_module(str(expected["module"]))

    surfaces = {surface.surface_id: surface for surface in iter_registered_surfaces()}
    assert set(surfaces) == {str(expected["surface_id"]) for expected in TARGETS.values()}
    for expected in TARGETS.values():
        surface = surfaces[str(expected["surface_id"])]
        assert surface.mandatory_transports == expected["mandatory_transports"]
        assert surface.optional_transports == []

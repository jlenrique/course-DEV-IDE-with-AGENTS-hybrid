from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.parity.contracts._audit import emit_registration_manifest
from app.parity.contracts._declaration import SurfaceTransportDeclaration
from app.parity.contracts._decorator import parity_contract
from app.parity.contracts._registry import (
    DuplicateSurfaceError,
    _clear_registered_surfaces_for_tests,
    iter_registered_surfaces,
    register_surface,
)


@pytest.fixture(autouse=True)
def clear_surface_registry():
    _clear_registered_surfaces_for_tests()
    yield
    _clear_registered_surfaces_for_tests()


def test_surface_transport_declaration_validates_valid_input():
    declaration = SurfaceTransportDeclaration(
        surface_id="section_02a_g0",
        mandatory_transports=["cli", "http"],
        optional_transports=["mcp-stdio"],
    )

    assert declaration.surface_id == "section_02a_g0"
    assert declaration.optional_transports == ["mcp-stdio"]


def test_surface_transport_declaration_accepts_valid_alias_of():
    declaration = SurfaceTransportDeclaration(
        surface_id="G0A",
        mandatory_transports=["cli"],
        alias_of="G1",
    )

    assert declaration.alias_of == "G1"


def test_surface_transport_declaration_rejects_invalid_alias_family():
    with pytest.raises(ValidationError):
        SurfaceTransportDeclaration(
            surface_id="G0A",
            mandatory_transports=["cli"],
            alias_of="G9",
        )


def test_surface_transport_declaration_alias_default_is_none():
    declaration = SurfaceTransportDeclaration(
        surface_id="surface_without_alias",
        mandatory_transports=["cli"],
    )

    assert declaration.alias_of is None


@pytest.mark.parametrize(
    "payload",
    [
        {"surface_id": "x", "mandatory_transports": [], "optional_transports": []},
        {
            "surface_id": "x",
            "mandatory_transports": ["cli"],
            "optional_transports": ["cli"],
        },
        {
            "surface_id": "x",
            "mandatory_transports": ["telepathy"],
            "optional_transports": [],
        },
    ],
)
def test_surface_transport_declaration_rejects_invalid_input(payload):
    with pytest.raises(ValidationError):
        SurfaceTransportDeclaration.model_validate(payload)


def test_parity_contract_decorator_registers_and_returns_wrapped_object():
    def handler() -> str:
        return "ok"

    decorated = parity_contract(
        surface_id="surface_a",
        mandatory_transports=["cli"],
        optional_transports=["http"],
    )(handler)

    assert decorated is handler
    assert [item.surface_id for item in iter_registered_surfaces()] == ["surface_a"]


def test_parity_contract_decorator_registers_alias_relationship():
    def handler() -> str:
        return "ok"

    parity_contract(
        surface_id="G0A",
        mandatory_transports=["cli"],
        alias_of="G1",
    )(handler)

    registered = list(iter_registered_surfaces())
    assert registered[0].surface_id == "G0A"
    assert registered[0].alias_of == "G1"


def test_register_surface_rejects_duplicate_surface_id():
    declaration = SurfaceTransportDeclaration(
        surface_id="surface_a",
        mandatory_transports=["cli"],
    )
    register_surface(declaration)

    with pytest.raises(DuplicateSurfaceError):
        register_surface(declaration)


def test_iter_registered_surfaces_returns_deterministic_order():
    register_surface(
        SurfaceTransportDeclaration(surface_id="surface_b", mandatory_transports=["cli"])
    )
    register_surface(
        SurfaceTransportDeclaration(surface_id="surface_a", mandatory_transports=["http"])
    )

    assert [item.surface_id for item in iter_registered_surfaces()] == [
        "surface_a",
        "surface_b",
    ]


def test_emit_registration_manifest_writes_stable_json(tmp_path):
    register_surface(
        SurfaceTransportDeclaration(
            surface_id="surface_a",
            mandatory_transports=["cli"],
            optional_transports=["http"],
        )
    )
    manifest_path = emit_registration_manifest(tmp_path / "manifest.json")

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert list(payload) == ["generated_at", "schema_version", "surfaces"]
    assert payload["schema_version"] == 1
    assert payload["surfaces"][0]["surface_id"] == "surface_a"

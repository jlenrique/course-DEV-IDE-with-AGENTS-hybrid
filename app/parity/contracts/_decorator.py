"""Decorator entry point for parity-contract self-registration."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from app.parity.contracts._declaration import (
    GateFamilyId,
    SurfaceTransportDeclaration,
    Transport,
)
from app.parity.contracts._registry import register_surface

Wrapped = TypeVar("Wrapped")


def parity_contract(
    *,
    surface_id: str,
    mandatory_transports: list[Transport],
    optional_transports: list[Transport] | None = None,
    alias_of: GateFamilyId | None = None,
) -> Callable[[Wrapped], Wrapped]:
    """Register a parity declaration and return the decorated object unchanged."""

    def _decorate(wrapped: Wrapped) -> Wrapped:
        declaration = SurfaceTransportDeclaration(
            surface_id=surface_id,
            mandatory_transports=mandatory_transports,
            optional_transports=optional_transports or [],
            alias_of=alias_of,
        )
        register_surface(declaration)
        return wrapped

    return _decorate


__all__ = ["parity_contract"]

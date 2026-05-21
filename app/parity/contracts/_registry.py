"""In-memory registry for parity-contract surface declarations."""

from __future__ import annotations

from collections.abc import Iterable

from app.parity.contracts._declaration import SurfaceTransportDeclaration

_REGISTERED_SURFACES: dict[str, SurfaceTransportDeclaration] = {}


class DuplicateSurfaceError(ValueError):
    """Raised when a surface_id is registered more than once."""


def register_surface(
    declaration: SurfaceTransportDeclaration,
) -> SurfaceTransportDeclaration:
    """Register one declaration, failing closed on duplicate surface IDs."""
    if declaration.surface_id in _REGISTERED_SURFACES:
        raise DuplicateSurfaceError(
            f"surface_id already registered: {declaration.surface_id}"
        )
    _REGISTERED_SURFACES[declaration.surface_id] = declaration
    return declaration


def iter_registered_surfaces() -> Iterable[SurfaceTransportDeclaration]:
    """Yield registered declarations in deterministic surface_id order."""
    for surface_id in sorted(_REGISTERED_SURFACES):
        yield _REGISTERED_SURFACES[surface_id]


def _clear_registered_surfaces_for_tests() -> None:
    _REGISTERED_SURFACES.clear()


__all__ = [
    "DuplicateSurfaceError",
    "iter_registered_surfaces",
    "register_surface",
]

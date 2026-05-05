"""Public parity-contract DSL surface."""

from app.parity.contracts._declaration import SurfaceTransportDeclaration
from app.parity.contracts._decorator import parity_contract
from app.parity.contracts._registry import (
    DuplicateSurfaceError,
    iter_registered_surfaces,
    register_surface,
)
from app.parity.contracts._sanctum import (
    DuplicateSanctumAlignmentError,
    SanctumAlignmentDeclaration,
    declare_sanctum_alignment,
    emit_sanctum_alignment_manifest,
    iter_sanctum_alignments,
)

_AUDIT_EXPORTS = {
    "AuditResult",
    "emit_registration_manifest",
    "run_self_registration_audit",
}


def __getattr__(name: str):
    if name in _AUDIT_EXPORTS:
        from app.parity.contracts import _audit

        return getattr(_audit, name)
    raise AttributeError(name)


__all__ = [
    "AuditResult",
    "DuplicateSanctumAlignmentError",
    "DuplicateSurfaceError",
    "SanctumAlignmentDeclaration",
    "SurfaceTransportDeclaration",
    "declare_sanctum_alignment",
    "emit_registration_manifest",
    "emit_sanctum_alignment_manifest",
    "iter_registered_surfaces",
    "iter_sanctum_alignments",
    "parity_contract",
    "register_surface",
    "run_self_registration_audit",
]

"""Audit-chain integrity exceptions."""


class AuditChainIntegrityError(Exception):
    """Root exception for audit-chain integrity violations (FR-7c-50)."""


class AuditChainOrderError(AuditChainIntegrityError):
    """Out-of-order timestamp for a tripwire_id in the ledger."""


class AuditChainParentLinkError(AuditChainIntegrityError):
    """Missing parent trace_id when fired_verdict is 'fired' or 'marginal-fired'."""


__all__ = [
    "AuditChainIntegrityError",
    "AuditChainOrderError",
    "AuditChainParentLinkError",
]

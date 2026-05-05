"""Pure audit-chain integrity checks for TripwireLedgerEntry rows."""

from __future__ import annotations

from app.audit.errors import AuditChainOrderError, AuditChainParentLinkError
from app.models.tripwire_ledger import TripwireLedgerEntry

_FIRE_VERDICTS = {"fired", "marginal-fired"}


def verify_audit_chain(entries: list[TripwireLedgerEntry]) -> None:
    """Validate monotonic per-tripwire order and fired-verdict trace linkage."""
    last_fired_at_by_tripwire: dict[str, object] = {}
    for index, entry in enumerate(entries):
        tripwire_id = entry.tripwire_id.value
        previous_fired_at = last_fired_at_by_tripwire.get(tripwire_id)
        if previous_fired_at is not None and entry.fired_at <= previous_fired_at:
            raise AuditChainOrderError(
                f"entry {index} for {tripwire_id} is not monotonic by fired_at"
            )
        last_fired_at_by_tripwire[tripwire_id] = entry.fired_at
        if entry.fired_verdict in _FIRE_VERDICTS and entry.trace_id is None:
            raise AuditChainParentLinkError(
                f"entry {index} for {tripwire_id} is missing trace_id"
            )


__all__ = ["verify_audit_chain"]

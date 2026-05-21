"""App-namespace Marcus dispatch contract surface."""

from app.marcus.dispatch.contract import (
    DispatchEnvelope,
    DispatchKind,
    DispatchOutcome,
    DispatchReceipt,
    build_dispatch_envelope,
    build_dispatch_receipt,
)

__all__ = [
    "DispatchEnvelope",
    "DispatchKind",
    "DispatchOutcome",
    "DispatchReceipt",
    "build_dispatch_envelope",
    "build_dispatch_receipt",
]

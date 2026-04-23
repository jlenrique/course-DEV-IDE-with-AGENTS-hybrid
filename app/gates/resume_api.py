"""`app.gates.resume_api` — HIL verdict-resume substrate (architecture D3, FR34).

**Slab 1 substrate stub.** The three authorized verdict-bridge modules named
in architecture §D3 (MCP tool `gate_decide`, FastAPI endpoint `gate_endpoint`,
CLI `gate_cli`) will call `resume_from_verdict()` to re-enter a paused graph
with an operator verdict. The bridge modules do not exist yet — they ship in
Slab 3 Story 3.3. This stub exists at Slab 1 so:

1. Import-linter Contract C3 has a concrete symbol to constrain (the three
   bridge modules as the ONLY permitted importers of this module).
2. `OperatorVerdict` from 1.2 has a typed consumer surface documented at the
   substrate layer, not deferred.
3. The tamper-evidence chain has a named entry point the ledger can track.

The function body is a named `NotImplementedError` — reaching it at runtime in
Slab 1 is a bug (no specialist has paused a graph yet). Slab 3 Story 3.3
replaces the body with the real resume path; the **signature is stable** so
C3 binds to the same symbol throughout.

Scheduler-import ban per Contract C2 forbids `app.gates.**` from importing
`threading` / `apscheduler` / `schedule`. Slab 3's real implementation
likewise must not spawn scheduler threads — verdict resume is operator-driven
only (no auto-approve path, FR34).
"""

from __future__ import annotations

from typing import NoReturn

from app.models.state.operator_verdict import OperatorVerdict


def resume_from_verdict(verdict: OperatorVerdict) -> NoReturn:
    """Resume a paused graph with an operator verdict (Slab 3 Story 3.3 wires the body).

    Args:
        verdict: A validated `OperatorVerdict` from the operator bridge layer.
            The verb (`approve` / `edit` / `reject`) determines the resume path.

    Raises:
        NotImplementedError: Always. Slab 1 ships the substrate stub; Slab 3
            replaces the body. The signature is stable so import-linter
            Contract C3 binds to the same symbol throughout.
    """
    raise NotImplementedError(
        "app.gates.resume_api.resume_from_verdict is a Slab 1 substrate stub. "
        "Slab 3 Story 3.3 wires the real resume path. "
        f"Received verdict: verb={verdict.verb!r} gate_id={verdict.gate_id!r}"
    )


__all__ = ["resume_from_verdict"]

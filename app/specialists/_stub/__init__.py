"""Passthrough specialist stub namespace (Slab 1 Story 1.6).

Slab 2 specialist migrations replace `passthrough_node` with real 9-node
specialist scaffolds under `app.specialists.{name}.graph`. 1.6 ships the
passthrough so the migrated v4.2 manifest can load + compile + run §01→§15
before any real specialist exists.
"""

from app.specialists._stub.passthrough_specialist import (
    PASSTHROUGH_SPECIALIST_ID,
    passthrough_node,
)

__all__ = ["PASSTHROUGH_SPECIALIST_ID", "passthrough_node"]

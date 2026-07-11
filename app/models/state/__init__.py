"""State model package — Slab 1 substrate (Story 1.2).

Eight Pydantic v2 state models + one stub (`ModelResolutionEntry`, replaced
by Story 1.3) that together encode the LangGraph state contract every
downstream handler reads + writes against. Each model ships with a
companion validator file under `app.models.state.validators` per NFR-M5
four-file-lockstep, plus shape-pin tests + golden fixtures + schema-pin
fixtures under `tests/unit/models/state/` and `tests/fixtures/models/state/`.

Reproducibility invariants encoded here:
- **NFR-X1** byte-for-byte replay — `RunState`/`StoryState` round-trip
- **NFR-X2** frozen graph version — `RunState.graph_version` (stub registry,
  Slab 4 Story 4.5 wires the real one)
- **NFR-X3** sanctum snapshot identity — `SanctumFingerprint`
- **NFR-X4** model selection trail — `RunState.model_resolution_trail`
  (`ModelResolutionEntry` stub, Story 1.3 replaces)
- **NFR-X5** documented temperature variance — `RunState.temperature` (0.0–2.0)
"""

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.node_checkpoint import NodeCheckpoint, NodeCheckpointStatus
from app.models.state.operator_verdict import OperatorVerdict, OperatorVerdictVerb
from app.models.state.run_state import ALLOWED_GRAPH_VERSIONS, LlmExecutionMode, RunState, RunStatus
from app.models.state.sanctum_fingerprint import SanctumFingerprint
from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn, SpecialistReturnVerb
from app.models.state.story_state import StoryState

__all__ = [
    "ALLOWED_GRAPH_VERSIONS",
    "CacheState",
    "LlmExecutionMode",
    "ModelResolutionEntry",
    "NodeCheckpoint",
    "NodeCheckpointStatus",
    "OperatorVerdict",
    "OperatorVerdictVerb",
    "RunState",
    "RunStatus",
    "SanctumFingerprint",
    "SpecialistEnvelope",
    "SpecialistReturn",
    "SpecialistReturnVerb",
    "StoryState",
]

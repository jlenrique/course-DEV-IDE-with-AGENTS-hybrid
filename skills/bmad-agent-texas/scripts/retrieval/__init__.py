"""Texas retrieval foundation — Shape 3-Disciplined contract.

Story 27-0 (Epic 27 Texas Intake Surface Expansion). See
`_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md` for
the full contract specification and Round-3 party-mode consensus record.

The retrieval subsystem partitions source-fetch work by knowledge-locality:

- **Editorial knowledge** (intent, acceptance criteria, provider choice) lives
  with Tracy (Epic 28 agent) — she authors `RetrievalIntent` objects.
- **Provider-DSL knowledge** (query formulation, fetch, pagination, native
  signal filtering) lives in per-provider `RetrievalAdapter` subclasses.
- **Dispatch + iteration orchestration** lives in this package's `dispatcher`
  module — thin routing layer with cross-validation fan-out support.

No real provider ships in 27-0. `FakeProvider` is the reference adapter
for contract-validation tests. Real providers land in follow-on stories:
scite (27-2), Consensus (27-2.5), image-sources (27-3), YouTube (27-4).

A unified `provider_directory` surfaces every retrieval-shape adapter AND
every locator-shape handler Texas can invoke (AC-B.8 operator amendment,
2026-04-18). Use `provider_directory.list_providers()` for the canonical
roster; `run_wrangler.py --list-providers` for CLI.
"""

from .base import RetrievalAdapter

# Story 27-2 Winston SHOULD-FIX: eager import of SciteProvider so
# `list_providers()` reflects the registered adapter on first call, independent
# of import-order. `__init_subclass__` registration still runs; this import
# just guarantees the class is loaded.
from .consensus_provider import ConsensusProvider  # noqa: E402,F401
from .contracts import (
    SCHEMA_VERSION,
    AcceptanceCriteria,
    ConvergenceSignal,
    ProviderHint,
    ProviderInfo,
    ProviderResult,
    ProviderShape,
    ProviderStatus,
    RefinementLogEntry,
    RetrievalIntent,
    RetrievalKind,
    SourceOrigin,
    TexasRow,
)
from .dispatcher import AdapterFactory, DispatchError, dispatch
from .mcp_client import (
    MCPAuthError,
    MCPClient,
    MCPClientError,
    MCPFetchError,
    MCPProtocolError,
    MCPRateLimitError,
    MCPServerConfig,
)
from .normalize import build_texas_row, coerce_authors
from .provider_directory import (
    get_provider,
    get_registered_adapter_class,
    list_providers,
    register_adapter,
    reset_adapter_registry,
)
from .refinement_registry import (
    RefinementStrategy,
    drop_filters_in_order,
    get_strategy,
    list_strategies,
    register_strategy,
)
from .scite_provider import SciteProvider  # noqa: E402,F401

__all__ = [
    "AcceptanceCriteria",
    "AdapterFactory",
    "ConsensusProvider",
    "ConvergenceSignal",
    "DispatchError",
    "MCPAuthError",
    "MCPClient",
    "MCPClientError",
    "MCPFetchError",
    "MCPProtocolError",
    "MCPRateLimitError",
    "MCPServerConfig",
    "ProviderHint",
    "ProviderInfo",
    "ProviderResult",
    "ProviderShape",
    "ProviderStatus",
    "RefinementLogEntry",
    "RefinementStrategy",
    "RetrievalAdapter",
    "RetrievalIntent",
    "RetrievalKind",
    "SCHEMA_VERSION",
    "SciteProvider",
    "SourceOrigin",
    "TexasRow",
    "build_texas_row",
    "coerce_authors",
    "dispatch",
    "drop_filters_in_order",
    "get_provider",
    "get_registered_adapter_class",
    "get_strategy",
    "list_providers",
    "list_strategies",
    "register_adapter",
    "register_strategy",
    "reset_adapter_registry",
]

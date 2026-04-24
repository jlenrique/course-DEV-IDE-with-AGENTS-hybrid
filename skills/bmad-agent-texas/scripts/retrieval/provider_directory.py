"""Texas provider directory — AC-B.8 (operator amendment, Story 27-0).

Single runtime surface enumerating everything Texas can fetch. Two population
paths:

1. **Retrieval-shape adapters** (scite, Consensus, YouTube, image, future LLM
   providers) auto-register via `RetrievalAdapter.__init_subclass__` when the
   subclass declares a `PROVIDER_INFO: ClassVar[ProviderInfo]`.

2. **Locator-shape handlers** (pdf, docx, md, html, notion, box, playwright)
   are declared statically below in `_LOCATOR_SHAPE_DIRECTORY`. These mirror
   the `LOCATOR_SHAPE_PROVIDERS` classification dict in
   `tests/contracts/test_transform_registry_lockstep.py` and are kept in
   lockstep by `test_provider_directory_locator_lockstep.py` (AC-T.10).

**Forward-looking placeholders** (backlog/ratified status) reserve directory
IDs for providers the team has explicitly ratified but not yet built
(`openai-chatgpt` per operator directive, 2026-04-18, plus future retrieval
surfaces). As each story lands and an adapter is authored (for example,
scite/Consensus in Epic 27), the registered adapter's `PROVIDER_INFO`
supersedes the placeholder; `test_provider_directory_roster_placeholders.py`
(AC-T.11) prevents silent-drop of placeholders.
"""

from typing import TYPE_CHECKING

from .contracts import ProviderInfo, ProviderShape, ProviderStatus

if TYPE_CHECKING:
    pass


_RETRIEVAL_ADAPTER_REGISTRY: dict[str, tuple[type, ProviderInfo]] = {}
"""Populated by `RetrievalAdapter.__init_subclass__` via `register_adapter`."""


_LOCATOR_SHAPE_DIRECTORY: tuple[ProviderInfo, ...] = (
    ProviderInfo(
        id="local_file",
        shape="locator",
        status="ready",
        capabilities=["text-read", "encoding-detect"],
        auth_env_vars=[],
        spec_ref=None,
        notes="Generic local text-file read; fallback extractor.",
    ),
    ProviderInfo(
        id="pdf",
        shape="locator",
        status="ready",
        capabilities=["text-extract", "page-count", "stub-detect"],
        auth_env_vars=[],
        spec_ref=None,
        notes="pypdf default; pdfplumber fallback (transform-registry.md PDF section).",
    ),
    ProviderInfo(
        id="docx",
        shape="locator",
        status="ready",
        capabilities=["text-extract", "headings", "tables-flattened"],
        auth_env_vars=[],
        spec_ref="_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md",
        notes="python-docx 1.2.0; wired 2026-04-17 via Story 27-1.",
    ),
    ProviderInfo(
        id="md",
        shape="locator",
        status="ready",
        capabilities=["text-read", "backslash-unescape"],
        auth_env_vars=[],
        spec_ref=None,
        notes="Direct read; escaped-markdown normalization in extract step.",
    ),
    ProviderInfo(
        id="html",
        shape="locator",
        status="ready",
        capabilities=["text-extract", "http-get"],
        auth_env_vars=[],
        spec_ref=None,
        notes=(
            "requests + HTML-to-text; fails on JS-rendered SPAs "
            "(fall through to playwright_html)."
        ),
    ),
    ProviderInfo(
        id="playwright_html",
        shape="locator",
        status="ready",
        capabilities=["dynamic-render", "js-spa", "auth-walled-offline-save"],
        auth_env_vars=[],
        spec_ref=None,
        notes="User-level Playwright MCP; offline re-extract of saved pages.",
    ),
    ProviderInfo(
        id="notion",
        shape="locator",
        status="ready",
        capabilities=["page-fetch", "database-query"],
        auth_env_vars=["NOTION_API_KEY"],
        spec_ref=None,
        notes="Notion direct REST API. Distinct from ratified notion-mcp provider (27-5).",
    ),
    ProviderInfo(
        id="box",
        shape="locator",
        status="ready",
        capabilities=["local-fs-read"],
        auth_env_vars=[],
        spec_ref=None,
        notes=(
            "Box Drive local filesystem sync. Distinct from ratified "
            "box credentialed-fetch provider (27-6)."
        ),
    ),
    # Ratified locator-shape stubs — stories exist; implementation pending.
    ProviderInfo(
        id="notion_mcp",
        shape="locator",
        status="ratified",
        capabilities=["page-fetch", "database-query", "mcp-mediated"],
        auth_env_vars=["NOTION_API_KEY"],
        spec_ref="_bmad-output/implementation-artifacts/27-5-notion-mcp-provider.md",
        notes=(
            "Epic 27 Story 27-5 ratified-stub, 3 pts. MCP-mediated Notion "
            "access distinct from direct-API notion provider."
        ),
    ),
    ProviderInfo(
        id="box_api",
        shape="locator",
        status="ratified",
        capabilities=["credentialed-fetch"],
        auth_env_vars=["BOX_CLIENT_ID", "BOX_CLIENT_SECRET"],
        spec_ref="_bmad-output/implementation-artifacts/27-6-box-provider.md",
        notes=(
            "Epic 27 Story 27-6 ratified-stub, 2 pts. Fetch-layer; "
            "extraction delegated to existing format handlers."
        ),
    ),
    ProviderInfo(
        id="playwright_mcp",
        shape="locator",
        status="ratified",
        capabilities=["dynamic-render", "mcp-mediated"],
        auth_env_vars=[],
        spec_ref="_bmad-output/implementation-artifacts/27-7-playwright-mcp-provider.md",
        notes=(
            "Epic 27 Story 27-7 ratified-stub, 3 pts. MCP-mediated sibling "
            "to existing playwright_html."
        ),
    ),
)


_RETRIEVAL_SHAPE_PLACEHOLDERS: tuple[ProviderInfo, ...] = (
    ProviderInfo(
        id="scite",
        shape="retrieval",
        status="ratified",
        capabilities=["citation-network", "supporting-contrasting-counts", "authority-tier"],
        auth_env_vars=["SCITE_USER_NAME", "SCITE_PASSWORD"],
        spec_ref="_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md",
        notes="Epic 27 Story 27-2 ratified. First retrieval-shape adapter against 27-0 contract.",
    ),
    ProviderInfo(
        id="consensus",
        shape="retrieval",
        status="ratified",
        capabilities=["evidence-synthesis", "meta-analysis", "cross-validation-partner-to-scite"],
        auth_env_vars=[
            "CONSENSUS_API_KEY",
            "CONSENSUS_USER_NAME",
            "CONSENSUS_PASSWORD",
        ],
        spec_ref="_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md",
        notes=(
            "Epic 27 Story 27-2.5 ratified-stub, 3 pts. Operator-directed "
            "cross-validation partner to scite."
        ),
    ),
    ProviderInfo(
        id="image",
        shape="retrieval",
        status="ratified",
        capabilities=["image-search", "sensory-bridges-integration"],
        auth_env_vars=[],
        spec_ref="_bmad-output/implementation-artifacts/27-3-image-provider.md",
        notes="Epic 27 Story 27-3 ratified-stub, 3 pts. Closes half of visual-source-gap backlog.",
    ),
    ProviderInfo(
        id="youtube",
        shape="retrieval",
        status="ratified",
        capabilities=["video-search", "audio-extract", "transcript-fetch"],
        auth_env_vars=["YOUTUBE_API_KEY"],
        spec_ref="_bmad-output/implementation-artifacts/27-4-youtube-provider.md",
        notes=(
            "Epic 27 Story 27-4 ratified-stub, 5 pts. Three-asset output "
            "(video + audio + transcript)."
        ),
    ),
    # Backlog placeholder per operator directive (2026-04-18). Not in Epic 27
    # roster yet; reserved to prevent directory-surface silence and signal
    # forward intent for a future LLM-research-assistant adapter.
    ProviderInfo(
        id="openai_chatgpt",
        shape="retrieval",
        status="backlog",
        capabilities=["llm-research-assist", "synthesis", "hypothesis-generation"],
        auth_env_vars=["OPENAI_API_KEY"],
        spec_ref=None,
        notes=(
            "Backlog placeholder per operator directive 2026-04-18. Distinct from provider "
            "adapters with deterministic DSLs — any LLM-in-the-loop adapter requires its "
            "own eval framework per Dr. Quinn guardrail (no LLM in query formulation v1). "
            "Promote to ratified story when eval-framework scope authored."
        ),
    ),
)


def register_adapter(cls: type, info: ProviderInfo) -> None:
    """Register a `RetrievalAdapter` subclass's `PROVIDER_INFO` in the runtime registry.

    Called automatically by `RetrievalAdapter.__init_subclass__`. Idempotent
    on the same class (overwrite permitted for module-reload scenarios);
    raises `ValueError` if a different class attempts to claim an already
    registered provider ID.
    """
    existing = _RETRIEVAL_ADAPTER_REGISTRY.get(info.id)
    if existing is not None and existing[0] is not cls:
        raise ValueError(
            f"Provider ID {info.id!r} is already registered by "
            f"{existing[0].__name__}; {cls.__name__} cannot re-register it. "
            f"Use a distinct PROVIDER_INFO.id."
        )
    _RETRIEVAL_ADAPTER_REGISTRY[info.id] = (cls, info)


def reset_adapter_registry() -> None:
    """Clear the runtime adapter registry. Intended for tests only."""
    _RETRIEVAL_ADAPTER_REGISTRY.clear()


def get_registered_adapter_class(provider_id: str) -> type | None:
    """Return the `RetrievalAdapter` subclass registered under `provider_id`, or None."""
    entry = _RETRIEVAL_ADAPTER_REGISTRY.get(provider_id)
    return entry[0] if entry is not None else None


def list_providers(
    *,
    shape: ProviderShape | None = None,
    status: ProviderStatus | None = None,
) -> list[ProviderInfo]:
    """Return the unified provider directory, optionally filtered by shape/status.

    Merge order:
      1. Registered retrieval-shape adapters (live `PROVIDER_INFO` from subclasses).
      2. Ratified / backlog retrieval-shape placeholders (only if no live adapter
         has claimed the same `id`).
      3. Static locator-shape declarations.

    Sorted by `(shape, id)` for deterministic output.
    """
    seen: set[str] = set()
    out: list[ProviderInfo] = []

    # Merge order matters: a live registered adapter SUPERSEDES a backlog or
    # ratified placeholder that claims the same id. When 27-2/27-2.5 ship live
    # scite/consensus adapters, registered PROVIDER_INFO wins over placeholder
    # entries in _RETRIEVAL_SHAPE_PLACEHOLDERS — no directory drift.
    for _cls, info in _RETRIEVAL_ADAPTER_REGISTRY.values():
        if info.id in seen:
            continue
        seen.add(info.id)
        out.append(info)

    for info in _RETRIEVAL_SHAPE_PLACEHOLDERS:
        if info.id in seen:
            continue
        seen.add(info.id)
        out.append(info)

    for info in _LOCATOR_SHAPE_DIRECTORY:
        if info.id in seen:
            continue
        seen.add(info.id)
        out.append(info)

    if shape is not None:
        out = [p for p in out if p.shape == shape]
    if status is not None:
        out = [p for p in out if p.status == status]

    out.sort(key=lambda p: (p.shape, p.id))
    return out


def get_provider(provider_id: str) -> ProviderInfo | None:
    """Return the `ProviderInfo` for `provider_id`, or None if not declared."""
    for info in list_providers():
        if info.id == provider_id:
            return info
    return None


__all__ = [
    "get_provider",
    "get_registered_adapter_class",
    "list_providers",
    "register_adapter",
    "reset_adapter_registry",
]

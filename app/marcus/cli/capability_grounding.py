"""Capability grounding — Marcus's honesty spine for the S5 interlocutor.

Builds a FACT-bound grounding context from the S4-generated capability overlay
(`state/config/capability-overlay.yaml`: per-specialist ``capability_state`` +
rationale + ``routed_at_nodes``). Marcus's LLM context is anchored on this map so
he answers "can you do X?" from the real dispatch graph, never up-leveling a
state (A9 / G-honest).

Beyond ``capability_state`` this carries:

- **Runtime-precondition flags (A9).** A capability can be ``wired`` in the
  dispatch graph yet blocked at runtime by a missing credential/token (live
  research before the scite OAuth token is set). The grounding context surfaces
  that as ``runtime_precondition`` so the honest read is "on the run path but
  blocked right now pending the research token," NOT a flat "yes."

- **Stale-overlay disclosure (A9).** If the committed overlay diverges from a
  fresh derivation (S4 CI parity hash fails), the context discloses Marcus is
  answering from a possibly-stale map, not asserting it as live fact.

Everything here is **pure** (no model call, no network): :func:`build_grounding_context`
takes the loaded overlay mapping + precondition facts + a ``stale`` boolean and
returns a deterministic, unit-testable context block. The interactive entrypoint
computes ``stale`` (via the S4 ``is_stale`` helper) and the runtime preconditions
(token presence) and injects them; offline tests inject fixtures.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app.runtime.economics import REPO_ROOT

DEFAULT_OVERLAY_PATH = REPO_ROOT / "state" / "config" / "capability-overlay.yaml"
SCITE_OAUTH_TOKEN_PATH = REPO_ROOT / "secrets" / "scite_oauth_token.json"

# The specialist whose `wired` state is additionally gated by a live credential.
# `texas` is the WIRED research-dispatch path (routed at manifest nodes 02/03) that
# calls scite/consensus — so "run live research now" honestly reads "on the run path
# (wired) but BLOCKED pending the research token" when the credential is absent.
# Do NOT attach the precondition to `tracy`/`aria` (both `present-but-unrouted`):
# overriding an un-routed state with "on the run path … blocked" would mis-read them
# as routed (T11 code-review, 2026-06-25). They keep their true present-but-unrouted read.
_RESEARCH_SPECIALISTS: frozenset[str] = frozenset({"texas"})


@dataclass(frozen=True)
class RuntimePrecondition:
    """A live precondition that gates an otherwise-routable capability.

    ``satisfied=False`` means the capability is on the run path (per the overlay)
    but blocked right now until the operator provides the named credential.
    """

    name: str
    satisfied: bool
    detail: str


@dataclass(frozen=True)
class CapabilityFact:
    """The honest, FACT-bound view of one specialist's capability."""

    specialist_id: str
    capability_state: str
    rationale: str
    routed_at_nodes: tuple[str, ...] = ()
    runtime_precondition: RuntimePrecondition | None = None

    @property
    def honest_summary(self) -> str:
        """One-line honest read — never up-levels the state."""
        if self.runtime_precondition is not None and not self.runtime_precondition.satisfied:
            return (
                f"{self.specialist_id}: on the run path ({self.capability_state}) "
                f"but BLOCKED right now pending {self.runtime_precondition.name} "
                f"({self.runtime_precondition.detail})"
            )
        return f"{self.specialist_id}: {self.capability_state} — {self.rationale}"


@dataclass(frozen=True)
class GroundingContext:
    """The full FACT-bound grounding block injected into Marcus's LLM context."""

    facts: dict[str, CapabilityFact]
    stale: bool = False
    content_hash: str = ""
    extra_preconditions: tuple[RuntimePrecondition, ...] = field(default_factory=tuple)

    def fact_for(self, specialist_id: str) -> CapabilityFact | None:
        return self.facts.get(specialist_id)

    def render(self) -> str:
        """Render the grounding block as plain text for the system prompt."""
        lines: list[str] = ["CAPABILITY GROUNDING (the honest, generated map — answer from THIS):"]
        if self.stale:
            lines.append(
                "  ⚠ STALE-MAP DISCLOSURE: the capability overlay diverges from a fresh "
                "derivation (CI parity hash failed). Answer from a possibly-stale map; "
                "do NOT assert these as live fact without flagging the staleness."
            )
        if self.content_hash:
            lines.append(f"  overlay content_hash: {self.content_hash}")
        for fact in sorted(self.facts.values(), key=lambda f: f.specialist_id):
            nodes = f" routed_at={list(fact.routed_at_nodes)}" if fact.routed_at_nodes else ""
            lines.append(f"  - {fact.honest_summary}{nodes}")
        return "\n".join(lines)


def load_overlay(path: Path = DEFAULT_OVERLAY_PATH) -> dict[str, Any]:
    """Load the generated capability overlay mapping from disk."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"capability overlay at {path} did not parse to a mapping")
    return payload


def research_token_precondition(
    *,
    scite_token_path: Path = SCITE_OAUTH_TOKEN_PATH,
    consensus_api_key_env: str = "CONSENSUS_API_KEY",
    env: dict[str, str] | None = None,
) -> RuntimePrecondition:
    """Compute the live-research precondition (scite OAuth token / CONSENSUS key).

    Live research is ``wired`` in the overlay but blocked when the scite OAuth
    token is absent AND ``CONSENSUS_API_KEY`` is unset (memory
    ``project_scite_mcp_oauth_not_basic``). Pure given its injected inputs.
    """
    environ = env if env is not None else dict(os.environ)
    has_scite = scite_token_path.is_file()
    has_consensus = bool(environ.get(consensus_api_key_env))
    satisfied = has_scite or has_consensus
    if satisfied:
        detail = "research credential present (scite token or CONSENSUS_API_KEY)"
    else:
        detail = (
            "scite OAuth token absent and CONSENSUS_API_KEY unset — run "
            "`python -m scripts.operator.scite_oauth_login` or set CONSENSUS_API_KEY"
        )
    return RuntimePrecondition(
        name="the research token",
        satisfied=satisfied,
        detail=detail,
    )


def build_grounding_context(
    overlay: dict[str, Any],
    *,
    stale: bool = False,
    research_precondition: RuntimePrecondition | None = None,
) -> GroundingContext:
    """Build the FACT-bound grounding context (PURE — no model call, no network).

    ``overlay`` is the loaded ``capability-overlay.yaml`` mapping. ``stale`` is the
    CI-parity result (injected; ``True`` triggers the A9 disclosure). The builder
    NEVER up-levels a state: each specialist's ``capability_state`` is copied
    verbatim. ``research_precondition`` (A9) is attached to the research-path
    specialists so a ``wired``-but-token-gated capability reads honestly.
    """
    specialists = overlay.get("specialists") or {}
    facts: dict[str, CapabilityFact] = {}
    for specialist_id, entry in specialists.items():
        if not isinstance(entry, dict):
            continue
        precondition = None
        if research_precondition is not None and specialist_id in _RESEARCH_SPECIALISTS:
            precondition = research_precondition
        routed = entry.get("routed_at_nodes") or []
        facts[specialist_id] = CapabilityFact(
            specialist_id=specialist_id,
            capability_state=str(entry.get("capability_state", "unknown")),
            rationale=str(entry.get("rationale", "")),
            routed_at_nodes=tuple(str(n) for n in routed),
            runtime_precondition=precondition,
        )
    extra = (research_precondition,) if research_precondition is not None else ()
    return GroundingContext(
        facts=facts,
        stale=stale,
        content_hash=str(overlay.get("content_hash", "")),
        extra_preconditions=extra,
    )


__all__ = [
    "CapabilityFact",
    "GroundingContext",
    "RuntimePrecondition",
    "build_grounding_context",
    "load_overlay",
    "research_token_precondition",
    "SCITE_OAUTH_TOKEN_PATH",
    "DEFAULT_OVERLAY_PATH",
]

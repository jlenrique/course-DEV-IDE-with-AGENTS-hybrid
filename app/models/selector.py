"""`app.models.selector` — three-level model-cascade resolver (Story 1.3, FR17–FR21).

Cascade order per architecture §D2:
  1. **per_call** — explicit `per_call_override` argument
  2. **per_specialist** — specialist's `model_config.yaml::default_model`
  3. **registry_default** — `PipelineRegistry.default_model_id`
  4. **auto_select_fallback** — `ModelSelectionPolicy` rule-driven (only if
     `auto_select_enabled=True` on the registry)

Each level that fires produces a `ModelResolutionEntry` capturing the
requested + resolved + reason + timestamp + (final-level only)
`cache_prefix_hash`. The selector returns the model_id + the entry; the
adapter is responsible for appending to `RunState.model_resolution_trail`.

NFR-I6 cache-prefix stability: `_compute_cache_prefix_hash` is deterministic
SHA-256 over a sorted-keys canonical-JSON tuple — same inputs ALWAYS produce
the same hash across processes. Do NOT use Python's `hash()` (process-randomized).

# FR24 cache-invalidation warning surface deferred to Slab 3 Story 3.5.
# Slab 1 captures the resolution trail so 3.5 can surface the warning at runtime.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

import yaml

from app.models.registry import PipelineRegistry
from app.models.selection_policy import ModelSelectionPolicy
from app.models.specialist_model_config import SpecialistModelConfig
from app.models.state.model_resolution_entry import ModelResolutionEntry, ResolutionLevel

REGISTRY_PATH: Path = Path(__file__).resolve().parent / "registry.yaml"
SELECTION_POLICY_PATH: Path = Path(__file__).resolve().parent / "selection_policy.yaml"
SPECIALISTS_DIR: Path = Path(__file__).resolve().parent.parent / "specialists"

_SPECIALIST_ID_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_-]+$")
"""Allowed characters for `specialist_id` (path-traversal prevention)."""


class ResolveResult(NamedTuple):
    """Result of a cascade resolution: the resolved model_id + audit entry."""

    model_id: str
    entry: ModelResolutionEntry


class ModelResolutionError(RuntimeError):
    """Raised when the cascade cannot resolve to any model_id (named, not silent)."""


def _compute_cache_prefix_hash(
    *,
    specialist_id: str,
    model_id: str,
    temperature: float,
    system_prompt_hash: str = "",
) -> str:
    """Deterministic SHA-256 over the canonical-JSON cache-prefix tuple (NFR-I6).

    Uses `json.dumps(..., sort_keys=True)` so key insertion order does not
    affect the hash. Returns lowercase-hex 64-char SHA-256.
    """
    canonical = json.dumps(
        {
            "specialist_id": specialist_id,
            "model_id": model_id,
            "temperature": temperature,
            "system_prompt_hash": system_prompt_hash,
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _load_registry(path: Path | None = None) -> PipelineRegistry:
    """Read REGISTRY_PATH (or override) at call time so test-side monkey-patches take effect.

    Default arguments bind at function-definition time in Python; reading the
    module-level constant inside the function body picks up rebindings via
    `selector.REGISTRY_PATH = ...` in tests.
    """
    resolved = path if path is not None else REGISTRY_PATH
    raw = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    return PipelineRegistry.model_validate(raw)


def _load_policy(path: Path | None = None) -> ModelSelectionPolicy:
    """Read SELECTION_POLICY_PATH (or override) at call time."""
    resolved = path if path is not None else SELECTION_POLICY_PATH
    raw = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    return ModelSelectionPolicy.model_validate(raw or {})


def _load_specialist_config(specialist_id: str) -> SpecialistModelConfig | None:
    """Return the specialist's model_config.yaml as a model, or None if absent.

    Slab 1 substrate: only the `_scaffold` reference is shipped; Slab 2
    specialist migrations populate per-specialist subdirectories. Returning
    None here means "no per_specialist level applies" — cascade falls
    through. Reads `SPECIALISTS_DIR` at call time so test monkey-patches apply.

    `specialist_id` is sanitized against `_SPECIALIST_ID_PATTERN` to prevent
    path-traversal attacks (e.g., ``"../etc/passwd"``) escaping
    `SPECIALISTS_DIR`. Invalid IDs raise `ModelResolutionError` rather than
    silently returning None — silent rejection would mask configuration errors
    upstream.
    """
    if not _SPECIALIST_ID_PATTERN.fullmatch(specialist_id):
        raise ModelResolutionError(
            f"specialist_id={specialist_id!r} contains characters outside the "
            f"allowed pattern {_SPECIALIST_ID_PATTERN.pattern!r}; cannot resolve "
            "model_config.yaml without risking path traversal."
        )
    config_path = SPECIALISTS_DIR / specialist_id / "model_config.yaml"
    if not config_path.exists():
        return None
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return SpecialistModelConfig.model_validate(raw)


def _make_entry(
    *,
    level: ResolutionLevel,
    requested: str | None,
    resolved: str,
    reason: str,
    cache_prefix_hash: str | None = None,
) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=level,
        requested=requested,
        resolved=resolved,
        reason=reason,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=cache_prefix_hash,
    )


def _is_available(model_id: str, registry: PipelineRegistry) -> bool:
    return any(e.model_id == model_id and e.available for e in registry.entries)


def _tier_of(model_id: str, registry: PipelineRegistry) -> str | None:
    for e in registry.entries:
        if e.model_id == model_id:
            return e.tier
    return None


def _try_auto_select(
    *,
    specialist_id: str,
    tier_request: str | None,
    registry: PipelineRegistry,
    policy: ModelSelectionPolicy,
) -> str | None:
    """First matching rule wins; return its first available fallback_chain entry."""
    context = {"specialist_id": specialist_id}
    if tier_request is not None:
        context["tier_request"] = tier_request
    for rule in policy.rules:
        if all(context.get(k) == v for k, v in rule.when.items()):
            for candidate in rule.fallback_chain:
                if _is_available(candidate, registry):
                    return candidate
    return None


def resolve(
    specialist_id: str,
    per_call_override: str | None = None,
    *,
    temperature: float = 0.0,
    tier_request: str | None = None,
    system_prompt_hash: str = "",
) -> ResolveResult:
    """Resolve `(model_id, ModelResolutionEntry)` via the three-level cascade.

    The returned entry captures the FINAL resolution (the level that won).
    Intermediate levels that were tried + missed are NOT recorded as entries
    in 1.3; the trail captures the winning level only. Slab 3 Story 3.5
    extends this to record the full per-level walk if needed.

    Raises `ModelResolutionError` if no level resolves to an available
    model_id — silent fallthrough is FORBIDDEN per spec AC-1.3-D.
    """
    registry = _load_registry()
    policy = _load_policy()
    specialist_config = _load_specialist_config(specialist_id)

    # Level 1: per_call
    if per_call_override is not None:
        if not _is_available(per_call_override, registry):
            raise ModelResolutionError(
                f"per_call_override={per_call_override!r} is not in the registry "
                f"(or available=False); cascade cannot fall through silently."
            )
        cache_hash = _compute_cache_prefix_hash(
            specialist_id=specialist_id,
            model_id=per_call_override,
            temperature=temperature,
            system_prompt_hash=system_prompt_hash,
        )
        entry = _make_entry(
            level="per_call",
            requested=per_call_override,
            resolved=per_call_override,
            reason="explicit per_call_override argument",
            cache_prefix_hash=cache_hash,
        )
        return ResolveResult(model_id=per_call_override, entry=entry)

    # Level 2: per_specialist
    if specialist_config is not None:
        candidate = specialist_config.default_model
        if _is_available(candidate, registry):
            cache_hash = _compute_cache_prefix_hash(
                specialist_id=specialist_id,
                model_id=candidate,
                temperature=temperature,
                system_prompt_hash=system_prompt_hash,
            )
            entry = _make_entry(
                level="per_specialist",
                requested=candidate,
                resolved=candidate,
                reason=(
                    f"specialist {specialist_id!r} declared "
                    f"default_model={candidate!r} in model_config.yaml"
                ),
                cache_prefix_hash=cache_hash,
            )
            return ResolveResult(model_id=candidate, entry=entry)

    # Level 3: registry_default
    if _is_available(registry.default_model_id, registry):
        cache_hash = _compute_cache_prefix_hash(
            specialist_id=specialist_id,
            model_id=registry.default_model_id,
            temperature=temperature,
            system_prompt_hash=system_prompt_hash,
        )
        entry = _make_entry(
            level="registry_default",
            requested=None,
            resolved=registry.default_model_id,
            reason=(
                f"PipelineRegistry.default_model_id={registry.default_model_id!r} "
                "available; per_call + per_specialist did not fire"
            ),
            cache_prefix_hash=cache_hash,
        )
        return ResolveResult(model_id=registry.default_model_id, entry=entry)

    # Level 4: auto_select_fallback (gated on registry flag)
    if registry.auto_select_enabled:
        candidate = _try_auto_select(
            specialist_id=specialist_id,
            tier_request=tier_request,
            registry=registry,
            policy=policy,
        )
        if candidate is not None:
            cache_hash = _compute_cache_prefix_hash(
                specialist_id=specialist_id,
                model_id=candidate,
                temperature=temperature,
                system_prompt_hash=system_prompt_hash,
            )
            tier = _tier_of(candidate, registry)
            entry = _make_entry(
                level="auto_select_fallback",
                requested=tier_request,
                resolved=candidate,
                reason=(
                    f"auto-select policy resolved to {candidate!r} "
                    f"(tier={tier!r}); registry default unavailable"
                ),
                cache_prefix_hash=cache_hash,
            )
            return ResolveResult(model_id=candidate, entry=entry)

    raise ModelResolutionError(
        f"cascade exhausted for specialist_id={specialist_id!r}; no level "
        f"resolved to an available model. registry_default={registry.default_model_id!r} "
        f"available={_is_available(registry.default_model_id, registry)}; "
        f"auto_select_enabled={registry.auto_select_enabled}."
    )


__all__ = [
    "ModelResolutionError",
    "REGISTRY_PATH",
    "ResolveResult",
    "SELECTION_POLICY_PATH",
    "SPECIALISTS_DIR",
    "resolve",
]

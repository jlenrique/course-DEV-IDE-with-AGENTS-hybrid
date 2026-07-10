"""Per-SME voice / styleguide / attribution / approval resolution (Mine 3).

Loads ``state/config/sme-registry.yaml``. Unknown SME keys hard-fail.
Unbound SMEs (HAI/PHS) return marked gaps — never silent Tejal styleguide_id.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "state" / "config" / "sme-registry.yaml"


class SmeRegistryError(ValueError):
    """Raised when SME resolution cannot proceed honestly."""


class SmeProfile(BaseModel):
    """Resolved per-SME binding (or explicit unbound gap)."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    sme_key: str
    display_name: str
    styleguide_id: str | None = None
    attribution: str
    approval_route: str
    voice_profile_ref: str
    unbound: bool = False
    fallback: bool = False
    reason: str = ""

    @field_validator("sme_key", "display_name", "attribution", "approval_route", "voice_profile_ref")
    @classmethod
    def _nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("SME profile string fields must be non-empty")
        return cleaned


class SmeRegistry(BaseModel):
    """Closed SME map + name aliases."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = "0.1"
    name_aliases: dict[str, str] = Field(default_factory=dict)
    smes: dict[str, dict[str, Any]] = Field(default_factory=dict)


def _load_raw(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SmeRegistryError(f"SME registry unreadable at {path}: {exc}") from exc
    try:
        payload = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise SmeRegistryError(f"SME registry malformed YAML at {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SmeRegistryError(f"SME registry must be a mapping at {path}")
    return payload


@lru_cache(maxsize=4)
def load_sme_registry(path: str | None = None) -> SmeRegistry:
    """Load and cache the SME registry from disk."""
    registry_path = Path(path) if path else DEFAULT_REGISTRY_PATH
    raw = _load_raw(registry_path)
    try:
        return SmeRegistry.model_validate(raw)
    except Exception as exc:  # pydantic ValidationError
        raise SmeRegistryError(f"SME registry invalid: {exc}") from exc


def clear_sme_registry_cache() -> None:
    """Test helper: clear the load cache."""
    load_sme_registry.cache_clear()


def resolve_sme_key(sme_name_or_key: str, *, registry: SmeRegistry | None = None) -> str:
    """Map a display name or key to the closed ``sme_key``."""
    reg = registry or load_sme_registry()
    raw = (sme_name_or_key or "").strip()
    if not raw:
        raise SmeRegistryError("SME name/key must be non-empty")
    if raw in reg.smes:
        return raw
    alias = reg.name_aliases.get(raw)
    if alias and alias in reg.smes:
        return alias
    # Case-insensitive alias fallback
    lowered = {k.lower(): v for k, v in reg.name_aliases.items()}
    alias = lowered.get(raw.lower())
    if alias and alias in reg.smes:
        return alias
    raise SmeRegistryError(
        f"unknown SME {raw!r}: not in closed registry keys "
        f"{sorted(reg.smes)} or name_aliases (never silent Tejal)"
    )


def resolve_sme_profile(
    sme_name_or_key: str,
    *,
    registry: SmeRegistry | None = None,
    registry_path: str | None = None,
) -> SmeProfile:
    """Resolve SME-keyed voice/styleguide/attribution/approval bindings.

    Unknown SME → ``SmeRegistryError`` (hard-fail).
    Unbound SME → ``fallback=True``, ``styleguide_id=None`` (marked gap).
    """
    reg = registry or load_sme_registry(registry_path)
    key = resolve_sme_key(sme_name_or_key, registry=reg)
    entry = reg.smes[key]
    unbound = bool(entry.get("unbound", False))
    styleguide_id = entry.get("styleguide_id")
    if styleguide_id is not None:
        styleguide_id = str(styleguide_id).strip() or None
    if unbound and styleguide_id is not None:
        raise SmeRegistryError(
            f"SME {key!r} marked unbound but carries styleguide_id="
            f"{styleguide_id!r} (inconsistent registry)"
        )
    # Never allow unbound profiles to inherit a Tejal guide id by accident
    tejal_id = None
    tejal_entry = reg.smes.get("tejal") or {}
    if tejal_entry.get("styleguide_id"):
        tejal_id = str(tejal_entry["styleguide_id"])
    if unbound and tejal_id and styleguide_id == tejal_id:
        raise SmeRegistryError(
            f"SME {key!r} must not reuse Tejal styleguide_id={tejal_id!r}"
        )
    return SmeProfile(
        sme_key=key,
        display_name=str(entry.get("display_name") or key),
        styleguide_id=None if unbound else styleguide_id,
        attribution=str(entry.get("attribution") or ""),
        approval_route=str(entry.get("approval_route") or ""),
        voice_profile_ref=str(entry.get("voice_profile_ref") or ""),
        unbound=unbound,
        fallback=unbound,
        reason=str(entry.get("reason") or "").strip(),
    )


def profiles_diverge(left: SmeProfile, right: SmeProfile) -> list[str]:
    """Return field names where two profiles differ (Mine 3 divergence witness)."""
    fields = (
        "sme_key",
        "styleguide_id",
        "attribution",
        "approval_route",
        "voice_profile_ref",
        "unbound",
        "fallback",
    )
    return [name for name in fields if getattr(left, name) != getattr(right, name)]


__all__ = [
    "DEFAULT_REGISTRY_PATH",
    "SmeProfile",
    "SmeRegistry",
    "SmeRegistryError",
    "clear_sme_registry_cache",
    "load_sme_registry",
    "profiles_diverge",
    "resolve_sme_key",
    "resolve_sme_profile",
]

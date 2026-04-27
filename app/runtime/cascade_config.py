"""Operator-editable cascade and pricing config loaders for economics."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
CASCADE_PATH = REPO_ROOT / "runtime" / "config" / "model_cascade.yaml"
PRICING_PATH = REPO_ROOT / "runtime" / "config" / "openai_pricing.yaml"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"


def normalize_agent_name(value: str) -> str:
    """Canonicalize agent identifiers across hyphen/underscore variants."""

    normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    if not normalized:
        raise ValueError("agent identifier must not normalize to empty")
    return normalized


class CascadeEntry(BaseModel):
    """One configured model assignment plus human rationale."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    model: str = Field(..., min_length=1)
    rationale: str = Field(..., min_length=1)
    aliases: tuple[str, ...] = Field(default_factory=tuple)


class CascadeConfig(BaseModel):
    """Economics-facing cascade mapping for Marcus + active specialists."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    marcus: CascadeEntry
    specialists: dict[str, CascadeEntry]
    sha256_digest: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=_DIGEST_PATTERN,
    )

    @model_validator(mode="after")
    def _reject_alias_collisions(self) -> CascadeConfig:
        seen: dict[str, str] = {}
        for name, entry in [("marcus", self.marcus), *sorted(self.specialists.items())]:
            canonical = normalize_agent_name(name)
            if canonical in seen:
                raise ValueError(f"duplicate cascade identifier {canonical!r}")
            seen[canonical] = name
            for alias in entry.aliases:
                normalized = normalize_agent_name(alias)
                if normalized in seen and seen[normalized] != name:
                    raise ValueError(
                        f"alias {alias!r} on {name!r} collides with {seen[normalized]!r}"
                    )
                seen[normalized] = name
        return self

    def resolve_entry(self, agent_name: str) -> tuple[str, CascadeEntry] | None:
        """Return the canonical configured agent id and its entry."""

        normalized = normalize_agent_name(agent_name)
        if normalized == "marcus":
            return ("marcus", self.marcus)
        for name, entry in self.specialists.items():
            if normalize_agent_name(name) == normalized:
                return (normalize_agent_name(name), entry)
            if any(normalize_agent_name(alias) == normalized for alias in entry.aliases):
                return (normalize_agent_name(name), entry)
        return None


class PricingEntry(BaseModel):
    """Manual OpenAI pricing row in USD per 1M tokens."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    input_per_1m_tokens_usd: float = Field(..., ge=0.0)
    output_per_1m_tokens_usd: float = Field(..., ge=0.0)


class PricingTable(BaseModel):
    """Pricing rows keyed by model id plus the file digest."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    models: dict[str, PricingEntry]
    sha256_digest: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=_DIGEST_PATTERN,
    )

    def compute_cost(self, model_id: str, *, input_tokens: int, output_tokens: int) -> float:
        if model_id not in self.models:
            raise KeyError(f"pricing missing model_id={model_id!r}")
        row = self.models[model_id]
        return (
            (input_tokens / 1_000_000.0) * row.input_per_1m_tokens_usd
            + (output_tokens / 1_000_000.0) * row.output_per_1m_tokens_usd
        )


def _load_yaml_with_digest(path: Path) -> tuple[object, str]:
    raw_bytes = path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    text = raw_bytes.decode("utf-8")
    payload = yaml.safe_load(text)
    return payload or {}, digest


def load_cascade(path: Path | None = None) -> CascadeConfig:
    """Load the operator-editable cascade config plus raw file digest."""

    target = path if path is not None else CASCADE_PATH
    payload, digest = _load_yaml_with_digest(target)
    if not isinstance(payload, dict):
        raise ValueError("cascade config must parse to a mapping")
    return CascadeConfig.model_validate({**payload, "sha256_digest": digest})


def load_pricing(path: Path | None = None) -> PricingTable:
    """Load the operator-editable pricing table plus raw file digest."""

    target = path if path is not None else PRICING_PATH
    payload, digest = _load_yaml_with_digest(target)
    if not isinstance(payload, dict):
        raise ValueError("pricing table must parse to a mapping")
    return PricingTable.model_validate({**payload, "sha256_digest": digest})


def ensure_pricing_covers_cascade(cascade: CascadeConfig, pricing: PricingTable) -> None:
    """Fail loudly when the pricing table omits any configured cascade model."""

    missing: set[str] = set()
    entries = [cascade.marcus, *cascade.specialists.values()]
    for entry in entries:
        if entry.model not in pricing.models:
            missing.add(entry.model)
    if missing:
        rendered = ", ".join(sorted(missing))
        raise ValueError(f"pricing table missing cascade model ids: {rendered}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the operator-editable runtime model cascade and pricing table."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "validate",
        help=(
            "Load the cascade and pricing configs and assert pricing covers "
            "every configured model."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "validate":
        parser.print_help()
        return 2

    try:
        cascade = load_cascade()
        pricing = load_pricing()
        ensure_pricing_covers_cascade(cascade, pricing)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("PASS: cascade + pricing validated")
    print(f"cascade_digest={cascade.sha256_digest}")
    print(f"pricing_digest={pricing.sha256_digest}")
    print(f"specialist_count={len(cascade.specialists)}")
    return 0


__all__ = [
    "CASCADE_PATH",
    "PRICING_PATH",
    "CascadeConfig",
    "CascadeEntry",
    "PricingEntry",
    "PricingTable",
    "ensure_pricing_covers_cascade",
    "load_cascade",
    "load_pricing",
    "main",
    "normalize_agent_name",
]


if __name__ == "__main__":
    raise SystemExit(main())

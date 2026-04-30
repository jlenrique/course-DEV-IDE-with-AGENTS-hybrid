"""Aggregate test for credential-rotation register + per-specialist rate-limit budgets.

Story 7b.12 T9 / AC-K / NFR-CG19 + NFR-CG20. Asserts:

- `state/config/credential-rotation-register.yaml` exists and carries a row
  for each of the 4 third-party API providers consumed by Slab 7b body
  specialists (gamma / kling / elevenlabs / wondercraft); each row declares
  `provider`, `owner`, `rotation_cadence_days`, `last_rotated`, `next_due`,
  and `secret_store_reference` (NFR-CG19);
- each of the 5 Slab 7b body specialists with rate-limit obligations
  (gary / kira / enrique / wanda / dan) declares `rate_limit_per_minute`
  + `daily_budget_usd` + `per_invocation_cap_usd` keys in
  `app/specialists/<name>/config.yaml` (NFR-CG20).

Note: Dan is LLM-only via shared facade (`dan-api-tbd-pending` retired at
7b.10 T1). Dan therefore has no credential-rotation-register row but DOES
declare LLM rate-limit + token-budget. Compositor is deterministic-pipeline
(no LLM, no API) and has no rate-limit-budget obligations.
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CREDENTIAL_REGISTER_PATH = (
    REPO_ROOT / "state" / "config" / "credential-rotation-register.yaml"
)
EXPECTED_PROVIDERS: frozenset[str] = frozenset(
    {"gamma", "kling", "elevenlabs", "wondercraft"}
)
EXPECTED_REGISTER_KEYS: frozenset[str] = frozenset(
    {
        "provider",
        "owner",
        "rotation_cadence_days",
        "last_rotated",
        "next_due",
        "secret_store_reference",
    }
)

EXPECTED_RATE_LIMIT_SPECIALISTS: frozenset[str] = frozenset(
    {"gary", "kira", "enrique", "wanda", "dan"}
)
EXPECTED_BUDGET_KEYS: frozenset[str] = frozenset(
    {
        "rate_limit_per_minute",
        "daily_budget_usd",
        "per_invocation_cap_usd",
    }
)


def _load_register() -> dict:
    assert CREDENTIAL_REGISTER_PATH.is_file(), (
        f"credential-rotation register missing: {CREDENTIAL_REGISTER_PATH}"
    )
    with CREDENTIAL_REGISTER_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def test_credential_register_present_and_well_shaped() -> None:
    data = _load_register()
    assert "credentials" in data, "credential-rotation register missing 'credentials' key"
    rows = data["credentials"]
    assert isinstance(rows, list), "'credentials' MUST be a list"
    assert len(rows) >= 4, f"expected >=4 credential rows, got {len(rows)}"


def test_credential_register_covers_all_four_third_party_providers() -> None:
    data = _load_register()
    rows = data["credentials"]
    providers = {row["provider"] for row in rows if isinstance(row, dict)}
    missing = EXPECTED_PROVIDERS - providers
    assert not missing, (
        f"credential-rotation register missing rows for providers: {sorted(missing)}"
    )


def test_each_credential_row_has_required_keys() -> None:
    data = _load_register()
    rows = data["credentials"]
    for row in rows:
        if not isinstance(row, dict):
            continue
        provider = row.get("provider", "<missing>")
        if provider not in EXPECTED_PROVIDERS:
            continue
        present = set(row.keys())
        missing = EXPECTED_REGISTER_KEYS - present
        assert not missing, (
            f"credential row for provider={provider!r} missing keys: {sorted(missing)}"
        )


def test_each_rate_limit_specialist_declares_budget_keys() -> None:
    for specialist in sorted(EXPECTED_RATE_LIMIT_SPECIALISTS):
        config_path = REPO_ROOT / "app" / "specialists" / specialist / "config.yaml"
        assert config_path.is_file(), (
            f"missing config.yaml for rate-limit specialist {specialist!r}: {config_path}"
        )
        with config_path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        assert isinstance(data, dict), (
            f"{specialist} config.yaml MUST parse to a mapping"
        )
        present = set(data.keys())
        missing = EXPECTED_BUDGET_KEYS - present
        assert not missing, (
            f"{specialist} config.yaml missing rate-limit/budget keys: {sorted(missing)}"
        )

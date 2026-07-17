"""Guard test for the Epic 43 HIL-projector replay fixtures (Story 43-0).

These fixtures (``tests/fixtures/hil_projector/``) are frozen, real render inputs
captured from runs ``5169a872`` and ``bc747b51`` per green-light rider R2. This
test is the durability + scrub guard: every fixture must parse, carry its
expected top-level keys, and contain NO surviving live credential (no raw
``server_nonce`` value, no raw resume-authorization ``digest`` literal).

Pure parse/assert — no projector import, no live calls, zero spend.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "hil_projector"

# The raw secret literals that lived in the source decision cards. The scrub
# replaced each with a stable placeholder; NONE of these may survive on disk.
RAW_NONCE_LITERALS = (
    "9c3b64d6193347a8ba156c716c4ffae7",  # G0E server_nonce
    "a90bf0ffa91646208587e4d163015472",  # G0R server_nonce
    "a0fc740948144877b69978ae6dd77ba1",  # G1  server_nonce
)
RAW_RESUME_DIGEST_LITERALS = (
    "a3eb1275d4cf9eda2c01221cfc1cc1a79bf76d1f5ba850e59d221610a4b0becb",  # G0E digest
    "f697a34cbce9fc41ef1f195c500176d8f4bf4f8f017d31d755935b0cd749644e",  # G0R digest
    "88046aab3085915b5042fdea0e26160254c1ef2145e1f220bc8c413a1d7a2082",  # G1  digest
)

# fixture filename -> required top-level keys (render-relevant structure pins).
JSON_FIXTURE_KEYS: dict[str, tuple[str, ...]] = {
    "operator-surface-5169a872.json": ("schema_version", "identity", "envelope", "trace"),
    "operator-surface-bc747b51.json": ("schema_version", "identity", "envelope", "next_action"),
    "g0-enrichment-bc747b51.json": ("typed_components", "provisional_los", "reconcile"),
    "decision-card-g0e-bc747b51.json": ("card", "server_nonce", "digest", "issued_at"),
    "decision-card-g0r-bc747b51.json": ("card", "server_nonce", "digest", "issued_at"),
    "decision-card-g1-bc747b51.json": ("card", "server_nonce", "digest", "issued_at"),
}
YAML_FIXTURE_KEYS: dict[str, tuple[str, ...]] = {
    "directive-5169a872.yaml": ("run_id", "corpus_dir", "sources"),
    "directive-bc747b51.yaml": ("run_id", "corpus_dir", "sources"),
}
DECISION_CARDS = (
    "decision-card-g0e-bc747b51.json",
    "decision-card-g0r-bc747b51.json",
    "decision-card-g1-bc747b51.json",
)
ALL_FIXTURES = tuple(JSON_FIXTURE_KEYS) + tuple(YAML_FIXTURE_KEYS)


def test_fixtures_directory_exists() -> None:
    assert FIXTURES.is_dir(), f"missing fixtures dir: {FIXTURES}"
    assert (FIXTURES / "README.md").is_file(), "provenance README must exist"


@pytest.mark.parametrize("name", sorted(JSON_FIXTURE_KEYS))
def test_json_fixture_parses_and_has_keys(name: str) -> None:
    data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    for key in JSON_FIXTURE_KEYS[name]:
        assert key in data, f"{name} missing top-level key {key!r}"


@pytest.mark.parametrize("name", sorted(YAML_FIXTURE_KEYS))
def test_yaml_directive_parses_and_has_keys(name: str) -> None:
    data = yaml.safe_load((FIXTURES / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    for key in YAML_FIXTURE_KEYS[name]:
        assert key in data, f"{name} missing top-level key {key!r}"
    sources = data["sources"]
    assert isinstance(sources, list) and sources, "directive must carry sources[]"
    # Render-relevant per-source columns (43-1 source-inventory table).
    for src in sources:
        assert {"ref_id", "role", "locator"} <= set(src)


@pytest.mark.parametrize("name", DECISION_CARDS)
def test_decision_card_credentials_are_redacted(name: str) -> None:
    data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert data["server_nonce"] == "REDACTED-NONCE"
    assert data["digest"] == "REDACTED-DIGEST"


@pytest.mark.parametrize("name", sorted(ALL_FIXTURES))
def test_no_raw_secret_literal_survives(name: str) -> None:
    text = (FIXTURES / name).read_text(encoding="utf-8")
    for literal in RAW_NONCE_LITERALS:
        assert literal not in text, f"raw server_nonce leaked in {name}"
    for literal in RAW_RESUME_DIGEST_LITERALS:
        assert literal not in text, f"raw resume-auth digest leaked in {name}"

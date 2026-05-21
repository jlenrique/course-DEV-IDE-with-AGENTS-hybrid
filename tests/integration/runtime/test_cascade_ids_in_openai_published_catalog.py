"""Catalog-membership audit — every model_id used by the runtime must appear
in the vendored OpenAI catalog snapshot.

This is the structural prevention for the "Plausible-Token Substrate
Contamination" anti-pattern (2026-04-26 post-cycle harvest entry). The lint
guard at tests/test_no_fictitious_model_ids.py scans for KNOWN fictitious IDs
by name; this test scans for ANY id not in the published catalog. They are
complementary: the lint guard is a fast denylist; this test is the allowlist.

Refresh tests/fixtures/openai_catalog_snapshot.json when OpenAI publishes
catalog changes (operator-gated cadence; ~quarterly).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "openai_catalog_snapshot.json"
CASCADE_PATH = REPO_ROOT / "runtime" / "config" / "model_cascade.yaml"
PRICING_PATH = REPO_ROOT / "runtime" / "config" / "openai_pricing.yaml"
REGISTRY_PATH = REPO_ROOT / "app" / "models" / "registry.yaml"
SELECTION_POLICY_PATH = REPO_ROOT / "app" / "models" / "selection_policy.yaml"
SPECIALISTS_DIR = REPO_ROOT / "app" / "specialists"
SCAFFOLD_PATH = SPECIALISTS_DIR / "_scaffold" / "model_config.yaml"


def _load_catalog() -> set[str]:
    data = json.loads(CATALOG_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return set(data["models"])


def _ids_from_cascade() -> set[str]:
    data = yaml.safe_load(CASCADE_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    if isinstance(data.get("marcus"), dict) and data["marcus"].get("model"):
        ids.add(data["marcus"]["model"])
    for entry in (data.get("specialists") or {}).values():
        if isinstance(entry, dict) and entry.get("model"):
            ids.add(entry["model"])
    return ids


def _ids_from_pricing() -> set[str]:
    data = yaml.safe_load(PRICING_PATH.read_text(encoding="utf-8"))
    return set((data.get("models") or {}).keys())


def _ids_from_registry() -> set[str]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    if data.get("default_model_id"):
        ids.add(data["default_model_id"])
    for entry in data.get("entries") or []:
        if entry.get("model_id"):
            ids.add(entry["model_id"])
    return ids


def _ids_from_selection_policy() -> set[str]:
    data = yaml.safe_load(SELECTION_POLICY_PATH.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for rule in data.get("rules") or []:
        for fallback in rule.get("fallback_chain") or []:
            ids.add(fallback)
    return ids


def _ids_from_specialist_configs() -> set[str]:
    ids: set[str] = set()
    for path in SPECIALISTS_DIR.glob("*/model_config.yaml"):
        if path == SCAFFOLD_PATH:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        if data.get("default_model"):
            ids.add(data["default_model"])
        for v in (data.get("per_node_overrides") or {}).values():
            if v:
                ids.add(v)
    return ids


def test_every_runtime_model_id_appears_in_openai_catalog_snapshot() -> None:
    catalog = _load_catalog()
    sources: dict[str, set[str]] = {
        "model_cascade.yaml": _ids_from_cascade(),
        "openai_pricing.yaml": _ids_from_pricing(),
        "registry.yaml": _ids_from_registry(),
        "selection_policy.yaml": _ids_from_selection_policy(),
        "app/specialists/*/model_config.yaml": _ids_from_specialist_configs(),
    }
    findings: list[str] = []
    for source, ids in sources.items():
        for model_id in sorted(ids):
            if model_id not in catalog:
                findings.append(f"{source}: {model_id!r} not in catalog snapshot")
    if findings:
        msg = (
            f"Found {len(findings)} runtime model_id(s) not in OpenAI catalog "
            f"snapshot at {CATALOG_SNAPSHOT_PATH.relative_to(REPO_ROOT)}.\n"
            f"Catalog snapshot contains: {sorted(catalog)}\n\n"
            + "\n".join(findings)
            + "\n\nFix: either correct the runtime config to use a real ID, or "
            "(if OpenAI has published a new model) refresh the catalog snapshot."
        )
        pytest.fail(msg)

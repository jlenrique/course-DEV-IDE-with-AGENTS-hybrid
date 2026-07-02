"""gamma-image-model-enum-refresh — doc-parity test + three-way lockstep pin.

Party record: `_bmad-output/planning-artifacts/
gamma-image-model-enum-refresh-greenlight-party-record-2026-07-02.md`.

D-2: THE PARITY PIN IS THE ACTUAL DELIVERABLE. Three copies of the
image-model enum exist BY DESIGN until the (deferred) single-SSOT story:

1. ``app/specialists/gary/_act.py::IMAGE_MODEL_VALUES`` (code authority),
2. ``state/config/schemas/creative-directive.schema.yaml``
   ``gamma_settings.image_model.allowed_values``,
3. ``state/config/schemas/creative-directive.schema.json``
   ``properties.gamma_settings.items.properties.image_model.enum``.

T1 discovery (2026-07-02): NO json-from-yaml generator exists — the ``.json``
is hand-maintained in lockstep with the ``.yaml`` (git history shows both
edited in the same commits; ``tests/test_creative_directive_schema.py`` pins
other facets but not this enum) -> the D-2 THREE-WAY set-equality pin applies.

D-1 (strict doc-parity): ``IMAGE_MODEL_VALUES`` == the documented accepted
values on the RECORDED real page fixture (provenance:
``tests/fixtures/retrieval/gamma_docs/README.md``), extracted with the audit
driver's OWN committed manifest extraction rules — never a second extraction
authority.

The catalog mention-pin + machine-readable ``provenance: documented-tier,
unverified-in-production`` marking enforce Dan's close-review conditions (2)
and Gary's reconciled live-availability condition (1).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from app.specialists.gary._act import IMAGE_MODEL_VALUES
from scripts.utilities import audit_gamma_docs as audit

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "retrieval" / "gamma_docs" / "image_model_accepted_values.md"
)
YAML_SCHEMA_PATH = REPO_ROOT / "state" / "config" / "schemas" / "creative-directive.schema.yaml"
JSON_SCHEMA_PATH = REPO_ROOT / "state" / "config" / "schemas" / "creative-directive.schema.json"
CATALOG_PATH = REPO_ROOT / "skills" / "gamma-api-mastery" / "references" / "parameter-catalog.md"

PROVENANCE_MARKING = "provenance: documented-tier, unverified-in-production"
"""Machine-readable never-rendered marking (Gary condition 1 / Dan condition 2).
Clears ONLY on a real production render — another doc read does not clear it."""

# The CURRENT never-rendered cohort. Initial cohort: the 11 models added at
# the 2026-07-02 reconciliation. Future never-rendered additions join this set
# AND the catalog marking together; entries clear ONLY on a real production
# render (another doc read does not clear them).
NEVER_RENDERED = frozenset(
    {
        "flux-1-pro",
        "flux-1-quick",
        "flux-1-ultra",
        "flux-kontext-max",
        "gpt-image-1-mini-high",
        "gpt-image-1-mini-low",
        "gpt-image-1-mini-medium",
        "gpt-image-2",
        "gpt-image-2-hd",
        "gpt-image-2-mini",
        "imagen-3-pro",
    }
)
"""Models in the enum that have never rendered in production (provenance-marked
in the catalog). Phase-2's FIRST styleguide binding one of them is the
designated live availability witness (party record rider); a story clearing a
marking after a real render updates this set alongside the catalog."""

_MODEL_TOKEN_RE = re.compile(r"^[a-z0-9.-]+$")


def _documented_tokens_from_fixture() -> set[str]:
    """Extract the documented model strings from the recorded real fixture
    using the driver's committed manifest item (same anchor/until/collect —
    no second extraction authority)."""
    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    item = next(i for i in items if i["item_id"] == "enum-parity-image-model")
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    status, scope = audit.extract_scope(text, item["extraction"])
    assert status == "ok", f"fixture no longer carries the declared anchor: {status}"
    assert scope is not None
    return set(audit.collect_tokens(scope, item["extraction"]))


def test_enum_matches_documented_accepted_values() -> None:
    """D-1 strict doc-parity: the frozen enum equals the documented set on the
    recorded real page — exact sets, both directions."""
    documented = _documented_tokens_from_fixture()
    diffs = {
        "phantom-in-enum-absent-from-docs": sorted(IMAGE_MODEL_VALUES - documented),
        "documented-absent-from-enum": sorted(documented - IMAGE_MODEL_VALUES),
    }
    assert diffs == {
        "phantom-in-enum-absent-from-docs": [],
        "documented-absent-from-enum": [],
    }, "IMAGE_MODEL_VALUES diverged from the documented accepted values (D-1)"


def _yaml_allowed_values() -> list[str]:
    payload = yaml.safe_load(YAML_SCHEMA_PATH.read_text(encoding="utf-8"))
    values = payload["gamma_settings"]["image_model"]["allowed_values"]
    assert isinstance(values, list)
    return [str(v) for v in values]


def _json_enum_values() -> list[str]:
    payload = json.loads(JSON_SCHEMA_PATH.read_text(encoding="utf-8"))
    values = payload["properties"]["gamma_settings"]["items"]["properties"]["image_model"]["enum"]
    assert isinstance(values, list)
    return [str(v) for v in values]


def test_image_model_enum_three_way_lockstep() -> None:
    """D-2 parity pin: schema yaml <-> schema json <-> IMAGE_MODEL_VALUES,
    SET EQUALITY (not subset), each serialized copy duplicate-free."""
    yaml_values = _yaml_allowed_values()
    json_values = _json_enum_values()
    assert len(yaml_values) == len(set(yaml_values)), "duplicate in schema yaml"
    assert len(json_values) == len(set(json_values)), "duplicate in schema json"
    assert set(yaml_values) == IMAGE_MODEL_VALUES, (
        "creative-directive.schema.yaml image_model.allowed_values diverged "
        "from IMAGE_MODEL_VALUES — the three surfaces move in ONE change-set (D-2)"
    )
    assert set(json_values) == IMAGE_MODEL_VALUES, (
        "creative-directive.schema.json image_model enum diverged from "
        "IMAGE_MODEL_VALUES — the three surfaces move in ONE change-set (D-2)"
    )


def _catalog_model_section() -> str:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    anchor = "#### `imageOptions.model`"
    start = text.index(anchor)
    body = text[start + len(anchor) :]
    cut = body.find("\n#### ")
    return body[:cut] if cut != -1 else body


def test_catalog_model_section_mentions_exactly_the_enum() -> None:
    """Convention mention-pin (D-2): the catalog's imageOptions.model section
    backticks exactly the enum's model strings — no stale removals linger, no
    documented addition goes uncataloged."""
    section = _catalog_model_section()
    tokens = {t for t in re.findall(r"`([^`\n]+)`", section) if _MODEL_TOKEN_RE.fullmatch(t)}
    assert sorted(tokens - IMAGE_MODEL_VALUES) == [], (
        "catalog mentions model strings that are not in IMAGE_MODEL_VALUES "
        "(stale rows must be removed at reconciliation)"
    )
    assert sorted(IMAGE_MODEL_VALUES - tokens) == [], (
        "enum model strings missing from the catalog's imageOptions.model section"
    )


def test_catalog_never_rendered_models_carry_machine_readable_provenance() -> None:
    """Gary condition 1 / Dan condition 2: EVERY catalog entry for a
    never-rendered model carries the exact machine-readable marking, in a
    parseable per-model row (display-consumable by the Phase-2 authoring
    surface)."""
    section = _catalog_model_section()
    assert "Unclassified — never rendered, tier TBD" in section, (
        "the explicit Unclassified row is required in the AC text (Amelia L-5)"
    )
    marked_models: set[str] = set()
    for line in section.splitlines():
        if PROVENANCE_MARKING not in line:
            continue
        row_models = {t for t in re.findall(r"`([^`\n]+)`", line) if _MODEL_TOKEN_RE.fullmatch(t)}
        assert row_models, f"a provenance-marked catalog row carries no model string: {line!r}"
        marked_models |= row_models
    assert marked_models == set(NEVER_RENDERED), (
        "the set of provenance-marked (never-rendered) catalog models must be "
        "exactly the CURRENT never-rendered cohort (NEVER_RENDERED, "
        "provenance-marked in the catalog); the marking clears ONLY on a real "
        "production render"
    )

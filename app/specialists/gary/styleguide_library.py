"""CD-owned Gamma styleguide library — loader + resolver (single source of truth).

This module is the shared spine for both the Gary consumption seam
(``_normalized_gamma_settings``) and the offline write-gate
(``scripts/utilities/validate_gamma_style_guides.py``). It loads
``state/config/gamma-style-guides.yaml`` and expands a named styleguide record
into the flat base-layer API keys Gary already understands.

Design guardrails:
- The expansion emits ONLY recognized Gamma setting keys; presentation metadata
  and the optional ``scripted`` block are structurally incapable of reaching a
  ``gamma_settings[]`` item (they live under keys this module never reads for the
  resolved surface). This is what keeps Gary's :375 unknown-key gate meaningful.
- ``production_mode`` is the discriminated-union tag. A ``studio`` record that
  carries any Classic-only surface field is a hard error
  (``gamma.styleguide.surface-violation``), never a silent coercion.
- An unresolvable name is a hard error (``gamma.styleguide.unknown``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError
from scripts.utilities.file_helpers import project_root as _project_root

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a shipped dependency
    yaml = None  # type: ignore[assignment]

PROJECT_ROOT = _project_root()
GAMMA_STYLE_GUIDES_PATH = PROJECT_ROOT / "state" / "config" / "gamma-style-guides.yaml"

# The flat base-layer keys this resolver is allowed to emit. A strict subset of
# Gary's GAMMA_SETTING_KEYS (minus ``variant_id`` / ``styleguide``), asserted at
# import time by the seam's tests so the two can never drift apart.
RESOLVED_API_KEYS = frozenset(
    {
        "theme",
        "text_mode",
        "amount",
        "audience",
        "tone",
        "language",
        "image_source",
        "image_model",
        "image_style_preset",
        "image_style",
        "keywords",
        "dimensions",
        # Style-level persistent prose register (party-ratified 2026-07-02). The
        # api/Classic path emits this so Gary composes it as a SEPARATE, style-first
        # part of the real Gamma ``additionalInstructions`` generation param — it
        # COMPLEMENTS, never overwrites, the per-deck source-derived instructions.
        # Studio deliberately does NOT emit it (see _expand_studio).
        "additional_instructions",
        "production_mode",
        "studio_template_id",
    }
)

# Classic-only surface a ``studio`` record is forbidden from carrying (spec §3).
# Airtight discriminated-union: this covers text/format AND the foundational theme
# + every Classic visuals directive (image_source/model/preset/custom_style). On a
# studio record the create-from-template *is* the style authority, so ANY of these
# is a surface-violation, never a silent coercion (code-review item #3a).
STYLEGUIDE_CLASSIC_ONLY_KEYS = frozenset(
    {
        "text_mode",
        "dimensions",
        "amount",
        "tone",
        "audience",
        "language",
        "keywords",
        "num_cards",
        "card_split",
        "theme",
        "image_source",
        "image_model",
        "image_style_preset",
        "custom_style",
    }
)

SURFACE_VIOLATION_TAG = "gamma.styleguide.surface-violation"
UNKNOWN_TAG = "gamma.styleguide.unknown"
INCOMPLETE_TAG = "gamma.styleguide.incomplete"
LOAD_ERROR_TAG = "gamma.styleguide.load-error"

# --- Leg-C: the sealed, registry-bound `scripted` closed-vocab namespace ----------
# `scripted` is NOT an engine/interpreter — it is "a switch with one case". v1 registry
# is EXACTLY {min_cluster_floor}; adding a class is a party-mode GOVERNANCE act (a code
# change to this constant), never a yaml edit. The `scripted_enum.classes` list in the
# runtime yaml is the human-readable declaration; THIS constant is the enforced
# authority so the yaml can never self-authorize a new class.
SCRIPTED_ENUM_CLASSES = frozenset({"min_cluster_floor"})
SCRIPTED_UNKNOWN_CLASS_TAG = "gamma.scripted.unknown-class"
SCRIPTED_BAD_VALUE_TAG = "gamma.scripted.bad-value"


class StyleguideError(SpecialistDispatchError):
    """Raised for an unresolvable or surface-violating styleguide record.

    Carries a ``tag`` so the Gary seam can re-raise it as a ``GaryActError`` with
    the same taxonomy without importing Gary here (avoids a circular import).

    Taxonomy re-base (contracts-triage row 20, 2026-07-02): dispatch-family per
    PIN-AUD-3T so an uncaught escape error-pauses recoverably instead of killing
    the walk (base is RuntimeError-derived; all existing by-name handlers
    preserved).
    """


def _is_present(value: Any) -> bool:
    """A field ``counts`` only when it is a non-null, non-sentinel value."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "default"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def load_style_guides(path: str | Path | None = None) -> dict[str, Any]:
    """Load and shallow-validate the styleguide library YAML mapping.

    Every load/parse failure (missing file, malformed YAML, non-mapping top-level,
    empty ``style_guides``) is wrapped in ``StyleguideError`` (tag
    ``gamma.styleguide.load-error``) so Gary's ``except StyleguideError`` path
    error-pauses recoverably instead of crashing the walk with a bare
    ``FileNotFoundError`` / ``yaml.YAMLError`` / ``ValueError`` (code-review item #2).
    """
    if yaml is None:  # pragma: no cover
        raise StyleguideError(
            "pyyaml is required to load the gamma styleguide library",
            tag=LOAD_ERROR_TAG,
        )
    resolved = Path(path) if path is not None else GAMMA_STYLE_GUIDES_PATH
    try:
        payload = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise StyleguideError(
            f"failed to load styleguide library at {resolved}: {exc}",
            tag=LOAD_ERROR_TAG,
        ) from exc
    if not isinstance(payload, dict):
        raise StyleguideError(
            f"expected a YAML mapping at {resolved}", tag=LOAD_ERROR_TAG
        )
    guides = payload.get("style_guides")
    if not isinstance(guides, dict) or not guides:
        raise StyleguideError(
            f"no style_guides mapping in {resolved}", tag=LOAD_ERROR_TAG
        )
    return payload


def classic_surface_keys(record: dict[str, Any]) -> set[str]:
    """Return which Classic-only base-layer keys a record encodes (non-empty)."""
    present: set[str] = set()
    if _is_present((record.get("theme") or {}).get("id")):
        present.add("theme")
    pc = record.get("prompt_configuration") or {}
    text_content = pc.get("text_content") or {}
    for src, key in (
        ("mode", "text_mode"),
        ("amount", "amount"),
        ("audience", "audience"),
        ("tone", "tone"),
        ("language", "language"),
    ):
        if _is_present(text_content.get(src)):
            present.add(key)
    visuals = pc.get("visuals") or {}
    for src, key in (
        ("keywords", "keywords"),
        ("image_source", "image_source"),
        ("image_model", "image_model"),
        ("style_preset", "image_style_preset"),
        ("custom_style", "custom_style"),
    ):
        if _is_present(visuals.get(src)):
            present.add(key)
    fmt = pc.get("format") or {}
    if _is_present(fmt.get("card_split")):
        present.add("card_split")
    generation = pc.get("generation") or {}
    if _is_present(generation.get("num_cards")):
        present.add("num_cards")
    card_options = (record.get("page_settings") or {}).get("card_options") or {}
    if _is_present(card_options.get("dimensions")):
        present.add("dimensions")
    return present


def _expand_api(record: dict[str, Any], name: str) -> dict[str, Any]:
    resolved: dict[str, Any] = {"production_mode": "api"}
    theme = record.get("theme") or {}
    # Resolver completeness fail-loud (code-review item #1, symmetry with the studio
    # gamma_id requirement): an api record MUST carry a real theme.id. A themeless
    # base would let ``_theme_id`` silently fall back to ``themes[0].id`` — an
    # arbitrary WRONG theme on a paid deck. Refuse it here.
    if not _is_present(theme.get("id")):
        raise StyleguideError(
            f"styleguide {name!r} is production_mode='api' but has no theme.id "
            f"(resolver completeness failure)",
            tag=INCOMPLETE_TAG,
        )
    resolved["theme"] = str(theme["id"]).strip()

    pc = record.get("prompt_configuration") or {}
    text_content = pc.get("text_content") or {}
    for src, key in (
        ("mode", "text_mode"),
        ("amount", "amount"),
        ("audience", "audience"),
        ("tone", "tone"),
        ("language", "language"),
    ):
        value = text_content.get(src)
        if _is_present(value):
            resolved[key] = str(value).strip()

    visuals = pc.get("visuals") or {}
    if _is_present(visuals.get("image_source")):
        resolved["image_source"] = str(visuals["image_source"]).strip()
    if _is_present(visuals.get("image_model")):
        resolved["image_model"] = str(visuals["image_model"]).strip()
    if _is_present(visuals.get("style_preset")):
        resolved["image_style_preset"] = str(visuals["style_preset"]).strip()
    if _is_present(visuals.get("custom_style")):
        resolved["image_style"] = str(visuals["custom_style"]).strip()
    keywords = visuals.get("keywords")
    if _is_present(keywords):
        resolved["keywords"] = [str(k).strip() for k in keywords if str(k).strip()]

    # Style-level persistent prose register (party-ratified 2026-07-02). Emitted as a
    # cleaned LIST of non-empty strings; an absent / empty / blank-only list resolves
    # to key-ABSENT (identical to today ⇒ additive-safe). Malformed shapes (non-list)
    # are the write-gate's job — the resolver stays tolerant and simply skips emission.
    extra_instructions = pc.get("additional_instructions")
    if isinstance(extra_instructions, list):
        cleaned = [str(item).strip() for item in extra_instructions if str(item).strip()]
        if cleaned:
            resolved["additional_instructions"] = cleaned

    card_options = (record.get("page_settings") or {}).get("card_options") or {}
    if _is_present(card_options.get("dimensions")):
        resolved["dimensions"] = str(card_options["dimensions"]).strip()
    return resolved


def _expand_studio(record: dict[str, Any], name: str) -> dict[str, Any]:
    violations = sorted(classic_surface_keys(record) & STYLEGUIDE_CLASSIC_ONLY_KEYS)
    if violations:
        raise StyleguideError(
            f"styleguide {name!r} is production_mode='studio' but carries "
            f"Classic-only surface field(s) {violations}; the template is the "
            f"style authority (surface-violation)",
            tag=SURFACE_VIOLATION_TAG,
        )
    template = record.get("studio_template") or {}
    gamma_id = str(template.get("gamma_id") or "").strip()
    if not gamma_id:
        raise StyleguideError(
            f"styleguide {name!r} is production_mode='studio' but has no "
            f"studio_template.gamma_id",
            tag=SURFACE_VIOLATION_TAG,
        )
    # Studio ``additional_instructions`` disposition — TEMPLATE-LOCK-ONLY BY DESIGN
    # (party-ratified 2026-07-02, Gary + Dan unanimous). A studio record MAY carry
    # ``prompt_configuration.additional_instructions`` (it is NOT a Classic-only key,
    # so it is not a surface-violation and the write-gate validates its shape), but the
    # resolver INTENTIONALLY does not emit it: the Gamma create-from-template call has
    # no ``additionalInstructions`` channel, and the studio_prompt_lock wrapper is the
    # sole studio style-authority surface. The value is a documented template-lock
    # annotation; this non-emission is deliberate + tested, never an accidental drop.
    return {"production_mode": "studio", "studio_template_id": gamma_id}


def expand_record(record: dict[str, Any], *, name: str) -> dict[str, Any]:
    """Expand one styleguide record into flat base-layer API keys.

    Emits ONLY keys in ``RESOLVED_API_KEYS``. Studio records that carry Classic-only
    surface raise ``StyleguideError`` (surface-violation).
    """
    production_mode = str(record.get("production_mode") or "api").strip().lower()
    resolved = (
        _expand_studio(record, name)
        if production_mode == "studio"
        else _expand_api(record, name)
    )
    leaked = set(resolved) - RESOLVED_API_KEYS
    assert not leaked, f"styleguide resolver emitted non-API keys: {sorted(leaked)}"
    return resolved


def scripted_entries(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the ``scripted`` entries a record carries (tolerant of a single dict
    OR a list of entries). Reads ONLY the ``scripted`` block — NEVER the resolved
    API surface.
    """
    if not isinstance(record, dict):
        return []
    block = record.get("scripted")
    if block is None:
        return []
    if isinstance(block, dict):
        return [block]
    if isinstance(block, list):
        return [e for e in block if isinstance(e, dict)]
    return []


def resolve_scripted(record: dict[str, Any], class_name: str) -> Any:
    """Scripted-only accessor: return the typed scalar for ``class_name`` or ``None``.

    LEAK GUARD (symmetric to Gary's metadata-quarantine): this function reads ONLY the
    ``scripted`` block and returns a BARE scalar; it has structurally NO path to
    ``RESOLVED_API_KEYS`` / ``gamma_settings[]``. An unregistered class is a hard error
    (``gamma.scripted.unknown-class``) — never a silent ``None``. A malformed value on a
    registered class is a hard error (``gamma.scripted.bad-value``).
    """
    if class_name not in SCRIPTED_ENUM_CLASSES:
        raise StyleguideError(
            f"unknown scripted class {class_name!r}; not in the sealed registry "
            f"{sorted(SCRIPTED_ENUM_CLASSES)}",
            tag=SCRIPTED_UNKNOWN_CLASS_TAG,
        )
    for entry in scripted_entries(record):
        if str(entry.get("class") or "").strip() != class_name:
            continue
        value = entry.get("value")
        if class_name == "min_cluster_floor" and (
            isinstance(value, bool) or not isinstance(value, int) or value < 1
        ):
            raise StyleguideError(
                f"scripted {class_name!r} value must be a positive int; got {value!r}",
                tag=SCRIPTED_BAD_VALUE_TAG,
            )
        return value
    return None


def resolve_styleguide(
    name: str,
    *,
    guides: dict[str, Any] | None = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve a styleguide name to its flat base-layer API keys.

    Raises ``StyleguideError(tag='gamma.styleguide.unknown')`` for an unknown name
    and ``StyleguideError(tag='gamma.styleguide.surface-violation')`` for a studio
    record carrying Classic-only surface.
    """
    if guides is None:
        guides = load_style_guides(path).get("style_guides", {})
    record = guides.get(name)
    if not isinstance(record, dict):
        raise StyleguideError(
            f"unknown styleguide {name!r}; not present in the styleguide library",
            tag=UNKNOWN_TAG,
        )
    return expand_record(record, name=name)

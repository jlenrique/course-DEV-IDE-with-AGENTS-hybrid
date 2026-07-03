"""Hermetic offline write-gate for the CD-owned Gamma styleguide library.

The operator-required "copacetic-quality audit" of
``state/config/gamma-style-guides.yaml``. Runs OFFLINE / in CI with NO network.
The only network-touching path is the ``--check-existence`` flag (OFF by default),
which live-verifies theme/template ids against the Gamma API.

Enforces (spec §2):
- completeness with INVERTED polarity: a null/"default"/empty REQUIRED surface field
  FAILS (a present value is the passing state, absence is the failure);
- FROZEN enums reused from ``app/specialists/gary/_act.py`` (never re-derived);
- discriminated-union: ``production_mode: studio`` FORBIDS the Classic-only surface
  (``gamma.styleguide.surface-violation``); ``api`` requires a theme + full surface;
- coherence-triad: theme + art-style/keywords + dimensions agree and a
  ``presentation.narrative.triad_rationale`` prose is present;
- roster floor: >= 1 Classic (api) and >= 1 Studio guide present.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Allow direct CLI invocation (``python scripts/utilities/validate_gamma_style_guides.py``)
# by ensuring the repo root is importable before the ``app`` imports below.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.specialists.gary._act import (  # noqa: E402
    CARD_DIMENSION_VALUES,
    IMAGE_MODEL_VALUES,
    IMAGE_SOURCE_VALUES,
    IMAGE_STYLE_PRESET_VALUES,
    PRODUCTION_MODE_VALUES,
    TEXT_AMOUNT_UI_VALUES,
    TEXT_LANGUAGE_VALUES,
    TEXT_MODE_VALUES,
)
from app.specialists.gary.learned_dependencies import (  # noqa: E402
    GAMMA_LEARNED_RULES_LOCK_PATH,
    active_learned_rules,
    apply_learned_rules,
    check_manifest_pin,
    load_manifest,
)
from app.specialists.gary.styleguide_library import (  # noqa: E402
    GAMMA_STYLE_GUIDES_PATH,
    SCRIPTED_ENUM_CLASSES,
    StyleguideError,
    expand_record,
    load_style_guides,
    scripted_entries,
)

# Lifecycle marking (session-07 green-light A1, Winston + Dan converged, BLOCKING):
# the candidate-vs-permanent lifecycle is SCHEMA, not convention. A record absent a
# lifecycle is treated as `candidate` (the safe state is the lazy state) and WARNED
# loudly; an explicit `candidate` must carry its promotion contract fields.
_LIFECYCLE_VALUES: frozenset[str] = frozenset({"candidate", "permanent", "deprecated"})

# Frozen-enum reuse: {resolved base key -> allowed value set}. Sourced from _act.py.
_ENUM_CHECKS: dict[str, frozenset[str]] = {
    "text_mode": TEXT_MODE_VALUES,
    "language": TEXT_LANGUAGE_VALUES,
    "image_style_preset": IMAGE_STYLE_PRESET_VALUES,
    "image_model": IMAGE_MODEL_VALUES,
    "image_source": IMAGE_SOURCE_VALUES,
    "dimensions": CARD_DIMENSION_VALUES,
}


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "default"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


# --- AC-5: prose-vs-param non-contradiction (advances the filed follow-on
#     `gamma-prose-vs-param-noncontradiction-validator`). Conservative first cut:
#     CONTRADICTION with a structured param is an ERROR; mere REDUNDANCY with Gary's
#     hardcoded card rule is a WARN. Token matching is case-insensitive substring on the
#     joined prose. Extending the rule-set stays under the filed follow-on. -------------
_ADDITIONAL_INSTRUCTIONS_TAG = "gamma.styleguide.additional-instructions-invalid"
_PROSE_CONTRADICTS_TAG = "gamma.prose.contradicts-param"
_PROSE_ECHOES_TAG = "gamma.prose.echoes-param"
# Non-photographic presets (everything real except `photorealistic`; `custom` is
# author-defined free-text so it is intentionally excluded from the axis).
_NONPHOTO_PRESETS = frozenset({"illustration", "abstract", "3D", "lineArt"})
# High-precision tokens matched with a LEADING word boundary (``\btoken``) so plurals/
# inflections are caught (photograph → photographs) but mid-word bleed is NOT (telephoto,
# photosynthesis, photocopy). Ambiguous single words that collide with content vocabulary
# (bare ``photo``, ``vector``, ``sketch``) are deliberately omitted — precision over
# recall for a hard write-gate ERROR (code-review A). Extending stays under the filed
# follow-on `gamma-prose-vs-param-noncontradiction-validator`.
_PROSE_PHOTO_TOKENS = ("photorealistic", "photo-realistic", "photograph", "photographic")
_PROSE_ILLUSTRATION_TOKENS = (
    "illustration", "illustrated", "line art", "line-art", "lineart",
    "vector illustration", "vector art", "vector graphic", "cartoon", "hand-drawn",
)
_PROSE_STOCK_PHOTO_TOKENS = (
    "stock photo", "stock image", "stock imagery", "unsplash", "real photograph",
)
_PROSE_CARD_RULE_TOKENS = (
    "one card per section", "one card per", "do not add a cover", "do not merge",
    "do not split", "leading heading", "verbatim",
)
# Best-effort same-clause negation guard so prose that FORBIDS the wrong medium
# ("never use photographs; keep everything illustrated") is not misread as asserting it.
# NOT a general negation solver — deliberately conservative (per repo guidance that
# bag-of-words negation must never be the sole live guard on generative text).
_NEGATION_RE = re.compile(
    r"\b(no|not|never|avoid|without|don't|dont|exclude|excluding|neither|nor|non)\b"
)


def _clause_prefix(prose: str, idx: int) -> str:
    """The (up to 40 chars of) text in the same clause immediately before ``idx``."""
    return re.split(r"[.;:!?]", prose[:idx])[-1][-40:]


def _prose_positively_asserts(prose: str, tokens: tuple[str, ...]) -> bool:
    """True iff ``prose`` (lowercased) POSITIVELY asserts any token — a leading-word-
    boundary match that is NOT negated within the same clause."""
    for token in tokens:
        for match in re.finditer(r"\b" + re.escape(token), prose):
            if not _NEGATION_RE.search(_clause_prefix(prose, match.start())):
                return True
    return False


def _record_additional_instructions(record: dict[str, Any]) -> Any:
    return (record.get("prompt_configuration") or {}).get("additional_instructions")


def _validate_additional_instructions_shape(name: str, record: dict[str, Any]) -> list[str]:
    """AC-1: the optional ``prompt_configuration.additional_instructions`` (BOTH modes)
    must be a NON-EMPTY list of NON-EMPTY strings when present. Absent ⇒ clean no-op."""
    ai = _record_additional_instructions(record)
    if ai is None:
        return []
    if not isinstance(ai, list) or not ai:
        return [
            f"{name}: prompt_configuration.additional_instructions must be a non-empty "
            f"list of strings when present [{_ADDITIONAL_INSTRUCTIONS_TAG}]"
        ]
    errors: list[str] = []
    for item in ai:
        if not isinstance(item, str) or not item.strip():
            errors.append(
                f"{name}: prompt_configuration.additional_instructions entries must be "
                f"non-empty strings; got {item!r} [{_ADDITIONAL_INSTRUCTIONS_TAG}]"
            )
    return errors


def _validate_prose_noncontradiction(
    name: str, record: dict[str, Any], resolved: dict[str, Any]
) -> tuple[list[str], list[str]]:
    """AC-5: flag style ``additional_instructions`` prose that CONTRADICTS a structured
    param (ERROR) or merely ECHOES Gary's hardcoded card rule (WARN). Reads the RESOLVED
    surface for preset/source, so studio records (no resolved preset/source) skip the
    contradiction axes by construction. Absent/blank prose ⇒ clean no-op."""
    ai = _record_additional_instructions(record)
    if isinstance(ai, list):
        prose = " ".join(str(x) for x in ai if isinstance(x, str))
    elif isinstance(ai, str):
        prose = ai
    else:
        prose = ""
    prose = prose.lower()
    if not prose.strip():
        return ([], [])
    errors: list[str] = []
    warnings: list[str] = []
    preset = str(resolved.get("image_style_preset") or "").strip()
    source = str(resolved.get("image_source") or "").strip()
    if preset in _NONPHOTO_PRESETS and _prose_positively_asserts(prose, _PROSE_PHOTO_TOKENS):
        errors.append(
            f"{name}: additional_instructions prose implies photographic imagery but "
            f"image_style_preset={preset!r} is non-photographic [{_PROSE_CONTRADICTS_TAG}]"
        )
    elif preset == "photorealistic" and _prose_positively_asserts(
        prose, _PROSE_ILLUSTRATION_TOKENS
    ):
        errors.append(
            f"{name}: additional_instructions prose implies illustration/vector imagery "
            f"but image_style_preset='photorealistic' [{_PROSE_CONTRADICTS_TAG}]"
        )
    if source == "aiGenerated" and _prose_positively_asserts(prose, _PROSE_STOCK_PHOTO_TOKENS):
        errors.append(
            f"{name}: additional_instructions prose asks for stock photography but "
            f"image_source='aiGenerated' [{_PROSE_CONTRADICTS_TAG}]"
        )
    # The card-rule echo WARN only applies where Gary's card rule actually ships — the
    # api/Classic composition path. Studio prose is a never-emitted template-lock
    # annotation, so echoing the card rule there is meaningless (code-review C).
    production_mode = str(record.get("production_mode") or "api").strip().lower()
    if production_mode == "api" and _prose_positively_asserts(prose, _PROSE_CARD_RULE_TOKENS):
        warnings.append(
            f"{name}: additional_instructions prose echoes Gary's hardcoded card-structure "
            f"rule (merely-redundant; the rule ships structurally) [{_PROSE_ECHOES_TAG}]"
        )
    return (errors, warnings)


# studio-via-api-override-plumbing (step 1) tags.
_STUDIO_THEME_ID_TAG = "gamma.studio.theme-id-invalid"
_STUDIO_IMAGE_MODEL_TAG = "gamma.studio.image-model-invalid"
_STUDIO_OVERRIDE_ON_CLASSIC_TAG = "gamma.studio.override-on-classic"
_STUDIO_DERIVED_FROM_TAG = "gamma.studio.derived-from-invalid"
# The single source-of-truth image-model enum (from _act.py). Reused, NEVER hand-copied,
# so the studio-accepted set can never drift from the catalog (A4 drift guard).
_STUDIO_IMAGE_MODEL_VALUES: frozenset[str] = IMAGE_MODEL_VALUES


def _validate_studio_overrides(name: str, record: dict[str, Any]) -> list[str]:
    """Studio-scoped ``studio_template.{theme_id, image_model}`` overrides (step 1).

    - ``theme_id``: an opaque Gamma id — string-validate only (non-empty when present),
      NO enum (it is not in any registry we own).
    - ``image_model``: enum-validate against the SINGLE catalog enum (``IMAGE_MODEL_VALUES``
      from _act.py) — a bogus value fails with field + value named.

    ``derived_from`` shape is validated separately (``_validate_derived_from_shape``) so it
    runs on ALL records (api + studio), not just the studio branch (F5).
    """
    errors: list[str] = []
    template = record.get("studio_template") or {}
    theme_id = template.get("theme_id")
    if theme_id is not None and (not isinstance(theme_id, str) or not theme_id.strip()):
        errors.append(
            f"{name}: studio_template.theme_id must be a non-empty string when present; "
            f"got {theme_id!r} [{_STUDIO_THEME_ID_TAG}]"
        )
    image_model = template.get("image_model")
    if image_model is not None and (
        not isinstance(image_model, str)
        or str(image_model).strip() not in _STUDIO_IMAGE_MODEL_VALUES
    ):
        errors.append(
            f"{name}: studio_template.image_model={image_model!r} is not one of "
            f"{sorted(_STUDIO_IMAGE_MODEL_VALUES)} (frozen enum from _act.py) "
            f"[{_STUDIO_IMAGE_MODEL_TAG}]"
        )
    return errors


def _validate_derived_from_shape(name: str, record: dict[str, Any]) -> list[str]:
    """``derived_from`` optional lineage annotation: a well-formed non-empty string when
    present. Runs on ALL records (api + studio) — a malformed ``derived_from`` on a
    Classic record is caught too (F5). The RESOLVER never reads it; validator-only (A5)."""
    derived_from = record.get("derived_from")
    if derived_from is not None and (
        not isinstance(derived_from, str) or not derived_from.strip()
    ):
        return [
            f"{name}: derived_from must be a non-empty string when present; "
            f"got {derived_from!r} [{_STUDIO_DERIVED_FROM_TAG}]"
        ]
    return []


def _validate_no_studio_overrides_on_classic(name: str, record: dict[str, Any]) -> list[str]:
    """A Classic (``production_mode: api``) record may NOT carry the studio-only
    ``studio_template.{theme_id, image_model}`` overrides — they ride a studio record
    ONLY. Reject both directions (studio-via-api-override-plumbing, step 1 / A2)."""
    template = record.get("studio_template") or {}
    illegal = sorted(
        key for key in ("theme_id", "image_model") if _is_present(template.get(key))
    )
    if not illegal:
        return []
    return [
        f"{name}: production_mode='api' (Classic) record carries studio-only "
        f"override(s) studio_template.{illegal}; these ride a studio record only "
        f"[{_STUDIO_OVERRIDE_ON_CLASSIC_TAG}]"
    ]


def _triad_rationale(record: dict[str, Any]) -> Any:
    return ((record.get("presentation") or {}).get("narrative") or {}).get("triad_rationale")


def _validate_scripted(name: str, record: dict[str, Any]) -> list[str]:
    """Validate the sealed ``scripted`` closed-vocab block (Leg-C).

    A ``scripted`` entry is ``{class, value:int>0, rationale:<style-identity str>,
    provenance{authoring_styleguide, envelope_write_stamp}}``. Enforces:
    closed-enum membership (unregistered class -> RED ``gamma.scripted.unknown-class``),
    positive-int value, a mandatory style-identity ``rationale`` (bars content/pedagogy
    smuggling), and envelope-provenance presence. Absent block -> clean no-op.
    """
    errors: list[str] = []
    block = record.get("scripted")
    if block is None:
        return errors
    if not isinstance(block, (dict, list)):
        return [
            f"{name}: scripted must be a mapping or a list of entries "
            f"[gamma.scripted.malformed]"
        ]
    entries = scripted_entries(record)
    if not entries:
        return [f"{name}: scripted block has no valid entries [gamma.scripted.malformed]"]
    # P6 (Leg-C review): a scripted class may appear at most ONCE. Two entries of the
    # same class would let the first silently win across the 3 readers (validator,
    # gary accessor, orchestrator) — RED it instead of a silent first-wins.
    seen_classes: set[str] = set()
    for entry in entries:
        class_name = str(entry.get("class") or "").strip()
        if not class_name:
            errors.append(
                f"{name}: scripted entry missing a `class` [gamma.scripted.unknown-class]"
            )
            continue
        if class_name in seen_classes:
            errors.append(
                f"{name}: duplicate scripted class {class_name!r} — a class may appear "
                f"at most once (first-wins is silent) [gamma.scripted.duplicate-class]"
            )
            continue
        seen_classes.add(class_name)
        if class_name not in SCRIPTED_ENUM_CLASSES:
            errors.append(
                f"{name}: unregistered scripted class {class_name!r} (registry="
                f"{sorted(SCRIPTED_ENUM_CLASSES)}) [gamma.scripted.unknown-class]"
            )
            continue
        if class_name == "min_cluster_floor":
            value = entry.get("value")
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                errors.append(
                    f"{name}: scripted {class_name} value must be a positive int; got "
                    f"{value!r} [gamma.scripted.bad-value]"
                )
        if not _is_present(entry.get("rationale")):
            errors.append(
                f"{name}: scripted {class_name} requires a non-empty style-identity "
                f"`rationale` [gamma.scripted.missing-rationale]"
            )
        prov = entry.get("provenance")
        if (
            not isinstance(prov, dict)
            or not _is_present(prov.get("authoring_styleguide"))
            or not _is_present(prov.get("envelope_write_stamp"))
        ):
            errors.append(
                f"{name}: scripted {class_name} requires "
                f"provenance{{authoring_styleguide, envelope_write_stamp}} "
                f"[gamma.scripted.missing-provenance]"
            )
    return errors


def _validate_one(name: str, record: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate one styleguide record.

    Returns ``(errors, warnings)``. Errors fail the exit code; warnings surface
    loudly but only fail the exit code under ``--strict`` (see ``main``). WARN rules
    are for valid-but-subordinated configs Gary's Gamma-truth flags as merges, not
    invalid states — never hard-block a valid styleguide (green-light Decision 2).
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return ([f"{name}: styleguide record must be a mapping"], warnings)

    production_mode = str(record.get("production_mode") or "").strip().lower()
    if production_mode not in PRODUCTION_MODE_VALUES:
        errors.append(
            f"{name}: production_mode must be one of {sorted(PRODUCTION_MODE_VALUES)}; "
            f"got {record.get('production_mode')!r}"
        )
        # Without a valid discriminant the rest of the checks are undefined.
        return (errors, warnings)

    # --- Discriminated-union surface + expansion (shares Gary's resolver) ---------
    try:
        resolved = expand_record(record, name=name)
    except StyleguideError as exc:
        errors.append(f"{name}: {exc} [{exc.tag}]")
        resolved = {}

    # --- Completeness, INVERTED polarity (null/default/empty on required FAILS) ----
    if production_mode == "api":
        required = {
            "theme.id": (record.get("theme") or {}).get("id"),
            "prompt_configuration.text_content.mode": (
                (record.get("prompt_configuration") or {}).get("text_content") or {}
            ).get("mode"),
            "prompt_configuration.visuals.image_source": (
                (record.get("prompt_configuration") or {}).get("visuals") or {}
            ).get("image_source"),
            "page_settings.card_options.dimensions": (
                (record.get("page_settings") or {}).get("card_options") or {}
            ).get("dimensions"),
        }
    else:  # studio
        required = {
            "studio_template.gamma_id": (record.get("studio_template") or {}).get("gamma_id"),
        }
    for field, value in required.items():
        if not _is_present(value):
            errors.append(
                f"{name}: required field {field} is null/default/empty "
                f"(inverted-polarity completeness failure)"
            )

    # --- Studio per-record overrides (studio-via-api-override-plumbing, step 1) -----
    #     theme_id (string) + image_model (frozen enum) ride ONLY a studio record; a
    #     Classic (api) record carrying them is a hard error (discriminated-union, A2).
    if production_mode == "studio":
        errors.extend(_validate_studio_overrides(name, record))
    else:  # api / Classic
        errors.extend(_validate_no_studio_overrides_on_classic(name, record))
    # derived_from shape is mode-independent (F5): validate it on BOTH api + studio.
    errors.extend(_validate_derived_from_shape(name, record))

    # --- amount: Gamma UI vocabulary, conditional on text mode (2026-07-03) ---------
    #     Authority: skills/gamma-api-mastery/references/gamma-style-control-map.md. The
    #     registry stores UI labels (Minimal/Concise/Detailed/Extensive); Gary translates
    #     to the API value. amount is required for generate/condense, forbidden for
    #     preserve (Gamma ignores it), and must be a UI value (never the API value).
    if production_mode == "api":
        tc = (record.get("prompt_configuration") or {}).get("text_content") or {}
        mode = str(tc.get("mode") or "").strip().lower()
        amount_raw = tc.get("amount")
        amount_present = _is_present(amount_raw)
        if mode in {"generate", "condense"} and not amount_present:
            errors.append(
                f"{name}: text_content.amount is required when mode is generate/condense "
                f"[gamma.text.amount-required]"
            )
        if mode == "preserve" and amount_present:
            errors.append(
                f"{name}: text_content.amount must be absent when mode is preserve "
                f"(Gamma ignores amount in preserve) [gamma.text.amount-mode]"
            )
        if amount_present and str(amount_raw).strip().lower() not in TEXT_AMOUNT_UI_VALUES:
            errors.append(
                f"{name}: text_content.amount={amount_raw!r} is not a Gamma UI amount "
                f"value {sorted(TEXT_AMOUNT_UI_VALUES)}; the registry stores UI vocabulary "
                f"(not the API value) [gamma.text.amount-ui-values]"
            )

    # --- Frozen-enum validation on the RESOLVED surface ---------------------------
    for key, allowed in _ENUM_CHECKS.items():
        if key in resolved and str(resolved[key]).strip() not in allowed:
            errors.append(
                f"{name}: {key}={resolved[key]!r} is not one of {sorted(allowed)} "
                f"(frozen enum from _act.py)"
            )

    # --- Cross-field: image_style_preset='custom' REQUIRES a custom_style ----------
    # Gary raises `image_style is required when image_style_preset='custom'` at
    # dispatch; the offline write-gate must reject the same config at write time so a
    # would-crash-at-render style never ships (code-review item #6).
    if str(resolved.get("image_style_preset") or "").strip() == "custom" and not _is_present(
        resolved.get("image_style")
    ):
        errors.append(
            f"{name}: image_style_preset='custom' requires a custom_style "
            f"(visuals.custom_style) or Gary crashes at dispatch"
        )

    # --- Rule 2 (ERROR): image_model honored only under image_source=aiGenerated ----
    # On the RESOLVED surface: a model string is a silent no-op under unsplash/
    # webAllImages/giphy/pictographic/etc. Fail loud at write time (Gary's Gamma-truth).
    if _is_present(resolved.get("image_model")) and (
        str(resolved.get("image_source") or "").strip() != "aiGenerated"
    ):
        errors.append(
            f"{name}: image_model={resolved.get('image_model')!r} is set but "
            f"image_source={resolved.get('image_source')!r} != 'aiGenerated'; the "
            f"model string is a silent no-op under non-aiGenerated sources "
            f"[gamma.dep.image-model-source]"
        )

    # --- Rule 3 (WARN, RAW record): named preset subordinates a set image_style -----
    # Evaluated on the RAW record (the resolver keeps both, but the raw fields are the
    # CD-authored intent). A named preset dominates the card theme while a set
    # image_style (visuals.custom_style) may be silently subordinated. WARN (a merge,
    # not invalid — never hard-block), surfaced LOUD/visible, never a silent drop.
    visuals = (record.get("prompt_configuration") or {}).get("visuals") or {}
    raw_preset = str(visuals.get("style_preset") or "").strip()
    if raw_preset and raw_preset != "custom" and _is_present(visuals.get("custom_style")):
        warnings.append(
            f"{name}: image_style_preset={raw_preset!r} is a named preset AND "
            f"image_style (visuals.custom_style) is also set; the preset dominates the "
            f"card theme and the top-level image_style may be silently subordinated. "
            f"To let the custom style dominate, set image_style_preset='custom' — do NOT "
            f"drop the source-derived custom_style (protected source-detail conveyance) "
            f"[gamma.dep.preset-style-subordinated]"
        )

    # --- Coherence-triad: theme + art-style/keywords + dimensions + prose ----------
    if not _is_present(_triad_rationale(record)):
        errors.append(
            f"{name}: coherence-triad requires a non-empty "
            f"presentation.narrative.triad_rationale prose"
        )
    if production_mode == "api":
        visuals = (record.get("prompt_configuration") or {}).get("visuals") or {}
        art_axis = _is_present(visuals.get("keywords")) or _is_present(
            visuals.get("style_preset")
        ) or _is_present(visuals.get("custom_style"))
        if not art_axis:
            errors.append(
                f"{name}: coherence-triad art axis empty (needs keywords or a "
                f"style_preset/custom_style to agree with theme + dimensions)"
            )

    # --- Lifecycle (session-07 A1): candidate | permanent | deprecated -------------
    errors.extend(_validate_lifecycle_errors(name, record))
    warnings.extend(_validate_lifecycle_warnings(name, record))

    # --- Scripted block (Leg-C): sealed registry-bound closed-vocab namespace ------
    errors.extend(_validate_scripted(name, record))

    # --- Style-level additional_instructions (AC-1 shape + AC-5 non-contradiction) --
    errors.extend(_validate_additional_instructions_shape(name, record))
    prose_errors, prose_warnings = _validate_prose_noncontradiction(name, record, resolved)
    errors.extend(prose_errors)
    warnings.extend(prose_warnings)
    return (errors, warnings)


def _validate_lifecycle_errors(name: str, record: dict[str, Any]) -> list[str]:
    """Hard-blocking lifecycle rules (session-07 green-light A1).

    - An explicit lifecycle value must be in the closed enum.
    - An explicit ``candidate`` must carry ``promotion_criteria`` (the B-corpus
      stress-test + re-run reliability contract) and ``authored_session``
      provenance, so a candidate can never masquerade as production nor lose the
      record of what promotion requires.
    """
    errors: list[str] = []
    raw = record.get("lifecycle")
    if raw is None:
        return errors  # absent -> WARN path (safe-default candidate)
    value = str(raw).strip().lower()
    if value not in _LIFECYCLE_VALUES:
        errors.append(
            f"{name}: lifecycle={raw!r} is not one of {sorted(_LIFECYCLE_VALUES)} "
            f"[gamma.lifecycle.unknown-value]"
        )
        return errors
    if value == "candidate":
        if not _is_present(record.get("promotion_criteria")):
            errors.append(
                f"{name}: lifecycle=candidate requires a non-empty promotion_criteria "
                f"(B-corpus stress-test + re-run reliability contract) "
                f"[gamma.lifecycle.missing-promotion-criteria]"
            )
        if not _is_present(record.get("authored_session")):
            errors.append(
                f"{name}: lifecycle=candidate requires authored_session provenance "
                f"[gamma.lifecycle.missing-authored-session]"
            )
    return errors


def _validate_lifecycle_warnings(name: str, record: dict[str, Any]) -> list[str]:
    """Loud non-fatal lifecycle surface: absence defaults to candidate."""
    if record.get("lifecycle") is None:
        return [
            f"{name}: no lifecycle field — treated as CANDIDATE (safe default); "
            f"mark permanent only through the promotion gate "
            f"[gamma.lifecycle.defaulted-candidate]"
        ]
    return []


def validate_style_guides_full(
    data: dict[str, Any],
    *,
    check_existence: bool = False,
    lock_path: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Return ``(errors, warnings)`` for the styleguide library payload.

    Errors are hard-blocking (fail the exit code). Warnings surface loudly but only
    fail the exit code under ``--strict`` (see ``main``). This is the full/pinned
    output shape; ``validate_style_guides`` is the back-compatible errors-only view.

    Leg-B2: the top-level ``learned_dependencies`` block (default empty / absent) is
    pinned by the identity manifest (``check_manifest_pin``) and its ACTIVE rules are
    applied per-record via the pure declarative interpreter (``apply_learned_rules``),
    routing to the same (errors, warnings) channels. An absent block + empty manifest
    is a clean no-op. This path is hermetic — a FILE store, never the Postgres ledger.

    ``check_existence`` is the ONLY network path (theme/template live existence). It
    is OFF by default so the CI/hermetic run never touches the network.
    """
    errors: list[str] = []
    warnings: list[str] = []
    guides = data.get("style_guides")
    if not isinstance(guides, dict) or not guides:
        return (["style_guides mapping is missing or empty"], warnings)

    # --- Learned-dependencies pin (Leg-B2): active rule-id set is pinned by the
    #     identity manifest (superset + predicate_hash + fixture existence). ----------
    active_rules = active_learned_rules(data.get("learned_dependencies"))
    manifest = load_manifest(
        lock_path if lock_path is not None else GAMMA_LEARNED_RULES_LOCK_PATH
    )
    errors.extend(check_manifest_pin(active_rules, manifest))

    classic_count = 0
    studio_count = 0
    for name in sorted(guides):
        record = guides[name]
        rec_errors, rec_warnings = _validate_one(name, record)
        errors.extend(rec_errors)
        warnings.extend(rec_warnings)
        # --- Apply ACTIVE learned rules per-record (offline, gated by the pin) -------
        if active_rules and isinstance(record, dict):
            try:
                resolved = expand_record(record, name=name)
            except StyleguideError:
                resolved = {}
            le, lw = apply_learned_rules(record, resolved, active_rules, name=name)
            errors.extend(le)
            warnings.extend(lw)
        if isinstance(record, dict):
            mode = str(record.get("production_mode") or "").strip().lower()
            if mode == "api":
                classic_count += 1
            elif mode == "studio":
                studio_count += 1

    # --- Roster floor -------------------------------------------------------------
    if classic_count < 1:
        errors.append("roster floor: at least 1 Classic (api) styleguide is required")
    if studio_count < 1:
        errors.append("roster floor: at least 1 Studio styleguide is required")

    if check_existence:
        errors.extend(_check_existence(guides))
    return (errors, warnings)


def validate_style_guides(
    data: dict[str, Any],
    *,
    check_existence: bool = False,
    strict: bool = False,
) -> list[str]:
    """Back-compatible errors-only view over :func:`validate_style_guides_full`.

    Default behavior is unchanged (existing callers see the same error list). Under
    ``strict=True`` the warnings are folded into the returned list so a warning also
    fails the exit code.
    """
    errors, warnings = validate_style_guides_full(data, check_existence=check_existence)
    if strict:
        return errors + warnings
    return errors


def _check_existence(guides: dict[str, Any]) -> list[str]:  # pragma: no cover - network
    """Live theme/template existence check (the ONLY network-touching path)."""
    from scripts.api_clients.gamma_client import GammaClient

    errors: list[str] = []
    client = GammaClient()
    # Real Gamma API caps `limit` at 50 (HTTP 400 above it). Pagination beyond
    # the first 50 themes is a filed follow-on (styleguide-validator-live-existence-hardening).
    theme_ids = {t.get("id") for t in client.list_themes(limit=50)}
    for name, record in guides.items():
        if not isinstance(record, dict):
            continue
        if str(record.get("production_mode") or "").strip().lower() == "api":
            theme_id = (record.get("theme") or {}).get("id")
            if theme_id and theme_id not in theme_ids:
                errors.append(f"{name}: theme id {theme_id!r} not found in live Gamma themes")
        # Studio template existence has no cheap list endpoint; a real render is the
        # authoritative check (Leg-A AC#5), so we only note the id here.
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=GAMMA_STYLE_GUIDES_PATH,
        help="path to gamma-style-guides.yaml",
    )
    parser.add_argument(
        "--check-existence",
        action="store_true",
        help="ALSO live-verify theme/template ids against the Gamma API (network).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat WARNINGS as failures too (they are surfaced but non-fatal by default).",
    )
    args = parser.parse_args(argv)

    data = load_style_guides(args.path)
    errors, warnings = validate_style_guides_full(
        data, check_existence=args.check_existence
    )

    # Warnings surface LOUD/visible even when non-fatal (green-light Decision 2 —
    # never a silent drop).
    if warnings:
        print(f"WARN: {len(warnings)} styleguide warning(s):")
        for warn in warnings:
            print(f"  ! {warn}")

    if errors:
        print(f"FAIL: {len(errors)} styleguide validation error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    if warnings and args.strict:
        print("FAIL(--strict): warnings present and --strict is set")
        return 1
    print(f"OK: {args.path} is copacetic ({len(data.get('style_guides', {}))} styleguide(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

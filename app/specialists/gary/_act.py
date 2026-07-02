"""Gary Class-C Gamma API act implementation."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.gamma_dispatch import GammaDispatchError, dispatch_to_gamma
from app.specialists.gary.styleguide_library import (
    RESOLVED_API_KEYS,
    STYLEGUIDE_CLASSIC_ONLY_KEYS,
    SURFACE_VIOLATION_TAG,
    StyleguideError,
    resolve_styleguide,
)
from scripts.api_clients.gamma_client import GammaClient
from skills.gamma_api_mastery.scripts.gamma_operations import (
    download_export,
    materialize_exported_slide_paths_by_title,
)

_LOGGER = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-gary"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-gamma" / "references"
TEXT_AMOUNT_VALUES = frozenset({"brief", "medium", "detailed", "extensive"})
TEXT_LANGUAGE_VALUES = frozenset({"en"})
TEXT_MODE_VALUES = frozenset({"generate", "condense", "preserve"})
IMAGE_STYLE_PRESET_VALUES = frozenset(
    {"photorealistic", "illustration", "abstract", "3D", "lineArt", "custom"}
)
IMAGE_SOURCE_VALUES = frozenset(
    {
        "aiGenerated",
        "pexels",
        "webFreeToUse",
        "webFreeToUseCommercially",
        "themeAccent",
        "placeholder",
        "noImages",
        "pictographic",
        "giphy",
        "webAllImages",
    }
)
# Doc-parity: https://developers.gamma.app/reference/image-model-accepted-values.md
# Last reconciled: 2026-07-02 (strict doc-parity, D-1).
# Refresh via: scripts/utilities/audit_gamma_docs.py (drift files to the learned store).
IMAGE_MODEL_VALUES = frozenset(
    {
        "flux-1-quick",
        "flux-2-klein",
        "flux-kontext-fast",
        "imagen-3-flash",
        "gpt-image-1-mini-low",
        "luma-photon-flash-1",
        "gpt-image-2-mini",
        "flux-1-pro",
        "imagen-3-pro",
        "flux-2-pro",
        "gpt-image-1-mini-medium",
        "ideogram-v3-turbo",
        "luma-photon-1",
        "recraft-v4",
        "leonardo-phoenix",
        "flux-2-flex",
        "flux-2-max",
        "flux-kontext-pro",
        "ideogram-v3",
        "imagen-4-pro",
        "recraft-v3",
        "gemini-2.5-flash-image",
        "gpt-image-1-mini-high",
        "gpt-image-1-medium",
        "gpt-image-2",
        "flux-1-ultra",
        "imagen-4-ultra",
        "dall-e-3",
        "gemini-3.1-flash-image-mini",
        "flux-kontext-max",
        "recraft-v3-svg",
        "recraft-v4-svg",
        "ideogram-v3-quality",
        "gemini-3.1-flash-image",
        "gemini-3-pro-image",
        "gemini-3.1-flash-image-hd",
        "gpt-image-2-hd",
        "gpt-image-1-high",
        "gemini-3-pro-image-hd",
        "recraft-v4-pro",
    }
)
CARD_DIMENSION_VALUES = frozenset(
    {"fluid", "16x9", "4x3", "pageless", "letter", "a4", "1x1", "4x5", "9x16"}
)
GAMMA_SETTING_KEYS = frozenset(
    {
        "variant_id",
        "theme",
        "template",
        "image_style",
        "density",
        "amount",
        "tone",
        "audience",
        "language",
        "text_mode",
        "image_style_preset",
        "image_model",
        "image_source",
        "dimensions",
        "keywords",
        # Studio production mode (party-ratified 2026-06-25). production_mode
        # "studio" routes this variant to a per-slide Gamma create-from-template
        # call (a single full-bleed image-card per slide) instead of the Classic
        # generate path; "api" (default) is the unchanged Classic path.
        "production_mode",
        "studio_template_id",
        # CD-owned styleguide library (Leg-A 2026-07-01). When present, names a
        # record in state/config/gamma-style-guides.yaml whose resolved base-layer
        # API keys seed this variant BEFORE per-variant overrides. It is the ONLY
        # key added here; metadata/scripted keys are STRIPPED by the resolver and
        # never reach a gamma_settings[] item (so the unknown-key gate below stays
        # meaningful).
        "styleguide",
    }
)
# Drift-guard (code-review item #4): the styleguide resolver may only emit keys Gary
# recognizes, or a resolved base-layer key would trip the unknown-key gate below at
# dispatch. Assert the subset at import time so the two frozensets can never diverge.
assert not (RESOLVED_API_KEYS - GAMMA_SETTING_KEYS), (
    "styleguide RESOLVED_API_KEYS drifted outside GAMMA_SETTING_KEYS: "
    f"{sorted(RESOLVED_API_KEYS - GAMMA_SETTING_KEYS)}"
)
PRODUCTION_MODE_VALUES = frozenset({"api", "studio"})
# Classic-only surface a per-variant override may NOT carry on a studio-bound variant
# (code-review item #3b), expressed as gamma_settings item keys. ``custom_style`` maps
# to the ``image_style`` item key; ``num_cards``/``card_split`` are not gamma_settings
# keys (they trip the unknown-key gate first) but stay listed for parity.
_STUDIO_FORBIDDEN_ITEM_KEYS = (STYLEGUIDE_CLASSIC_ONLY_KEYS - {"custom_style"}) | {"image_style"}


def _setting_present(value: Any) -> bool:
    """A per-variant override ``counts`` only when it is a non-empty value."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True
# Lock-and-replace prompt (n=2 live-verified 2026-06-25; see
# _bmad-output/implementation-artifacts/studio-mode-evidence/). FROZEN: this string
# is what makes Studio *be* Studio — a prose-heavy / restructuring prompt silently
# regenerates the card to Classic typography (the demonstrated fallback). Edit only
# deliberately; the studio guard below is the runtime backstop.
_STUDIO_LOCK_WRAPPER = (
    "LOCK THE DESIGN. Keep exactly ONE single full-bleed image card with the title "
    "and key data embedded in the illustration. DO NOT convert the full-bleed image "
    "card into Classic typography. DO NOT add, remove, or reorder cards, and DO NOT "
    "change the card type or layout.\n\n"
    "ONLY swap the image subject to this new topic, matching the template's existing "
    "visual style:\n{slide_content}"
)
# Studio guard threshold — discriminate a genuine Studio image-card from a silently
# fallen-back Classic card by ASPECT RATIO (content- and lightness-independent, and it
# matches the actual fallback MECHANISM). A Studio image-card inherits the template's
# 16:9 frame (w/h = 1.778); a Classic regen falls back to Gamma's default card
# dimensions and exports near-square/tall. Calibrated on real artifacts: the documented
# Classic fallback = 2400x2324 (ar 1.03); every genuine Studio card (dark goldens AND
# light infographic trial-5 slides) = 2400x1350 (ar 1.778). Threshold sits in the gap.
# (Color/brightness heuristics were tried first but false-positived on clean light-
# infographic Studio cards — trial-5 slide-03 nonwhite 0.25, slide-09 only 418 colors,
# both unmistakably Studio.)
_STUDIO_MIN_ASPECT_RATIO = 1.4
DEFAULT_VARIANT_PAIR: tuple[dict[str, Any], dict[str, Any]] = (
    {
        "variant_id": "A",
        "theme": "njim9kuhfnljvaa",
        "template": "default",
        "image_style_preset": "illustration",
        "amount": "brief",
        # text_mode=preserve (Fidelity L1, 2026-06-24). Under the prior default
        # `generate`, Gamma RE-MINTED source numbers on variant A — source
        # "$5.2 trillion" rendered as "$4.5 trillion" (+ invented 60%/35%, $760B);
        # the variant-faithful narration then read the WRONG figure to the learner
        # (the figure-citation gate only checks narration ⊆ rendered slide, not the
        # source). In a health-economics course a fabricated figure is a credibility
        # defect, not a style nit. `generate`'s prose-reflow latitude IS the
        # re-minting mechanism; `preserve` removes it deterministically while the
        # theme/type/palette + imagery (the real A/B differentiation) survive intact.
        # Party-mode 4/4 + Dr. Quinn synthesis (impasse chain): blanket preserve on A,
        # reframed as removing an un-designed defect-causing behavior, not over-correction.
        # Per-slide text_mode (preserve-numeric-slides-only) is a deferred enhancement
        # (text_mode is per-variant, not per-slide; see deferred-inventory
        # `fidelity-L1-per-slide-text-mode`). Downstream the L2 source-fidelity audit
        # is the regression guard.
        "text_mode": "preserve",
        "audience": (
            "Faculty and instructional designers familiar with Canvas and course "
            "design, American English"
        ),
        "tone": "Clear, professional, engaging in American English",
        "language": "en",
        "image_source": "aiGenerated",
        # Pure representation (code-review item #5): the last baked-in 16:9 forcing on
        # the unbound-variant path is removed — publication-time anti-crop (16:9 for
        # Descript) is a runtime policy follow-on, not a fixture default.
        "dimensions": "fluid",
    },
    {
        "variant_id": "B",
        "theme": "e8tz1vxb9v1urqp",
        "template": "default",
        "image_style_preset": "lineArt",
        "image_model": "recraft-v3-svg",
        "keywords": [
            "blueprint",
            "technical line drawing",
            "dotted construction lines",
            "architectural",
            "single-accent color",
        ],
        "amount": "brief",
        # text_mode=preserve (not the default `generate`, and NOT `condense`) keeps the
        # briefed chunk text verbatim on the slide. This fixes TWO failure modes at once,
        # both observed 2026-06-24 on variant B:
        #  1. title-drift: under `generate`, B's editorial tone re-titled slide-06
        #     ("Deliberate physician leadership is the unifying answer"), breaking the
        #     bijective title-match (gamma.export.brief-unmatched). preserve keeps the
        #     `# {title}` heading verbatim, so the match always resolves.
        #  2. figure-loss: under `condense`, B re-rendered quantitative content as prose
        #     ("training remains scarce" instead of "18% receive training"), dropping the
        #     numbers the variant-agnostic narration cites -> G5 fidelity-figure-
        #     contradiction whenever B was the picked variant. preserve keeps the source
        #     figures on the slide, so perception sees them and fidelity passes.
        # Visual A/B distinctness still comes from theme + lineArt/blueprint imagery.
        "text_mode": "preserve",
        "tone": "Confident, precise, lightly editorial - American English",
        "audience": (
            "Faculty and instructional designers familiar with Canvas and course "
            "design, American English"
        ),
        "language": "en",
        "image_source": "aiGenerated",
        # Pure representation (code-review item #5): 16:9 forcing removed here too.
        "dimensions": "fluid",
    },
)
GARY_REFERENCES = (
    "content-type-mapping.md",
    "context-envelope-schema.md",
    "theme-template-preview.md",
    "quality-assessment.md",
)


class GaryActError(SpecialistDispatchError):
    """Raised when Gary cannot produce a valid Gamma output envelope.

    Taxonomy re-base (live-path tranche, 2026-06-12): dispatch-family so a
    mid-walk failure error-pauses recoverably instead of killing the trial.
    """


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise GaryActError("gary envelope cache_prefix is not JSON", tag="gamma.malformed") from exc
    if not isinstance(decoded, dict):
        raise GaryActError(
            "gary envelope cache_prefix must decode to an object",
            tag="gamma.wrong-type",
        )
    return decoded


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows: list[str] = []
    for path in sorted(sanctum_dir.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            rows.append(f"{path.relative_to(sanctum_dir).as_posix()}\t{digest}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts: list[str] = []
    for name in GARY_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _slides(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("slides") or payload.get("per_slide_directives") or []
    if not raw:
        # Taxonomy re-base tranche (2026-06-12): the fabricated slide-01
        # roster was the slides-leg sibling of quinn_r's ninth seam —
        # absence of inputs is a contract violation, never a mode switch.
        raise GaryActError(
            "gary dispatched with no slides/per_slide_directives; refusing "
            "to fabricate a placeholder roster",
            tag="gamma.slides.starved",
        )
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise GaryActError("gary slides must be a list of objects", tag="gamma.slides.invalid")
    return raw


def _theme_id(
    client: GammaClient,
    payload: dict[str, Any],
    *,
    themes: list[dict[str, Any]] | None = None,
) -> str | None:
    theme_limit = int(payload.get("theme_limit", 20))
    requested = str(payload.get("theme_id") or "").strip()
    themes = themes if themes is not None else client.list_themes(limit=theme_limit)
    if requested:
        return _resolve_and_validate_theme(requested, themes)
    for theme in themes:
        if isinstance(theme, dict):
            value = theme.get("id") or theme.get("themeId") or theme.get("gammaId")
            if value:
                return str(value)
    return None


def _resolve_and_validate_theme(
    requested: str,
    themes: list[dict[str, Any]],
) -> str:
    lookup: dict[str, str] = {}
    for theme in themes:
        if not isinstance(theme, dict):
            continue
        value = theme.get("id") or theme.get("themeId") or theme.get("gammaId")
        if not value:
            continue
        theme_id = str(value)
        lookup[theme_id] = theme_id
        name = theme.get("name")
        if name:
            lookup[str(name)] = theme_id
    if requested in lookup:
        return lookup[requested]
    raise GaryActError(
        f"gamma theme {requested!r} not found in list_themes() window",
        tag="gamma.theme.invalid",
    )


def _validate_enum_setting(
    settings: dict[str, Any],
    key: str,
    allowed: frozenset[str],
    *,
    omit_sentinels: frozenset[str] = frozenset({"", "default"}),
) -> None:
    value = settings.get(key)
    normalized = str(value).strip()
    if value is None or normalized in omit_sentinels:
        return
    if normalized not in allowed:
        raise GaryActError(
            f"gamma_settings.{key} must be one of {sorted(allowed)}; got {value!r}",
            tag="gamma.settings.invalid",
        )


def _normalized_gamma_settings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("gamma_settings")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise GaryActError(
            "gamma_settings must be a list when present",
            tag="gamma.settings.invalid",
        )
    # DEFAULT_VARIANT_PAIR is the per-variant BASE SEED only (styleguide-less path,
    # the ``else`` branch below); it is NOT a dispatch roster. The return projects
    # ONLY the variants actually named in ``raw`` (``present_ids``, payload order), so
    # a seed here can never re-introduce an unrequested variant into the returned list.
    # (base-seed only; superseded once cd-envelope-authoring lands.)
    by_variant: dict[str, dict[str, Any]] = {
        item["variant_id"]: dict(item) for item in DEFAULT_VARIANT_PAIR
    }
    present_ids: dict[str, None] = {}  # ordered set — payload order, determinism (AC#3)
    for item in raw:
        if item is None:
            continue
        if not isinstance(item, dict):
            raise GaryActError(
                "gamma_settings entries must be objects",
                tag="gamma.settings.invalid",
            )
        variant_id = str(item.get("variant_id") or "").strip().upper()
        if variant_id not in {"A", "B"}:
            raise GaryActError(
                "gamma_settings variant_id must be A or B",
                tag="gamma.settings.invalid",
            )
        # A payload naming the SAME variant twice would silently merge-accumulate
        # (order-dependent, non-obvious) into a single projected entry. Fail loud so
        # a duplicated variant surfaces up-front, consistent with the fail-loud
        # philosophy of the surrounding guards (Blind Hunter SHOULD-FIX).
        if variant_id in present_ids:
            raise GaryActError(
                f"gamma_settings names variant {variant_id} more than once",
                tag="gamma.settings.invalid",
            )
        present_ids[variant_id] = None
        unknown = sorted(set(item) - GAMMA_SETTING_KEYS)
        if unknown:
            raise GaryActError(
                f"gamma_settings contains unknown key(s): {unknown}",
                tag="gamma.settings.invalid",
            )
        # Styleguide base-layer seed (Leg-A). When this variant names a CD-owned
        # styleguide, the library record is the AUTHORITATIVE base — it replaces the
        # DEFAULT_VARIANT_PAIR smoke fixture as the seed — and per-variant explicit
        # keys below still override it. The resolver emits ONLY recognized API keys
        # (metadata/scripted stripped), so nothing here can trip the :375 gate.
        styleguide_name = item.get("styleguide")
        if styleguide_name is not None:
            # A PRESENT styleguide key must name a real guide. A blank value fails
            # loud (code-review item #10) — never silently reverts to the smoke
            # fixture (asymmetric with the unknown-name fail-loud that follows).
            name_str = str(styleguide_name).strip()
            if not name_str:
                raise GaryActError(
                    "gamma_settings.styleguide is present but blank; a present "
                    "styleguide key must name a real guide",
                    tag="gamma.styleguide.unknown",
                )
            try:
                resolved_base = resolve_styleguide(name_str)
            except StyleguideError as exc:
                raise GaryActError(str(exc), tag=exc.tag) from exc
            merged = {"variant_id": variant_id, **resolved_base}
        else:
            # Honesty WARN (AC#7): a present variant with no bound styleguide seeds
            # from the DEFAULT_VARIANT_PAIR smoke fixture — a hidden default that the
            # CD-owned styleguide library is meant to supersede. Observability only
            # (no output change); the fail-loud flip is deferred to cd-envelope-authoring.
            _LOGGER.warning(
                "variant %s present with no bound styleguide; seeding from "
                "DEFAULT_VARIANT_PAIR base — fail-loud deferred to cd-envelope-authoring",
                variant_id,
            )
            merged = dict(by_variant[variant_id])
        for key in GAMMA_SETTING_KEYS - {"variant_id", "styleguide"}:
            value = item.get(key)
            if value is None:
                continue
            if key == "keywords":
                if not isinstance(value, list):
                    raise GaryActError(
                        "gamma_settings.keywords must be a list of strings",
                        tag="gamma.settings.invalid",
                    )
                cleaned = [str(part).strip() for part in value if str(part).strip()]
                # An empty/blank-only keyword LIST means "unset" (symmetry with the
                # empty-string skip below) — do NOT clobber the styleguide's curated
                # keywords to empty (code-review item #7).
                if cleaned:
                    merged[key] = cleaned
            elif str(value).strip():
                merged[key] = str(value).strip()
        if "amount" not in merged and merged.get("density") not in (None, "balanced"):
            merged["amount"] = merged["density"]
        _validate_enum_setting(
            merged,
            "amount",
            TEXT_AMOUNT_VALUES,
            omit_sentinels=frozenset({"", "default", "balanced"}),
        )
        _validate_enum_setting(merged, "language", TEXT_LANGUAGE_VALUES)
        _validate_enum_setting(
            merged,
            "text_mode",
            TEXT_MODE_VALUES,
            omit_sentinels=frozenset({"", "default", "generate"}),
        )
        _validate_enum_setting(merged, "image_style_preset", IMAGE_STYLE_PRESET_VALUES)
        _validate_enum_setting(
            merged,
            "image_model",
            IMAGE_MODEL_VALUES,
            omit_sentinels=frozenset({"", "default", "auto"}),
        )
        _validate_enum_setting(merged, "image_source", IMAGE_SOURCE_VALUES)
        _validate_enum_setting(merged, "dimensions", CARD_DIMENSION_VALUES)
        # Studio mode (party-ratified 2026-06-25): default "api" (Classic, unchanged);
        # "studio" REQUIRES studio_template_id, validated here at config-read so a
        # misconfigured studio variant fails loudly up-front, never mid-dispatch.
        production_mode = str(merged.get("production_mode") or "api").strip().lower()
        merged["production_mode"] = production_mode
        if production_mode not in PRODUCTION_MODE_VALUES:
            raise GaryActError(
                f"gamma_settings.production_mode must be one of "
                f"{sorted(PRODUCTION_MODE_VALUES)}; got {production_mode!r}",
                tag="gamma.settings.invalid",
            )
        if production_mode == "studio" and not str(merged.get("studio_template_id") or "").strip():
            raise GaryActError(
                "gamma_settings.production_mode='studio' requires studio_template_id",
                tag="gamma.settings.invalid",
            )
        # Studio discriminated-union airtight (code-review item #3b): a per-variant
        # Classic override on a studio-bound variant must FAIL LOUD, not be silently
        # dropped. We inspect the EXPLICIT per-variant keys (``item``), so the
        # unbound direct-studio path — which inherits Classic keys from the smoke
        # fixture but declares none itself — is unaffected.
        if production_mode == "studio":
            classic_overrides = sorted(
                key
                for key in _STUDIO_FORBIDDEN_ITEM_KEYS
                if key in item and _setting_present(item.get(key))
            )
            if classic_overrides:
                raise GaryActError(
                    f"gamma_settings variant {variant_id} is production_mode='studio' "
                    f"but carries Classic-only override(s) {classic_overrides}; the "
                    f"template is the style authority (surface-violation)",
                    tag=SURFACE_VIOLATION_TAG,
                )
        by_variant[variant_id] = merged
    # A NON-EMPTY gamma_settings whose entries are all skipped (e.g. ``[None]``)
    # yields an empty ``present_ids`` → an empty return → the CONSUMER's ``or (...)``
    # fallback re-dispatches the default A/B fixture, silently re-introducing the
    # exact unbound-fixture dispatch this story retired. Fail loud instead. AC#4 is
    # preserved: an EMPTY ``raw`` (and ``raw is None``, handled above) still returns
    # ``[]`` — only a NON-EMPTY raw that names zero valid variants raises here.
    if raw and not present_ids:
        raise GaryActError(
            "gamma_settings has entries but names no valid variant",
            tag="gamma.settings.invalid",
        )
    # Project ONLY the payload-present variants, in payload order — retire the
    # hardcoded ``[A, B]`` padding that paid-dispatched an unbound fixture deck.
    return [by_variant[variant_id] for variant_id in present_ids]


def _theme_id_for_variant(
    base_theme_id: str | None,
    settings: dict[str, Any],
    themes: list[dict[str, Any]],
) -> str | None:
    theme = str(settings.get("theme") or "").strip()
    if theme and theme != "default":
        return _resolve_and_validate_theme(theme, themes)
    return base_theme_id


def _text_options_for_variant(settings: dict[str, Any]) -> dict[str, str]:
    amount = str(settings.get("amount") or settings.get("density") or "").strip()
    tone = str(settings.get("tone") or "").strip()
    audience = str(settings.get("audience") or "").strip()
    language = str(settings.get("language") or "").strip()
    options: dict[str, str] = {}
    if amount and amount not in {"balanced", "default"}:
        options["amount"] = amount
    if tone and tone not in {"professional", "default"}:
        options["tone"] = tone
    if audience and audience != "default":
        options["audience"] = audience
    if language and language != "default":
        options["language"] = language
    return options


def _image_options_for_variant(settings: dict[str, Any]) -> dict[str, str]:
    style = str(settings.get("image_style") or "").strip()
    style_preset = str(settings.get("image_style_preset") or "").strip()
    model = str(settings.get("image_model") or "").strip()
    source = str(settings.get("image_source") or "").strip()
    options: dict[str, str] = {}
    if source and source != "default":
        options["source"] = source
    if model and model not in {"default", "auto"}:
        options["model"] = model
    if style_preset and style_preset != "default":
        if style_preset == "custom" and not style:
            raise GaryActError(
                "gamma_settings.image_style is required when image_style_preset='custom'",
                tag="gamma.settings.invalid",
            )
        options["stylePreset"] = style_preset
        if style_preset == "custom" and style:
            options["style"] = style
        return options
    if style:
        options["style"] = style
    return options


def _card_options_for_variant(settings: dict[str, Any]) -> dict[str, str]:
    dimensions = str(settings.get("dimensions") or "").strip()
    if not dimensions or dimensions == "default":
        return {}
    return {"dimensions": dimensions}


def _instructions_for_variant(
    payload: dict[str, Any],
    *,
    variant: str,
    settings: dict[str, Any] | None,
) -> str:
    parts = [
        str(payload.get("additional_instructions") or "").strip(),
        "Use each section's leading heading as that card's title verbatim; "
        "produce exactly one card per section; do not add a cover, agenda, "
        "divider, or summary card; do not merge or split sections.",
    ]
    if settings is not None:
        # The structured style settings (image_style_preset/amount/tone/audience/
        # language) travel STRUCTURALLY via imageOptions/textOptions only — echoing
        # them here would be merely-redundant (and risk the model painting a stray
        # `key=value` onto a card) and once rendered `image_style=None`. Keywords stay
        # in this prose channel as natural imagery guidance so their source-derived
        # VALUES reach Gamma and compose on top of the styleguide base.
        keywords = settings.get("keywords")
        if isinstance(keywords, list) and keywords:
            parts.append(
                f"Emphasize this imagery: {', '.join(str(item) for item in keywords)}."
            )
    parts.append(f"Variant {variant}.")
    return " ".join(part for part in parts if part).strip()


def _slide_title(slide: dict[str, Any], index: int) -> str:
    """The briefed card title — the SINGLE source for both the Gamma card
    heading (in `_input_text`) and the export title-match key (`expected_slots`).

    Storyboard-correctness follow-on (2026-06-19): Gamma free-titles and merges
    pages unless each input chunk leads with the exact briefed title under
    `cardSplit=inputTextBreaks`. Sharing one helper guarantees the heading we
    send and the key we match on cannot drift apart.
    """
    return str(
        slide.get("title")
        or slide.get("prompt")
        or slide.get("visual_description")
        or f"slide-{index:02d}"
    )


def _input_text(slides: list[dict[str, Any]], payload: dict[str, Any]) -> str:
    if payload.get("input_text"):
        return str(payload["input_text"])
    chunks = []
    for index, slide in enumerate(slides, start=1):
        title = _slide_title(slide, index)
        body = str(
            slide.get("prompt") or slide.get("brief") or slide.get("visual_description") or ""
        ).strip()
        # The `\n---\n` break is load-bearing under cardSplit=inputTextBreaks
        # (it delimits cards), so a body that embeds it would split a spurious
        # extra card and fail the bijective match. Neutralize any embedded
        # delimiter before it reaches the card splitter.
        body = body.replace("\n---\n", " ")
        # Lead every chunk with the exact briefed title as a heading so Gamma
        # adopts it as the card title verbatim under cardSplit=inputTextBreaks;
        # the export title-matcher (bijective containment) then resolves cleanly
        # instead of fail-louding on Gamma's invented page titles.
        chunk = f"# {title}" if not body or body == title else f"# {title}\n\n{body}"
        chunks.append(chunk)
    return "\n---\n".join(chunks)


def build_vera_g3_invocation(slide_output: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [row["file_path"] for row in slide_output if row.get("file_path")]
    return {"specialist_id": "vera", "gate_id": "G3", "artifact_paths": paths}


def _safe_slug(value: str) -> str:
    """Filesystem-safe token for a slide_id used inside an export filename.

    Stops a caller-supplied slide_id that contains path separators or OS-illegal
    characters from steering ``download_export`` outside ``export_dir``.
    """
    slug = "".join(c if (c.isalnum() or c in "._-") else "-" for c in value).strip("-")
    return slug or "slide"


def _studio_slide_content(slide: dict[str, Any], index: int) -> str:
    """Subject text for one Studio card's lock-and-replace prompt (minimal directive;
    the template is the style authority — we only swap the subject)."""
    title = _slide_title(slide, index)
    body = str(
        slide.get("visual_description")
        or slide.get("prompt")
        or slide.get("body")
        or slide.get("brief")
        or ""
    ).strip()
    return f'Title: "{title}"\n{body}' if body else f'Title: "{title}"'


def _assert_studio_image_card(png_path: Path, *, slide_id: str, generation_id: str) -> None:
    """Fail loud if a studio generation silently returned a Classic card.

    The REST get_generation response carries no card-type marker, so the guard
    inspects the exported PNG's ASPECT RATIO: a Studio image-card inherits the
    template's 16:9 frame (w/h ~ 1.78), while a silent Classic fallback exports at
    Gamma's default near-square/tall card dimensions. Content- and lightness-
    independent. Calibrated against the real artifacts in studio-mode-evidence/.
    Recoverable family (error-pause + trial recover).
    """
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(png_path) as raw:
            width, height = raw.size
    except (UnidentifiedImageError, OSError) as exc:
        # A zero-byte / truncated / non-PNG export must NOT escape as a bare
        # PIL OSError (which is not a SpecialistDispatchError and would kill the
        # trial) — re-raise into the recoverable family this guard promises.
        raise GammaDispatchError(
            f"studio generation for slide {slide_id} produced an unreadable "
            f"export ({png_path}): {exc}. generation_id={generation_id}",
            tag="gamma.studio.export-unreadable",
        ) from exc
    if width <= 0 or height <= 0:
        raise GammaDispatchError(
            f"studio generation for slide {slide_id} produced a degenerate image "
            f"({width}x{height}); the export is corrupt, not a Classic fallback. "
            f"generation_id={generation_id}",
            tag="gamma.studio.export-unreadable",
        )
    aspect = width / height
    if aspect < _STUDIO_MIN_ASPECT_RATIO:
        raise GammaDispatchError(
            f"studio generation for slide {slide_id} returned a non-Studio "
            f"(Classic-looking) card: aspect_ratio={aspect:.3f} ({width}x{height}, "
            f"min {_STUDIO_MIN_ASPECT_RATIO}); a Studio image-card is 16:9, a Classic "
            f"fallback is near-square. Refusing silent fallback. "
            f"generation_id={generation_id}",
            tag="gamma.studio.classic-fallback",
        )


def _generate_studio_variant(
    client: GammaClient,
    slides: list[dict[str, Any]],
    variant_settings: dict[str, Any],
    export_dir: Path,
    variant: str,
    calls: list[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Per-slide Gamma create-from-template (Studio image-cards).

    One template call per slide -> one full-bleed Studio PNG whose slide_id is known
    by the caller (so no title-matching is needed). Returns ``{slide_id: file_path}``
    and ``{slide_id: generation_id}``. Each PNG is guarded against silent Classic
    fallback; the guard fails on the FIRST bad slide rather than after N paid cards.
    """
    template_id = str(variant_settings.get("studio_template_id") or "").strip()
    slide_paths: dict[str, str] = {}
    slide_gen_ids: dict[str, str] = {}
    for index, slide in enumerate(slides, start=1):
        slide_id = str(slide.get("slide_id") or f"slide-{index:02d}")
        if slide_id in slide_paths:
            # Two slides sharing a slide_id would overwrite each other's PNG on
            # disk (same filename) and mis-bind storyboard rows to the wrong
            # card while silently losing a paid generation. Fail loud instead.
            raise GammaDispatchError(
                f"duplicate slide_id {slide_id!r} in studio variant {variant}: "
                f"per-slide cards must have unique slide_ids.",
                tag="gamma.slides.invalid",
            )
        prompt = _STUDIO_LOCK_WRAPPER.format(slide_content=_studio_slide_content(slide, index))
        ack = client.generate_from_template(template_id, prompt, export_as="png")
        raw_id = ack.get("generationId") or ack.get("id") or ack.get("generation_id")
        if not raw_id:
            raise GammaDispatchError(
                f"studio from-template returned no id for slide {slide_id}; keys={sorted(ack)}",
                tag="gamma.generation.id-missing",
            )
        generation_id = str(raw_id)
        calls.append(generation_id)
        completed = client.wait_for_generation(generation_id)
        export_url = completed.get("exportUrl") or completed.get("export_url")
        if not (isinstance(export_url, str) and export_url.strip()):
            raise GammaDispatchError(
                f"studio generation for slide {slide_id} returned no exportUrl; "
                f"generation_id={generation_id}",
                tag="gamma.export.missing",
            )
        downloaded = download_export(
            export_url,
            output_dir=export_dir,
            filename=f"gary_{variant}_studio_{index:02d}_{_safe_slug(slide_id)}.png",
        )
        png_path = Path(str(downloaded))
        _assert_studio_image_card(png_path, slide_id=slide_id, generation_id=generation_id)
        slide_paths[slide_id] = str(png_path)
        slide_gen_ids[slide_id] = generation_id
    return slide_paths, slide_gen_ids


def generate_gamma_variants(
    payload: dict[str, Any], *, client: GammaClient | None = None
) -> dict[str, Any]:
    client = client or GammaClient()
    slides = _slides(payload)
    export_dir = Path(str(payload.get("export_dir") or REPO_ROOT / "runs" / "gary-gamma"))
    export_dir.mkdir(parents=True, exist_ok=True)
    theme_limit = int(payload.get("theme_limit", 20))
    themes = client.list_themes(limit=theme_limit)
    theme_id = _theme_id(client, payload, themes=themes)
    gamma_settings = _normalized_gamma_settings(payload)
    variants = tuple(item["variant_id"] for item in gamma_settings) or (
        ("A", "B") if bool(payload.get("double_dispatch")) else ("A",)
    )
    # double_dispatch vs explicit single-variant contradiction (Edge Case Hunter
    # SHOULD-FIX): when double_dispatch is requested BUT an EXPLICIT gamma_settings
    # names <2 variants, the explicit list correctly WINS (single-variant-binds-one
    # is the story intent) — but the contradiction must be surfaced, not silent.
    # WARN only; dispatch behavior (explicit list wins) is unchanged.
    if bool(payload.get("double_dispatch")) and gamma_settings and len(variants) < 2:
        _LOGGER.warning(
            "double_dispatch requested but explicit gamma_settings names %d variant(s) "
            "(%s); only the named variant(s) dispatch",
            len(variants),
            ", ".join(variants),
        )
    settings_by_variant = {item["variant_id"]: item for item in gamma_settings}
    output: list[dict[str, Any]] = []
    calls: list[str] = []
    dropped_pages: list[dict[str, Any]] = []
    for variant in variants:
        variant_settings = settings_by_variant.get(variant)
        # Studio fork (party-ratified 2026-06-25). When this variant is configured
        # production_mode="studio", produce per-slide Gamma create-from-template
        # image-cards instead of the Classic generate path, then build the SAME
        # row contract and continue. The Classic path below is byte-unchanged and
        # is the default whenever production_mode is absent/"api".
        if variant_settings is not None and variant_settings.get("production_mode") == "studio":
            studio_paths, studio_gen_ids = _generate_studio_variant(
                client, slides, variant_settings, export_dir, variant, calls
            )
            for index, slide in enumerate(slides, start=1):
                slide_id = str(slide.get("slide_id") or f"slide-{index:02d}")
                output.append(
                    {
                        "slide_id": slide_id,
                        "card_number": index,
                        "dispatch_variant": variant,
                        "variant_id": variant,
                        "gamma_settings": variant_settings,
                        # Index directly (not .get(..., "")) so a slide_id that
                        # diverges from the generator's keys fails loud rather
                        # than emitting a silent empty file_path downstream.
                        "file_path": studio_paths[slide_id],
                        "generation_id": studio_gen_ids[slide_id],
                        "display_title": str(slide.get("title") or "").strip() or slide_id,
                        "visual_description": str(
                            slide.get("visual_description") or slide.get("prompt") or ""
                        ),
                    }
                )
            continue
        generation_kwargs: dict[str, Any] = {
            "num_cards": len(slides),
            "theme_id": (
                _theme_id_for_variant(theme_id, variant_settings, themes)
                if variant_settings is not None
                else theme_id
            ),
            # cardSplit=inputTextBreaks pins one card per `\n---\n` chunk, so
            # Gamma can no longer merge/split briefed slides (the 6->5 collapse
            # that orphaned slide-05/06). With the title-led chunks above, each
            # card is titled with the briefed title and binds bijectively.
            "card_split": "inputTextBreaks",
            "additional_instructions": _instructions_for_variant(
                payload,
                variant=variant,
                settings=variant_settings,
            ),
            "export_as": "png",
        }
        if variant_settings is not None:
            text_options = _text_options_for_variant(variant_settings)
            image_options = _image_options_for_variant(variant_settings)
            text_mode = str(variant_settings.get("text_mode") or "").strip()
            if text_mode and text_mode not in {"default", "generate"}:
                generation_kwargs["text_mode"] = text_mode
            if text_options:
                generation_kwargs["text_options"] = text_options
            if image_options:
                generation_kwargs["image_options"] = image_options
        # Styleguide library is now the SOLE determinant of card dimensions (Leg-A,
        # 2026-07-01). The former unconditional `{"dimensions": "16x9", ...}` override
        # here is REMOVED: the resolved style's `dimensions` alone drives cardOptions
        # (fluid -> fluid, 16x9 -> 16:9, absent -> cardOptions omitted). The Descript
        # anti-crop OUTCOME is preserved as a publication-time policy follow-on
        # (`styleguide-16x9-publication-boundary-safety`), NOT a generation-time force;
        # Phase-2 runs stop at Storyboard B (pre-Descript) so no in-arc regression.
        card_options = (
            _card_options_for_variant(variant_settings) if variant_settings is not None else {}
        )
        if card_options:
            generation_kwargs["card_options"] = card_options
        generation = client.generate_deck(
            _input_text(slides, payload),
            **generation_kwargs,
        )
        raw_generation_id = (
            generation.get("generation_id")
            or generation.get("id")
            or generation.get("generationId")
        )
        if not raw_generation_id:
            # Trial-3 cycle-2 root-cause hardening (2026-06-12): the old
            # fabricated per-variant fixture-id sentinel here was the EIGHTH
            # silent seam — it masked generate_deck returning a bare POST ack
            # and let untracked spend + empty slide rows flow to G2C.
            # Recoverable family: error-pause + `trial recover` retries.
            raise GammaDispatchError(
                f"gamma generation returned no id for variant {variant}; "
                f"keys={sorted(generation)}",
                tag="gamma.generation.id-missing",
            )
        generation_id = str(raw_generation_id)
        calls.append(generation_id)
        # Storyboard-correctness fix (party-ratified 2026-06-18): match the
        # exported pages to briefed slide_ids by TITLE (deterministic bijective
        # containment), NOT by position. Gamma injects a cover + merges/drops +
        # rephrases titles, so the page order does not correspond to the brief
        # order. The matcher surfaces the cover (dropped), a merged-away brief
        # (brief-unmatched), a stray page (page-unmatched), and collisions
        # (title-ambiguous) instead of silently shifting every slide.
        expected_slots = [
            (
                str(slide.get("slide_id") or f"slide-{index:02d}"),
                _slide_title(slide, index),
            )
            for index, slide in enumerate(slides, start=1)
        ]
        export_url = generation.get("exportUrl") or generation.get("export_url")
        if isinstance(export_url, str) and export_url.strip():
            downloaded_export = download_export(
                export_url, output_dir=export_dir, filename=f"gary_{variant}.png"
            )
            match = materialize_exported_slide_paths_by_title(
                Path(str(downloaded_export)),
                requested_format="png",
                expected_slots=expected_slots,
                module_lesson_part=variant,
                export_dir=export_dir,
                label=variant,
            )
            if match.ambiguous:
                raise GammaDispatchError(
                    f"gamma export title-ambiguous for variant {variant}: "
                    f"{match.ambiguous}",
                    tag="gamma.export.title-ambiguous",
                )
            if match.unmatched_keys:
                raise GammaDispatchError(
                    f"gamma export left briefed slide(s) unmatched for variant "
                    f"{variant}: {match.unmatched_keys}; unmatched pages: "
                    f"{[p.get('title') for p in match.unmatched_pages]}",
                    tag="gamma.export.brief-unmatched",
                )
            if match.unmatched_pages:
                raise GammaDispatchError(
                    f"gamma export produced non-leading unmatched page(s) for "
                    f"variant {variant}: {[p.get('title') for p in match.unmatched_pages]}",
                    tag="gamma.export.page-unmatched",
                )
            slide_paths = dict(match.matched)
            dropped_pages.extend({"variant": variant, **d} for d in match.dropped_pages)
        else:
            # Legacy fallback: generation already carries materialized rows
            # keyed by slide_id (no export to title-match).
            slide_paths = {}
            rows = generation.get("gary_slide_output")
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and row.get("slide_id"):
                        slide_paths[str(row["slide_id"])] = str(row.get("file_path", ""))
        for index, slide in enumerate(slides, start=1):
            slide_id = str(slide.get("slide_id") or f"slide-{index:02d}")
            output.append(
                {
                    "slide_id": slide_id,
                    "card_number": index,
                    "dispatch_variant": variant,
                    "variant_id": variant,
                    "gamma_settings": variant_settings,
                    "file_path": slide_paths.get(slide_id, ""),
                    "generation_id": generation_id,
                    # Observation A (folded in): the real slide title (original
                    # casing, objective-free), so the storyboard surface can
                    # stop showing the bare slide_id.
                    "display_title": str(slide.get("title") or "").strip() or slide_id,
                    "visual_description": str(
                        slide.get("visual_description") or slide.get("prompt") or ""
                    ),
                }
            )
    if output and not any(row.get("file_path") for row in output):
        # Twice-bitten guard (deferred this morning, bitten this evening):
        # slide rows with no materialized artifacts are quality theater —
        # downstream gates would review metadata, not slides. Recoverable.
        raise GammaDispatchError(
            f"no slide artifacts materialized for generation(s) {calls}; "
            "every gary_slide_output row has an empty file_path",
            tag="gamma.export.unmaterialized",
        )
    return {
        "generation_id": calls[0],
        "status": "complete",
        "theme_resolution": {"theme_id": theme_id, "handshake": "list_themes"},
        "generation_mode": "double-dispatch" if len(variants) == 2 else "single-dispatch",
        "calls_made": len(calls),
        "variant_gamma_settings": gamma_settings,
        "gary_slide_output": output,
        # Decision #1 provenance: engine cover pages dropped during title
        # matching are recorded here, never silently vanished.
        "dropped_pages": dropped_pages,
        "vera_g3_invocation": build_vera_g3_invocation(output),
    }


def act(state: RunState, *, client: GammaClient | None = None) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("gary act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    tag = "gamma.dispatch.ok"
    try:
        if payload.get("slides") or payload.get("per_slide_directives") or payload.get("prompt"):
            receipt = generate_gamma_variants(payload, client=client)
        else:
            receipt = dispatch_to_gamma(
                directive_path=payload.get("directive_path"),
                export_dir=payload.get("export_dir"),
            )
            tag = "receipt.parsed.ok"
    except GammaDispatchError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    except GaryActError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    if not isinstance(receipt.get("gary_slide_output"), list) or not receipt["gary_slide_output"]:
        raise GaryActError("gamma receipt missing slide output", tag="gamma.output.missing")
    output = {"specialist_id": "gary", **receipt, "model_id": last_entry.resolved}
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag=tag),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(output),
            entries_count=entries_count + 1,
        ).model_dump(mode="json"),
    }


# Amelia a.1 (party review 2026-06-12): the payload contract participates in
# the act's import graph so it cannot rot as an orphan module.
from app.specialists.gary.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "CONSUMED_PAYLOAD_KEYS",
    "DEFAULT_VARIANT_PAIR",
    "GARY_REFERENCES",
    "GaryActError",
    "SANCTUM_DIR",
    "act",
    "build_vera_g3_invocation",
    "decode_envelope_payload",
    "generate_gamma_variants",
    "read_references",
    "read_sanctum_digest",
]

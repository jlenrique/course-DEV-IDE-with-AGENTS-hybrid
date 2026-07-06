"""Thin byte-compatible re-export of the shared Gamma styleguide resolver.

Canonical-arc S1 (D1, 2026-07-06): the deterministic resolution core moved
VERBATIM to the neutral :mod:`app.styleguide.resolver` so
``app.specialists.cd``, ``app.specialists.gary``, and
``app.marcus.orchestrator`` can all resolve styleguides without importing
``app.specialists.gary`` (strangler-fig per the amended W2 contract,
`styleguide-binding-cd-contract-2026-07-06.md`). This module preserves the
FULL prior public API byte-compatibly — every existing import site
(`gary/_act.py`, `gary/learned_dependencies.py`, `irene_pass1/_act.py`,
`scripts/utilities/validate_gamma_style_guides.py`, tests) keeps working
unchanged, including the private helpers tests exercise directly.
"""

from __future__ import annotations

from app.styleguide.resolver import (
    ADDITIONAL_INSTRUCTIONS_TAG,
    GAMMA_STYLE_GUIDES_PATH,
    INCOMPLETE_TAG,
    LOAD_ERROR_TAG,
    PROJECT_ROOT,
    RESOLVED_API_KEYS,
    SCRIPTED_BAD_VALUE_TAG,
    SCRIPTED_ENUM_CLASSES,
    SCRIPTED_UNKNOWN_CLASS_TAG,
    STUDIO_OVERRIDE_INVALID_TAG,
    STYLEGUIDE_CLASSIC_ONLY_KEYS,
    SURFACE_VIOLATION_TAG,
    UNKNOWN_TAG,
    StyleguideError,
    _expand_api,
    _expand_studio,
    _is_present,
    classic_surface_keys,
    expand_record,
    load_style_guides,
    resolve_scripted,
    resolve_styleguide,
    scripted_entries,
    yaml,
)

__all__ = [
    "ADDITIONAL_INSTRUCTIONS_TAG",
    "GAMMA_STYLE_GUIDES_PATH",
    "INCOMPLETE_TAG",
    "LOAD_ERROR_TAG",
    "PROJECT_ROOT",
    "RESOLVED_API_KEYS",
    "SCRIPTED_BAD_VALUE_TAG",
    "SCRIPTED_ENUM_CLASSES",
    "SCRIPTED_UNKNOWN_CLASS_TAG",
    "STUDIO_OVERRIDE_INVALID_TAG",
    "STYLEGUIDE_CLASSIC_ONLY_KEYS",
    "SURFACE_VIOLATION_TAG",
    "UNKNOWN_TAG",
    "StyleguideError",
    "_expand_api",
    "_expand_studio",
    "_is_present",
    "classic_surface_keys",
    "expand_record",
    "load_style_guides",
    "resolve_scripted",
    "resolve_styleguide",
    "scripted_entries",
    "yaml",
]

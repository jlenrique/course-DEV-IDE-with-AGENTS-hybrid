"""Neutral shared home of the deterministic Gamma styleguide resolver.

Canonical-arc S1 (D1, 2026-07-06): the resolution core was extracted from
``app.specialists.gary.styleguide_library`` (which remains a thin
byte-compatible re-export) so ``app.specialists.cd``,
``app.specialists.gary``, and ``app.marcus.orchestrator`` can all resolve
styleguides without importing ``app.specialists.gary``.
"""

from __future__ import annotations

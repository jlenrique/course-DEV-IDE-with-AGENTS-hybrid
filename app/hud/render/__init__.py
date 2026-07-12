"""Flight-deck render package (Story 35.5; AD-12 + UX spines binding).

Pure projection→HTML render for the Operator HUD. ``app.hud`` renders only —
it never imports the orchestrator, the gate machinery, or the legacy
``scripts`` readers (import-linter HUD1). See :mod:`app.hud.render.page`.
"""

from __future__ import annotations

from app.hud.render.page import ZONE_IDS, render_page, render_zones

__all__ = ["ZONE_IDS", "render_page", "render_zones"]

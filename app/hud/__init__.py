"""Operator HUD view package (Epic 35 / Story 35.4).

The read-only ("dumb-terminal") view side of the single-writer projected
read model (ARCHITECTURE-SPINE.md). Everything here consumes the
runtime-owned operator-surface projection through the contract's lenient
reader ONLY — this package imports nothing from
``app.marcus.orchestrator``, ``scripts.utilities.hud_data_sources``, or
``app.gates`` (import-linter enforced, pyproject.toml). It never parses the
projection with the strict producer model (AD-4): a strict parse in the
HUD white-screens on the very additive evolution the contract permits.
"""

from __future__ import annotations

__all__: list[str] = []

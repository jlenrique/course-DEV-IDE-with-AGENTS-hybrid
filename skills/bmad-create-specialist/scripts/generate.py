"""Wrapper that dispatches to the importable generator module."""

from __future__ import annotations

from skills.bmad_create_specialist.scripts.generate import main

if __name__ == "__main__":
    raise SystemExit(main())

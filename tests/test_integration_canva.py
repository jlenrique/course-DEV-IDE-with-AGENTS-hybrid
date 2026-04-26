"""Canva MCP integration validation tests (Story 1.10).

Canva uses OAuth via remote MCP — no API key to test directly.
These tests validate the MCP configuration is documented and
the known blocker status is accurately captured.
"""

from __future__ import annotations

from scripts.utilities.file_helpers import project_root

ROOT = project_root()


class TestCanvaIntegration:
    def test_mcp_blocker_documented(self):
        """Verify Canva's OAuth blocker is documented in tool-access-matrix."""
        content = (
            ROOT / "resources/tool-inventory/tool-access-matrix.md"
        ).read_text(encoding="utf-8")
        assert "Canva" in content
        assert "OAuth" in content or "redirect" in content

    def test_preflight_classifies_canva_as_blocked(self):
        """Verify pre-flight runner knows Canva is blocked."""
        from skills.pre_flight_check.scripts.preflight_runner import (
            BLOCKED_TOOLS,
        )

        assert "Canva" in BLOCKED_TOOLS

    def test_local_env_template_is_present(self):
        """Migration policy (post-Slab-3 close): .env.example IS the canonical
        operator-onboarding template; reverses primary-repo policy that forbid
        env templates in-tree."""
        assert (ROOT / ".env.example").exists()

    def test_admin_guide_documents_canva(self):
        """Verify admin guide documents Canva (OAuth / MCP context)."""
        content = (ROOT / "docs" / "admin-guide.md").read_text(encoding="utf-8")
        assert "Canva" in content or "canva" in content.lower()

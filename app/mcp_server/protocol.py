"""MCP protocol-version pin for the migration runtime (FR2 substrate, Story 1.1c).

The pinned value is sourced from the shipped ``mcp`` SDK
(``mcp.types.DEFAULT_NEGOTIATED_VERSION``) so an SDK upgrade can never silently
shift our protocol surface without a code change here. Re-exporting the SDK
constant rather than hard-coding a date string also means the validator-test
in 1.1d's parity assertion can compare both sides against the same upstream
source-of-truth.

Story 1.1c lands the pin only — Story 1.1d wires the per-PR-or-nightly
subprocess smoke that verifies a stdio round-trip negotiates this version.
"""

from __future__ import annotations

from mcp.types import DEFAULT_NEGOTIATED_VERSION as _SDK_DEFAULT_NEGOTIATED_VERSION
from mcp.types import LATEST_PROTOCOL_VERSION as _SDK_LATEST_PROTOCOL_VERSION

MCP_PROTOCOL_VERSION: str = _SDK_DEFAULT_NEGOTIATED_VERSION
"""Negotiated protocol version this server speaks. Sourced from the shipped SDK."""

MCP_LATEST_PROTOCOL_VERSION: str = _SDK_LATEST_PROTOCOL_VERSION
"""Latest protocol version the SDK can claim; recorded for forensic value."""

__all__ = ["MCP_LATEST_PROTOCOL_VERSION", "MCP_PROTOCOL_VERSION"]

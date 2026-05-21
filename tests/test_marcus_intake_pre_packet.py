"""Tests for lifted ``prepare_irene_packet`` function (Story 30-2a).

Covers:
* AC-T.2 — happy path + returned dict keys + written packet content.
* AC-T.3 — parametrized missing-input error paths.
* AC-T.4 — optional ingestion-receipt absence (no-op fallback).
* AC-T.6 — 30-2b unblock handshake import + signature smoke.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from app.marcus.intake.pre_packet import prepare_irene_packet


def _write_bundle(
    bundle_dir: Path,
    *,
    include_ingestion_receipt: bool = True,
    metadata_overrides: dict | None = None,
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "extracted.md").write_text(
        "# Extracted Content\n\nSection 1 body.\n",
        encoding="utf-8",
    )
    metadata: dict = {
        "primary_source": "example.pdf",
        "total_sections": 3,
        "overall_confidence": 0.92,
    }
    if metadata_overrides:
        metadata.update(metadata_overrides)
    (bundle_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    (bundle_dir / "operator-directives.md").write_text(
        "# Operator Directives\n\n- Focus on Part 1.\n",
        encoding="utf-8",
    )
    if include_ingestion_receipt:
        (bundle_dir / "ingestion-quality-gate-receipt.md").write_text(
            "# Ingestion Quality Gate Receipt\n\nStatus: pass.\n",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# AC-T.2 — happy path
# ---------------------------------------------------------------------------


def test_prepare_irene_packet_happy_path(tmp_path: Path) -> None:
    """AC-T.2 — well-formed bundle produces packet + returned dict."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = prepare_irene_packet(
        bundle_dir=bundle_dir,
        run_id="TEST-RUN-001",
        output_path=output_path,
    )

    # Return-shape pin.
    assert set(result.keys()) == {
        "packet_path",
        "sections",
        "has_directives",
        "has_ingestion_receipt",
    }
    assert result["packet_path"] == str(output_path)
    assert result["sections"] == 15  # fixed by the function body's section list
    assert result["has_directives"] is True
    assert result["has_ingestion_receipt"] is True

    # Written-file content pin.
    assert output_path.is_file()
    written = output_path.read_text(encoding="utf-8")
    for expected_header in (
        "# Irene Packet for TEST-RUN-001",
        "## Source Bundle Summary",
        "## Operator Directives",
        "## Ingestion Quality Receipt",
        "## Extracted Content",
    ):
        assert expected_header in written, f"Missing header: {expected_header!r}"

    # Metadata projection pin.
    assert "- Primary source: example.pdf" in written
    assert "- Total sections: 3" in written
    assert "- Extraction confidence: 0.92" in written


# ---------------------------------------------------------------------------
# AC-T.3 — parametrized missing-input error paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_file",
    ["extracted.md", "metadata.json", "operator-directives.md"],
)
def test_prepare_irene_packet_missing_required_input(
    missing_file: str, tmp_path: Path
) -> None:
    """AC-T.3 — missing any required file → FileNotFoundError naming it."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    (bundle_dir / missing_file).unlink()

    with pytest.raises(FileNotFoundError) as exc_info:
        prepare_irene_packet(
            bundle_dir=bundle_dir,
            run_id="TEST-RUN-002",
            output_path=tmp_path / "out" / "irene-packet.md",
        )
    assert missing_file in str(exc_info.value)


# ---------------------------------------------------------------------------
# AC-T.4 — optional ingestion-receipt absence
# ---------------------------------------------------------------------------


def test_prepare_irene_packet_without_ingestion_receipt(tmp_path: Path) -> None:
    """AC-T.4 — missing ingestion-quality-gate-receipt.md is a no-op fallback."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir, include_ingestion_receipt=False)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = prepare_irene_packet(
        bundle_dir=bundle_dir,
        run_id="TEST-RUN-003",
        output_path=output_path,
    )

    assert result["has_ingestion_receipt"] is False
    written = output_path.read_text(encoding="utf-8")
    # Section header still present; body after it is empty.
    assert "## Ingestion Quality Receipt" in written


# ---------------------------------------------------------------------------
# AC-T.6 — 30-2b unblock handshake
# ---------------------------------------------------------------------------


def test_30_2b_unblock_handshake_import_surface() -> None:
    """AC-T.6 — ``from marcus.intake.pre_packet import prepare_irene_packet`` works.

    The imported function exposes the three-arg signature 30-2b will wrap.
    """
    sig = inspect.signature(prepare_irene_packet)
    assert list(sig.parameters.keys()) == ["bundle_dir", "run_id", "output_path"]
    assert callable(prepare_irene_packet)

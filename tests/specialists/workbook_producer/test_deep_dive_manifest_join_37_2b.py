"""R19 (Story 37.2b remediation): deep-dive manifest hash disagreement is VISIBLE.

The G2 structured-side join (`_merge_deep_dive_source_refs`) retains the
earlier research-leg manifest entry deterministically, but a source_hash
disagreement for the same source_ref is surfaced via ``logger.warning`` —
never a silent ``setdefault``.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from app.specialists.workbook_producer._act import _merge_deep_dive_source_refs


def _row(source_ref: str, source_hash: str) -> SimpleNamespace:
    return SimpleNamespace(source_ref=source_ref, source_hash=source_hash)


def test_hash_disagreement_warns_and_retains_manifest_entry(
    caplog: pytest.LogCaptureFixture,
) -> None:
    manifest = {"retrieval:scite:10.5772/intechopen.94054": "sha256:" + "a" * 64}
    with caplog.at_level(logging.WARNING, logger="app.specialists.workbook_producer._act"):
        _merge_deep_dive_source_refs(
            manifest,
            [_row("retrieval:scite:10.5772/intechopen.94054", "sha256:" + "b" * 64)],
        )
    assert any(
        "deep-dive manifest hash disagreement" in record.message
        for record in caplog.records
    )
    # Deterministic retention: the earlier entry wins either way.
    assert manifest["retrieval:scite:10.5772/intechopen.94054"] == "sha256:" + "a" * 64


def test_agreeing_or_new_rows_join_silently(
    caplog: pytest.LogCaptureFixture,
) -> None:
    manifest = {"ref-a": "sha256:" + "a" * 64}
    with caplog.at_level(logging.WARNING, logger="app.specialists.workbook_producer._act"):
        _merge_deep_dive_source_refs(
            manifest,
            [_row("ref-a", "sha256:" + "a" * 64), _row("ref-b", "sha256:" + "b" * 64)],
        )
    assert not caplog.records
    assert manifest == {
        "ref-a": "sha256:" + "a" * 64,
        "ref-b": "sha256:" + "b" * 64,
    }

"""UDAC v1 RED-first floor — the neutral Run Asset Index model + resolver.

Covers §F amendments at the model level (no runner needed):
  - MT-3 fail-loud matrix: (before/after ratification boundary) × (present/missing/
    stale-digest) → the exact AssetResolutionError TAG for each raise case, resolve
    for present, the typed legacy-mode marker in the provisional window + RAISE
    post-boundary for a required asset. No silent path.
  - MT-5 / TX-5: the RAI digest is RECOMPUTED FROM DISK (corrupt-on-disk → stale).
  - TX-2: cross-schema/algo comparison REFUSES (raises), never "stale".
  - TX-3: additive enrichment re-pin bumps revision, does NOT false-stale.
  - Monotonic + idempotent mark_ratified (M-5 both-walks parity precondition).
  - absent → null digest, never compared (TX-5).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.run_asset_index import (
    DIGEST_SCHEMA_VERSION,
    TAG_ABSENT,
    TAG_CORRUPT,
    TAG_INDEX_CORRUPT,
    TAG_MISSING,
    TAG_MONOTONIC,
    TAG_NOT_RATIFIED,
    TAG_SCHEMA_REFUSE,
    TAG_STALE,
    TAG_UNINDEXED,
    AssetResolutionError,
    AuthorityStatus,
    DigestAlgo,
    LegacyMode,
    RunAssetEntry,
    RunAssetIndex,
    compare_digests,
    digest_structured_payload,
    load_rai,
    recompute_digest_from_disk,
    resolve_asset,
    write_rai,
)

_NOW = datetime(2026, 6, 28, 12, 0, tzinfo=UTC)
_PAYLOAD = {"corpus_fingerprint": "fp-abc", "typed_components": [{"id": "c1"}]}


def _write_asset(run_dir: Path, payload: dict | None = None) -> str:
    run_dir.mkdir(parents=True, exist_ok=True)
    body = payload if payload is not None else _PAYLOAD
    (run_dir / "g0-enrichment.json").write_text(json.dumps(body), encoding="utf-8")
    return digest_structured_payload(body)


def _ratified_index(run_dir: Path, *, digest: str) -> RunAssetIndex:
    index = RunAssetIndex()
    index.mark_ratified(
        asset_id="g0-enrichment",
        path="g0-enrichment.json",
        digest=digest,
        digest_algo=DigestAlgo.CANONICAL_SHA256,
        ratified_at=_NOW,
        produced_by_node="G0E",
        revision=0,
    )
    return index


# ---------------------------------------------------------------------------
# MT-5 / TX-5 — digest recomputed from disk
# ---------------------------------------------------------------------------


def test_rai_digest_recomputes_from_disk(tmp_path: Path) -> None:
    """A correct-on-disk asset resolves; CORRUPT-on-disk → stale-raise (MT-5)."""
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)

    resolved = resolve_asset(index, "g0-enrichment", run_dir=tmp_path)
    assert resolved.authority_status is AuthorityStatus.RATIFIED
    assert resolved.legacy_mode is LegacyMode.NONE
    assert resolved.digest == digest

    # Corrupt the on-disk asset AFTER the producer wrote its claimed digest.
    (tmp_path / "g0-enrichment.json").write_text(
        json.dumps({"corpus_fingerprint": "fp-abc", "typed_components": []}),
        encoding="utf-8",
    )
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path)
    assert exc.value.tag == TAG_STALE


def test_recompute_from_disk_binary(tmp_path: Path) -> None:
    blob = tmp_path / "audio.bin"
    blob.write_bytes(b"\x00\x01\x02proof")
    import hashlib

    assert recompute_digest_from_disk(blob, DigestAlgo.FILE_CONTENT_SHA256) == (
        hashlib.sha256(b"\x00\x01\x02proof").hexdigest()
    )


# ---------------------------------------------------------------------------
# MT-3 — fail-loud matrix: (before/after boundary) × (present/missing/stale)
# ---------------------------------------------------------------------------


def test_mt3_present_after_boundary_resolves(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)
    resolved = resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=True)
    assert resolved.legacy_mode is LegacyMode.NONE


def test_mt3_missing_after_boundary_raises(tmp_path: Path) -> None:
    digest = digest_structured_payload(_PAYLOAD)  # claimed, but never written
    index = _ratified_index(tmp_path, digest=digest)
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=True)
    assert exc.value.tag == TAG_MISSING


def test_mt3_stale_after_boundary_raises(tmp_path: Path) -> None:
    _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest="deadbeef-wrong-digest")
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=True)
    assert exc.value.tag == TAG_STALE


def test_mt3_unindexed_raises(tmp_path: Path) -> None:
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(RunAssetIndex(), "g0-enrichment", run_dir=tmp_path)
    assert exc.value.tag == TAG_UNINDEXED


def test_mt3_provisional_required_raises_but_marks_legacy_when_optional(tmp_path: Path) -> None:
    """Before the boundary: a REQUIRED provisional asset RAISES; an OPTIONAL one
    returns the TYPED legacy-mode marker (no silent fallback) — LEGACY-MODE-IS-TYPED."""
    index = RunAssetIndex(
        entries={
            "g0-enrichment": RunAssetEntry(
                asset_id="g0-enrichment",
                path="g0-enrichment.json",
                digest=None,
                digest_algo=DigestAlgo.CANONICAL_SHA256,
                authority_status=AuthorityStatus.PROVISIONAL,
            )
        }
    )
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=True)
    assert exc.value.tag == TAG_NOT_RATIFIED

    optional = resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=False)
    assert optional.legacy_mode is LegacyMode.PROVISIONAL_FALLBACK


def test_mt3_absent_null_digest_never_compared(tmp_path: Path) -> None:
    """TX-5: absent carries null digest; required-absent raises, never digest-compares."""
    index = RunAssetIndex(
        entries={
            "ratified-los": RunAssetEntry(
                asset_id="ratified-los",
                path="ratified-los.json",
                digest=None,
                digest_algo=None,
                authority_status=AuthorityStatus.ABSENT,
            )
        }
    )
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "ratified-los", run_dir=tmp_path, require_ratified=True)
    assert exc.value.tag == TAG_ABSENT
    optional = resolve_asset(index, "ratified-los", run_dir=tmp_path, require_ratified=False)
    assert optional.digest is None
    assert optional.legacy_mode is LegacyMode.PROVISIONAL_FALLBACK


# ---------------------------------------------------------------------------
# TX-2 — cross-schema/algo comparison REFUSES (raise, not "stale")
# ---------------------------------------------------------------------------


def test_tx2_cross_schema_refuses() -> None:
    with pytest.raises(AssetResolutionError) as exc:
        compare_digests(
            left_digest="a",
            left_algo=DigestAlgo.CANONICAL_SHA256,
            left_schema="1.0",
            right_digest="a",
            right_algo=DigestAlgo.CANONICAL_SHA256,
            right_schema="2.0",
        )
    assert exc.value.tag == TAG_SCHEMA_REFUSE


def test_tx2_cross_algo_refuses() -> None:
    with pytest.raises(AssetResolutionError) as exc:
        compare_digests(
            left_digest="a",
            left_algo=DigestAlgo.CANONICAL_SHA256,
            left_schema="1.0",
            right_digest="a",
            right_algo=DigestAlgo.FILE_CONTENT_SHA256,
            right_schema="1.0",
        )
    assert exc.value.tag == TAG_SCHEMA_REFUSE


def test_tx2_same_schema_algo_compares() -> None:
    assert compare_digests(
        left_digest="a",
        left_algo=DigestAlgo.CANONICAL_SHA256,
        left_schema=DIGEST_SCHEMA_VERSION,
        right_digest="a",
        right_algo=DigestAlgo.CANONICAL_SHA256,
        right_schema=DIGEST_SCHEMA_VERSION,
    )


# ---------------------------------------------------------------------------
# TX-3 — additive enrichment re-pin (revision bump, NO false-stale)
# ---------------------------------------------------------------------------


def test_tx3_additive_repin_bumps_revision_no_false_stale(tmp_path: Path) -> None:
    """Append P2/P3 to g0-enrichment.json → revision bumps + re-pins, no stale error."""
    digest_v0 = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest_v0)
    assert index.get("g0-enrichment").revision == 0

    # Legitimately GROW the artifact (P2 citations + P3 pedagogy layered on).
    grown = dict(_PAYLOAD)
    grown["citation_resolutions"] = [{"component_id": "c1", "resolution_status": "resolved"}]
    grown["pedagogy_annotations"] = [{"component_id": "c1", "bloom": "analyze"}]
    (tmp_path / "g0-enrichment.json").write_text(json.dumps(grown), encoding="utf-8")

    later = datetime(2026, 6, 28, 13, 0, tzinfo=UTC)
    entry = index.repin_additive("g0-enrichment", run_dir=tmp_path, ratified_at=later)
    assert entry.revision == 1
    assert entry.ratified_at == later
    assert entry.digest == digest_structured_payload(grown)

    # The grown artifact resolves cleanly at the new revision — NOT stale.
    resolved = resolve_asset(index, "g0-enrichment", run_dir=tmp_path, require_ratified=True)
    assert resolved.revision == 1
    assert resolved.legacy_mode is LegacyMode.NONE


def test_tx3_repin_noop_when_unchanged(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)
    entry = index.repin_additive("g0-enrichment", run_dir=tmp_path, ratified_at=_NOW)
    assert entry.revision == 0  # unchanged bytes → no bump


# ---------------------------------------------------------------------------
# Monotonic + idempotent mark_ratified (M-5 precondition)
# ---------------------------------------------------------------------------


def test_idempotent_recross_preserves_ratified_at(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)
    first_at = index.get("g0-enrichment").ratified_at

    # Re-cross the SAME gate on a recover walk (same revision, same on-disk digest).
    later = datetime(2026, 6, 28, 14, 0, tzinfo=UTC)
    index.mark_ratified(
        asset_id="g0-enrichment",
        path="g0-enrichment.json",
        digest=digest,
        digest_algo=DigestAlgo.CANONICAL_SHA256,
        ratified_at=later,
        produced_by_node="G0E",
        revision=0,
    )
    assert index.get("g0-enrichment").ratified_at == first_at  # NOT regressed/duplicated


def test_same_revision_digest_divergence_raises(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)
    with pytest.raises(AssetResolutionError) as exc:
        index.mark_ratified(
            asset_id="g0-enrichment",
            path="g0-enrichment.json",
            digest="different-digest-same-revision",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
            ratified_at=_NOW,
            produced_by_node="G0E",
            revision=0,
        )
    assert exc.value.tag == TAG_STALE


# ---------------------------------------------------------------------------
# F2 — corrupt file → TAGGED error, never a raw exception that escapes the channel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("body", [b"", b"{not json", b"\xff\xfe\x00bad-utf8"])
def test_f2_recompute_corrupt_asset_raises_tagged(tmp_path: Path, body: bytes) -> None:
    asset = tmp_path / "g0-enrichment.json"
    asset.write_bytes(body)
    with pytest.raises(AssetResolutionError) as exc:
        recompute_digest_from_disk(asset, DigestAlgo.CANONICAL_SHA256)
    assert exc.value.tag == TAG_CORRUPT


def test_f2_resolve_corrupt_asset_raises_tagged_not_stale(tmp_path: Path) -> None:
    """A corrupt ratified asset raises `udac.asset-corrupt` (distinct from stale)."""
    digest = _write_asset(tmp_path)
    index = _ratified_index(tmp_path, digest=digest)
    (tmp_path / "g0-enrichment.json").write_bytes(b"")  # zero-byte corruption
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path)
    assert exc.value.tag == TAG_CORRUPT


def test_f2_load_rai_corrupt_raises_tagged_not_validationerror(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    write_rai(tmp_path, _ratified_index(tmp_path, digest=digest))
    (tmp_path / "run-asset-index.json").write_text("{ truncated", encoding="utf-8")
    with pytest.raises(AssetResolutionError) as exc:
        load_rai(tmp_path)
    assert exc.value.tag == TAG_INDEX_CORRUPT


def test_write_rai_is_atomic_roundtrip(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    idx = _ratified_index(tmp_path, digest=digest)
    write_rai(tmp_path, idx)
    # No leftover temp file; the index round-trips.
    assert not list(tmp_path.glob("run-asset-index.json.*.tmp"))
    reloaded = load_rai(tmp_path)
    assert reloaded.get("g0-enrichment").digest == digest


# ---------------------------------------------------------------------------
# Blind-F5 — resolve REFUSES across a digest_schema_version bump
# ---------------------------------------------------------------------------


def test_blind_f5_resolve_refuses_on_schema_version_mismatch(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = RunAssetIndex(
        entries={
            "g0-enrichment": RunAssetEntry(
                asset_id="g0-enrichment",
                path="g0-enrichment.json",
                digest=digest,
                digest_algo=DigestAlgo.CANONICAL_SHA256,
                digest_schema_version="999.0",  # a future schema
                ratified_at=_NOW,
                produced_by_node="G0E",
                authority_status=AuthorityStatus.RATIFIED,
            )
        }
    )
    with pytest.raises(AssetResolutionError) as exc:
        resolve_asset(index, "g0-enrichment", run_dir=tmp_path)
    assert exc.value.tag == TAG_SCHEMA_REFUSE


def test_revision_regression_raises(tmp_path: Path) -> None:
    digest = _write_asset(tmp_path)
    index = RunAssetIndex()
    index.mark_ratified(
        asset_id="g0-enrichment",
        path="g0-enrichment.json",
        digest=digest,
        digest_algo=DigestAlgo.CANONICAL_SHA256,
        ratified_at=_NOW,
        produced_by_node="G0E",
        revision=3,
    )
    with pytest.raises(AssetResolutionError) as exc:
        index.mark_ratified(
            asset_id="g0-enrichment",
            path="g0-enrichment.json",
            digest=digest,
            digest_algo=DigestAlgo.CANONICAL_SHA256,
            ratified_at=_NOW,
            produced_by_node="G0E",
            revision=2,
        )
    assert exc.value.tag == TAG_MONOTONIC

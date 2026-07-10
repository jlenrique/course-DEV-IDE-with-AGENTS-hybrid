"""UDAC v1 — Run Asset Index (RAI): the neutral ACCESS + USE contract.

Operator-mandated Universal Downstream Asset Contract (Step 8.5). Ratified design:
``_bmad-output/planning-artifacts/udac-universal-downstream-asset-contract-strawman-2026-06-28.md``
§F (binding amendments M-1..5 / TX-1..5 / MT-1..7 + Winston's RAI-WRITER-SEPARATION /
TWO-LOADERS / RESOLVE-ASSET-LIVES-NEUTRAL / LEGACY-MODE-IS-TYPED).

RESOLVE-ASSET-LIVES-NEUTRAL (Winston). This module is models-side
(``app.marcus.lesson_plan``) so BOTH the orchestrator — which BUILDS the index at
the ratification gates — AND the specialists — which CONSUME the passed-in resolved
view — import it without violating Contract M3. It imports **no**
``app.marcus.orchestrator`` module (the workbook local-read precedent).

TWO-LOADERS-NOT-ONE (Winston). The existing FAIL-SOFT loaders
(``g0_enrichment_wiring.load_enrichment_result`` / ``workbook_enrichment.load_enrichment_card``)
stay untouched for the pre-ratification / backward-compat path. ``resolve_asset``
here is the NEW FAIL-LOUD resolver: once an asset is RATIFIED in the RAI, a
consumer that cannot resolve / digest-match it RAISES :class:`AssetResolutionError`
(a ``SpecialistDispatchError`` subclass) → the runner's existing recoverable pause.

Digest discipline (Texas TX-1/2/5). The RAI digest is RECOMPUTED FROM DISK bytes
(never a producer self-report): ``canonical_sha256`` of the PUBLIC serialized
projection for structured assets, ``file_content_hash`` for opaque binaries. Each
entry pins ``digest_algo`` + ``digest_schema_version``; the comparison helper
REFUSES (raises) to compare across schema/algo rather than reporting a false
"stale". ``absent`` carries a null digest that is never compared.

Additive enrichment (Texas TX-3). ``g0-enrichment.json`` legitimately GROWS after
its gate (P2 citations + P3 pedagogy layer onto the same artifact). Growth is an
explicit ``revision`` bump + re-pin (``repin_additive``), NOT a stale error; the
stale-check is mismatch vs the digest at the asset's CURRENT revision.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from app.specialists.dispatch_errors import AssetResolutionError

RAI_SCHEMA_VERSION: Final[str] = "1.0"
DIGEST_SCHEMA_VERSION: Final[str] = "1.0"
RAI_BASENAME: Final[str] = "run-asset-index.json"

# Fail-loud tags (carried on AssetResolutionError.tag).
TAG_UNINDEXED: Final[str] = "udac.asset-unindexed"
TAG_MISSING: Final[str] = "udac.asset-missing"
TAG_STALE: Final[str] = "udac.asset-stale"
TAG_NOT_RATIFIED: Final[str] = "udac.asset-not-ratified"
TAG_ABSENT: Final[str] = "udac.asset-absent"
TAG_SCHEMA_REFUSE: Final[str] = "udac.digest-schema-refuse"
TAG_MONOTONIC: Final[str] = "udac.revision-monotonic-violation"
TAG_CORRUPT: Final[str] = "udac.asset-corrupt"
TAG_INDEX_CORRUPT: Final[str] = "udac.index-corrupt"


class AuthorityStatus(StrEnum):
    """Authority of an asset in the run — orthogonal to its content-address (TX-5)."""

    RATIFIED = "ratified"
    PROVISIONAL = "provisional"
    ABSENT = "absent"


class DigestAlgo(StrEnum):
    """Pinned per asset (TX-1): structured vs opaque-binary content addressing."""

    CANONICAL_SHA256 = "canonical_sha256"  # canonical-JSON of the public projection
    FILE_CONTENT_SHA256 = "file_content_sha256"  # raw bytes (opaque binary)


class LegacyMode(StrEnum):
    """Typed receipt marker (Winston LEGACY-MODE-IS-TYPED).

    Provisional-window ONLY: records that a consumer fell back to constants
    because the asset was not yet ratified. It is NOT a badge for silent
    post-boundary fallback — a REQUIRED asset that is not ratified RAISES.
    """

    NONE = "none"  # asset ratified + resolved; no fallback
    PROVISIONAL_FALLBACK = "provisional_fallback"  # pre-ratification constants used


class AssetUsage(StrEnum):
    """Per-consumer declaration verb (USE/audit spine)."""

    USED = "used"  # the consumer actually read it and it shaped output
    AVAILABLE_ONLY = "available_only"  # present but not consumed this run


# ---------------------------------------------------------------------------
# Digest helpers (TX-1/5) — recomputed FROM DISK, never producer self-report
# ---------------------------------------------------------------------------


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize_json_value(inner) for key, inner in value.items()}
    if isinstance(value, list | tuple):
        return [_normalize_json_value(inner) for inner in value]
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    return value


def _canonical_sha256(payload: Any) -> str:
    """SHA-256 of canonical-JSON (sorted keys, stable separators, hashseed-independent).

    Faithful reimplementation of ``app.runtime.compiled_graph_digest.canonical_sha256``
    (no new digest scheme, §C) kept local so the M3-sacred neutral module stays
    dependency-light + import-cycle-free.
    """
    canonical = json.dumps(
        _normalize_json_value(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def digest_structured_payload(payload: dict[str, Any]) -> str:
    """Content-address a structured PUBLIC projection (``canonical_sha256``; TX-1)."""
    return _canonical_sha256(payload)


def digest_binary_path(path: Path) -> str:
    """Content-address opaque bytes (``file_content_hash`` equivalent; TX-1)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recompute_digest_from_disk(asset_path: Path, digest_algo: DigestAlgo) -> str:
    """Recompute an asset's digest from its ON-DISK bytes (TX-5 / MT-5).

    The orchestrator NEVER trusts a producer's self-reported digest — a corrupt
    or post-ratification-mutated file diverges here → stale-raise at resolve.

    A truncated / zero-byte / non-utf8 / non-JSON ratified asset raises a TAGGED
    :class:`AssetResolutionError` (``udac.asset-corrupt``) rather than a raw
    ``OSError`` / ``JSONDecodeError`` / ``UnicodeDecodeError`` — so a partially
    written asset routes through the runner's recoverable pause, never an uncaught
    crash (review F2).
    """
    if digest_algo is DigestAlgo.CANONICAL_SHA256:
        try:
            loaded = json.loads(asset_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AssetResolutionError(
                f"asset at {asset_path.name!r} is corrupt / unreadable as JSON: {exc}",
                tag=TAG_CORRUPT,
            ) from exc
        return _canonical_sha256(loaded)
    if digest_algo is DigestAlgo.FILE_CONTENT_SHA256:
        try:
            return digest_binary_path(asset_path)
        except OSError as exc:
            raise AssetResolutionError(
                f"asset at {asset_path.name!r} is unreadable: {exc}", tag=TAG_CORRUPT
            ) from exc
    raise AssetResolutionError(  # pragma: no cover - exhaustive enum guard
        f"unknown digest_algo {digest_algo!r}", tag=TAG_SCHEMA_REFUSE
    )


def compare_digests(
    *,
    left_digest: str | None,
    left_algo: DigestAlgo,
    left_schema: str,
    right_digest: str | None,
    right_algo: DigestAlgo,
    right_schema: str,
) -> bool:
    """Compare two digests; REFUSE (raise) across schema/algo (TX-2).

    A cross-schema/algo comparison is a CATEGORY error, never a "stale" verdict —
    a legacy digest must never silently mis-compare against a UDAC record.
    """
    if left_algo != right_algo or left_schema != right_schema:
        raise AssetResolutionError(
            "refuse cross-schema/algo digest comparison "
            f"(left={left_algo.value}@{left_schema} right={right_algo.value}@{right_schema})",
            tag=TAG_SCHEMA_REFUSE,
        )
    return left_digest == right_digest


# ---------------------------------------------------------------------------
# RAI models (§F.1)
# ---------------------------------------------------------------------------


class RunAssetEntry(BaseModel):
    """One ratified/provisional/absent asset in the Run Asset Index."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    asset_id: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1, description="Run-relative path to the asset.")
    digest: str | None = Field(
        default=None,
        description="Content digest at the current revision; null iff absent (TX-5).",
    )
    digest_algo: DigestAlgo | None = Field(default=None)
    digest_schema_version: str = Field(default=DIGEST_SCHEMA_VERSION)
    revision: int = Field(default=0, ge=0)
    ratified_at: datetime | None = Field(default=None)
    produced_by_node: str | None = Field(default=None)
    authority_status: AuthorityStatus = Field(...)
    derived_from: str | None = Field(
        default=None,
        description="Source corpus_fingerprint / input closure (TX-4 trust chain).",
    )


class ResolvedAsset(BaseModel):
    """The verified resolution result of the v1 fail-loud dispatch GUARD.

    v1 SCOPE (review Blind-F4): ``resolve_asset`` resolves + verifies (recompute
    digest from disk, raise on stale/missing/corrupt) and RETURNS this view; the
    orchestrator's dispatch guard discards it after the raise-or-pass check. Threading
    this resolved view INTO each specialist's payload (so a consumer reads the
    located asset off this object instead of via its existing enrichment-access path)
    is DEFERRED plumbing — the P5 consumers keep their current access paths, now
    GUARDED by UDAC. So v1 delivers the fail-loud USE guarantee + the on-disk RAI as
    the auditable ACCESS index; it does not yet inject the path into specialists.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    asset_id: str
    path: str
    digest: str | None
    authority_status: AuthorityStatus
    produced_by_node: str | None
    revision: int
    legacy_mode: LegacyMode = LegacyMode.NONE


class RunAssetIndex(BaseModel):
    """The single in-run ACCESS spine (``<run_dir>/run-asset-index.json``)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    rai_schema_version: str = Field(default=RAI_SCHEMA_VERSION)
    entries: dict[str, RunAssetEntry] = Field(default_factory=dict)

    def get(self, asset_id: str) -> RunAssetEntry | None:
        return self.entries.get(asset_id)

    def mark_ratified(
        self,
        *,
        asset_id: str,
        path: str,
        digest: str,
        digest_algo: DigestAlgo,
        ratified_at: datetime,
        produced_by_node: str | None,
        revision: int = 0,
        derived_from: str | None = None,
    ) -> RunAssetEntry:
        """Stamp an asset ratified — idempotent + monotonic (M-1 / M-5).

        - new asset → insert RATIFIED;
        - same revision → idempotent no-op preserving the FIRST ``ratified_at``
          (both-walks parity: a re-crossed gate on recover must not regress or
          duplicate the stamp). A same-revision digest divergence is a real
          inconsistency → raise (it is NOT an additive bump; use ``repin_additive``);
        - higher revision → additive re-pin (delegated to ``repin_additive`` for
          the gate path; direct callers may pass it here);
        - lower revision → monotonic violation → raise.
        """
        existing = self.entries.get(asset_id)
        if existing is None:
            entry = RunAssetEntry(
                asset_id=asset_id,
                path=path,
                digest=digest,
                digest_algo=digest_algo,
                digest_schema_version=DIGEST_SCHEMA_VERSION,
                revision=revision,
                ratified_at=ratified_at,
                produced_by_node=produced_by_node,
                authority_status=AuthorityStatus.RATIFIED,
                derived_from=derived_from,
            )
            self.entries[asset_id] = entry
            return entry
        if revision < existing.revision:
            raise AssetResolutionError(
                f"monotonic violation for {asset_id!r}: revision {revision} < "
                f"recorded {existing.revision}",
                tag=TAG_MONOTONIC,
            )
        if revision == existing.revision:
            if existing.digest != digest:
                raise AssetResolutionError(
                    f"same-revision digest divergence for {asset_id!r} "
                    "(not an additive bump — call repin_additive for legitimate growth)",
                    tag=TAG_STALE,
                )
            return existing  # idempotent: preserve first ratified_at (M-5)
        updated = existing.model_copy(
            update={
                "digest": digest,
                "revision": revision,
                "ratified_at": ratified_at,
                "produced_by_node": produced_by_node or existing.produced_by_node,
                "derived_from": derived_from or existing.derived_from,
                "authority_status": AuthorityStatus.RATIFIED,
            }
        )
        self.entries[asset_id] = updated
        return updated

    def repin_additive(
        self,
        asset_id: str,
        *,
        run_dir: Path,
        ratified_at: datetime,
        produced_by_node: str | None = None,
    ) -> RunAssetEntry:
        """Re-pin an asset that legitimately GREW (TX-3 — bump revision, no stale).

        Recomputes the digest from disk; if the artifact grew (digest changed) the
        ``revision`` bumps and ``{digest, ratified_at}`` re-pin. An unchanged
        artifact is a no-op. This is the ONLY sanctioned path for an additive layer
        (P2 citations / P3 pedagogy onto ``g0-enrichment.json``) to update the RAI.
        """
        existing = self.entries.get(asset_id)
        if existing is None:
            raise AssetResolutionError(
                f"cannot repin unknown asset {asset_id!r}", tag=TAG_UNINDEXED
            )
        if existing.digest_algo is None:
            raise AssetResolutionError(
                f"cannot repin {asset_id!r}: no digest_algo pinned", tag=TAG_SCHEMA_REFUSE
            )
        new_digest = recompute_digest_from_disk(run_dir / existing.path, existing.digest_algo)
        if new_digest == existing.digest:
            return existing
        updated = existing.model_copy(
            update={
                "digest": new_digest,
                "revision": existing.revision + 1,
                "ratified_at": ratified_at,
                "produced_by_node": produced_by_node or existing.produced_by_node,
            }
        )
        self.entries[asset_id] = updated
        return updated

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


def resolve_asset(
    index: RunAssetIndex,
    asset_id: str,
    *,
    run_dir: Path,
    require_ratified: bool = True,
) -> ResolvedAsset:
    """Resolve an asset to a passed-in view — FAIL-LOUD past ratification (M-4 / MT-3).

    - asset not indexed → raise (``udac.asset-unindexed``);
    - ABSENT → null digest, never compared (TX-5); raise if ``require_ratified``;
    - PROVISIONAL → raise if ``require_ratified`` (post-boundary required asset),
      else return a ``PROVISIONAL_FALLBACK`` view (the typed legacy-mode marker);
    - RATIFIED → recompute the digest FROM DISK; a missing file raises
      ``udac.asset-missing``, a digest mismatch raises ``udac.asset-stale``.
    """
    entry = index.entries.get(asset_id)
    if entry is None:
        raise AssetResolutionError(
            f"asset {asset_id!r} is not in the Run Asset Index", tag=TAG_UNINDEXED
        )
    if entry.authority_status is AuthorityStatus.ABSENT:
        if require_ratified:
            raise AssetResolutionError(
                f"asset {asset_id!r} is absent — no ratified asset to resolve",
                tag=TAG_ABSENT,
            )
        return _provisional_view(entry)
    if entry.authority_status is AuthorityStatus.PROVISIONAL:
        if require_ratified:
            raise AssetResolutionError(
                f"asset {asset_id!r} is not yet ratified (provisional)",
                tag=TAG_NOT_RATIFIED,
            )
        return _provisional_view(entry)
    # RATIFIED — verify against disk bytes.
    asset_path = run_dir / entry.path
    if not asset_path.is_file():
        raise AssetResolutionError(
            f"ratified asset {asset_id!r} is missing on disk at {entry.path!r}",
            tag=TAG_MISSING,
        )
    if entry.digest_algo is None:
        raise AssetResolutionError(  # pragma: no cover - defensive
            f"ratified asset {asset_id!r} has no digest_algo pinned",
            tag=TAG_SCHEMA_REFUSE,
        )
    # Blind-F5: a future digest_schema_version bump must REFUSE rather than silently
    # recompute under the new scheme and mis-compare against an old pin (TX-2 spirit).
    if entry.digest_schema_version != DIGEST_SCHEMA_VERSION:
        raise AssetResolutionError(
            f"ratified asset {asset_id!r} pinned at digest_schema_version "
            f"{entry.digest_schema_version!r} != current {DIGEST_SCHEMA_VERSION!r}; "
            "refusing to recompute across schema versions",
            tag=TAG_SCHEMA_REFUSE,
        )
    recomputed = recompute_digest_from_disk(asset_path, entry.digest_algo)
    if recomputed != entry.digest:
        raise AssetResolutionError(
            f"ratified asset {asset_id!r} is STALE: on-disk digest "
            f"{recomputed[:12]}… != RAI digest {str(entry.digest)[:12]}… "
            f"(revision {entry.revision})",
            tag=TAG_STALE,
        )
    return ResolvedAsset(
        asset_id=entry.asset_id,
        path=entry.path,
        digest=entry.digest,
        authority_status=AuthorityStatus.RATIFIED,
        produced_by_node=entry.produced_by_node,
        revision=entry.revision,
        legacy_mode=LegacyMode.NONE,
    )


def _provisional_view(entry: RunAssetEntry) -> ResolvedAsset:
    return ResolvedAsset(
        asset_id=entry.asset_id,
        path=entry.path,
        digest=entry.digest,
        authority_status=entry.authority_status,
        produced_by_node=entry.produced_by_node,
        revision=entry.revision,
        legacy_mode=LegacyMode.PROVISIONAL_FALLBACK,
    )


# ---------------------------------------------------------------------------
# Disk I/O (disk-primary; §F.1)
# ---------------------------------------------------------------------------


def rai_path(run_dir: Path) -> Path:
    return run_dir / RAI_BASENAME


def load_rai(run_dir: Path) -> RunAssetIndex | None:
    """Rehydrate the RAI from disk (disk is SSOT). ``None`` when absent (M-3).

    A truncated / partially written / non-utf8 RAI raises a TAGGED
    :class:`AssetResolutionError` (``udac.index-corrupt``) rather than a raw
    pydantic ``ValidationError`` / ``OSError`` — so a corrupt index routes through
    the runner's recoverable pause, never an uncaught crash (review F2).
    """
    path = rai_path(run_dir)
    if not path.is_file():
        return None
    try:
        return RunAssetIndex.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        # pydantic ValidationError subclasses ValueError.
        raise AssetResolutionError(
            f"run-asset-index.json is corrupt / unreadable: {exc}",
            tag=TAG_INDEX_CORRUPT,
        ) from exc


def write_rai(run_dir: Path, index: RunAssetIndex) -> Path:
    """Atomically write the RAI (temp file + ``os.replace``) so a crash mid-write
    never leaves a torn index a later walk would choke on (Blind-F2)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    path = rai_path(run_dir)
    tmp = path.with_name(f"{RAI_BASENAME}.{os.getpid()}.tmp")
    tmp.write_text(index.to_json(), encoding="utf-8")
    os.replace(tmp, path)
    return path


# ---------------------------------------------------------------------------
# Gate → asset map (M-2) + consumer registry (USE/audit spine, §F.5)
# ---------------------------------------------------------------------------


class AssetSpec(BaseModel):
    """A gate-ratified asset's identity + on-disk shape (the M-2 map row)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    asset_id: str
    rel_path: str
    digest_algo: DigestAlgo


# Per §F.2 M-2: stamp ratified_at + produced_by_node off ``last_gate_crossed``.
# Mine-next trust T1 (2026-07-10): pin every gate whose run-dir path is
# VERIFIABLY materialised by a production writer. The gate writer no-ops
# harmlessly on any mapped asset whose file is absent, so rows are
# side-effect-free until the file lands. Residual G4/G4A voice-selection +
# Pass-2 envelope paths remain under bundle_dir (not run-dir root) and stay
# OUT of this map until a run-dir projection exists — see deferred
# ``udac-v1-universality-complete-gate-asset-map`` residual note.
GATE_ASSET_MAP: Final[dict[str, tuple[AssetSpec, ...]]] = {
    "G0E": (
        AssetSpec(
            asset_id="g0-enrichment",
            rel_path="g0-enrichment.json",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
        ),
    ),
    "G0R": (
        AssetSpec(
            asset_id="ratified-los",
            rel_path="ratified-los.json",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
        ),
    ),
    # G1: Irene Pass-1 locked lesson plan (JSON companion beside irene-pass1.md).
    "G1": (
        AssetSpec(
            asset_id="locked-lesson-plan",
            rel_path="irene-pass1.lesson-plan.json",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
        ),
    ),
    # G2C: durable storyboard-publish receipt written by storyboard_publisher.
    "G2C": (
        AssetSpec(
            asset_id="authorized-storyboard",
            rel_path="storyboard-publish-G2C.json",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
        ),
    ),
    # Story concierge-coverage-assurance-interlock (Round-4 integration): the DERIVED
    # coverage receipt is a gate-G3 RunAssetEntry pinned with CANONICAL_SHA256. Its
    # on-disk projection is volatile-free (no generated_at) so the SHA survives the
    # resume/recover G3 crossing. The gate writer no-ops harmlessly when the file is
    # absent (the pre-integration provisional window), so this row is side-effect-free
    # until the G3 derive seam lands the receipt.
    "G3": (
        AssetSpec(
            asset_id="coverage-receipt",
            rel_path="coverage-receipt.json",
            digest_algo=DigestAlgo.CANONICAL_SHA256,
        ),
    ),
}


class ConsumerAssetDeclaration(BaseModel):
    """One asset a consumer declares it consumes (A.2 receipt shape)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    asset_id: str
    usage: AssetUsage


class ConsumerDeclaration(BaseModel):
    """A downstream consumer's full asset declaration (the audit spine)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    consumer_id: str
    consumes: tuple[ConsumerAssetDeclaration, ...]

    def required_assets(self) -> tuple[str, ...]:
        return tuple(c.asset_id for c in self.consumes if c.usage is AssetUsage.USED)


def _decl(consumer_id: str, *pairs: tuple[str, AssetUsage]) -> ConsumerDeclaration:
    return ConsumerDeclaration(
        consumer_id=consumer_id,
        consumes=tuple(
            ConsumerAssetDeclaration(asset_id=a, usage=u) for a, u in pairs
        ),
    )


# §F.5 — the 4 P5 consumers (workbook/gary/irene USE g0-enrichment; enrique is a
# genuine available_only — it consumes irene's voice_direction, not g0 directly) +
# compositor/motion DECLARED-non-consuming-with-MT-2-tripwire (declaration is in v1;
# only their consumption PLUMBING is deferred).
CONSUMER_REGISTRY: Final[dict[str, ConsumerDeclaration]] = {
    "workbook": _decl("workbook", ("g0-enrichment", AssetUsage.USED)),
    "gary": _decl("gary", ("g0-enrichment", AssetUsage.USED)),
    "irene": _decl("irene", ("g0-enrichment", AssetUsage.USED)),
    "enrique": _decl(
        "enrique",
        ("g0-enrichment", AssetUsage.AVAILABLE_ONLY),
        # The audio-spend consumer USES the coverage receipt (the fail-loud gate reads
        # it before enrique dispatches) — concierge-coverage-assurance-interlock.
        ("coverage-receipt", AssetUsage.USED),
    ),
    "compositor": _decl("compositor", ("g0-enrichment", AssetUsage.AVAILABLE_ONLY)),
    "kira": _decl("kira", ("g0-enrichment", AssetUsage.AVAILABLE_ONLY)),
}


__all__ = [
    "DIGEST_SCHEMA_VERSION",
    "GATE_ASSET_MAP",
    "RAI_BASENAME",
    "RAI_SCHEMA_VERSION",
    "TAG_ABSENT",
    "TAG_CORRUPT",
    "TAG_INDEX_CORRUPT",
    "TAG_MISSING",
    "TAG_MONOTONIC",
    "TAG_NOT_RATIFIED",
    "TAG_SCHEMA_REFUSE",
    "TAG_STALE",
    "TAG_UNINDEXED",
    "AssetResolutionError",
    "AssetSpec",
    "AssetUsage",
    "AuthorityStatus",
    "CONSUMER_REGISTRY",
    "ConsumerAssetDeclaration",
    "ConsumerDeclaration",
    "DigestAlgo",
    "LegacyMode",
    "ResolvedAsset",
    "RunAssetEntry",
    "RunAssetIndex",
    "compare_digests",
    "digest_binary_path",
    "digest_structured_payload",
    "load_rai",
    "rai_path",
    "recompute_digest_from_disk",
    "resolve_asset",
    "write_rai",
]

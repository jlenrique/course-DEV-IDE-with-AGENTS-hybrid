"""Shared styleguide-resolution parity core (canonical-arc S3 D2).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`.

Two exports, both PURE:

- :func:`canonical_resolution_digest` — the sha256-over-canonical-JSON digest
  of a ``resolved`` mapping, extracted here so CD's emission
  (``app/specialists/cd/graph.py``, the ``resolution_digest`` field) and
  Gary's shadow comparator digest IDENTICALLY (byte-for-byte — the S1
  determinism pin `tests/specialists/cd/test_styleguide_resolution_emission.py`
  stays green UNMODIFIED through the extraction, AC-7).
- :func:`compare_styleguide_resolution` — the TOTAL (never-raise) comparator
  classifying CD's authoring-time ``styleguide_resolution`` block against
  Gary's dispatch-time view into the ratified trichotomy
  (``ok`` / ``expected-ordering-gap`` / ``divergence``).

Parity semantics (Amelia, on the record): the comparator instruments INPUT
drift across time, not resolver logic — it compares BASE-LAYER resolutions
(Gary's ``resolved_base`` BEFORE per-variant explicit-key overrides).
Per-variant overrides are Gary-legitimate and must never false-diverge.

Import boundary: this module imports NOTHING from ``app.specialists.cd``,
``app.specialists.gary``, or ``app.marcus`` — the pyproject S1 contract
("cd + app.styleguide never import app.specialists.gary") inherits over it.
The comparator also never touches picker pickability (F-704: pickable ≠
resolvable; lifecycle/visibility enforcement stays pick-time).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

PARITY_RECEIPT_SCHEMA_VERSION = 1

# F-402/F-304 (binding): the schema-v1 SSOT is the COMMITTED CD emission —
# the FULL key set byte-verified at cd/graph.py:572-586. A v1 block missing
# any of these is a CONTRACT VIOLATION, not a tolerable degrade.
CD_STYLEGUIDE_RESOLUTION_V1_KEYS: frozenset[str] = frozenset(
    {
        "schema_version",
        "status",
        "input_picks",
        "bound_guides",
        "resolved",
        "layering_manifest",
        "resolution_digest",
        "directive_digest",
        "default_provenance",
        "errors",
    }
)

_CD_V1_STATUSES: frozenset[str] = frozenset(
    {"resolved", "no_picks_at_authoring", "unresolvable_pick"}
)

_OUTCOME_OK = "ok"
_OUTCOME_GAP = "expected-ordering-gap"
_OUTCOME_DIVERGENCE = "divergence"


def _canonical_json(payload: Any) -> str:
    # Byte-identical to CD's original private helper (sort_keys +
    # ensure_ascii + compact separators) — the shared digest algorithm.
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


# T11 P4: bounded repr excerpt for unserializable values folded into receipts.
_UNSERIALIZABLE_EXCERPT_LIMIT = 512


def _bounded_repr(value: Any) -> str:
    try:
        text = repr(value)
    except Exception:  # noqa: BLE001 — a broken __repr__ must not break the receipt
        text = f"<repr failed for {type(value).__name__}>"
    if len(text) > _UNSERIALIZABLE_EXCERPT_LIMIT:
        text = text[:_UNSERIALIZABLE_EXCERPT_LIMIT] + "...[truncated]"
    return f"<unserializable {type(value).__name__}: {text}>"


def _json_safe(value: Any) -> Any:
    """Deep-copy ``value`` into fresh JSON-serializable containers (T11 P4).

    Receipts must survive envelope persistence (the run.json dump) for ANY
    input and must never alias live source objects: JSON-clean values are
    preserved exactly (fresh containers — a post-receipt mutation of the
    source can never reach the receipt); anything unserializable is guarded
    to a bounded repr excerpt instead of raising downstream.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {
            (key if isinstance(key, str) else str(key)): _json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return _bounded_repr(value)


def canonical_resolution_digest(resolved: Any) -> str:
    """sha256 of the canonical JSON of a ``resolved`` mapping.

    The ONE digest algorithm both CD's ``resolution_digest`` emission and the
    parity comparator use — extracted so they can never drift (D2a).
    """
    return hashlib.sha256(_canonical_json(resolved).encode("utf-8")).hexdigest()


def _receipt(
    *,
    outcome: str,
    reason: str,
    cd_status: Any = None,
    cd_resolution_digest: Any = None,
    gary_resolution_digest: Any = None,
    cd_directive_digest: Any = None,
    gary_directive_digest: Any = None,
    trial_start_directive_digest: Any = None,
    cd_bound_guides: list[dict[str, Any]] | None = None,
    gary_bound_guides: list[dict[str, Any]] | None = None,
    detail: Any = None,
) -> dict[str, Any]:
    return {
        "schema_version": PARITY_RECEIPT_SCHEMA_VERSION,
        "outcome": outcome,
        "reason": reason,
        "cd_status": cd_status,
        # F-702: eligible for the S-flip parity clock iff CD's status is
        # ``resolved`` AND the outcome is a clean match — nothing else counts.
        "clock_eligible": outcome == _OUTCOME_OK
        and reason == "match"
        and cd_status == "resolved",
        "cd_resolution_digest": cd_resolution_digest,
        "gary_resolution_digest": gary_resolution_digest,
        "cd_directive_digest": cd_directive_digest,
        "gary_directive_digest": gary_directive_digest,
        "trial_start_directive_digest": trial_start_directive_digest,
        "cd_bound_guides": cd_bound_guides if cd_bound_guides is not None else [],
        "gary_bound_guides": gary_bound_guides if gary_bound_guides is not None else [],
        "detail": detail,
    }


def _name_digest_pairs(bound_guides: Any) -> list[dict[str, Any]]:
    """Normalize a bound_guides list to comparable ``{name, ssot_digest}``
    pairs (lifecycle/visibility are pick-time DATA, not parity surface)."""
    if not isinstance(bound_guides, list):
        return []
    return [
        {"name": entry.get("name"), "ssot_digest": entry.get("ssot_digest")}
        for entry in bound_guides
        if isinstance(entry, dict)
    ]


def compare_styleguide_resolution(cd_block: Any, gary_view: Any) -> dict[str, Any]:
    """Classify CD's block vs Gary's dispatch-time view. PURE and TOTAL.

    ``gary_view``: ``{picks: {variant: guide_name}, resolved_base:
    {variant: resolver_output}, ssot_digest, directive_digest,
    trial_start_directive_digest}`` — the base-layer surface ONLY.

    NEVER raises and NEVER alters dispatch: any internal surprise is folded
    into a ``divergence/contract-violation`` receipt (loud in the data plane,
    silent in the control plane).

    T11 P4: the returned receipt is sanitized through :func:`_json_safe` —
    deep-decoupled from the live inputs and JSON-serialization-safe for ANY
    input, extending the never-raise guarantee through envelope persistence
    (the run.json dump). The crash-path fallback detail carries best-effort
    digests (guarded) alongside ``comparator_error``.
    """
    try:
        return _json_safe(_classify(cd_block, gary_view))
    except Exception as exc:  # noqa: BLE001 — total by contract, never raise
        try:
            return _json_safe(
                _receipt(
                    outcome=_OUTCOME_DIVERGENCE,
                    reason="contract-violation",
                    detail=_crash_detail(exc, cd_block, gary_view),
                )
            )
        except Exception:  # noqa: BLE001 — last-resort totality (e.g. RecursionError)
            return _receipt(
                outcome=_OUTCOME_DIVERGENCE,
                reason="contract-violation",
                detail={"comparator_error": type(exc).__name__},
            )


def _crash_detail(exc: Exception, cd_block: Any, gary_view: Any) -> dict[str, Any]:
    """Crash-path fallback detail: comparator_error plus best-effort digests
    (each lookup guarded — the crash path must never crash)."""
    try:
        message = f"{type(exc).__name__}: {exc}"
    except Exception:  # noqa: BLE001 — a broken __str__ must not break the fallback
        message = type(exc).__name__
    detail: dict[str, Any] = {"comparator_error": message}
    try:
        if isinstance(cd_block, dict):
            detail["cd_resolution_digest"] = cd_block.get("resolution_digest")
            detail["cd_directive_digest"] = cd_block.get("directive_digest")
        if isinstance(gary_view, dict):
            detail["gary_directive_digest"] = gary_view.get("directive_digest")
            detail["trial_start_directive_digest"] = gary_view.get(
                "trial_start_directive_digest"
            )
            detail["gary_ssot_digest"] = gary_view.get("ssot_digest")
    except Exception:  # noqa: BLE001 — best-effort by contract
        pass
    return detail


def _classify(cd_block: Any, gary_view: Any) -> dict[str, Any]:
    view = gary_view if isinstance(gary_view, dict) else {}
    picks = view.get("picks") if isinstance(view.get("picks"), dict) else {}
    resolved_base = (
        view.get("resolved_base") if isinstance(view.get("resolved_base"), dict) else {}
    )
    gary_ssot_digest = view.get("ssot_digest")
    gary_directive_digest = view.get("directive_digest")
    trial_start_digest = view.get("trial_start_directive_digest")
    gary_resolution_digest = canonical_resolution_digest(resolved_base)
    gary_bound_guides = [
        {"name": name, "ssot_digest": gary_ssot_digest} for name in picks.values()
    ]

    common: dict[str, Any] = {
        "gary_resolution_digest": gary_resolution_digest,
        "gary_directive_digest": gary_directive_digest,
        "trial_start_directive_digest": trial_start_digest,
        "gary_bound_guides": gary_bound_guides,
    }

    # 1) Absent block: pre-S1 bundle / legacy envelope (F-802 tolerance).
    if cd_block is None:
        return _receipt(
            outcome=_OUTCOME_GAP, reason="cd-envelope-absent-legacy", **common
        )
    if not isinstance(cd_block, dict):
        return _receipt(
            outcome=_OUTCOME_DIVERGENCE,
            reason="contract-violation",
            detail={"cd_block": cd_block, "gary_view": view},
            **common,
        )

    # 2) Forward-compat: a NEWER schema is an ordering gap, never WARN-spam.
    #    T11 P2 (Auditor's ruling): a version CLAIM is valid iff
    #    ``type(x) is int`` — bool is excluded (True == 1 must not coerce into
    #    v1), floats/strings are not valid claims. Any non-int claim is a
    #    contract violation below, never a schema-newer tolerance.
    schema_version = cd_block.get("schema_version")
    valid_version_claim = type(schema_version) is int
    if valid_version_claim and schema_version > 1:
        return _receipt(
            outcome=_OUTCOME_GAP,
            reason="cd-schema-newer",
            cd_status=cd_block.get("status"),
            **common,
        )

    # 3) F-304 contract teeth: a v1 block carries the FULL committed key set,
    #    a version claim of exactly 1, and a known status.
    missing = sorted(CD_STYLEGUIDE_RESOLUTION_V1_KEYS - set(cd_block))
    cd_status = cd_block.get("status")
    if (
        not valid_version_claim
        or schema_version != 1
        or missing
        or cd_status not in _CD_V1_STATUSES
    ):
        return _receipt(
            outcome=_OUTCOME_DIVERGENCE,
            reason="contract-violation",
            cd_status=cd_status,
            cd_resolution_digest=cd_block.get("resolution_digest"),
            cd_directive_digest=cd_block.get("directive_digest"),
            cd_bound_guides=_name_digest_pairs(cd_block.get("bound_guides")),
            detail={
                "cd_block": cd_block,
                "gary_view": view,
                "missing_keys": missing,
            },
            **common,
        )

    cd_directive_digest = cd_block.get("directive_digest")
    cd_resolution_digest = cd_block.get("resolution_digest")
    cd_bound_guides = _name_digest_pairs(cd_block.get("bound_guides"))
    common.update(
        {
            "cd_status": cd_status,
            "cd_resolution_digest": cd_resolution_digest,
            "cd_directive_digest": cd_directive_digest,
            "cd_bound_guides": cd_bound_guides,
        }
    )

    # 4) F-702 status-keying: the F-202 asymmetry (Gary seeds
    #    DEFAULT_VARIANT_PAIR; CD binds default-A) is keyed on STATUS and the
    #    seeds are deliberately NOT settings-compared.
    if cd_status == "no_picks_at_authoring":
        if not picks:
            return _receipt(
                outcome=_OUTCOME_OK, reason="status-keyed-no-picks", **common
            )
        # Pick landed after 4.75 (legacy/G2B-era flow) — expected, INFO-class.
        return _receipt(outcome=_OUTCOME_GAP, reason="cd-saw-no-picks", **common)

    # 5) F-703 drift discrimination: any disagreement among the COMPARABLE
    #    digests (None = not-comparable, NEVER a mismatch) means the directive
    #    mutated mid-walk — resolution comparison is not meaningful.
    comparable = {
        digest
        for digest in (trial_start_digest, cd_directive_digest, gary_directive_digest)
        if isinstance(digest, str) and digest
    }
    if len(comparable) > 1:
        return _receipt(outcome=_OUTCOME_GAP, reason="directive-drift", **common)

    # 6) Same bytes, CD could not resolve, Gary resolved cleanly (Gary's audit
    #    only runs after its resolve loop COMPLETED) — resolver disagreement
    #    is a real defect.
    if cd_status == "unresolvable_pick":
        return _receipt(
            outcome=_OUTCOME_DIVERGENCE,
            reason="cd-unresolvable-but-gary-resolved",
            detail={"cd_block": cd_block, "gary_view": view},
            **common,
        )

    # 7) cd_status == "resolved": genuine parity comparison — pick sets,
    #    bound guides (name + ssot digest), base-resolution digests.
    cd_resolved = cd_block.get("resolved")
    cd_variants = set(cd_resolved) if isinstance(cd_resolved, dict) else set()
    same_pick_sets = set(picks) == cd_variants
    same_bound = sorted(
        (str(pair.get("name")), str(pair.get("ssot_digest"))) for pair in cd_bound_guides
    ) == sorted(
        (str(pair.get("name")), str(pair.get("ssot_digest"))) for pair in gary_bound_guides
    )
    same_resolution = gary_resolution_digest == cd_resolution_digest
    if same_pick_sets and same_bound and same_resolution:
        return _receipt(outcome=_OUTCOME_OK, reason="match", **common)
    return _receipt(
        outcome=_OUTCOME_DIVERGENCE,
        reason="resolution-mismatch",
        detail={"cd_block": cd_block, "gary_view": view},
        **common,
    )


__all__ = [
    "CD_STYLEGUIDE_RESOLUTION_V1_KEYS",
    "PARITY_RECEIPT_SCHEMA_VERSION",
    "canonical_resolution_digest",
    "compare_styleguide_resolution",
]

"""Canonical-arc S3 D2 — the shared styleguide parity comparator (RED-first plan #1).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`.

The comparator is PURE and TOTAL (never raises, never alters dispatch) and
classifies CD's authoring-time `styleguide_resolution` block against Gary's
dispatch-time view into the ratified trichotomy:

- ``ok`` (silent): ``match`` | ``status-keyed-no-picks`` (F-702/F-202)
- ``expected-ordering-gap`` (INFO): ``cd-saw-no-picks`` | ``directive-drift``
  (F-703) | ``cd-envelope-absent-legacy`` | ``cd-schema-newer``
- ``divergence`` (WARN): ``resolution-mismatch`` |
  ``cd-unresolvable-but-gary-resolved`` | ``contract-violation`` (F-304/F-402)

Covers AC-1 (comparator legs of the non-vacuity trio), AC-2 (status-keying +
clock_eligible truth table), AC-3 (drift discrimination; ``None`` digest is
not-comparable, never a mismatch), and AC-6 (contract teeth).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from app.styleguide.parity import (
    CD_STYLEGUIDE_RESOLUTION_V1_KEYS,
    canonical_resolution_digest,
    compare_styleguide_resolution,
)

# A realistic resolver output (flat base-layer API keys).
RES_A: dict[str, Any] = {"production_mode": "api", "theme": "t-1", "tone": "calm"}
RES_A_OTHER: dict[str, Any] = {"production_mode": "api", "theme": "t-1", "tone": "urgent"}

RECEIPT_KEYS = {
    "schema_version",
    "outcome",
    "reason",
    "cd_status",
    "clock_eligible",
    "cd_resolution_digest",
    "gary_resolution_digest",
    "cd_directive_digest",
    "gary_directive_digest",
    "trial_start_directive_digest",
    "cd_bound_guides",
    "gary_bound_guides",
    "detail",
}


def _cd_block(
    *,
    status: str = "resolved",
    resolved: dict[str, Any] | None = None,
    bound_guides: list[dict[str, Any]] | None = None,
    directive_digest: str | None = "d-1",
    **overrides: Any,
) -> dict[str, Any]:
    """A schema-v1 CD block carrying the FULL F-402 key set (byte-verified at
    cd/graph.py:572-586)."""
    resolved = {} if resolved is None else resolved
    block: dict[str, Any] = {
        "schema_version": 1,
        "status": status,
        "input_picks": None,
        "bound_guides": bound_guides if bound_guides is not None else [],
        "resolved": resolved,
        "layering_manifest": {
            "base_layer": "styleguide_defaults",
            "composition_rule": "source_derived_wins",
        },
        "resolution_digest": canonical_resolution_digest(resolved),
        "directive_digest": directive_digest,
        "default_provenance": None,
        "errors": [],
    }
    block.update(overrides)
    return block


def _gary_view(
    *,
    picks: dict[str, str] | None = None,
    resolved_base: dict[str, Any] | None = None,
    ssot_digest: str | None = "ssot-1",
    directive_digest: str | None = "d-1",
    trial_start: str | None = "d-1",
) -> dict[str, Any]:
    return {
        "picks": picks or {},
        "resolved_base": resolved_base or {},
        "ssot_digest": ssot_digest,
        "directive_digest": directive_digest,
        "trial_start_directive_digest": trial_start,
    }


def _matched_pair() -> tuple[dict[str, Any], dict[str, Any]]:
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1", "lifecycle": "standard"}],
    )
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": RES_A})
    return cd, gary


# --- shared digest helper (AC-7 support: byte-identical to CD's algorithm) ----


def test_canonical_resolution_digest_matches_cd_canonical_json_algorithm() -> None:
    resolved = {"B": RES_A, "A": RES_A_OTHER}
    expected = hashlib.sha256(
        json.dumps(
            resolved, sort_keys=True, ensure_ascii=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    assert canonical_resolution_digest(resolved) == expected


def test_v1_key_set_is_the_f402_committed_emission() -> None:
    expected = {
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
    assert set(CD_STYLEGUIDE_RESOLUTION_V1_KEYS) == expected


# --- ok/match (AC-1 fixture 2, comparator leg) --------------------------------


def test_match_is_ok_and_clock_eligible() -> None:
    cd, gary = _matched_pair()
    receipt = compare_styleguide_resolution(cd, gary)
    assert set(receipt) == RECEIPT_KEYS
    assert receipt["schema_version"] == 1
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["cd_status"] == "resolved"
    assert receipt["clock_eligible"] is True
    assert receipt["cd_resolution_digest"] == canonical_resolution_digest({"A": RES_A})
    assert receipt["gary_resolution_digest"] == receipt["cd_resolution_digest"]
    assert receipt["cd_directive_digest"] == "d-1"
    assert receipt["gary_directive_digest"] == "d-1"
    assert receipt["trial_start_directive_digest"] == "d-1"
    assert receipt["detail"] is None


# --- ok/status-keyed-no-picks (AC-2, F-702/F-202) ------------------------------


def test_status_keyed_no_picks_never_compares_the_default_seed() -> None:
    # CD binds the F-202 default-A resolution at authoring time; Gary seeds
    # DEFAULT_VARIANT_PAIR at runtime. The two DIFFER by design — the case is
    # keyed on status and NOT settings-compared (F-804 assertion): outcome is
    # ok even though the resolution digests disagree, and Gary's side shows
    # an EMPTY compared surface (the seed never entered the view).
    cd = _cd_block(
        status="no_picks_at_authoring",
        resolved={"A": RES_A},
        bound_guides=[
            {"name": "default-guide", "ssot_digest": "ssot-1", "lifecycle": "standard"}
        ],
        default_provenance=(
            "authoring-time default; gary runtime seeds DEFAULT_VARIANT_PAIR "
            "until S2/S4"
        ),
    )
    gary = _gary_view(picks={}, resolved_base={})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "status-keyed-no-picks"
    assert receipt["clock_eligible"] is False
    assert receipt["gary_resolution_digest"] == canonical_resolution_digest({})
    assert receipt["gary_resolution_digest"] != receipt["cd_resolution_digest"]
    assert receipt["gary_bound_guides"] == []


# --- expected-ordering-gap/cd-saw-no-picks (AC-1 fixture 3, comparator leg) ----


def test_cd_saw_no_picks_but_gary_has_picks_is_gap() -> None:
    cd = _cd_block(status="no_picks_at_authoring", resolved={"A": RES_A})
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": RES_A_OTHER})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-saw-no-picks"
    assert receipt["clock_eligible"] is False


# --- expected-ordering-gap/directive-drift (AC-3, F-703) -----------------------


@pytest.mark.parametrize(
    ("trial_start", "cd_digest", "gary_digest"),
    [
        ("d-OLD", "d-1", "d-1"),  # trial-start != cd
        ("d-1", "d-OLD", "d-1"),  # cd != gary-read
        (None, "d-OLD", "d-1"),  # third not-comparable; remaining two disagree
    ],
)
def test_digest_drift_is_gap_never_divergence(
    trial_start: str | None, cd_digest: str, gary_digest: str
) -> None:
    # Otherwise-DIVERGENT resolutions: without F-703 this would cry WARN.
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
        directive_digest=cd_digest,
    )
    gary = _gary_view(
        picks={"A": "guide-y"},
        resolved_base={"A": RES_A_OTHER},
        directive_digest=gary_digest,
        trial_start=trial_start,
    )
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "directive-drift"
    # All three digests echoed verbatim for triage.
    assert receipt["trial_start_directive_digest"] == trial_start
    assert receipt["cd_directive_digest"] == cd_digest
    assert receipt["gary_directive_digest"] == gary_digest


def test_none_digest_is_not_comparable_never_a_mismatch() -> None:
    # F-703: ``None`` is NOT a drift signal. trial-start absent (legacy run)
    # with the remaining two digests EQUAL and matched resolutions ⇒ ok/match.
    cd, gary = _matched_pair()
    gary["trial_start_directive_digest"] = None
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["trial_start_directive_digest"] is None


def test_all_digests_none_still_compares_resolutions() -> None:
    # Zero comparable digests: comparison proceeds on resolutions alone
    # (never classified as drift when nothing disagrees).
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
        directive_digest=None,
    )
    gary = _gary_view(
        picks={"A": "guide-x"},
        resolved_base={"A": RES_A},
        directive_digest=None,
        trial_start=None,
    )
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"


def test_drift_precedes_unresolvable_classification() -> None:
    # A mutated directive makes resolution comparison meaningless — drift
    # wins even when CD reported unresolvable_pick.
    cd = _cd_block(status="unresolvable_pick", directive_digest="d-OLD")
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": RES_A})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "directive-drift"


# --- expected-ordering-gap/legacy + schema-newer (AC-6) ------------------------


def test_absent_cd_block_is_legacy_gap() -> None:
    receipt = compare_styleguide_resolution(None, _gary_view())
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-envelope-absent-legacy"
    assert receipt["cd_status"] is None
    assert receipt["clock_eligible"] is False


def test_schema_version_2_is_gap_never_warn_spam() -> None:
    cd = _cd_block(schema_version=2)
    receipt = compare_styleguide_resolution(cd, _gary_view())
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-schema-newer"


# --- divergence (AC-1 fixture 1 comparator leg + AC-6 teeth) --------------------


def test_resolution_mismatch_is_divergence_with_both_envelopes() -> None:
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
    )
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": RES_A_OTHER})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "resolution-mismatch"
    assert receipt["clock_eligible"] is False
    # §7: the WARN receipt carries BOTH envelopes + digests.
    assert receipt["detail"] == {"cd_block": cd, "gary_view": gary}


def test_mid_run_ssot_drift_is_divergence_and_discriminable() -> None:
    # Same directive bytes, same guide name, but the SSOT changed between
    # CD's read and Gary's read: bound-guide ssot digests disagree. The
    # receipt's bound_guides expose the drift for triage (F-806 family).
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-OLD"}],
    )
    gary = _gary_view(
        picks={"A": "guide-x"}, resolved_base={"A": RES_A_OTHER}, ssot_digest="ssot-NEW"
    )
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "resolution-mismatch"
    assert receipt["cd_bound_guides"] == [{"name": "guide-x", "ssot_digest": "ssot-OLD"}]
    assert receipt["gary_bound_guides"] == [{"name": "guide-x", "ssot_digest": "ssot-NEW"}]


def test_pick_set_disagreement_is_divergence() -> None:
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
    )
    gary = _gary_view(picks={"B": "guide-x"}, resolved_base={"B": RES_A})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "resolution-mismatch"


def test_cd_unresolvable_but_gary_resolved_same_bytes_is_divergence() -> None:
    cd = _cd_block(status="unresolvable_pick")
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": RES_A})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "cd-unresolvable-but-gary-resolved"


@pytest.mark.parametrize("missing_key", sorted(CD_STYLEGUIDE_RESOLUTION_V1_KEYS))
def test_v1_block_missing_any_ssot_key_is_contract_violation(missing_key: str) -> None:
    # F-304: the FULL emitted key set is the contract — a v1 block missing
    # keys is a violation, never a tolerable degrade. (schema_version removal
    # is also a violation: an unversioned block cannot claim v1 tolerance.)
    cd, gary = _matched_pair()
    del cd[missing_key]
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "contract-violation"


def test_unknown_v1_status_is_contract_violation() -> None:
    cd = _cd_block(status="mystery-status")
    receipt = compare_styleguide_resolution(cd, _gary_view())
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "contract-violation"


def test_non_mapping_block_is_contract_violation() -> None:
    receipt = compare_styleguide_resolution(42, _gary_view())
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "contract-violation"


# --- T11 P2: schema_version claim is valid iff type(x) is int (bool excluded) ----


@pytest.mark.parametrize(
    "bogus_version",
    [True, 1.0, "2", "1", False, 2.0, None],
    ids=["bool-true", "float-one", "str-two", "str-one", "bool-false", "float-two", "none"],
)
def test_non_int_schema_version_claim_is_contract_violation(bogus_version: Any) -> None:
    # P2 (Auditor's ruling): a non-int is NOT a valid forward-compat claim —
    # bool/float/str coercion must never pass as v1 (True == 1, 1.0 == 1) and
    # must never earn the cd-schema-newer tolerance ("2", 2.0).
    cd, gary = _matched_pair()
    cd["schema_version"] = bogus_version
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "contract-violation"
    assert receipt["clock_eligible"] is False


def test_int_schema_version_gt_one_is_still_schema_newer() -> None:
    # The valid forward-compat claim keeps its gap tolerance (never WARN-spam).
    cd, _ = _matched_pair()
    cd["schema_version"] = 3
    receipt = compare_styleguide_resolution(cd, _gary_view())
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-schema-newer"


# --- T11 P4: serialization-safe, decoupled receipt payloads ----------------------


def test_p4_receipt_is_decoupled_from_live_source_objects() -> None:
    # The divergence detail must NOT alias the live cd contribution / gary
    # view: mutating the sources AFTER receipt computation leaves the receipt
    # unchanged (the receipt is an attestation, not a live pointer).
    cd = _cd_block(
        resolved={"A": dict(RES_A)},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
    )
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": dict(RES_A_OTHER)})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    snapshot = json.dumps(receipt, sort_keys=True)
    cd["resolved"]["A"]["tone"] = "MUTATED-AFTER-RECEIPT"
    cd["bound_guides"][0]["ssot_digest"] = "MUTATED"
    gary["resolved_base"]["A"]["tone"] = "MUTATED-AFTER-RECEIPT"
    gary["picks"]["B"] = "sneaky-late-pick"
    assert json.dumps(receipt, sort_keys=True) == snapshot, (
        "post-receipt mutation of the source objects leaked into the receipt"
    )


def test_p4_unserializable_view_value_yields_persistable_receipt() -> None:
    # Non-crash path: an unserializable digest value still classifies (via
    # the not-comparable rule) AND the receipt survives json.dumps for
    # envelope persistence (bounded repr excerpt, never a raise).
    cd, gary = _matched_pair()
    gary["directive_digest"] = object()
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] in {"ok", "expected-ordering-gap", "divergence"}
    dumped = json.dumps(receipt)  # must not raise
    assert "unserializable" in dumped


def test_p4_crash_path_detail_carries_best_effort_digests() -> None:
    # Crash path (digest computation raises on an unserializable resolver
    # output): the fallback detail carries best-effort digests alongside
    # comparator_error, and the receipt still json.dumps cleanly.
    cd = _cd_block(
        resolved={"A": RES_A},
        bound_guides=[{"name": "guide-x", "ssot_digest": "ssot-1"}],
    )
    gary = _gary_view(picks={"A": "guide-x"}, resolved_base={"A": {"bad": object()}})
    receipt = compare_styleguide_resolution(cd, gary)
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "contract-violation"
    detail = receipt["detail"]
    assert "comparator_error" in detail
    assert detail["cd_resolution_digest"] == cd["resolution_digest"]
    assert detail["cd_directive_digest"] == "d-1"
    assert detail["gary_directive_digest"] == "d-1"
    assert detail["trial_start_directive_digest"] == "d-1"
    json.dumps(receipt)  # must not raise


# --- totality (never raises) ----------------------------------------------------


@pytest.mark.parametrize(
    ("cd_block", "gary_view"),
    [
        (42, None),
        ("not-a-dict", {"picks": "not-a-dict"}),
        (_cd_block(), {"resolved_base": object()}),  # unserializable view
        ({"schema_version": "one"}, _gary_view()),
        (_cd_block(bound_guides="not-a-list"), _gary_view(picks={"A": "g"})),
    ],
)
def test_comparator_is_total_never_raises(cd_block: Any, gary_view: Any) -> None:
    receipt = compare_styleguide_resolution(cd_block, gary_view)
    assert set(receipt) == RECEIPT_KEYS
    assert receipt["outcome"] in {"ok", "expected-ordering-gap", "divergence"}


# --- AC-2: clock_eligible truth table --------------------------------------------


@pytest.mark.parametrize(
    ("cd_block", "gary_view", "expected_outcome", "expected_reason", "expected_clock"),
    [
        (*_matched_pair(), "ok", "match", True),
        (
            _cd_block(status="no_picks_at_authoring", resolved={"A": RES_A}),
            _gary_view(),
            "ok",
            "status-keyed-no-picks",
            False,
        ),
        (
            _cd_block(status="no_picks_at_authoring", resolved={"A": RES_A}),
            _gary_view(picks={"A": "g"}, resolved_base={"A": RES_A}),
            "expected-ordering-gap",
            "cd-saw-no-picks",
            False,
        ),
        (
            _cd_block(resolved={"A": RES_A}, directive_digest="d-OLD"),
            _gary_view(picks={"A": "g"}, resolved_base={"A": RES_A}),
            "expected-ordering-gap",
            "directive-drift",
            False,
        ),
        (None, _gary_view(), "expected-ordering-gap", "cd-envelope-absent-legacy", False),
        (
            _cd_block(schema_version=2),
            _gary_view(),
            "expected-ordering-gap",
            "cd-schema-newer",
            False,
        ),
        (
            _cd_block(resolved={"A": RES_A}, bound_guides=[{"name": "g", "ssot_digest": "s"}]),
            _gary_view(picks={"A": "g"}, resolved_base={"A": RES_A_OTHER}, ssot_digest="s"),
            "divergence",
            "resolution-mismatch",
            False,
        ),
        (
            _cd_block(status="unresolvable_pick"),
            _gary_view(picks={"A": "g"}, resolved_base={"A": RES_A}),
            "divergence",
            "cd-unresolvable-but-gary-resolved",
            False,
        ),
        (
            {k: v for k, v in _cd_block().items() if k != "errors"},
            _gary_view(),
            "divergence",
            "contract-violation",
            False,
        ),
    ],
)
def test_clock_eligible_true_only_on_resolved_match(
    cd_block: Any,
    gary_view: dict[str, Any],
    expected_outcome: str,
    expected_reason: str,
    expected_clock: bool,
) -> None:
    receipt = compare_styleguide_resolution(cd_block, gary_view)
    assert receipt["outcome"] == expected_outcome
    assert receipt["reason"] == expected_reason
    assert receipt["clock_eligible"] is expected_clock
    if receipt["clock_eligible"]:
        # F-702: eligibility REQUIRES CD status ``resolved`` AND outcome ok/match.
        assert receipt["cd_status"] == "resolved"
        assert (receipt["outcome"], receipt["reason"]) == ("ok", "match")

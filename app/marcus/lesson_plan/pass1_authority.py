"""Canonical durable-identity receipt for Irene Pass-1 lesson plans.

The production envelope retains one Irene contribution per manifest node.  This
module turns that existing history into a small, digest-bound receipt so later
Pass-1 refinements can reject reuse of an identity that disappeared from an
intermediate plan.  It is deliberately pure: validation never repairs or
mutates a plan.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from app.marcus.lesson_plan.pass1_source_span_catalog import (
    Pass1SourceSpanCatalogError,
    build_pass1_source_span_catalog,
)
from app.marcus.lesson_plan.slide_authority import (
    SlideAuthorityInvalidError,
    resolve_exact_anchor_source,
)
from app.models.pass1_source_section import Pass1AuthenticatedSourceSection

LEGACY_SCHEMA_VERSION = "pass1-plan-authority.v1"
SCHEMA_VERSION = "pass1-plan-authority.v2"
_SPAN_ID = re.compile(r"^span:sha256:[0-9a-f]{64}$")
_SOURCE_ID = re.compile(
    r"^slides/slide-[1-9][0-9]*-[^/]+\.md\|sha256:[0-9a-f]{64}$"
)


class Pass1PlanAuthorityError(ValueError):
    """The candidate plan or its cumulative authority receipt is invalid."""


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Pass1PlanAuthorityError("Pass-1 authority is not canonical JSON") from exc


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 71
        and value.startswith("sha256:")
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def plan_digest(plan: dict[str, Any]) -> str:
    """Digest the exact candidate plan without coercion."""
    return _digest(plan)


def _plan_units(plan: object) -> list[dict[str, Any]]:
    units = plan.get("plan_units") if isinstance(plan, dict) else None
    if not isinstance(units, list) or not all(isinstance(unit, dict) for unit in units):
        raise Pass1PlanAuthorityError("Pass-1 plan_units must be a list of objects")
    return units


def assert_unique_plan_unit_ids(plan: object) -> None:
    """Reject blank/duplicate IDs before normalization can conceal ambiguity."""
    seen: set[str] = set()
    for unit in _plan_units(plan):
        unit_id = unit.get("unit_id")
        if (
            not isinstance(unit_id, str)
            or not unit_id
            or unit_id != unit_id.strip()
            or unit_id in seen
        ):
            raise Pass1PlanAuthorityError(
                "Pass-1 plan carries a blank or duplicate unit_id"
            )
        seen.add(unit_id)


def _is_in_scope(unit: dict[str, Any]) -> bool:
    decision = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    if decision not in {"in-scope", "out-of-scope"}:
        raise Pass1PlanAuthorityError(
            "plan unit scope_decision must resolve to in-scope or out-of-scope"
        )
    return decision == "in-scope"


def _plan_authority_version(plan: dict[str, Any]) -> str:
    units = _plan_units(plan)
    catalog_digest = plan.get("source_span_catalog_digest")
    carries_ids = ["source_ref_ids" in unit for unit in units]
    if catalog_digest is None and not any(carries_ids):
        return LEGACY_SCHEMA_VERSION
    if not _is_sha256(catalog_digest):
        raise Pass1PlanAuthorityError(
            "Pass-1 projected plan catalog digest is invalid"
        )
    if not all(carries_ids):
        raise Pass1PlanAuthorityError(
            "Pass-1 projected plan must carry source_ref_ids for every unit"
        )
    return SCHEMA_VERSION


def _identity_row(
    unit: dict[str, Any], *, source_id: str | None, active: bool, schema_version: str
) -> dict[str, Any]:
    raw_refs = unit.get("source_refs")
    if raw_refs is None:
        raw_refs = []
    if not isinstance(raw_refs, list) or not all(isinstance(ref, str) for ref in raw_refs):
        raise Pass1PlanAuthorityError(
            f"unit {unit.get('unit_id', '')} source_refs must be an ordered string list"
        )
    row = {
        "unit_id": unit["unit_id"],
        "cluster_role": unit.get("cluster_role"),
        "parent_slide_id": unit.get("parent_slide_id"),
        "source_refs": list(raw_refs),
        "source_id": source_id,
        "active": active,
    }
    if schema_version == SCHEMA_VERSION:
        raw_ids = unit.get("source_ref_ids")
        if not isinstance(raw_ids, list) or not all(
            isinstance(span_id, str) and _SPAN_ID.fullmatch(span_id)
            for span_id in raw_ids
        ):
            raise Pass1PlanAuthorityError(
                f"unit {unit.get('unit_id', '')} source_ref_ids must be an ordered stable-ID list"
            )
        if len(raw_ids) != len(set(raw_ids)):
            raise Pass1PlanAuthorityError(
                f"unit {unit.get('unit_id', '')} source_ref_ids must not repeat"
            )
        if len(raw_ids) > 6:
            raise Pass1PlanAuthorityError(
                f"unit {unit.get('unit_id', '')} must select no more than six source spans"
            )
        row["source_ref_ids"] = list(raw_ids)
    return row


def _row_identity(row: dict[str, Any]) -> tuple[object, ...]:
    refs = row.get("source_refs")
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt has invalid source_refs")
    identity: tuple[object, ...] = (
        row.get("cluster_role"),
        row.get("parent_slide_id"),
        tuple(refs),
        row.get("source_id"),
    )
    if "source_ref_ids" in row:
        raw_ids = row.get("source_ref_ids")
        if not isinstance(raw_ids, list) or not all(
            isinstance(span_id, str) and _SPAN_ID.fullmatch(span_id)
            for span_id in raw_ids
        ):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt has invalid source_ref_ids"
            )
        if len(raw_ids) != len(set(raw_ids)):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt has duplicate source_ref_ids"
            )
        if len(raw_ids) > 6:
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt selects more than six source spans"
            )
        identity = (*identity, tuple(raw_ids))
    return identity


def _validate_cluster_authority(units: list[dict[str, Any]]) -> None:
    by_id = {str(unit["unit_id"]): unit for unit in units}
    positions = {str(unit["unit_id"]): index for index, unit in enumerate(units)}
    for unit in units:
        unit_id = str(unit["unit_id"])
        role = unit.get("cluster_role")
        parent = unit.get("parent_slide_id")
        if role == "head":
            if parent is not None:
                raise Pass1PlanAuthorityError(
                    f"head unit {unit_id} must not carry parent_slide_id"
                )
            continue
        if role != "interstitial":
            raise Pass1PlanAuthorityError(
                f"unit {unit_id} has invalid cluster_role authority"
            )
        if (
            not isinstance(parent, str)
            or not parent
            or parent == unit_id
            or parent not in by_id
            or by_id[parent].get("cluster_role") != "head"
            or positions[parent] >= positions[unit_id]
        ):
            raise Pass1PlanAuthorityError(
                f"interstitial unit {unit_id} has invalid parent authority"
            )
        if unit.get("cluster_id") != by_id[parent].get("cluster_id"):
            raise Pass1PlanAuthorityError(
                f"interstitial unit {unit_id} cluster disagrees with parent"
            )


def _validate_v2_projection(
    plan: dict[str, Any],
    *,
    source_sections: tuple[Pass1AuthenticatedSourceSection, ...],
) -> None:
    """Independently rejoin selected IDs to the exact projected source bytes."""
    try:
        catalog = build_pass1_source_span_catalog(source_sections)
    except Pass1SourceSpanCatalogError as exc:
        raise Pass1PlanAuthorityError(str(exc)) from exc
    if plan.get("source_span_catalog_digest") != catalog.catalog_digest:
        raise Pass1PlanAuthorityError(
            "Pass-1 projected plan catalog digest does not bind source sections"
        )
    by_id = {entry.span_id: entry for entry in catalog.entries}
    for unit in _plan_units(plan):
        unit_id = str(unit["unit_id"])
        raw_ids = unit.get("source_ref_ids")
        raw_refs = unit.get("source_refs")
        if not isinstance(raw_ids, list) or not isinstance(raw_refs, list):
            raise Pass1PlanAuthorityError(
                f"unit {unit_id} has invalid v2 source authority projection"
            )
        if not _is_in_scope(unit):
            if raw_ids or raw_refs:
                raise Pass1PlanAuthorityError(
                    f"out-of-scope unit {unit_id} carries source authority"
                )
            continue
        if not 1 <= len(raw_ids) <= 6:
            raise Pass1PlanAuthorityError(
                f"in-scope unit {unit_id} must select one to six source span IDs"
            )
        try:
            selected = [by_id[span_id] for span_id in raw_ids]
        except (KeyError, TypeError) as exc:
            raise Pass1PlanAuthorityError(
                f"unit {unit_id} selected an unknown or stale source span ID"
            ) from exc
        if [entry.text for entry in selected] != raw_refs:
            raise Pass1PlanAuthorityError(
                f"unit {unit_id} selected IDs disagree with projected source bytes"
            )
        if len({entry.source_id for entry in selected}) != 1:
            raise Pass1PlanAuthorityError(
                f"unit {unit_id} selected IDs cross source authority"
            )


def _validate_v2_receipt_catalog_history(
    receipt: dict[str, Any],
    *,
    source_sections: tuple[Pass1AuthenticatedSourceSection, ...],
) -> None:
    """Rejoin active and retired receipt history to the authenticated catalog."""
    try:
        catalog = build_pass1_source_span_catalog(source_sections)
    except Pass1SourceSpanCatalogError as exc:
        raise Pass1PlanAuthorityError(str(exc)) from exc
    if receipt.get("catalog_digest") != catalog.catalog_digest:
        raise Pass1PlanAuthorityError(
            "Pass-1 authority history catalog digest does not bind source sections"
        )
    by_id = {entry.span_id: entry for entry in catalog.entries}
    for row in receipt["identities"]:
        ids = row["source_ref_ids"]
        refs = row["source_refs"]
        if not ids:
            continue
        try:
            selected = [by_id[span_id] for span_id in ids]
        except KeyError as exc:
            raise Pass1PlanAuthorityError(
                f"authority history unit {row['unit_id']} carries an unknown source span ID"
            ) from exc
        if [entry.text for entry in selected] != refs:
            raise Pass1PlanAuthorityError(
                f"authority history unit {row['unit_id']} IDs disagree with source bytes"
            )
        source_ids = {entry.source_id for entry in selected}
        if source_ids != {row["source_id"]}:
            raise Pass1PlanAuthorityError(
                f"authority history unit {row['unit_id']} IDs disagree with source identity"
            )


def validate_receipt(receipt: object) -> dict[str, Any]:
    """Recursively validate and digest-check a serialized authority receipt."""
    if not isinstance(receipt, dict):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt shape is invalid")
    schema_version = receipt.get("schema_version")
    if schema_version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
        raise Pass1PlanAuthorityError("Pass-1 authority receipt version is invalid")
    expected_keys = {
        "schema_version",
        "plan_digest",
        "identities",
        "authority_digest",
    }
    if schema_version == SCHEMA_VERSION:
        expected_keys.add("catalog_digest")
    if set(receipt) != expected_keys:
        raise Pass1PlanAuthorityError("Pass-1 authority receipt shape is invalid")
    digest_value = receipt.get("plan_digest")
    if not _is_sha256(digest_value):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt plan digest is invalid")
    identities = receipt.get("identities")
    if not isinstance(identities, list):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt identities are invalid")
    if schema_version == SCHEMA_VERSION and not _is_sha256(
        receipt.get("catalog_digest")
    ):
        raise Pass1PlanAuthorityError(
            "Pass-1 authority receipt catalog digest is invalid"
        )
    seen: set[str] = set()
    for row in identities:
        expected_row_keys = {
            "unit_id",
            "cluster_role",
            "parent_slide_id",
            "source_refs",
            "source_id",
            "active",
        }
        if schema_version == SCHEMA_VERSION:
            expected_row_keys.add("source_ref_ids")
        if not isinstance(row, dict) or set(row) != expected_row_keys:
            raise Pass1PlanAuthorityError("Pass-1 authority receipt row is invalid")
        unit_id = row.get("unit_id")
        if (
            not isinstance(unit_id, str)
            or not unit_id
            or unit_id != unit_id.strip()
            or unit_id in seen
        ):
            raise Pass1PlanAuthorityError("Pass-1 authority receipt IDs are invalid")
        if not isinstance(row.get("active"), bool):
            raise Pass1PlanAuthorityError("Pass-1 authority receipt status is invalid")
        row_identity = _row_identity(row)
        role = row.get("cluster_role")
        parent = row.get("parent_slide_id")
        if role not in {"head", "interstitial"}:
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt cluster role is invalid"
            )
        if role == "head" and parent is not None:
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt head must not carry parent authority"
            )
        if role == "interstitial" and (
            not isinstance(parent, str) or not parent or parent == unit_id
        ):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt interstitial parent is invalid"
            )
        source_id = row.get("source_id")
        if source_id is not None and (
            not isinstance(source_id, str)
            or not source_id
            or (
                schema_version == SCHEMA_VERSION
                and _SOURCE_ID.fullmatch(source_id) is None
            )
        ):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt source identity is invalid"
            )
        source_refs = row_identity[2]
        if bool(source_refs) != (source_id is not None):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt source references disagree with source identity"
            )
        if schema_version == SCHEMA_VERSION:
            source_ref_ids = row_identity[-1]
            if len(source_ref_ids) != len(source_refs):
                raise Pass1PlanAuthorityError(
                    "Pass-1 authority receipt projected source references are misaligned"
                )
        seen.add(unit_id)
    row_by_id = {row["unit_id"]: row for row in identities}
    positions = {row["unit_id"]: index for index, row in enumerate(identities)}
    for row in identities:
        if row["cluster_role"] != "interstitial":
            continue
        parent = row["parent_slide_id"]
        parent_row = row_by_id.get(parent)
        if (
            parent_row is None
            or parent_row["cluster_role"] != "head"
            or positions[parent] >= positions[row["unit_id"]]
            or parent_row["source_id"] != row["source_id"]
        ):
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt interstitial parent authority is invalid"
            )
        if row["active"] and not parent_row["active"]:
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt active interstitial parent is retired"
            )
    retired_seen = False
    for row in identities:
        if not row["active"]:
            retired_seen = True
        elif retired_seen:
            raise Pass1PlanAuthorityError(
                "Pass-1 authority receipt active identity follows retired history"
            )
    body = {key: receipt[key] for key in receipt if key != "authority_digest"}
    if receipt.get("authority_digest") != _digest(body):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt digest mismatch")
    return json.loads(_canonical_bytes(receipt))


def finalize_plan_authority(
    plan: dict[str, Any],
    *,
    source_sections: (
        tuple[Pass1AuthenticatedSourceSection, ...]
        | tuple[tuple[str, str], ...]
    ),
    prior_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a candidate and return its cumulative immutable-ID receipt."""
    assert_unique_plan_unit_ids(plan)
    units = _plan_units(plan)
    schema_version = _plan_authority_version(plan)
    _validate_cluster_authority(units)
    if schema_version == SCHEMA_VERSION:
        _validate_v2_projection(plan, source_sections=source_sections)
    prior = validate_receipt(prior_receipt) if prior_receipt is not None else None
    if prior is not None and prior["schema_version"] != schema_version:
        if prior["schema_version"] == LEGACY_SCHEMA_VERSION:
            raise Pass1PlanAuthorityError(
                "legacy-v1 Pass-1 authority is read-only and cannot be silently upgraded"
            )
        raise Pass1PlanAuthorityError(
            "Pass-1 authority receipt version does not match candidate plan"
        )
    if (
        prior is not None
        and schema_version == SCHEMA_VERSION
        and prior["catalog_digest"] != plan["source_span_catalog_digest"]
    ):
        raise Pass1PlanAuthorityError(
            "Pass-1 source-span catalog identity changed during refinement"
        )
    if prior is not None and schema_version == SCHEMA_VERSION:
        _validate_v2_receipt_catalog_history(
            prior, source_sections=source_sections
        )
    prior_by_id = {
        row["unit_id"]: row for row in (prior.get("identities", []) if prior else [])
    }
    current_rows: list[dict[str, Any]] = []
    current_ids: set[str] = set()
    source_texts: tuple[tuple[str, str], ...]
    if all(
        isinstance(section, Pass1AuthenticatedSourceSection)
        for section in source_sections
    ):
        source_texts = tuple(
            (section.source_id, section.body) for section in source_sections
        )
    elif schema_version == LEGACY_SCHEMA_VERSION and all(
        isinstance(section, tuple)
        and len(section) == 2
        and all(isinstance(value, str) for value in section)
        for section in source_sections
    ):
        source_texts = source_sections
    else:
        raise Pass1PlanAuthorityError(
            "current Pass-1 authority requires authenticated source-section records"
        )
    for unit in units:
        unit_id = str(unit["unit_id"])
        current_ids.add(unit_id)
        source_id: str | None = None
        if _is_in_scope(unit):
            if not source_sections:
                raise Pass1PlanAuthorityError(
                    f"unit {unit_id} has no declared source-slide inventory"
                )
            try:
                source_id, _anchors = resolve_exact_anchor_source(
                    unit_id=unit_id,
                    raw_anchors=unit.get("source_refs"),
                    source_texts=source_texts,
                )
            except SlideAuthorityInvalidError as exc:
                raise Pass1PlanAuthorityError(str(exc)) from exc
        row = _identity_row(
            unit,
            source_id=source_id,
            active=True,
            schema_version=schema_version,
        )
        previous = prior_by_id.get(unit_id)
        if previous is not None:
            if previous["active"] is False:
                raise Pass1PlanAuthorityError(
                    f"retired unit_id {unit_id} cannot be restored"
                )
            if _row_identity(previous) != _row_identity(row):
                raise Pass1PlanAuthorityError(
                    f"unit_id {unit_id} was recycled for different source/role authority"
                )
        current_rows.append(row)

    current_row_by_id = {row["unit_id"]: row for row in current_rows}
    for unit in units:
        if unit.get("cluster_role") != "interstitial":
            continue
        unit_id = str(unit["unit_id"])
        parent_id = str(unit["parent_slide_id"])
        if (
            current_row_by_id[unit_id]["source_id"]
            != current_row_by_id[parent_id]["source_id"]
        ):
            raise Pass1PlanAuthorityError(
                f"interstitial unit {unit_id} source disagrees with parent"
            )

    retired_rows = [
        {**row, "active": False}
        for unit_id, row in prior_by_id.items()
        if unit_id not in current_ids
    ]
    body: dict[str, Any] = {
        "schema_version": schema_version,
        "plan_digest": plan_digest(plan),
        "identities": [*current_rows, *retired_rows],
    }
    if schema_version == SCHEMA_VERSION:
        body["catalog_digest"] = plan["source_span_catalog_digest"]
    return {**body, "authority_digest": _digest(body)}


def assert_receipt_matches_plan(plan: dict[str, Any], receipt: object) -> None:
    """Fail if a persisted current-format receipt does not bind this plan."""
    validated = validate_receipt(receipt)
    schema_version = _plan_authority_version(plan)
    if validated["schema_version"] != schema_version:
        if validated["schema_version"] == LEGACY_SCHEMA_VERSION:
            raise Pass1PlanAuthorityError(
                "legacy-v1 Pass-1 authority is read-only and cannot bind a projected v2 plan"
            )
        raise Pass1PlanAuthorityError(
            "Pass-1 authority receipt version does not match lesson plan"
        )
    if (
        schema_version == SCHEMA_VERSION
        and validated["catalog_digest"] != plan["source_span_catalog_digest"]
    ):
        raise Pass1PlanAuthorityError(
            "Pass-1 authority receipt catalog digest disagrees with lesson plan"
        )
    if validated["plan_digest"] != plan_digest(plan):
        raise Pass1PlanAuthorityError("Pass-1 authority receipt does not bind lesson plan")
    plan_units = _plan_units(plan)
    assert_unique_plan_unit_ids(plan)
    _validate_cluster_authority(plan_units)
    active_rows = [row for row in validated["identities"] if row["active"]]
    active_ids = [row["unit_id"] for row in active_rows]
    plan_ids = [unit["unit_id"] for unit in plan_units]
    if active_ids != plan_ids:
        raise Pass1PlanAuthorityError(
            "Pass-1 authority receipt is not the ordered active plan projection"
        )
    for unit, row in zip(plan_units, active_rows, strict=True):
        expected_identity = _identity_row(
            unit,
            source_id=row.get("source_id"),
            active=True,
            schema_version=schema_version,
        )
        if _row_identity(row) != _row_identity(expected_identity):
            raise Pass1PlanAuthorityError(
                f"Pass-1 authority receipt identity disagrees with unit {unit['unit_id']}"
            )
        in_scope = _is_in_scope(unit)
        source_id = row.get("source_id")
        if in_scope and (not isinstance(source_id, str) or not source_id):
            raise Pass1PlanAuthorityError(
                f"in-scope unit {unit['unit_id']} has no exact source authority"
            )
        if not in_scope and source_id is not None:
            raise Pass1PlanAuthorityError(
                f"out-of-scope unit {unit['unit_id']} carries source authority"
            )


__all__ = [
    "LEGACY_SCHEMA_VERSION",
    "SCHEMA_VERSION",
    "Pass1PlanAuthorityError",
    "assert_receipt_matches_plan",
    "assert_unique_plan_unit_ids",
    "finalize_plan_authority",
    "plan_digest",
    "validate_receipt",
]

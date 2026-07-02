"""Gamma live-doc audit driver — Leg-E AC#4/#5 (`gamma-doc-audit`).

Compares the DOCUMENTED tier (live developers.gamma.app markdown, fetched
through the Texas `gamma_docs` retrieval adapter) against code-authoritative
frozen enums (`app/specialists/gary/_act.py`, resolved via dotted `code_ref`
pointers — never literals) and doc-fact expectations, classifies every audit
item into EXACTLY ONE of three terminal states, and files the learned-store
observations ledger's first real writes (candidate-only, digest-idempotent).

Binding rules implemented here (green-light party record, S-1..S-4):

* **Reachability (D-2 / M-3):** the adapter is resolved THROUGH
  `provider_directory` dispatch (`RetrievalIntent` + `retrieval.dispatch`) —
  never direct instantiation. This module is the SOLE writer of
  `GAMMA_LEARNED_OBSERVATIONS_PATH`.
* **Classification (S-2):** transport failure -> indeterminate; anchor present
  but comparison fails -> drift-detected; anchor/section ABSENT ->
  drift-detected `kind: doc-restructure` (LOUD, non-zero exit, run-report only,
  NO ledger write); ambiguous multi-match or `known_losses` implicating the
  fact -> indeterminate (can never mint confirmed, Texas T-7).
* **Enum asymmetry (A-2):** enum-value-absent-from-docs -> `doc-drift`;
  documented-value-absent-from-enum -> `coverage-gap` (distinct kinds).
* **Writes (S-1):** drift-detected always writes; confirmed writes ONLY when it
  resolves/updates a STANDING candidate (citing its observation_id);
  indeterminate / doc-restructure never write. Dan's wording-triple is a FILING
  GATE: the driver rejects-and-reports candidates missing any leg of
  DOCUMENTED / OBSERVED / CONSEQUENCE (+ doc URL).
* **Exit tiers (S-3, as amended by review amendment P6):** REAL items alone
  drive tiers — `probe` participates ONLY via the integrity check and
  `findings_only` items are report-only. 0 = ran, all real items confirmed;
  10 = real drift detected (loud + scriptable, NOT a failure semantic);
  20 = VOID (pre-flight probe failed, real items indeterminate without a
  certified verdict, zero real items, or integrity failure — e.g. the labeled
  probe classifying `confirmed`). A VOID run writes NOTHING: the exit tier is
  computed BEFORE the write phase; ledger writes and the doc-sources stamp are
  both gated on a non-VOID, non-dry run (review P1/P3).
* **Unavailability (M-11 / W-5):** pre-flight `llms.txt` probe -> VOID before
  any item runs; mid-run fetch failure -> indeterminate; ZERO retries.

sys.path bootstrap precedent: `validate_gamma_style_guides.py:28-48`.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Allow direct CLI invocation by ensuring the repo root AND the Texas retrieval
# package root are importable before the imports below.
_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (_REPO_ROOT, _REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import yaml  # noqa: E402
from retrieval import ProviderHint, RetrievalIntent, dispatch  # noqa: E402
from retrieval.gamma_docs_provider import canonical_doc_url  # noqa: E402

from app.specialists.gary.learned_dependencies import (  # noqa: E402
    GAMMA_LEARNED_OBSERVATIONS_PATH,
    append_observation,
    read_observations,
)

# --- Constants (pinned by tests) ---------------------------------------------- #

EXIT_OK = 0
"""Ran; every REAL item confirmed (probe/findings-only excluded — P6)."""
EXIT_DRIFT = 10
"""Ran; REAL drift detected (the audit WORKING, not a failure semantic — S-3)."""
EXIT_VOID = 20
"""VOID: pre-flight failed / uncertified (indeterminates) / integrity failure.
A VOID run writes NOTHING (no ledger rows, no doc-sources stamp) — P1."""

PREFLIGHT_URL = "https://developers.gamma.app/llms.txt"

DEFAULT_MANIFEST_PATH = (
    _REPO_ROOT / "skills" / "gamma-api-mastery" / "references"
    / "gamma-doc-audit-manifest.yaml"
)
DEFAULT_DOC_SOURCES_PATH = (
    _REPO_ROOT / "skills" / "gamma-api-mastery" / "references" / "doc-sources.yaml"
)
DEFAULT_LEDGER_PATH = GAMMA_LEARNED_OBSERVATIONS_PATH
"""The REAL SSOT — tests always override with tmp_path ledgers (AC#6)."""

SOURCE_COMPONENT = "scripts/utilities/audit_gamma_docs.py"

TERMINAL_STATES = ("confirmed", "drift-detected", "indeterminate")

_ITEM_KINDS = frozenset({"enum-parity", "doc-fact", "probe"})
_COMPARATORS = frozenset({"enum-membership", "literal-presence", "numeric"})
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_ITEM_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
_CODE_REF_RE = re.compile(r"[\w.]+:[A-Za-z_]\w*")


class ManifestError(ValueError):
    """Malformed audit manifest (fail-loud at load, before any fetch)."""


# --- Manifest ------------------------------------------------------------------ #


def load_audit_manifest(path: str | Path) -> list[dict[str, Any]]:
    """Load + validate the committed audit manifest. Returns the item list."""
    return _validate_manifest_items(_read_manifest_payload(path))


def _read_manifest_payload(path: str | Path) -> dict[str, Any]:
    """Read + parse the manifest ONCE (N8: run_audit reuses this payload)."""
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise ManifestError(f"audit manifest not found: {manifest_path}")
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ManifestError("audit manifest must be a mapping")
    return payload


def _validate_manifest_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate the parsed manifest payload. Returns the item list."""
    derived_from = str(payload.get("derived_from") or "")
    if "doc-sources.yaml" not in derived_from:
        raise ManifestError(
            "manifest must cite doc-sources.yaml via `derived_from` (S-4 / A-7)"
        )
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise ManifestError("manifest `items` must be a non-empty list")
    seen_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ManifestError(f"manifest item must be a mapping; got {item!r}")
        item_id = str(item.get("item_id") or "")
        if not _ITEM_ID_RE.fullmatch(item_id):
            raise ManifestError(f"bad item_id {item_id!r} (lowercase kebab-case)")
        if item_id in seen_ids:
            raise ManifestError(f"duplicate item_id {item_id!r}")
        seen_ids.add(item_id)
        kind = item.get("kind")
        if kind not in _ITEM_KINDS:
            raise ManifestError(f"{item_id}: kind must be one of {sorted(_ITEM_KINDS)}")
        if item.get("comparator") not in _COMPARATORS:
            raise ManifestError(
                f"{item_id}: comparator must be one of {sorted(_COMPARATORS)}"
            )
        doc_url = str(item.get("doc_url") or "")
        if not doc_url.startswith("https://developers.gamma.app/"):
            raise ManifestError(f"{item_id}: doc_url must be a developers.gamma.app URL")
        if kind == "enum-parity":
            code_ref = str(item.get("code_ref") or "")
            if not _CODE_REF_RE.fullmatch(code_ref):
                raise ManifestError(
                    f"{item_id}: enum-parity requires a dotted code_ref "
                    f"'module.path:ATTR' (W-3 pointer table); got {code_ref!r}"
                )
            if "expected_documented" in item:
                raise ManifestError(
                    f"{item_id}: enum-parity items must not carry value literals "
                    f"(no second SSOT)"
                )
        else:
            if "expected_documented" not in item:
                raise ManifestError(
                    f"{item_id}: {kind} items require `expected_documented`"
                )
            expected = item["expected_documented"]
            # P2 (review): None / empty / whitespace-only expectations are
            # manifest DEFECTS — an empty literal is vacuously "present" and
            # would mint confirmed for free. Fail loud at load.
            if expected is None or not str(expected).strip():
                raise ManifestError(
                    f"{item_id}: `expected_documented` must be a non-empty, "
                    f"non-whitespace value; got {expected!r} (P2)"
                )
        extraction = item.get("extraction")
        if extraction is not None and not isinstance(extraction, dict):
            raise ManifestError(f"{item_id}: extraction must be a mapping")
        item.setdefault("extraction", {})
    return items


def resolve_code_ref(code_ref: str) -> frozenset | set:
    """Resolve `module.path:ATTR` to the live frozenset (no third enum copy, A-1)."""
    module_name, _, attr = str(code_ref).partition(":")
    if not module_name or not attr:
        raise ValueError(f"code_ref must be 'module.path:ATTR'; got {code_ref!r}")
    module = importlib.import_module(module_name)
    value = getattr(module, attr)
    if not isinstance(value, (frozenset, set)):
        raise ValueError(
            f"code_ref {code_ref!r} resolved to {type(value).__name__}, not a set"
        )
    return value


# --- Fetch (through provider_directory dispatch — D-2) -------------------------- #


def fetch_page(url: str, *, fetch_interval_s: float = 0.0) -> dict[str, Any]:
    """Fetch ONE doc page through Texas dispatch. Never raises.

    Returns ``{"ok": bool, "row": TexasRow | None, "error": str | None}``.
    ``ok`` requires HTTP 200; anything else (transport failure, dispatch
    failure, non-200) is data for the S-2 `indeterminate` branch. ZERO retries.
    """
    canonical = canonical_doc_url(url)
    if fetch_interval_s > 0:
        time.sleep(fetch_interval_s)
    intent = RetrievalIntent(
        intent=f"gamma live-doc audit fetch: {canonical}",
        provider_hints=[
            ProviderHint(provider="gamma_docs", params={"pages": [canonical]})
        ],
        kind="direct_ref",
        iteration_budget=1,
    )
    try:
        result = dispatch(intent)
    except Exception as exc:  # noqa: BLE001 — W-5: the DRIVER catches per item
        return {"ok": False, "row": None, "error": f"{type(exc).__name__}: {exc}"}
    rows = getattr(result, "rows", None) or []
    row = rows[0] if rows else None
    if row is None:
        return {"ok": False, "row": None, "error": "dispatch returned no rows"}
    meta = (row.provider_metadata or {}).get("gamma_docs") or {}
    status = meta.get("http_status")
    if status != 200:
        return {"ok": False, "row": row, "error": f"HTTP {status}"}
    return {"ok": True, "row": row, "error": None}


# --- Extraction ------------------------------------------------------------------ #


def extract_scope(text: str, extraction: dict[str, Any]) -> tuple[str, str | None]:
    """Return ``(status, scope_text)``.

    status: ``"ok"`` | ``"anchor-absent"`` | ``"ambiguous"``. With no declared
    anchor the whole page is the scope (doc-restructure requires a DECLARED
    anchor that vanished — S-2).
    """
    anchor = extraction.get("anchor")
    if not anchor:
        return ("ok", text)
    count = text.count(anchor)
    if count == 0:
        return ("anchor-absent", None)
    if count > 1:
        return ("ambiguous", None)
    start = text.index(anchor)
    tail = text[start:]
    until = extraction.get("until")
    if until:
        cut = tail.find(until, len(anchor))
        if cut != -1:
            tail = tail[:cut]
    return ("ok", tail)


def collect_tokens(scope: str, extraction: dict[str, Any]) -> list[str]:
    """Collect inline-code tokens per the manifest-declared extraction rules."""
    line_pattern = extraction.get("line_pattern")
    line_re = re.compile(line_pattern) if line_pattern else None
    after_colon = bool(extraction.get("after_colon"))
    first_only = bool(extraction.get("first_token_per_line"))
    excluded = {str(t) for t in (extraction.get("exclude_tokens") or [])}
    tokens: list[str] = []
    seen: set[str] = set()
    for line in scope.splitlines():
        if line_re is not None and not line_re.search(line):
            continue
        segment = line.split(":", 1)[1] if (after_colon and ":" in line) else line
        found = _INLINE_CODE_RE.findall(segment)
        if first_only:
            found = found[:1]
        for token in found:
            token = token.strip()
            if not token or token in excluded or token in seen:
                continue
            seen.add(token)
            tokens.append(token)
    return tokens


# --- Classification (S-2, TOTAL per M-5) ------------------------------------------ #


def _receipt(item: dict[str, Any], page: Any) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "doc_url": item.get("doc_url"),
        "final_url": canonical_doc_url(str(item.get("doc_url") or "")),
        "http_status": None,
        "fetched_at": None,
        "content_sha256": None,
        "anchor_sha256": None,
    }
    row = page.get("row") if isinstance(page, dict) else None
    if row is not None:
        meta = (row.provider_metadata or {}).get("gamma_docs") or {}
        # N2: the receipt's final_url is the RESPONSE URL (post-redirect) when
        # the provider recorded one; the requested canonical URL otherwise.
        receipt["final_url"] = (
            meta.get("final_url") or meta.get("doc_url") or receipt["final_url"]
        )
        receipt["http_status"] = meta.get("http_status")
        receipt["fetched_at"] = meta.get("fetched_at")
        receipt["content_sha256"] = meta.get("content_sha256")
    return receipt


def _base_result(item: dict[str, Any], page: Any) -> dict[str, Any]:
    return {
        "item_id": item.get("item_id"),
        "kind": item.get("kind"),
        "probe": item.get("kind") == "probe",
        "findings_only": bool(item.get("findings_only")),
        "standing_candidate": item.get("standing_candidate"),
        "consequence": item.get("consequence"),
        "terminal_state": "indeterminate",
        "drift_kinds": [],
        "diffs": {},
        "reason": "",
        "documented_claim": "",
        "observed": "",
        "receipt": _receipt(item, page),
    }


def classify_item(item: dict[str, Any], page: Any) -> dict[str, Any]:
    """TOTAL classifier: exactly one of the three terminal states, never raises."""
    result = _base_result(item, page)
    try:
        return _classify_inner(item, page, result)
    except Exception as exc:  # noqa: BLE001 — M-5 totality: no exception escape
        result["terminal_state"] = "indeterminate"
        result["reason"] = f"classifier-exception: {type(exc).__name__}: {exc}"
        return result


def _classify_inner(
    item: dict[str, Any], page: Any, result: dict[str, Any]
) -> dict[str, Any]:
    # Transport / dispatch / HTTP failure -> indeterminate (S-2, no write).
    if not isinstance(page, dict) or not page.get("ok") or page.get("row") is None:
        error = page.get("error") if isinstance(page, dict) else "no page result"
        result["reason"] = f"transport/fetch failure: {error}"
        return result
    row = page["row"]
    meta = (row.provider_metadata or {}).get("gamma_docs") or {}
    # T-7 indeterminate floor: known_losses implicating the page can never
    # mint `confirmed`.
    if meta.get("known_losses"):
        result["reason"] = f"known_losses implicate the page: {meta['known_losses']}"
        return result

    extraction = item.get("extraction")
    if not isinstance(extraction, dict):
        result["reason"] = "malformed item: extraction is not a mapping"
        return result

    comparator = item.get("comparator")
    if comparator not in _COMPARATORS:
        result["reason"] = f"malformed item: unknown comparator {comparator!r}"
        return result

    text = row.body
    status, scope = extract_scope(text, extraction)
    if status == "anchor-absent":
        anchor = extraction.get("anchor")
        result["terminal_state"] = "drift-detected"
        result["drift_kinds"] = ["doc-restructure"]
        result["diffs"] = {"doc-restructure": [str(anchor)]}
        result["reason"] = (
            f"declared anchor {anchor!r} absent from the fetched page "
            f"(doc-restructure: run-report only, no ledger write)"
        )
        result["observed"] = f"anchor {anchor!r} not found"
        return result
    if status == "ambiguous":
        result["reason"] = (
            f"ambiguous extraction: anchor {extraction.get('anchor')!r} matches "
            f"more than once (can never mint confirmed — T-7)"
        )
        return result
    assert scope is not None
    result["receipt"]["anchor_sha256"] = (
        "sha256:" + hashlib.sha256(scope.encode("utf-8")).hexdigest()
    )

    if comparator == "literal-presence":
        return _classify_literal(item, scope, result)
    if comparator == "numeric":
        return _classify_numeric(item, extraction, scope, result)
    return _classify_enum(item, extraction, scope, result)


def _classify_literal(
    item: dict[str, Any], scope: str, result: dict[str, Any]
) -> dict[str, Any]:
    expected = str(item.get("expected_documented"))
    # P8 line-anchor convention (documented in the manifest header): an
    # expected literal beginning with "\n" means "at start of a line";
    # prepending "\n" to the haystack makes start-of-page count as a line
    # start, so a heading at byte 0 still matches.
    haystack = ("\n" + scope) if expected.startswith("\n") else scope
    result["documented_claim"] = f"the docs state {expected!r}"
    if expected in haystack:
        result["terminal_state"] = "confirmed"
        result["observed"] = f"literal {expected!r} present in the scoped section"
        result["reason"] = "documented literal present"
    else:
        result["terminal_state"] = "drift-detected"
        result["drift_kinds"] = ["doc-drift"]
        result["diffs"] = {"doc-drift": [expected]}
        result["observed"] = f"literal {expected!r} ABSENT from the scoped section"
        result["reason"] = "documented literal absent"
    return result


def _classify_numeric(
    item: dict[str, Any],
    extraction: dict[str, Any],
    scope: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    pattern = extraction.get("value_pattern")
    if not pattern:
        result["reason"] = "malformed item: numeric comparator without value_pattern"
        return result
    matches = sorted(set(re.findall(pattern, scope)))
    expected = item.get("expected_documented")
    result["documented_claim"] = f"the docs state the value {expected!r}"
    if not matches:
        result["terminal_state"] = "drift-detected"
        result["drift_kinds"] = ["doc-drift"]
        result["diffs"] = {"doc-drift": [f"expected={expected}", "documented=<none>"]}
        result["observed"] = "documented value no longer present"
        result["reason"] = "numeric value not found in scoped section"
        return result
    if len(matches) > 1:
        result["reason"] = (
            f"ambiguous extraction: multiple distinct values {matches} "
            f"(can never mint confirmed — T-7)"
        )
        return result
    documented = matches[0]
    if float(documented) == float(expected):
        result["terminal_state"] = "confirmed"
        result["observed"] = f"documented value {documented} matches expectation"
        result["reason"] = "numeric value matches"
    else:
        result["terminal_state"] = "drift-detected"
        result["drift_kinds"] = ["doc-drift"]
        result["diffs"] = {
            "doc-drift": sorted([f"expected={expected}", f"documented={documented}"])
        }
        result["observed"] = f"documented value {documented} != expected {expected}"
        result["reason"] = "numeric value mismatch"
    return result


def _classify_enum(
    item: dict[str, Any],
    extraction: dict[str, Any],
    scope: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    if not extraction.get("anchor"):
        result["reason"] = "malformed item: enum-membership requires a declared anchor"
        return result
    enum_values = resolve_code_ref(str(item.get("code_ref")))
    tokens = collect_tokens(scope, extraction)
    expectation = extraction.get("expectation", "enumerated")
    result["documented_claim"] = (
        "the scoped doc section enumerates the accepted values"
        if expectation == "enumerated"
        else "the scoped doc section documents a FREE-TEXT surface (no value vocabulary)"
    )
    if expectation == "not-enumerated":
        if tokens:
            result["terminal_state"] = "drift-detected"
            result["drift_kinds"] = ["doc-drift"]
            result["diffs"] = {"doc-drift": sorted(tokens)}
            result["observed"] = (
                f"docs began enumerating a value vocabulary: {sorted(tokens)}"
            )
            result["reason"] = "not-enumerated expectation violated"
            return result
        # P7 (review): an EMPTY token collection is not a positive finding —
        # it is exactly what an extraction miss looks like. Require a positive
        # witness: the scoped section has content beyond the anchor AND, when
        # the manifest declares a witness_pattern, it matches. Else T-7 floor.
        anchor = str(extraction.get("anchor") or "")
        section_body = scope[len(anchor):] if anchor and scope.startswith(anchor) else scope
        if not section_body.strip():
            result["reason"] = (
                "not-enumerated: scoped section is empty beyond the anchor — "
                "no positive witness (can never mint confirmed — T-7 / P7)"
            )
            return result
        witness_pattern = extraction.get("witness_pattern")
        if witness_pattern and not re.search(str(witness_pattern), scope):
            result["reason"] = (
                f"not-enumerated: declared witness_pattern {witness_pattern!r} "
                f"absent from the scoped section — no positive witness "
                f"(can never mint confirmed — T-7 / P7)"
            )
            return result
        result["terminal_state"] = "confirmed"
        result["observed"] = (
            "no enumerated vocabulary documented; positive free-text witness "
            "present (as expected)"
        )
        result["reason"] = "free-text surface confirmed with positive witness"
        return result
    if not tokens:
        result["reason"] = (
            "extraction yielded zero tokens where an enumeration was expected "
            "(extraction-miss; can never mint confirmed — T-7)"
        )
        return result
    token_set = set(tokens)
    missing_from_docs = sorted(enum_values - token_set)
    absent_from_enum = sorted(token_set - enum_values)
    drift_kinds: list[str] = []
    diffs: dict[str, list[str]] = {}
    if missing_from_docs:
        drift_kinds.append("doc-drift")
        diffs["doc-drift"] = missing_from_docs
    if absent_from_enum:
        drift_kinds.append("coverage-gap")
        diffs["coverage-gap"] = absent_from_enum
    if drift_kinds:
        result["terminal_state"] = "drift-detected"
        result["drift_kinds"] = drift_kinds
        result["diffs"] = diffs
        result["observed"] = (
            f"enum {item.get('code_ref')} vs documented tokens: "
            f"enum-values-absent-from-docs={missing_from_docs}; "
            f"documented-values-absent-from-enum={absent_from_enum}"
        )
        result["reason"] = "enum-membership divergence"
    else:
        result["terminal_state"] = "confirmed"
        result["observed"] = (
            f"documented tokens exactly cover enum {item.get('code_ref')}"
        )
        result["reason"] = "enum-membership parity"
    return result


# --- Observations (S-1 mapping + D-2 wording-triple filing gate) ------------------ #


def passes_wording_triple(behavior: Any) -> bool:
    """Dan's wording standard: DOCUMENTED + OBSERVED + CONSEQUENCE + a doc URL."""
    if not isinstance(behavior, str):
        return False
    return (
        "DOCUMENTED:" in behavior
        and "OBSERVED:" in behavior
        and "CONSEQUENCE:" in behavior
        and ("https://" in behavior or "http://" in behavior)
    )


def compute_output_digest(
    item_id: str, anchor_sha256: str, terminal_state: str, diff: list[str]
) -> str:
    """AC#5 recipe as amended by review amendment P10 (ratified): sha256 over
    (item_id, per-item normalized ANCHOR-scope text sha256 [anchor_sha256],
    terminal_state, sorted diff) — canonical JSON. Keyed to the item's OWN
    scoped text (not the whole-page content_sha256) so churn elsewhere on a
    shared page no longer re-files every item; an unchanged-docs re-run is a
    ledger NO-OP."""
    payload = json.dumps(
        {
            "anchor_sha256": anchor_sha256,
            "diff": sorted(diff),
            "item_id": item_id,
            "terminal_state": terminal_state,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _behavior_text(
    result: dict[str, Any], observed_suffix: str, consequence: str
) -> str:
    receipt = result["receipt"]
    return (
        f"DOCUMENTED: {result['documented_claim']} "
        f"({receipt['final_url']}, fetched {receipt['fetched_at']}). "
        f"OBSERVED: {observed_suffix} "
        f"CONSEQUENCE: {consequence}"
    )


def observations_for_result(
    result: dict[str, Any], run_ctx: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Map one classified item to its ledger observations per S-1.

    Returns ``(observations, rejects)``; rejects are wording-triple filing-gate
    failures (reported, never filed).
    """
    observations: list[dict[str, Any]] = []
    rejects: list[dict[str, Any]] = []
    state = result["terminal_state"]

    if result["probe"] or result["findings_only"] or state == "indeterminate":
        return (observations, rejects)

    candidates: list[tuple[str, list[str], str]] = []  # (kind, diff, observed text)
    if state == "drift-detected":
        for kind in result["drift_kinds"]:
            if kind == "doc-restructure":
                continue  # S-2: run-report only; manifest-fix follow-on at close.
            diff = list(result["diffs"].get(kind, []))
            candidates.append((kind, diff, f"{result['observed']} (kind: {kind})."))
    elif state == "confirmed" and result.get("standing_candidate"):
        # P11 wording (docs-still-drifted direction): the docs still carry the
        # documented claim the live-observed candidate contradicts — the
        # candidate STANDS (re-confirmed against live docs). Never worded as
        # "resolved"/"retired"; docs-changed lands as drift with
        # standing_candidate_ref instead.
        candidates.append(
            (
                "standing-candidate-resolution",
                [],
                (
                    f"{result['observed']}. The standing candidate "
                    f"{result['standing_candidate']} (live-observed reality) "
                    f"STANDS — re-confirmed against the live docs, which still "
                    f"carry the documented claim it contradicts."
                ),
            )
        )

    consequence = str(result.get("consequence") or "").strip()
    standing = result.get("standing_candidate")
    known_ids: frozenset[str] = run_ctx.get("ledger_observation_ids") or frozenset()
    for kind, diff, observed_text in candidates:
        # P5: a cited standing candidate MUST exist in the ledger before any
        # observation citing it is filed — a miss is a dangling citation,
        # routed through the reject-and-report channel.
        if standing and standing not in known_ids:
            rejects.append(
                {
                    "item_id": result["item_id"],
                    "kind": kind,
                    "reason": (
                        f"standing-candidate verification: cited "
                        f"observation_id {standing!r} not found in the ledger "
                        f"— dangling citation, rejected not filed (P5)"
                    ),
                }
            )
            continue
        behavior = _behavior_text(result, observed_text, consequence)
        if not consequence or not passes_wording_triple(behavior):
            rejects.append(
                {
                    "item_id": result["item_id"],
                    "kind": kind,
                    "reason": (
                        "wording-triple filing gate: DOCUMENTED/OBSERVED/"
                        "CONSEQUENCE (+doc URL) incomplete — missing operational "
                        "consequence"
                        if not consequence
                        else "wording-triple filing gate: behavior text incomplete"
                    ),
                }
            )
            continue
        slug = result["item_id"] + ("" if kind == "doc-drift" else f"-{kind}")
        if kind == "standing-candidate-resolution":
            slug = result["item_id"] + "-standing-resolution"
        output_digest = compute_output_digest(
            result["item_id"],
            str(result["receipt"].get("anchor_sha256") or ""),
            state,
            diff,
        )
        # P10: an 8-hex digest suffix keeps same-day doc changes from minting
        # duplicate observation_ids.
        digest8 = output_digest.removeprefix("sha256:")[:8]
        observation: dict[str, Any] = {
            "observation_id": f"obs-gamma-{slug}-{run_ctx['date']}-{digest8}",
            "observed_at": run_ctx["observed_at"],
            "output_digest": output_digest,
            "source_component": SOURCE_COMPONENT,
            "behavior": behavior,
            "status": "candidate",
            "birthing_run_ref": run_ctx["birthing_run_ref"],
            "item_id": result["item_id"],
            "kind": kind,
            "terminal_state": state,
            "doc_url": result["receipt"]["final_url"],
            "diff": sorted(diff),
        }
        if result.get("standing_candidate"):
            key = (
                "resolves_observation_id"
                if kind == "standing-candidate-resolution"
                else "standing_candidate_ref"
            )
            observation[key] = result["standing_candidate"]
        observations.append(observation)
    return (observations, rejects)


# --- Exit tiers (S-3) -------------------------------------------------------------- #


def compute_exit_tier(
    results: list[dict[str, Any]],
    *,
    preflight_ok: bool,
    integrity_failure: bool = False,
) -> int:
    """0 all-real-confirmed / 10 real drift / 20 VOID.

    P6 (ratified spec amendment): `probe` and `findings_only` items are
    EXCLUDED from tier aggregation — the labeled probe participates ONLY via
    the integrity check (a probe that CONFIRMS -> integrity_failure -> VOID);
    findings-only items are report-only evidence. Real items alone drive
    tiers: all real confirmed -> 0; any real drift -> 10; any real
    uncertified (indeterminate) without drift -> 20.

    VOID also covers: failed pre-flight, integrity failure, and a run with
    ZERO real items — a run that could not certify every real item must never
    read as "no drift" (W-5).
    """
    if not preflight_ok or integrity_failure:
        return EXIT_VOID
    real = [
        r for r in results if not r.get("probe") and not r.get("findings_only")
    ]
    if not real:
        return EXIT_VOID
    states = [r["terminal_state"] for r in real]
    if any(s == "drift-detected" for s in states):
        return EXIT_DRIFT
    if any(s == "indeterminate" for s in states):
        return EXIT_VOID
    return EXIT_OK


# --- doc-sources stamping (W-3) ----------------------------------------------------- #


def stamp_doc_sources(path: str | Path, timestamp: str) -> None:
    """Update ONLY the `last_refreshed:` line (surgical, format-preserving).

    N6: preserves the file's original line-ending convention (detected from
    the raw bytes), so a CRLF-authored file is not silently rewritten to LF.
    """
    doc_path = Path(path)
    raw = doc_path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    new_text, count = re.subn(
        r"(?m)^last_refreshed:.*$", f'last_refreshed: "{timestamp}"', text, count=1
    )
    if count != 1:
        raise ValueError(f"no last_refreshed line found in {doc_path}")
    with doc_path.open("w", encoding="utf-8", newline=newline) as fh:
        fh.write(new_text)


# --- Ledger helpers ------------------------------------------------------------------ #


def _ledger_stats(ledger_path: Path) -> dict[str, Any]:
    data = ledger_path.read_bytes() if ledger_path.exists() else b""
    lines = len([ln for ln in data.decode("utf-8").splitlines() if ln.strip()])
    return {"lines": lines, "sha256": "sha256:" + hashlib.sha256(data).hexdigest()}


def _ledger_precheck_error(ledger_path: Path) -> str | None:
    """P4 write-phase totality: validate the EXISTING ledger before any write.

    A missing ledger is fine (first write creates it). An unreadable file or
    any line that does not parse as JSON returns an error message — the run
    goes VOID (report written, exit 20) instead of crashing mid-write-loop.
    """
    if not ledger_path.exists():
        return None
    try:
        text = ledger_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"ledger unreadable: {type(exc).__name__}: {exc}"
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            return f"ledger line {line_no} is not valid JSON: {exc}"
    return None


# --- Run ------------------------------------------------------------------------------ #


def run_audit(
    *,
    manifest_path: str | Path,
    ledger_path: str | Path = DEFAULT_LEDGER_PATH,
    evidence_dir: str | Path,
    doc_sources_path: str | Path = DEFAULT_DOC_SOURCES_PATH,
    dry_run: bool = False,
    fetch_interval_s: float = 1.0,
    preflight_url: str | None = None,
) -> int:
    """Full-manifest audit run. Returns the S-3 exit tier; writes the run report."""
    started_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_path = Path(manifest_path)
    ledger_path = Path(ledger_path)
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # N8: read + parse the manifest ONCE; validation reuses the same payload.
    payload = _read_manifest_payload(manifest_path)
    items = _validate_manifest_items(payload)
    probe_url = preflight_url or str(payload.get("preflight_url") or PREFLIGHT_URL)

    report: dict[str, Any] = {
        "driver": SOURCE_COMPONENT,
        "started_at": started_at,
        "manifest_path": str(manifest_path),
        "dry_run": dry_run,
        "preflight": {"url": probe_url, "ok": False, "error": None},
        "items": [],
        "terminal_state_counts": {},
        "integrity_failure": False,
        "ledger": {},
        "exit_tier": EXIT_VOID,
    }

    def _void(reason_key: str | None = None, reason: str | None = None) -> int:
        if reason_key:
            report["ledger"] = {"path": str(ledger_path), reason_key: reason}
        report["exit_tier"] = EXIT_VOID
        report["finished_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_report(evidence_dir, report)
        return EXIT_VOID

    # Pre-flight probe: VOID-before-start if the doc site is down (M-11).
    # N1: a 200 with an EMPTY llms.txt body is NOT a passing pre-flight.
    preflight = fetch_page(probe_url, fetch_interval_s=0.0)
    if preflight["ok"] and not (preflight["row"].body or "").strip():
        preflight = {
            "ok": False,
            "row": preflight["row"],
            "error": "preflight llms.txt returned 200 with an EMPTY body (N1)",
        }
    report["preflight"]["ok"] = bool(preflight["ok"])
    report["preflight"]["error"] = preflight["error"]
    if not preflight["ok"]:
        return _void()

    # P4: pre-validate the EXISTING ledger right after pre-flight — an
    # unparseable ledger goes VOID with a report, never a mid-write traceback.
    precheck_error = _ledger_precheck_error(ledger_path)
    if precheck_error:
        return _void("precheck_error", precheck_error)

    # One fetch per unique page per run (Dev Notes), paced <=1 req/s.
    pages: dict[str, dict[str, Any]] = {}
    for item in items:
        url = canonical_doc_url(str(item["doc_url"]))
        if url not in pages:
            pages[url] = fetch_page(
                url, fetch_interval_s=fetch_interval_s if pages else 0.0
            )

    results = [
        classify_item(item, pages.get(canonical_doc_url(str(item["doc_url"]))))
        for item in items
    ]

    # Integrity: a labeled probe that CONFIRMS means the teeth are broken.
    integrity_failure = any(
        r["probe"] and r["terminal_state"] == "confirmed" for r in results
    )
    report["integrity_failure"] = integrity_failure
    report["items"] = results
    report["terminal_state_counts"] = dict(
        Counter(r["terminal_state"] for r in results)
    )

    # P1: the exit tier (and integrity verdict) is computed BEFORE the write
    # phase — a VOID run (any cause) writes NOTHING: no ledger rows, no
    # doc-sources stamp. The report still records would-have-written rows.
    exit_tier = compute_exit_tier(
        results, preflight_ok=True, integrity_failure=integrity_failure
    )
    void = exit_tier == EXIT_VOID

    run_ctx = {
        "observed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "birthing_run_ref": _relative_evidence_ref(evidence_dir),
        # P5: standing-candidate citations are verified against the ledger
        # AS IT EXISTS BEFORE this run's writes.
        "ledger_observation_ids": frozenset(
            str(obs.get("observation_id") or "")
            for obs in read_observations(ledger_path)
        ),
    }
    all_observations: list[dict[str, Any]] = []
    all_rejects: list[dict[str, Any]] = []
    for result in results:
        observations, rejects = observations_for_result(result, run_ctx)
        all_observations.extend(observations)
        all_rejects.extend(rejects)

    writes_allowed = not dry_run and not void
    before = _ledger_stats(ledger_path)
    written = 0
    noop = 0
    write_phase_error: str | None = None
    if writes_allowed:
        # P4: an unexpected write-phase exception lands report + EXIT_VOID,
        # never a bare traceback / exit 1.
        try:
            for observation in all_observations:
                if append_observation(ledger_path, observation):
                    written += 1
                else:
                    noop += 1
        except Exception as exc:  # noqa: BLE001 — totality at the write phase
            write_phase_error = f"{type(exc).__name__}: {exc}"
    after = _ledger_stats(ledger_path)

    if write_phase_error:
        exit_tier = EXIT_VOID
        void = True

    # P3 stamp gate (subsumed by P1): stamp ONLY on a non-dry, non-VOID run.
    if not dry_run and not void:
        stamp_doc_sources(doc_sources_path, run_ctx["observed_at"])

    report["ledger"] = {
        "path": str(ledger_path),
        "before_lines": before["lines"],
        "after_lines": after["lines"],
        "before_sha256": before["sha256"],
        "after_sha256": after["sha256"],
        "written": written,
        "noop": noop,
        "rejected": all_rejects,
        "precheck_error": None,
        "write_phase_error": write_phase_error,
        "would_write": (
            [obs["observation_id"] for obs in all_observations]
            if not writes_allowed
            else []
        ),
    }
    report["exit_tier"] = exit_tier
    report["finished_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_report(evidence_dir, report)
    return exit_tier


def _relative_evidence_ref(evidence_dir: Path) -> str:
    """Repo-relative posix path (D-3: real evidence-dir birthing_run_ref).

    N9: an out-of-repo evidence dir fails LOUD — birthing_run_ref is
    repo-relative by contract; silently recording an absolute machine-local
    path would poison the ledger's provenance.
    """
    try:
        return evidence_dir.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"evidence_dir {evidence_dir} resolves outside the repo root "
            f"{_REPO_ROOT}; birthing_run_ref must be repo-relative (D-3 / N9)"
        ) from exc


def _md_cell(value: Any) -> str:
    """N5: escape '|' so free-text (anchors, reasons) cannot shred the table."""
    return str(value).replace("|", "\\|")


def _write_report(evidence_dir: Path, report: dict[str, Any]) -> None:
    (evidence_dir / "run-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# gamma-doc-audit run report",
        "",
        f"- driver: `{report['driver']}`",
        f"- started_at: {report['started_at']}",
        f"- dry_run: {report['dry_run']}",
        f"- preflight: {report['preflight']}",
        f"- exit_tier: **{report['exit_tier']}**",
        f"- terminal_state_counts: {report['terminal_state_counts']}",
        "",
        "| item_id | state | kinds | http | reason |",
        "|---|---|---|---|---|",
    ]
    for result in report.get("items", []):
        lines.append(
            f"| {_md_cell(result['item_id'])} | {_md_cell(result['terminal_state'])} | "
            f"{_md_cell(','.join(result['drift_kinds']) or '-')} | "
            f"{_md_cell(result['receipt'].get('http_status'))} | "
            f"{_md_cell(result['reason'][:120])} |"
        )
    ledger = report.get("ledger") or {}
    if ledger:
        lines += [
            "",
            f"- ledger: `{ledger.get('path')}`",
            f"- lines before/after: {ledger.get('before_lines')} -> "
            f"{ledger.get('after_lines')} (written={ledger.get('written')}, "
            f"noop={ledger.get('noop')})",
            f"- sha256 before: {ledger.get('before_sha256')}",
            f"- sha256 after:  {ledger.get('after_sha256')}",
            f"- rejected (wording-triple gate): {ledger.get('rejected')}",
        ]
    (evidence_dir / "run-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


# --- CLI -------------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=DEFAULT_MANIFEST_PATH,
        help="audit manifest YAML (default: the committed Leg-E manifest)",
    )
    parser.add_argument(
        "--ledger-path", type=Path, default=Path(DEFAULT_LEDGER_PATH),
        help="observations ledger JSONL (default: the REAL SSOT; tests override)",
    )
    parser.add_argument(
        "--evidence-dir", type=Path, default=None,
        help="evidence directory (default: _bmad-output/implementation-artifacts/"
        "evidence/leg-e-gamma-docs-audit-<UTC>/)",
    )
    parser.add_argument(
        "--doc-sources-path", type=Path, default=DEFAULT_DOC_SOURCES_PATH,
        help="doc-sources.yaml to stamp last_refreshed on (non-dry runs)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="classify + report WITHOUT writing the ledger or stamping doc-sources",
    )
    parser.add_argument(
        "--fetch-interval", type=float, default=1.0,
        help="seconds between page fetches (politeness; default 1.0)",
    )
    parser.add_argument(
        "--preflight-url", type=str, default=None,
        help="override the llms.txt pre-flight probe URL",
    )
    args = parser.parse_args(argv)

    evidence_dir = args.evidence_dir
    if evidence_dir is None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        evidence_dir = (
            _REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "evidence"
            / f"leg-e-gamma-docs-audit-{stamp}"
        )

    try:
        exit_tier = run_audit(
            manifest_path=args.manifest,
            ledger_path=args.ledger_path,
            evidence_dir=evidence_dir,
            doc_sources_path=args.doc_sources_path,
            dry_run=args.dry_run,
            fetch_interval_s=args.fetch_interval,
            preflight_url=args.preflight_url,
        )
    except ManifestError as exc:
        # N8: a malformed manifest is a loud, scriptable VOID — never a
        # bare traceback out of the CLI.
        print(f"gamma-doc-audit: manifest error (VOID): {exc}", file=sys.stderr)
        return EXIT_VOID
    print(f"gamma-doc-audit exit tier: {exit_tier} (report: {evidence_dir})")
    return exit_tier


if __name__ == "__main__":
    raise SystemExit(main())

"""Runner-integration glue (Step 3 render + Step 4 G3 derive/write — FINALIZED).

The OFFLINE-tested core of the G3 coverage seam. ``_derive_and_write_coverage_receipt``
is the ONE shared helper the production runner calls at BOTH walk sites (start +
continuation), guarded ``gate_id == "G3"``. It:

  1. drops the "past G3 / receipt expected" marker FIRST (so a later derive failure
     still trips the fail-loud gate, never a silent bypass);
  2. loads the AUTHORED coverage annotations from ``g0-enrichment.json``;
  3. marshals the run's OWN deck + narration surfaces into anchors
     (``_marshal_coverage_surfaces``) — deck rows from
     ``exports/gary-dispatch-payload.json`` and narration from
     ``exports/segment-manifest-storyboard-b.yaml`` (the run-dir export SSOT, R5-A7);
  4. DERIVES the receipt (idempotent), WRITES the canonical RAI artifact, and RENDERS
     the standalone ``coverage-report.html`` (Step 3, FORK B → B1).

LINEAGE (MF3): the ``slide_id → source-ordinal`` map is built from the REAL persisted
``slide_briefs`` (``package_builder.output.slides``, carrying ``{slide_id, source_ref}``)
when available — the order-immune SSOT — with positional re-derivation from the
authoritative (locked / count-matched, non-ambiguous) ``plan_units`` as the fallback.
Every unresolved join is recorded as a receipt DIAGNOSTIC (never a crash); the gate
is fail-loud once the receipt-expected marker is dropped (per the keystone), and the
VACUOUS-RECEIPT GUARD (in ``coverage_gate``) refuses a no-clean-join receipt.
"""

from __future__ import annotations

import json
import logging
import re
from html import escape
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from app.gates.section_07c.storyboard_html_emitter import render_coverage_section
from app.marcus.lesson_plan.coverage_annotation import (
    CoverageAnnotation,
    load_coverage_annotation,
)
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution,
    CoverageReceipt,
    derive_coverage_receipt,
)
from app.marcus.orchestrator.coverage_anchors import (
    build_coverage_anchors,
    resolve_slide_key_lineage,
)
from app.marcus.orchestrator.coverage_gate_wiring import (
    coverage_gate_active,
    mark_coverage_receipt_expected,
    write_coverage_receipt,
)
from app.marcus.orchestrator.enrichment_consumption import (
    project_ambiguous_narration_ordinals,
)

logger = logging.getLogger(__name__)

COVERAGE_GATE_ID: str = "G3"
COVERAGE_REPORT_BASENAME: str = "coverage-report.html"
G0_ENRICHMENT_BASENAME: str = "g0-enrichment.json"

# The run-dir export SSOT the marshaller reads deck + narration from (R5-A7): mirror
# the run-dir read discipline of ``_load_coverage_annotations`` — NOT the brittle
# positional ``production_envelope.contributions[*]`` traversal (that is used ONLY for
# the plan_units / slide_briefs lineage).
GARY_DISPATCH_BASENAME: str = "gary-dispatch-payload.json"
SEGMENT_MANIFEST_BASENAME: str = "segment-manifest-storyboard-b.yaml"
EXPORTS_DIRNAME: str = "exports"
#: Additive ledger-only F-012 spans persisted at the G0E build site (R5-A8).
NON_VERBATIM_SPANS_KEY: str = "non_verbatim_spans"

# Annotation-breadcrumb canonicalizers (R5-A1/A3/MF4). ONLY a breadcrumb whose prefix
# denotes a SLIDE bridges to a slide ordinal: a bare integer ("1") or the explicit
# "Slide N" prefix (case-insensitive). A "Page N" / "Chapter N" / section-title
# breadcrumb is NOT a slide reference and matches NEITHER → unresolved_locator (no
# silent cross-namespace credit, MF4). A FRACTIONAL/interstitial "Slide 4.5" resolves
# to its PARENT integer (4), NEVER trailing-digits to the fractional tail (5). The
# resulting clean-int ordinal is additionally CORROBORATED against ``known_ordinals``
# (same discipline the fractional path already uses) by the bridge function.
_SLIDE_INT_RE: re.Pattern[str] = re.compile(r"^\s*(?:slide\s*)?(\d+)\s*$", re.IGNORECASE)
_SLIDE_FRACTIONAL_RE: re.Pattern[str] = re.compile(
    r"^\s*(?:slide\s*)?(\d+)\.\d+\s*$", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Authored-annotation load (from the frozen g0-enrichment.json)
# ---------------------------------------------------------------------------


def _load_coverage_annotations(run_dir: Path) -> tuple[CoverageAnnotation, ...]:
    """Rehydrate the authored coverage annotations from ``g0-enrichment.json``.

    Defensive: an absent / unreadable / coverage-free enrichment file yields ``()`` (a
    vacuous receipt, PASS-vacuous), never a crash.
    """
    path = run_dir / G0_ENRICHMENT_BASENAME
    if not path.is_file():
        return ()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("coverage: g0-enrichment.json unreadable at %s → no annotations", run_dir)
        return ()
    raw = payload.get("coverage_annotations") if isinstance(payload, dict) else None
    if not isinstance(raw, list) or not raw:
        return ()
    out: list[CoverageAnnotation] = []
    for item in raw:
        try:
            out.append(load_coverage_annotation(item))
        except (ValueError, TypeError):
            logger.warning("coverage: dropping malformed coverage annotation in g0-enrichment.json")
    return tuple(out)


# ---------------------------------------------------------------------------
# Marshalling — read the run's OWN deck + narration from exports (SSOT, R5-A7),
# normalize all three surfaces onto ONE canonical source-ordinal key (R5-A1/A2/A3).
# ---------------------------------------------------------------------------


def _as_list(value: Any) -> list[dict[str, Any]]:
    return [v for v in value if isinstance(v, dict)] if isinstance(value, list) else []


class _MarshalResult(NamedTuple):
    deck_rows: list[dict[str, Any]]
    narration_rows: list[dict[str, Any]]
    slide_key_map: dict[str, str]
    ambiguous_ordinals: set[str]
    known_ordinals: set[str]
    collision_ordinals: set[str]
    diagnostics: list[str]


def _read_deck_rows(run_dir: Path) -> list[dict[str, Any]]:
    """``exports/gary-dispatch-payload.json::gary_slide_output`` (defensive; never raises)."""
    path = run_dir / EXPORTS_DIRNAME / GARY_DISPATCH_BASENAME
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return _as_list(payload.get("gary_slide_output")) if isinstance(payload, dict) else []


def _read_narration_rows(run_dir: Path) -> list[dict[str, Any]]:
    """``exports/segment-manifest-storyboard-b.yaml::segments`` (defensive; never raises)."""
    path = run_dir / EXPORTS_DIRNAME / SEGMENT_MANIFEST_BASENAME
    if not path.is_file():
        return []
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    return _as_list(payload.get("segments")) if isinstance(payload, dict) else []


def _load_card_payload(run_dir: Path) -> dict[str, Any] | None:
    """The frozen g0-enrichment card (for the ambiguous-narration projector)."""
    path = run_dir / G0_ENRICHMENT_BASENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _normalize_deck_row(row: dict[str, Any]) -> dict[str, Any]:
    """Real Gary row -> the shape ``build_coverage_anchors`` consumes (R5-A7).

    ``display_title`` -> ``title``; ``visual_description`` -> ``body``; ``slide_id`` is
    the deck join key (no ``slide_index`` exists on a real row). Keeps
    ``coverage_anchors.py`` M3-pure (it never learns the Gary export schema).
    """
    return {
        "slide_id": row.get("slide_id"),
        "card_number": row.get("card_number"),
        "title": row.get("display_title") or row.get("title") or "",
        "body": row.get("visual_description") or row.get("body") or "",
    }


def _unit_in_scope(unit: dict[str, Any]) -> bool:
    """Mirror ``package_builders._unit_included`` (in unless ratified out-of-scope)."""
    decision: Any = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    return decision != "out-of-scope"


def _in_scope_units(plan_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [u for u in plan_units if isinstance(u, dict) and _unit_in_scope(u)]


def _derive_slide_briefs(plan_units: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Re-derive ``slide_briefs`` from plan_units (M3-clean replica of package_builders).

    ``build_gary_briefs`` indexes the IN-SCOPE units 1-based into ``slide-{i:02d}`` with
    ``source_ref = unit_id`` — the honest lineage carrier the deck join keys on. We
    replicate ONLY the id mapping (no CD directive needed) so the marshaller never
    imports the specialist/builder tree.
    """
    return [
        {
            "slide_id": f"slide-{index:02d}",
            "source_ref": str(unit.get("unit_id") or f"unit-{index}"),
        }
        for index, unit in enumerate(_in_scope_units(plan_units), start=1)
    ]


def _lesson_plan_candidates(rs: dict[str, Any]) -> list[tuple[list[dict[str, Any]], bool]]:
    """``[(plan_units, is_locked)]`` across the envelope contributions (+ legacy top-level).

    A contribution whose ``output.locked_scope.locked is True`` contributes its
    ``locked_scope.plan_units`` as a LOCKED (authoritative) candidate; otherwise its
    ``lesson_plan.plan_units`` is an unlocked candidate. Order preserved.
    """
    candidates: list[tuple[list[dict[str, Any]], bool]] = []
    env = rs.get("production_envelope")
    contributions = env.get("contributions") if isinstance(env, dict) else None
    if isinstance(contributions, list):
        for contrib in contributions:
            if not isinstance(contrib, dict):
                continue
            output = contrib.get("output")
            if not isinstance(output, dict):
                continue
            locked_scope = output.get("locked_scope")
            if isinstance(locked_scope, dict) and locked_scope.get("locked") is True:
                pu = locked_scope.get("plan_units")
                if isinstance(pu, list) and pu:
                    candidates.append(([u for u in pu if isinstance(u, dict)], True))
                    continue
            lesson_plan = output.get("lesson_plan")
            pu = lesson_plan.get("plan_units") if isinstance(lesson_plan, dict) else None
            if isinstance(pu, list) and pu:
                candidates.append(([u for u in pu if isinstance(u, dict)], False))
    if not candidates:
        lesson_plan = rs.get("lesson_plan") if isinstance(rs.get("lesson_plan"), dict) else {}
        pu = rs.get("plan_units") or lesson_plan.get("plan_units")
        if isinstance(pu, list) and pu:
            candidates.append(([u for u in pu if isinstance(u, dict)], False))
    return candidates


def _select_plan_units(
    run_state: dict[str, Any] | None, deck_count: int
) -> tuple[list[dict[str, Any]], bool]:
    """Select the AUTHORITATIVE lesson plan (MF3): ``(plan_units, ambiguous)``.

    Several contributions can carry a ``lesson_plan`` (an early plan + a re-refinement
    + a locked one). A re-refinement plan with the SAME in-scope count but REVERSED
    unit order would otherwise swap ordinals and credit coverage from the wrong slide
    (the MF3 false-PASS). Selection discipline:

      1. a LOCKED plan (``locked_scope.locked is True``) is authoritative;
      2. else prefer the candidate whose IN-SCOPE length matches the deck row count;
      3. if ≥2 such candidates differ in IN-SCOPE UNIT ORDER, the lineage is
         AMBIGUOUS — ``ambiguous=True`` (the marshaller degrades to forced missing
         when no persisted ``slide_briefs`` disambiguate; never a silent wrong-pick).

    The plan_units returned still seed the ``unit_id → source-ordinal`` map; when the
    REAL persisted ``slide_briefs`` are available they bind ``slide_id → source_ref``
    explicitly (order-immune), so the unit ORDER no longer matters.
    """
    rs = run_state if isinstance(run_state, dict) else {}
    candidates = _lesson_plan_candidates(rs)
    if not candidates:
        return [], False
    locked = [pu for pu, is_locked in candidates if is_locked]
    if locked:
        return locked[-1], False
    plans = [pu for pu, _ in candidates]
    exact = [pu for pu in plans if len(_in_scope_units(pu)) == deck_count and deck_count > 0]
    pool = exact if exact else plans
    ambiguous = False
    if len(pool) >= 2:
        orders = {
            tuple(u.get("unit_id") for u in _in_scope_units(pu)) for pu in pool
        }
        ambiguous = len(orders) > 1
    return pool[-1], ambiguous


def _extract_slide_briefs(run_state: dict[str, Any] | None) -> list[dict[str, str]]:
    """Read the REAL persisted ``slide_briefs`` lineage (MF3 lineage SSOT).

    ``package_builder.output.slides`` carries one row per FINAL slide with
    ``{slide_id, source_ref}`` (``source_ref`` = the plan ``unit_id`` the slide was
    built from) — the honest ``slide_id → source`` binding, IMMUNE to plan-order
    swaps (unlike positional re-derivation). When ≥2 contributions carry ``slides``,
    the LAST non-empty set wins (most-refined). Returns ``[]`` when no persisted
    briefs exist (positional re-derivation is the fallback only).
    """
    rs = run_state if isinstance(run_state, dict) else {}
    env = rs.get("production_envelope")
    contributions = env.get("contributions") if isinstance(env, dict) else None
    if not isinstance(contributions, list):
        return []
    result: list[dict[str, str]] = []
    for contrib in contributions:
        if not isinstance(contrib, dict):
            continue
        output = contrib.get("output")
        slides = output.get("slides") if isinstance(output, dict) else None
        if not isinstance(slides, list):
            continue
        cur: list[dict[str, str]] = []
        for s in slides:
            if not isinstance(s, dict):
                continue
            slide_id = str(s.get("slide_id") or "").strip()
            source_ref = str(s.get("source_ref") or "").strip()
            if slide_id and source_ref:
                cur.append({"slide_id": slide_id, "source_ref": source_ref})
        if cur:
            result = cur
    return result


def _collision_aware_slide_key_map(
    plan_units: list[dict[str, Any]], slide_briefs: list[dict[str, str]]
) -> tuple[dict[str, str], set[str], set[str], list[str]]:
    """The deck ``{final_slide_id: source_ordinal}`` map with the R5-A2 collision guard.

    Returns ``(clean_map, known_ordinals, collision_ordinals, diagnostics)``. When ≥2
    DISTINCT source slides (different ``source_slide_id``) resolve to the SAME ordinal
    (a cross-Part "Slide 1" collision), that ordinal is AMBIGUOUS: it is OMITTED from
    the map (never last-write-wins), so every deck row + annotation point on it forces
    ``missing`` + a diagnostic. Clustered sub-slides that share ONE source head are NOT
    a collision (same ``source_slide_id``), so they keep their shared ordinal.
    """
    lineage = resolve_slide_key_lineage(plan_units, slide_briefs)
    sources_by_ordinal: dict[str, set[str]] = {}
    for row in lineage:
        sources_by_ordinal.setdefault(row["ordinal"], set()).add(row["source_slide_id"])
    collision_ordinals = {o for o, srcs in sources_by_ordinal.items() if len(srcs) > 1}
    clean_map = {
        row["final_slide_id"]: row["ordinal"]
        for row in lineage
        if row["ordinal"] not in collision_ordinals
    }
    known_ordinals = set(clean_map.values())
    diagnostics = [
        (
            f"coverage-marshal: source-ordinal {ordinal!r} is AMBIGUOUS — "
            f"{len(sources_by_ordinal[ordinal])} distinct source slides collide "
            "(R5-A2 collision guard) → omitted, forced missing (never last-write-wins)"
        )
        for ordinal in sorted(collision_ordinals)
    ]
    return clean_map, known_ordinals, collision_ordinals, diagnostics


def _marshal_coverage_surfaces(
    run_state: dict[str, Any] | None,
    run_dir: Path,
) -> _MarshalResult:
    """Read deck + narration from the run-dir exports (SSOT) and normalize all three
    surfaces onto ONE canonical source-ordinal key (R5-A1/A2/A3/A7).

    * **Deck** — rows from ``exports/gary-dispatch-payload.json``, normalized
      (``display_title``/``visual_description`` → ``title``/``body``); identified by
      ``slide_id`` and mapped to a source ordinal via the collision-aware lineage map.
    * **Narration** — segments from ``exports/segment-manifest-storyboard-b.yaml``, each
      fed through the SAME map (keyed by ``narration.slide_id``) so it lands on the same
      source-ordinal key (today they wrongly key off the raw ``slide_id``).
    * **Lineage** — ``plan_units`` from ``run_state`` only (``slide_briefs`` re-derived).

    EVERY unresolved join appends a diagnostic; NOTHING here raises.
    """
    diagnostics: list[str] = []

    raw_deck = _read_deck_rows(run_dir)
    if not raw_deck:
        diagnostics.append(
            "coverage-marshal: no deck rows resolved "
            "(exports/gary-dispatch-payload.json::gary_slide_output absent/empty)"
        )
    deck_rows = [_normalize_deck_row(r) for r in raw_deck]

    raw_narration = _read_narration_rows(run_dir)
    if not raw_narration:
        diagnostics.append(
            "coverage-marshal: no narration rows resolved "
            "(exports/segment-manifest-storyboard-b.yaml::segments absent/empty)"
        )

    plan_units, plan_ambiguous = _select_plan_units(run_state, len(deck_rows))
    if not plan_units:
        diagnostics.append(
            "coverage-marshal: plan_units lineage unresolved "
            "(production_envelope.contributions[*].output.lesson_plan.plan_units empty)"
        )
    # MF3: the REAL persisted slide_briefs (package_builder.slides) are the lineage
    # SSOT — they bind slide_id → source_ref explicitly, immune to plan-order swaps.
    # Positional re-derivation is the FALLBACK only; under an ambiguous plan with no
    # persisted briefs the lineage is UNRESOLVED → degrade to forced missing (never a
    # silent wrong-plan pick).
    real_briefs = _extract_slide_briefs(run_state)
    if real_briefs:
        slide_briefs: list[dict[str, str]] = real_briefs
    elif plan_ambiguous:
        diagnostics.append(
            "coverage-marshal: lesson-plan selection is AMBIGUOUS — ≥2 candidate plans "
            "tie on in-scope count but differ in unit order, and NO persisted slide_briefs "
            "(package_builder.slides) disambiguate; lineage UNRESOLVED → ordinals degraded "
            "(forced missing), never a silent wrong-plan pick (MF3)"
        )
        slide_briefs = []
    else:
        slide_briefs = _derive_slide_briefs(plan_units)
    slide_key_map, known_ordinals, collision_ordinals, collide_diags = (
        _collision_aware_slide_key_map(plan_units, slide_briefs)
    )
    diagnostics.extend(collide_diags)
    if not slide_key_map and plan_units:
        diagnostics.append(
            "coverage-marshal: slide_key_map empty after lineage + collision reconciliation "
            "(no deck row resolves to a clean source ordinal)"
        )

    # Narration onto the SAME canonical source-ordinal key (R5-A1): feed each segment's
    # slide_id through the deck map so narration meets deck on the source ordinal.
    narration_rows: list[dict[str, Any]] = []
    for seg in raw_narration:
        if not isinstance(seg, dict):
            continue
        sid = str(seg.get("slide_id") or "").strip()
        ordinal = slide_key_map.get(sid)
        if ordinal is None:
            if sid:
                diagnostics.append(
                    f"coverage-marshal: narration segment slide_id {sid!r} did not reconcile "
                    "to a source ordinal (collision-omitted or off-lineage) → narration dropped"
                )
            continue
        narration_rows.append({"slide_key": ordinal, "narration_text": seg.get("narration_text")})

    ambiguous = set(project_ambiguous_narration_ordinals(_load_card_payload(run_dir)))

    return _MarshalResult(
        deck_rows=deck_rows,
        narration_rows=narration_rows,
        slide_key_map=slide_key_map,
        ambiguous_ordinals=ambiguous,
        known_ordinals=known_ordinals,
        collision_ordinals=collision_ordinals,
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Annotation-breadcrumb bridge (R5-A1/A3) + F-012 ledger read (R5-A8)
# ---------------------------------------------------------------------------


def _canonical_breadcrumb_ordinal(
    slide_key: str, known_ordinals: set[str], collision_ordinals: set[str]
) -> str | None:
    """Bridge an annotation breadcrumb onto the canonical source-ordinal key (R5-A1/A3/MF4).

    * SLIDE integer (bare "1" or "Slide 1", case-insensitive) → its ordinal
      (normalized, "01"→"1") IFF that ordinal is a known, non-colliding ordinal
      (MF4 corroboration — same discipline the fractional path uses). Collision-omitted
      or non-corroborated → ``None`` (R5-A2/MF4 → ``unresolved_locator``).
    * "Page N" / "Chapter N" / section-title → ``None``: these are NOT slide references,
      so they NEVER bridge to a slide ordinal (MF4 — no silent cross-namespace credit).
    * FRACTIONAL/interstitial ("Slide 4.5") → its PARENT integer (4) IFF that parent is a
      known, non-colliding ordinal (lineage corroboration); else ``None``. It NEVER
      trailing-digits to the fractional tail (5) (R5-A3, BLOCKING).
    """
    s = str(slide_key or "").strip()
    clean = _SLIDE_INT_RE.match(s)
    if clean:
        canon = str(int(clean.group(1)))
        if canon in collision_ordinals or canon not in known_ordinals:
            return None  # collision-omitted or not corroborated → degrade
        return canon
    fractional = _SLIDE_FRACTIONAL_RE.match(s)
    if fractional:
        parent = str(int(fractional.group(1)))
        if parent in known_ordinals and parent not in collision_ordinals:
            return parent
        return None  # degrade to missing — NEVER the fractional tail
    return None


def _build_slide_key_bridge(
    annotation_slide_keys: list[str], known_ordinals: set[str], collision_ordinals: set[str]
) -> tuple[dict[str, str | None], list[str]]:
    """``{breadcrumb_slide_key: canonical_ordinal | None}`` + unresolved-join diagnostics."""
    bridge: dict[str, str | None] = {}
    diagnostics: list[str] = []
    for slide_key in annotation_slide_keys:
        canon = _canonical_breadcrumb_ordinal(slide_key, known_ordinals, collision_ordinals)
        bridge[slide_key] = canon
        if canon is None:
            diagnostics.append(
                f"coverage-marshal: annotation breadcrumb {slide_key!r} did not bridge to a "
                "canonical source ordinal (section-title / collision-omitted / unresolvable "
                "fractional) → unresolved_locator, forced missing (R5-A4)"
            )
    return bridge, diagnostics


def _load_non_verbatim_diagnostics(run_dir: Path) -> tuple[str, ...]:
    """Read F-012 ``non_verbatim_spans`` from g0-enrichment.json → diagnostic strings (R5-A8).

    Ledger-only (NEVER a hard ``missing`` row): a dropped paraphrase is recoverable; the
    gate's teeth are must-cover ``missing``. Defensive: absent/garbage → ``()``.
    """
    payload = _load_card_payload(run_dir)
    raw = payload.get(NON_VERBATIM_SPANS_KEY) if isinstance(payload, dict) else None
    if not isinstance(raw, list):
        return ()
    out: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(
            "coverage-nonverbatim (F-012, ledger-only): component "
            f"{item.get('component_id')!r} slide_key {item.get('slide_key')!r} dropped "
            f"non-verbatim span: {item.get('span')!r}"
        )
    return tuple(out)


# ---------------------------------------------------------------------------
# Step 3 — standalone coverage-report.html (FORK B → B1)
# ---------------------------------------------------------------------------


def _write_coverage_report_html(run_dir: Path, receipt: CoverageReceipt) -> Path:
    """Write the standalone operator-facing ``coverage-report.html`` next to the receipt.

    Wraps the built ``render_coverage_section`` (machine-truth = the receipt JSON;
    HTML = the human view) in a minimal deterministic document with a back-link to
    ``run_summary.yaml``. Deterministic LF output.
    """
    section = render_coverage_section(receipt.model_dump(mode="json"))
    diags = receipt.diagnostics or ()
    diag_block = ""
    if diags:
        items = "\n".join(f"    <li>{escape(str(d))}</li>" for d in diags)
        diag_block = (
            '  <section class="coverage-diagnostics">\n'
            "    <h2>Marshalling diagnostics</h2>\n"
            f"    <ul>\n{items}\n    </ul>\n  </section>\n"
        )
    doc = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n  <meta charset="utf-8">\n'
        "  <title>Coverage report</title>\n</head>\n<body>\n"
        "  <h1>Source-note coverage report</h1>\n"
        '  <p><a href="run_summary.yaml">run_summary.yaml</a></p>\n'
        f"{diag_block}"
        f"  {section}\n"
        "</body>\n</html>\n"
    )
    path = run_dir / COVERAGE_REPORT_BASENAME
    path.write_text(doc, encoding="utf-8", newline="\n")
    _link_into_run_summary(run_dir)
    return path


def _link_into_run_summary(run_dir: Path) -> None:
    """Best-effort: record the coverage-report link in run_summary.yaml (never crash)."""
    summary = run_dir / "run_summary.yaml"
    if not summary.is_file():
        return
    try:
        import yaml

        data = yaml.safe_load(summary.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return
        if data.get("coverage_report") == COVERAGE_REPORT_BASENAME:
            return  # idempotent
        data["coverage_report"] = COVERAGE_REPORT_BASENAME
        summary.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
    except Exception:  # noqa: BLE001 - defensive: a run_summary link must never break the run
        logger.warning("coverage: could not link coverage-report into run_summary.yaml")


# ---------------------------------------------------------------------------
# Step 4 — the ONE shared both-walks helper (guarded gate_id == "G3")
# ---------------------------------------------------------------------------


def _derive_and_write_coverage_receipt(
    run_dir: Path,
    gate_id: str,
    run_state: dict[str, Any] | None,
) -> Path | None:
    """Derive + write + render the coverage receipt at the G3 storyboard-publish seam.

    Called at BOTH walk sites, guarded ``gate_id == "G3"``. No-op when coverage is OFF
    (byte-identical). DEFENSIVE end-to-end: a marshalling/derive failure records a
    diagnostic and still lands a (possibly vacuous) receipt — it NEVER crashes the
    runner. The "receipt expected" marker is dropped FIRST so even a total derive
    failure trips the fail-loud gate before audio spend.
    """
    if gate_id != COVERAGE_GATE_ID:
        return None
    if not coverage_gate_active():
        return None  # gate asleep → no receipt, byte-identical
    # Mark "past G3 / receipt expected" FIRST — a later failure must still fail loud.
    mark_coverage_receipt_expected(run_dir)
    try:
        annotations = _load_coverage_annotations(run_dir)
        marshalled = _marshal_coverage_surfaces(run_state, run_dir)
        anchors: dict[str, AnchorResolution] = build_coverage_anchors(
            marshalled.deck_rows,
            marshalled.narration_rows,
            marshalled.slide_key_map,
            marshalled.ambiguous_ordinals,
        )
        # Bridge the AUTHORED breadcrumb namespace ("Slide N") onto the canonical
        # source-ordinal namespace the anchors are keyed in (R5-A1/A3/A4).
        annotation_slide_keys = sorted(
            {sp.slide_key for ann in annotations for sp in ann.source_points}
        )
        key_bridge, bridge_diags = _build_slide_key_bridge(
            annotation_slide_keys, marshalled.known_ordinals, marshalled.collision_ordinals
        )
        # R5-A8: ledger-only F-012 NonVerbatimSpan diagnostics (never a hard missing).
        nv_diags = _load_non_verbatim_diagnostics(run_dir)
        diagnostics = (*marshalled.diagnostics, *bridge_diags, *nv_diags)
        receipt = derive_coverage_receipt(
            annotations, anchors, key_bridge=key_bridge, diagnostics=diagnostics
        )
        path = write_coverage_receipt(run_dir, receipt)
        _write_coverage_report_html(run_dir, receipt)
        if receipt.is_vacuous():
            logger.warning(
                "coverage: G3 receipt is VACUOUS (%d rows, 0 joined anchors) — NOT a clean "
                "pass (R5-A5); every authored span missed this run's own deck+narration",
                len(receipt.rows),
            )
        logger.info(
            "coverage: G3 receipt derived (%d rows, %d diagnostics) at %s",
            len(receipt.rows), len(receipt.diagnostics), path,
        )
        return path
    except Exception:  # noqa: BLE001 - defensive: G3 derivation must never crash the runner
        logger.exception(
            "coverage: G3 receipt derivation failed; marker stands so the fail-loud gate "
            "still fires before audio spend (no silent bypass)"
        )
        return None


__all__ = [
    "COVERAGE_GATE_ID",
    "COVERAGE_REPORT_BASENAME",
    "_derive_and_write_coverage_receipt",
    "_marshal_coverage_surfaces",
]

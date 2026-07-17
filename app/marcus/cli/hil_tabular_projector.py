"""Operator-facing HIL surface projector — Story 42.1 (finding C: tabular HIL).

Renders operator-facing human-in-the-loop review surfaces as markdown TABLES per
the worked exemplars in
``_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md``
§1 (gate identity, enrichment summary metrics, one-row-per-flag ungrounded
advisories, one-row-per-LO learning objectives).

The bc747b51 trial exposed the anti-pattern: after G0 confirm, enrichment printed
a sheaf of ``... excerpt is NOT grounded ...`` log lines with no table, then
``trial start`` emitted a single dense JSON blob and returned to the shell — an
unreviewable surface. This projector re-shapes that same material into tables so
the operator can actually read and decide.

Pagination follows the Marcus HIL Display Standards
(``skills/bmad-agent-marcus/references/conversation-mgmt.md`` §HIL Display
Standards): "for displays exceeding roughly 15 rows ... present the first page and
offer ``show next`` on demand". Numbered rows carry a unique sequential index as
the first column.

Contract fences (Story 42.1 Scope Fences):

* **Display-layer only.** The machine JSON on disk (``g0-enrichment.json`` /
  ``decision-card-*.json`` / ``operator-surface.json``) stays dense and is never
  mutated — this module only READS dicts and returns strings.
* **Pure / stdlib-only.** No side effects; the CLI printer (``emit_gate_surface``)
  is the only IO seam and it merely writes the rendered string to a stream.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import IO, Any

#: Marcus HIL Display Standards pagination threshold (rows).
PAGE_SIZE: int = 15

#: Bound (chars) for a summarized nested value in the generic renderer — mirrors
#: ``operator_surface_assembler._CONTEXT_ENTRY_MAX_CHARS`` (240) per Epic 43 rider
#: R2, so a fat nested value can never dump raw JSON into the operator surface.
_NESTED_VALUE_MAX_CHARS: int = 240

#: Fixed display width (chars) for the value column of the generic key/value table
#: (rider R5 — width-aware / fixed-width columns, no ugly wrap at 80 cols).
_GENERIC_VALUE_WIDTH: int = 60

#: Fixed display widths (chars) for the two long free-text columns of the G0
#: directive source-inventory table (Story 43-1, rider R5 — width-aware columns,
#: no ugly wrap at 80 cols). ``locator`` and the brief ``description`` are the
#: only unbounded columns; ref_id / role / min-words / excluded are naturally
#: short. Both are hard-capped via :func:`_truncate_cell`.
_DIRECTIVE_LOCATOR_WIDTH: int = 44
_DIRECTIVE_DESC_WIDTH: int = 44

#: Role ordering for the directive table's primary-first sort (Story 43-1, AC-1).
#: Unknown / excluded-only roles sort last; ties break lexically by ``ref_id``.
_DIRECTIVE_ROLE_RANK: dict[str, int] = {"primary": 0, "supporting": 1}

#: Human-friendly labels for the ``source_type`` of an ungrounded advisory
#: component. Speaker-notes narration is the dominant flagged kind (bc747b51: all
#: 12 ungrounded advisories were ``narration``); other types fall back to a
#: title-cased rendering of the raw ``source_type``.
_SOURCE_TYPE_KIND_LABELS: dict[str, str] = {
    "narration": "Narration (Speaker Notes)",
}


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Render a minimal GitHub-flavored markdown table.

    An empty ``rows`` still emits the header + separator so the operator sees the
    (empty) container rather than a silent gap.
    """
    head = "| " + " | ".join(str(h) for h in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([head, sep, *body])


def _paginate(
    rows: Sequence[Sequence[Any]], page_size: int
) -> tuple[list[Sequence[Any]], int]:
    """Return ``(first_page_rows, remaining_count)`` per the Display Standards.

    ``page_size <= 0`` disables pagination (returns every row). Otherwise the
    first ``page_size`` rows are shown and the remainder counted for a footer.
    """
    if page_size <= 0 or len(rows) <= page_size:
        return list(rows), 0
    return list(rows[:page_size]), len(rows) - page_size


def _pagination_footer(remaining: int) -> str:
    """Standard ``show next`` footer when a table was paginated."""
    return (
        f"_… {remaining} more row(s) not shown "
        f"(paginated at {PAGE_SIZE} per Marcus HIL Display Standards; `show next`)._"
    )


def _kind_label(component: Mapping[str, Any]) -> str:
    """Operator-facing "Kind" for an advisory row.

    Precedence: an explicit ``kind`` on the component > a mapped ``source_type``
    label > a title-cased raw ``source_type`` > an em-dash placeholder.
    """
    kind = component.get("kind")
    if kind:
        return str(kind)
    source_type = component.get("source_type")
    if not source_type:
        return "—"
    mapped = _SOURCE_TYPE_KIND_LABELS.get(str(source_type))
    if mapped:
        return mapped
    return str(source_type).replace("_", " ").title()


def render_gate_identity(identity: Mapping[str, Any]) -> str:
    """Exemplar — gate identity (trial / status / gate / ask) as a 2-col table."""
    rows = [
        ["Trial", identity.get("trial", "")],
        ["Status", identity.get("status", "")],
        ["Gate", identity.get("gate", "")],
        ["Ask", identity.get("ask", "")],
    ]
    return _md_table(["Item", "Value"], rows)


def _ungrounded_components(enrichment: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """The flagged-ungrounded components (the advisory rows) in document order."""
    components = enrichment.get("typed_components") or []
    return [c for c in components if isinstance(c, Mapping) and c.get("flagged_ungrounded")]


def render_enrichment_metrics(enrichment: Mapping[str, Any]) -> str:
    """Exemplar — enrichment summary metrics (typed / ungrounded / provisional-LOs).

    ``ungrounded`` count prefers the dense ``reconcile.n_ungrounded`` tally when
    present (the authoritative machine count) and otherwise counts the
    ``flagged_ungrounded`` components directly.
    """
    typed = len(enrichment.get("typed_components") or [])
    provisional = len(enrichment.get("provisional_los") or [])
    reconcile = enrichment.get("reconcile")
    if isinstance(reconcile, Mapping) and reconcile.get("n_ungrounded") is not None:
        ungrounded = int(reconcile["n_ungrounded"])
    else:
        ungrounded = len(_ungrounded_components(enrichment))
    rows = [
        ["Typed components", typed],
        ["Flagged ungrounded (advisory)", ungrounded],
        ["Provisional LOs", provisional],
    ]
    return _md_table(["Metric", "Count"], rows)


def render_ungrounded_advisories(
    enrichment: Mapping[str, Any], *, page_size: int = PAGE_SIZE
) -> str:
    """Exemplar — ungrounded advisories as ONE ROW PER FLAG (#, component_id,
    parent, Kind), with the advisory caption and Display-Standards pagination.

    This is the tabular replacement for the free-scroll ``... NOT grounded ...``
    log sheaf (AC-3).
    """
    advisories = _ungrounded_components(enrichment)
    caption = "_advisory (speaker notes) — adjudicate at G0E_"
    rows = [
        [
            idx,
            c.get("component_id", ""),
            c.get("parent_source_id", ""),
            _kind_label(c),
        ]
        for idx, c in enumerate(advisories, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "component_id", "parent", "Kind"], shown)
    parts = [caption, table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def render_learning_objectives(
    los: Sequence[Mapping[str, Any]],
    *,
    title: str = "Provisional LOs",
    page_size: int = PAGE_SIZE,
) -> str:
    """Exemplar — learning objectives as ONE ROW PER LO (#, Statement).

    Works for provisional (``g0-enrichment.provisional_los``) and ratified /
    refined (``decision-card-G0R.refined_los``) LO lists alike — both carry a
    ``statement`` field.
    """
    rows = [
        [idx, lo.get("statement", "") if isinstance(lo, Mapping) else str(lo)]
        for idx, lo in enumerate(los, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "Statement"], shown)
    parts = [f"**{title}**", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _truncate_cell(text: str, width: int) -> str:
    """Fixed-width guard (rider R5): hard-cap a display cell so the generic table
    cannot wrap ugly at 80 cols. ``width <= 0`` disables the cap.
    """
    if width <= 0 or len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _summarize_shallow(value: Any) -> str:
    """One-level peek used inside a list summary (never recurses further)."""
    if isinstance(value, Mapping):
        return f"{{{len(value)} field(s)}}"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return f"[{len(value)} item(s)]"
    return str(value)[:_NESTED_VALUE_MAX_CHARS]


def _summarize_nested_value(value: Any) -> str:
    """Bounded one-line summary of an arbitrary (possibly nested) value.

    Reuses the ``operator_surface_assembler._summarize_context_entry`` PATTERN
    (rider R2) — a concrete ``path`` > voice-option names > a ``kind (node_id)``
    tag > a field/count digest — generalized to any value and always bounded to
    ``_NESTED_VALUE_MAX_CHARS``. Never dumps raw nested JSON (AC-2).
    """
    if isinstance(value, Mapping):
        path = value.get("path")
        voices = value.get("voices")
        kind = value.get("kind")
        node = value.get("node_id")
        if isinstance(path, str) and path:
            text = path
        elif isinstance(voices, Sequence) and not isinstance(voices, (str, bytes)) and voices:
            names = [
                str(v.get("voice_name"))
                for v in voices
                if isinstance(v, Mapping) and v.get("voice_name")
            ]
            text = "voice options: " + ", ".join(names) if names else "voice options"
        elif kind and node:
            text = f"{kind} ({node})"
        else:
            fields = ", ".join(str(k) for k in list(value)[:8])
            text = f"{{{len(value)} field(s): {fields}}}" if fields else "{}"
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        text = f"[{len(value)} item(s)]"
        if value:
            text += f" e.g. {_summarize_shallow(value[0])}"
    else:
        text = str(value)
    return text[:_NESTED_VALUE_MAX_CHARS]


def render_generic_gate_content(
    content: Mapping[str, Any],
    *,
    title: str = "Gate content",
    page_size: int = PAGE_SIZE,
    value_width: int = _GENERIC_VALUE_WIDTH,
) -> str:
    """Generic FALLBACK renderer (AC-2) — project ANY paused gate's poll-surface /
    decision-card ``content`` mapping into a two-column ``Field | Value`` stderr
    table via :func:`_md_table`.

    Nested / complex values are bounded-summarized (``_summarize_nested_value`` —
    rider R2, 240-char cap) and every value cell is width-capped (rider R5); a
    deeply nested value is therefore never raw-dumped. Rows beyond ``page_size``
    paginate per the Marcus HIL Display Standards.

    This is the load-bearing scaffold: until a bespoke renderer is registered for a
    content type, this renderer tables it — so **no gate raw-dumps**.
    """
    rows: list[Sequence[Any]] = []
    for key, value in content.items():
        if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes)):
            display = _summarize_nested_value(value)
        else:
            display = "" if value is None else str(value)
        rows.append([key, _truncate_cell(display, value_width)])
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Field", "Value"], shown)
    parts = [f"**{title}**", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _source_is_excluded(source: Mapping[str, Any]) -> bool:
    """A directive source is excluded iff it carries a truthy ``excluded`` flag or
    a truthy ``excluded_reason``. The common ``excluded_reason: null`` is NOT
    excluded (the counts footer's ``X excluded`` tally rides on this predicate).
    """
    if source.get("excluded"):
        return True
    return bool(source.get("excluded_reason"))


def _directive_variant_slugs(gamma_settings: Any) -> dict[str, str]:
    """Map ``variant_id`` -> ``styleguide`` slug from a directive's
    ``gamma_settings`` list (each entry ``{variant_id, styleguide}``). Tolerant of
    a missing / malformed value — returns whatever well-formed entries exist.
    """
    slugs: dict[str, str] = {}
    if isinstance(gamma_settings, Sequence) and not isinstance(gamma_settings, (str, bytes)):
        for entry in gamma_settings:
            if isinstance(entry, Mapping):
                vid = entry.get("variant_id")
                slug = entry.get("styleguide")
                if vid is not None and slug is not None:
                    slugs[str(vid)] = str(slug)
    return slugs


def _corpus_basename(corpus_dir: Any) -> str:
    """Last path segment of a ``corpus_dir``, separator-agnostic and stdlib-pure
    (no ``os`` / ``pathlib`` platform coupling): normalize ``\\`` to ``/``, strip
    trailing slashes, take the final segment. Empty in, empty out.
    """
    text = str(corpus_dir or "").replace("\\", "/").rstrip("/")
    if not text:
        return ""
    return text.rsplit("/", 1)[-1]


def render_directive_sources(
    content: Mapping[str, Any],
    *,
    title: str = "G0 — Directive review",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G0 directive composition** renderer (Story 43-1) — project a
    composed *directive* mapping into the operator-approved source-inventory
    table so the operator can review the material partition (which sources, what
    roles, what floors) at the G0 confirm, instead of scanning a raw YAML dump.
    Registered under ``content_type="directive"``.

    Shape (operator-approved, BINDING — do not redesign)::

        G0 — Directive review   run <run_id> · corpus <corpus-basename>
        Variants:  A <styleguide-A> · B <styleguide-B>

        | ref | role | locator | min-words | excl | description |
        ...  (sorted PRIMARY-FIRST, lexical by ref within a role)

        N sources · P primary · S supporting · X excluded

    ``content`` is an ALREADY-PARSED directive mapping (``sources[]`` +
    ``run_id`` / ``corpus_dir`` / ``gamma_settings``) — the projector stays
    stdlib-pure, the caller (``trial.py``) does the ``yaml.safe_load``. The
    banner text is fixed to the approved shape; the contract ``title`` /
    ``page_size`` params are honored for pagination but the banner is not
    retitled. Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5).
    """
    sources = content.get("sources") or []
    source_list = [s for s in sources if isinstance(s, Mapping)]

    run_id = str(content.get("run_id") or "")
    corpus = _corpus_basename(content.get("corpus_dir"))
    slugs = _directive_variant_slugs(content.get("gamma_settings"))
    banner = f"G0 — Directive review   run {run_id} · corpus {corpus}"
    variants_line = f"Variants:  A {slugs.get('A', '—')} · B {slugs.get('B', '—')}"

    def _sort_key(entry: Mapping[str, Any]) -> tuple[int, str]:
        rank = _DIRECTIVE_ROLE_RANK.get(str(entry.get("role") or ""), 2)
        return (rank, str(entry.get("ref_id") or ""))

    ordered = sorted(source_list, key=_sort_key)
    rows: list[Sequence[Any]] = []
    for s in ordered:
        min_words = s.get("expected_min_words")
        rows.append(
            [
                s.get("ref_id", ""),
                s.get("role", ""),
                _truncate_cell(str(s.get("locator") or ""), _DIRECTIVE_LOCATOR_WIDTH),
                "—" if min_words is None else min_words,
                "yes" if _source_is_excluded(s) else "—",
                _truncate_cell(str(s.get("description") or ""), _DIRECTIVE_DESC_WIDTH),
            ]
        )

    shown, remaining = _paginate(rows, page_size)
    table = _md_table(
        ["ref", "role", "locator", "min-words", "excl", "description"], shown
    )

    n = len(source_list)
    p = sum(1 for s in source_list if str(s.get("role") or "") == "primary")
    sup = sum(1 for s in source_list if str(s.get("role") or "") == "supporting")
    x = sum(1 for s in source_list if _source_is_excluded(s))
    footer = f"{n} sources · {p} primary · {sup} supporting · {x} excluded"

    parts = [banner, variants_line, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    parts.extend(["", footer])
    return "\n".join(parts)


#: Renderer signature: ``(content, *, title, page_size) -> str``. Bespoke renderers
#: (43-1, 43-3…43-9) register against this contract; the generic fallback above
#: satisfies it for every content type with no bespoke renderer yet.
GateContentRenderer = Callable[..., str]

#: content-type key -> bespoke renderer. Intentionally EMPTY at 43-2: this story
#: ships the scaffold + the generic fallback; later stories register here. The
#: 43-10 structural-coverage test enumerates it via ``registered_content_types``.
_RENDERER_REGISTRY: dict[str, GateContentRenderer] = {}

#: SSOT — the canonical universe of operator-facing gate content types (Story
#: 43-10, AC-1). Sourced verbatim from the Epic 43 audit inventory
#: (``_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md``
#: §2) — every gate content type the operator reviews. This is the SINGLE set that
#: BOTH the 43-10 coverage-ratchet test and every future bespoke
#: ``register_renderer`` call reference; a new gate content type is added HERE
#: first, which forces the coverage test to demand a renderer or an explicit
#: waiver. Gate mapping (audit §2): ``directive`` G0 · ``estimator`` G1.5 ·
#: ``run_constants`` G1.5 · ``plan_unit`` G1A · ``per_slide_mode`` G2B ·
#: ``variant_ab`` G2M · ``literal_visual`` 06B · ``storyboard_targets`` 07C ·
#: ``motion_plan`` G2.5 · ``motion_clip`` G2F · ``storyboard_b`` G3B ·
#: ``voice_candidates`` G4A · ``input_package`` G4B · ``final_handoff`` G5 ·
#: ``research_packet`` · ``workbook``. Additive data only, no behavior change
#: (rider R7).
GATE_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "directive",  # G0 directive composition / sources[] material-partition
        "estimator",  # G1.5 run-budget estimator
        "run_constants",  # G1.5 run-constants lock
        "plan_unit",  # G1A PlanUnit ratification
        "per_slide_mode",  # G2B per-slide mode selection
        "variant_ab",  # G2M A/B variant selection
        "literal_visual",  # 06B literal-visual build targets
        "storyboard_targets",  # 07C storyboard build targets
        "motion_plan",  # G2.5 motion-plan status
        "motion_clip",  # G2F motion-clip card
        "storyboard_b",  # G3B storyboard / live-URL card
        "voice_candidates",  # G4A voice-candidate selection
        "input_package",  # G4B input-package preview
        "final_handoff",  # G5 final handoff artifacts + summary
        "research_packet",  # research packet content
        "workbook",  # workbook content
    }
)

#: SHRINK-ONLY waiver list (Story 43-10, AC-2/AC-3). A canonical gate content type
#: appears here ONLY while it still lacks a bespoke renderer; the coverage-ratchet
#: test (``tests/marcus/cli/test_projector_coverage_ratchet_43_10.py``) accepts a
#: type as "covered" iff it is EITHER in ``registered_content_types()`` OR waived
#: here. At 43-2 (zero bespoke renderers) this is the FULL canonical set: every
#: type falls back to the generic renderer, so every type is waived and the test is
#: green. INVARIANT — this list only ever SHRINKS: each bespoke-renderer story
#: (43-1, 43-3…43-9) MUST delete its type's row here in the SAME change that calls
#: ``register_renderer`` (the test enforces registry ∩ allowlist == ∅ — you cannot
#: both register and waive). Do NOT add a new entry to "quiet" the test for a newly
#: added gate; add the renderer instead. **Empty-at-epic-close:** Story 43-12
#: (governance close) asserts ``KNOWN_UNRENDERED_ALLOWLIST == frozenset()`` — the
#: last bespoke story empties this, and the epic cannot close while any row remains.
#:
#: Story 43-1 (the FIRST allowlist→registry move) deletes ``directive`` here in the
#: same change that registers :func:`render_directive_sources` — so ``directive`` is
#: now covered by a bespoke renderer, NOT waived (the 43-10 disjoint invariant
#: ``registry ∩ allowlist == ∅`` requires the deletion).
KNOWN_UNRENDERED_ALLOWLIST: frozenset[str] = frozenset(GATE_CONTENT_TYPES - {"directive"})


def register_renderer(content_type: str, renderer: GateContentRenderer) -> None:
    """Register a bespoke renderer for a gate ``content_type`` (AC-1 extension
    point) — the single, obvious way a later story plugs a bespoke table into the
    scaffold.
    """
    if not content_type:
        raise ValueError("content_type must be a non-empty key")
    _RENDERER_REGISTRY[content_type] = renderer


def registered_content_types() -> frozenset[str]:
    """The enumerable set of content-type keys with a BESPOKE renderer (AC-1).

    43-10's structural-coverage test consumes this to assert every gate content
    type is covered (its shrinking known-unrendered allowlist → 0).
    """
    return frozenset(_RENDERER_REGISTRY)


def get_renderer(content_type: str | None) -> GateContentRenderer:
    """Return the bespoke renderer registered for ``content_type``, else the
    generic fallback (:func:`render_generic_gate_content`)."""
    if content_type is None:
        return render_generic_gate_content
    return _RENDERER_REGISTRY.get(content_type, render_generic_gate_content)


def render_gate_content(
    content: Mapping[str, Any],
    *,
    content_type: str | None = None,
    title: str = "Gate content",
    page_size: int = PAGE_SIZE,
) -> str:
    """Dispatch ``content`` to its registered renderer, else the generic fallback
    (AC-1/AC-2). Every paused gate's own content flows through here, so no gate
    raw-dumps even before a bespoke renderer exists.
    """
    renderer = get_renderer(content_type)
    return renderer(content, title=title, page_size=page_size)


#: Story 43-1 — register the bespoke G0 directive renderer at import time. This is
#: the first allowlist→registry move: ``directive`` leaves
#: ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gains a bespoke renderer here, so the
#: G0 confirm surface tables its source inventory instead of raw-dumping YAML.
register_renderer("directive", render_directive_sources)


def render_hil_tables(surface: Mapping[str, Any], *, page_size: int = PAGE_SIZE) -> str:
    """Render an operator-facing HIL surface as stacked markdown tables.

    ``surface`` is a normalized dict; every section is optional and rendered only
    when present:

    * ``"gate_identity"``: ``{trial, status, gate, ask}`` -> gate-identity table.
    * ``"enrichment"``: a ``g0-enrichment.json`` dict -> metrics table +
      ungrounded-advisory table + provisional-LO table.
    * ``"learning_objectives"``: ``{"title": str, "rows": [ {statement}, ... ]}``
      -> an explicit LO table (e.g. G0R ratified/refined LOs). Rendered IN
      ADDITION to any provisional LOs from ``enrichment``.
    * ``"gate_content"``: ``{"content": Mapping, "content_type": str | None,
      "title": str}`` -> the paused gate's OWN poll-surface / decision-card content
      tabled via the renderer registry (bespoke if registered, else the generic
      fallback). This is the AC-3 scaffold so EVERY paused gate tables its content.

    Returns the sections joined by blank lines. An empty/None surface yields "".
    """
    sections: list[str] = []
    identity = surface.get("gate_identity")
    if identity:
        sections.append(render_gate_identity(identity))
    enrichment = surface.get("enrichment")
    if isinstance(enrichment, Mapping):
        sections.append(render_enrichment_metrics(enrichment))
        sections.append(render_ungrounded_advisories(enrichment, page_size=page_size))
        provisional = enrichment.get("provisional_los")
        if provisional:
            sections.append(
                render_learning_objectives(
                    provisional, title="Provisional LOs", page_size=page_size
                )
            )
    los_section = surface.get("learning_objectives")
    if isinstance(los_section, Mapping) and los_section.get("rows"):
        sections.append(
            render_learning_objectives(
                los_section["rows"],
                title=str(los_section.get("title", "Learning objectives")),
                page_size=page_size,
            )
        )
    gate_content = surface.get("gate_content")
    if isinstance(gate_content, Mapping) and isinstance(gate_content.get("content"), Mapping):
        sections.append(
            render_gate_content(
                gate_content["content"],
                content_type=gate_content.get("content_type"),
                title=str(gate_content.get("title", "Gate content")),
                page_size=page_size,
            )
        )
    return "\n\n".join(s for s in sections if s)


def build_gate_surface(
    *,
    gate_identity: Mapping[str, Any] | None = None,
    enrichment: Mapping[str, Any] | None = None,
    learning_objectives: Mapping[str, Any] | None = None,
    gate_content: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the normalized ``render_hil_tables`` surface dict from parts.

    Thin, keyword-only constructor so callers (CLI, tests) don't hand-shape the
    dict literal. Omitted parts are dropped. ``gate_content`` (the paused gate's
    own poll-surface / decision-card mapping) is a new optional part — additive
    within operator-surface v1 (rider R7), no schema bump.
    """
    surface: dict[str, Any] = {}
    if gate_identity:
        surface["gate_identity"] = dict(gate_identity)
    if enrichment is not None:
        surface["enrichment"] = enrichment
    if learning_objectives is not None:
        surface["learning_objectives"] = learning_objectives
    if gate_content is not None:
        surface["gate_content"] = gate_content
    return surface


def emit_gate_surface(
    surface: Mapping[str, Any],
    *,
    stream: IO[str],
    next_action: str | None = None,
    shell_context: str = "your shell prompt",
    raw_artifact: str | None = None,
) -> None:
    """CLI printer: write the tabular HIL surface (+ raw pointer + handoff cue) to
    ``stream``.

    The only IO seam in this module. Writes the rendered tables, then per AC-6 a
    consistent one-line raw-access pointer (the machine JSON on stdout is the
    documented raw form at EVERY gate — ``raw_artifact`` names the on-disk copy
    when known), then per AC-6 a handoff-cue footer stating the shell context and
    the exact resume affordance so the operator does not type ``c`` / ``approve``
    at the shell. ``next_action`` (when supplied) is the NEUTRAL next-step surface
    from ``app.marcus.cli.next_action.build_next_action`` — never an
    approve-prefilled command.
    """
    body = render_hil_tables(surface)
    if body:
        stream.write(body + "\n")
    raw_line = "raw: full machine JSON on stdout"
    if raw_artifact:
        raw_line += f" · on-disk: {raw_artifact}"
    stream.write("\n" + raw_line + "\n")
    gate = ""
    identity = surface.get("gate_identity")
    if isinstance(identity, Mapping):
        gate = str(identity.get("gate", ""))
    cue = (
        f"\nYou are back at {shell_context}; this trial is PAUSED"
        f"{f' at gate {gate}' if gate else ''} and nothing is running. "
        "Do NOT type 'c' / 'approve' here — that is not a shell command. "
        "To act, run one of the resume commands below."
    )
    stream.write(cue + "\n")
    if next_action:
        stream.write("\nNext step (Marcus proposes; you decide):\n")
        stream.write(next_action + "\n")


__all__ = [
    "GATE_CONTENT_TYPES",
    "KNOWN_UNRENDERED_ALLOWLIST",
    "PAGE_SIZE",
    "GateContentRenderer",
    "build_gate_surface",
    "emit_gate_surface",
    "get_renderer",
    "register_renderer",
    "registered_content_types",
    "render_directive_sources",
    "render_enrichment_metrics",
    "render_gate_content",
    "render_gate_identity",
    "render_generic_gate_content",
    "render_hil_tables",
    "render_learning_objectives",
    "render_ungrounded_advisories",
]

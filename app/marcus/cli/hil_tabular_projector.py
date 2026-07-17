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

from collections.abc import Mapping, Sequence
from typing import IO, Any

#: Marcus HIL Display Standards pagination threshold (rows).
PAGE_SIZE: int = 15

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
    return "\n\n".join(s for s in sections if s)


def build_gate_surface(
    *,
    gate_identity: Mapping[str, Any] | None = None,
    enrichment: Mapping[str, Any] | None = None,
    learning_objectives: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the normalized ``render_hil_tables`` surface dict from parts.

    Thin, keyword-only constructor so callers (CLI, tests) don't hand-shape the
    dict literal. Omitted parts are dropped.
    """
    surface: dict[str, Any] = {}
    if gate_identity:
        surface["gate_identity"] = dict(gate_identity)
    if enrichment is not None:
        surface["enrichment"] = enrichment
    if learning_objectives is not None:
        surface["learning_objectives"] = learning_objectives
    return surface


def emit_gate_surface(
    surface: Mapping[str, Any],
    *,
    stream: IO[str],
    next_action: str | None = None,
    shell_context: str = "your shell prompt",
) -> None:
    """CLI printer: write the tabular HIL surface (+ handoff cue) to ``stream``.

    The only IO seam in this module. Writes the rendered tables and, per AC-6, a
    handoff-cue footer stating the shell context and the exact resume affordance
    so the operator does not type ``c`` / ``approve`` at the shell. ``next_action``
    (when supplied) is the NEUTRAL next-step surface from
    ``app.marcus.cli.next_action.build_next_action`` — never an approve-prefilled
    command.
    """
    body = render_hil_tables(surface)
    if body:
        stream.write(body + "\n")
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
    "PAGE_SIZE",
    "build_gate_surface",
    "emit_gate_surface",
    "render_enrichment_metrics",
    "render_gate_identity",
    "render_hil_tables",
    "render_learning_objectives",
    "render_ungrounded_advisories",
]

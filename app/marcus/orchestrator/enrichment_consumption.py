"""P5-S2 (Step 6) — project the frozen G0 enriched corpus into deck + narration.

This is the ORCHESTRATOR-SIDE consumption layer that closes the second half of
the P5 loop: it READS the frozen, operator-confirmed ``G0EnrichmentResult`` card
payload (P1 typed_components + P3 pedagogy_annotations + provisional_los) and
projects it into the two deterministic learner-facing seams that the proven
producers already expose:

  * **Consumer A — narration role-seed** (``project_role_derived_voice_by_slide``):
    each narration component carrying a ``pedagogical_role`` is mapped, via the
    frozen ``PEDAGOGICAL_ROLE_TO_VOICE`` table, to a ``voice_direction`` DEFAULT
    keyed by the slide ordinal it teaches. The narration specialist (Irene Pass-2)
    applies this per-slide seed to its own frozen segment deltas. The directed
    DELIVERY of the narration then changes by pedagogical role — a deterministic,
    byte-exact learner-facing change (pace is the GUARANTEED dial; tone/energy are
    best-effort, never advertised audible — Step-5 §12).

  * **Consumer B — Gary deck directive hint** (``project_deck_enrichment_hint``):
    a SHORT STRUCTURED role/LO token (NOT prose) routed ONLY into Gary's
    ``additional_instructions`` so the directive SENT to Gamma is enrichment-shaped,
    byte-deterministically. The hint is STRUCTURALLY BARRED from the
    ``text_mode="preserve"`` card body and the Studio lock (GARY-A1); the live
    render is a confirmation, NOT a deterministic gate (MUR-5).

ARCHITECTURE (Winston A1–A6):
  * **No third loader (A1):** callers pass the already-loaded card-payload dict
    (read via the orchestrator's ``load_enrichment_result`` or the workbook's
    ``load_enrichment_card``). This module never opens a file.
  * **Map + matcher orchestrator-side (A3):** the frozen role→voice table AND the
    slide→component matcher live HERE, on the consumption boundary. The narration
    specialist does ZERO component matching — it only aligns its own segment ids to
    this precomputed per-slide map (an unavoidable delta-id re-key; the segment
    manifest does not exist until AFTER Pass-2, so the orchestrator cannot key by
    segment id — Winston A4 PINNED join: segment ``slide_id`` ordinal ↔ component
    ``Slide N`` locator ordinal, narration components only).
  * **Pure/deterministic (A5):** every function is pure, offline, zero network/model
    calls, never-raises; a card-absent / empty card ⇒ ``None`` / empty ⇒ the caller
    no-ops ⇒ byte-identical output.

P5-RO READ-ONLY INVARIANT: zero retrieval/network/model calls. READS the frozen
verdict; an LO statement is used VERBATIM in the deck hint.
"""

from __future__ import annotations

import os
import re
from typing import Any

# Single-sourced basename (A2) — re-exported for callers that want the constant
# without importing the lesson_plan model module directly.
from app.marcus.lesson_plan.g0_enrichment import ENRICHMENT_CARD_BASENAME
from app.marcus.lesson_plan.pedagogy_annotation import PEDAGOGY_ROLES

# ---------------------------------------------------------------------------
# Feature flag (GARY-A4) — deck enrichment kill-switch parity
# ---------------------------------------------------------------------------

# Default OFF so the proven deck directive stays byte-identical. AND-gated with
# card-presence: a woken flag with no enrichment card is still a no-op. Mirrors
# the narration flag (MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE) and the G0 flags.
MARCUS_DECK_ENRICHMENT_ACTIVE_ENV = "MARCUS_DECK_ENRICHMENT_ACTIVE"


def deck_enrichment_active() -> bool:
    """Return True iff the Gary deck enrichment hint is woken (default OFF)."""
    return os.environ.get(MARCUS_DECK_ENRICHMENT_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# ---------------------------------------------------------------------------
# The frozen role → voice_direction table (CD-amended, strawman §F.1)
# ---------------------------------------------------------------------------

#: ``pedagogical_role`` -> a ``voice_direction`` DEFAULT. ``pace`` is the GUARANTEED
#: dial (the reliable, audible signal); ``emotional_tone`` / ``energy`` are
#: best-effort (kept as receipts, never advertised audible — Step-5 §12).
#: worked_example / synthesis / assessment carry ``pace="slower"`` (Murat's
#: two-role-on-pace differential). FROZEN: shape-pinned by a test; a bump is a
#: governance change, not a silent edit.
PEDAGOGICAL_ROLE_TO_VOICE: dict[str, dict[str, str]] = {
    "definition": {"emotional_tone": "neutral", "pace": "neutral", "energy": "medium"},
    "motivation": {"emotional_tone": "warm", "pace": "neutral", "energy": "medium"},
    "worked_example": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
    "synthesis": {"emotional_tone": "reflective", "pace": "slower", "energy": "low"},
    "assessment": {"emotional_tone": "neutral", "pace": "slower", "energy": "medium"},
    "practice": {"emotional_tone": "encouraging", "pace": "neutral", "energy": "high"},
}

# EXHAUSTIVENESS guard (EDGE-2, mirrors the P3 partition guard in
# pedagogy_annotation.py): the role→voice map MUST cover the ENTIRE closed
# ``PedagogicalRole`` set. A future enum member added in pedagogy_annotation.py
# fails this guard at IMPORT until a voice row is assigned — so a new role can
# never silently get no seed. Raised explicitly (not ``assert``) so it holds under
# ``python -O``.
if set(PEDAGOGICAL_ROLE_TO_VOICE) != set(PEDAGOGY_ROLES):  # pragma: no cover - import-time
    raise RuntimeError(
        "PEDAGOGICAL_ROLE_TO_VOICE is not exhaustive over the closed PedagogicalRole "
        f"set: missing={sorted(set(PEDAGOGY_ROLES) - set(PEDAGOGICAL_ROLE_TO_VOICE))}, "
        f"phantom={sorted(set(PEDAGOGICAL_ROLE_TO_VOICE) - set(PEDAGOGY_ROLES))}"
    )

#: The provenance tier the annotation pass stamps onto a role-derived direction
#: (the frozen Step-1 contract enum). The SEED itself carries only VALUES — the
#: annotation leaf auto-derives ``source="role-derived"`` when the seed tier drove
#: the merged values AND no higher tier (CD defaults / operator override) did. A
#: seed that carried an explicit ``source`` would WIN over the leaf's computed
#: provenance (Remediation-7b), wrongly stamping ``role-derived`` even under an
#: override — so the seed must NOT carry ``source``.
ROLE_DERIVED_SOURCE = "role-derived"


# ---------------------------------------------------------------------------
# The closed pedagogical_role → rhetorical_role table (Story concierge-leg1a)
# ---------------------------------------------------------------------------

#: ``pedagogical_role`` -> the deterministic ``rhetorical_role`` Irene EMITS on the
#: role-derived voice-direction seed. This is the PRODUCER half of the v3
#: directed-voice tag channel whose CONSUMER (the Enrique v3 branch + the TAG-ONLY
#: ``app.specialists._shared.voice_provider_text`` compiler) already shipped and
#: party-closed (enhanced-vo-2). Before this table the seed carried only tone
#: (``PEDAGOGICAL_ROLE_TO_VOICE``), so ``rhetorical_role`` was always ``None`` on a
#: real run and the ``[slow]`` tag channel was INERT; this de-inerts it.
#:
#: Mirrors the ``PEDAGOGICAL_ROLE_TO_VOICE`` idiom EXACTLY: a module-level CLOSED
#: table, an import-time exhaustiveness guard over the closed ``PedagogicalRole`` set,
#: and a fail-safe accessor returning ``None`` for an unmapped role. FROZEN: shape-
#: pinned by a test; a bump is a governance change, not a silent edit.
#:
#: This slice maps EXACTLY ONE role to ``contrast_emphasis`` (the ``[slow]`` TONAL
#: tag): ``synthesis``. Rationale: synthesis is the lesson's "pull it together —
#: here's the key insight" beat; its existing voice row (``emotional_tone=reflective``,
#: ``energy=low``, ``pace=slower``) is already the measured/weighty delivery signature
#: that ``contrast_emphasis``'s ``[slow]`` reinforces, and it authors ZERO new words
#: (no source-containment risk -> no Vera-R7 dependency). ``warm_callback`` is
#: DELIBERATELY NOT mapped here — it requires structural callback authoring + Vera-R7
#: source-containment, which Leg-1b owns. Every other role maps to ``None`` -> NO
#: ``rhetorical_role`` emitted -> the v2 path, byte-identical to today (AC6).
#:
#: The VALUE is kept a plain ``str`` (it MUST be a member of the ``RhetoricalRole``
#: taxonomy declared in ``app.specialists.irene.authoring.pass_2_template`` and is
#: validated downstream by the ``VoiceDirection`` contract) so this orchestrator-side
#: DATA table never imports the specialist authoring tree — preserving the M3 fence,
#: exactly as the consumer leaf ``voice_provider_text.py`` treats ``rhetorical_role``
#: as a plain ``str`` riding in.
PEDAGOGICAL_ROLE_TO_RHETORICAL: dict[str, str | None] = {
    "definition": None,
    "motivation": None,
    "worked_example": None,
    "synthesis": "contrast_emphasis",
    "assessment": None,
    "practice": None,
}

# EXHAUSTIVENESS guard (mirrors the PEDAGOGICAL_ROLE_TO_VOICE guard above): the
# role→rhetorical map MUST cover the ENTIRE closed ``PedagogicalRole`` set, so a
# future enum member added in pedagogy_annotation.py fails this guard at IMPORT
# until a rhetorical mapping (a role or an explicit ``None``) is assigned — a new
# role can never silently get an undefined rhetorical mapping. Raised explicitly
# (not ``assert``) so it holds under ``python -O``.
if set(PEDAGOGICAL_ROLE_TO_RHETORICAL) != set(PEDAGOGY_ROLES):  # pragma: no cover - import-time
    raise RuntimeError(
        "PEDAGOGICAL_ROLE_TO_RHETORICAL is not exhaustive over the closed "
        "PedagogicalRole set: "
        f"missing={sorted(set(PEDAGOGY_ROLES) - set(PEDAGOGICAL_ROLE_TO_RHETORICAL))}, "
        f"phantom={sorted(set(PEDAGOGICAL_ROLE_TO_RHETORICAL) - set(PEDAGOGY_ROLES))}"
    )


def rhetorical_role_for_pedagogical_role(role: Any) -> str | None:
    """Map ONE ``pedagogical_role`` to its emitted ``rhetorical_role`` (or ``None``).

    Fail-safe (mirrors ``role_to_voice_direction``'s no-seed fail-safe): a role
    OUTSIDE the closed map (an ``other`` escape-hatch role, or a typo) returns
    ``None`` via ``dict.get`` — no ``rhetorical_role`` is emitted, so that segment
    stays on the v2 path (byte-identical). A mapped-but-unrhetorical role (e.g.
    ``definition``/``worked_example``) also returns ``None`` by table value. Only
    ``synthesis`` currently returns a role (``contrast_emphasis``).
    """
    return PEDAGOGICAL_ROLE_TO_RHETORICAL.get(str(role) if role is not None else "")


def role_to_voice_direction(role: Any) -> dict[str, str] | None:
    """Map ONE ``pedagogical_role`` to a ``voice_direction`` seed dict (or ``None``).

    Returns a NEW COPY of the frozen map row (VALUES only — ``emotional_tone`` /
    ``pace`` / ``energy``, PLUS ``rhetorical_role`` when the role maps to one;
    NO ``source``, so override precedence is preserved) so the caller can never
    mutate the table. A role outside the closed map (e.g. an ``other`` escape-hatch
    role, or a typo) returns ``None`` — the no-seed fail-safe (IR-A2): the segment
    falls back to the conservative built-in. When this seed is the highest-priority
    contributing tier, the annotation leaf stamps ``source="role-derived"``.

    Story concierge-leg1a: the deterministic ``rhetorical_role`` (from the closed
    ``PEDAGOGICAL_ROLE_TO_RHETORICAL`` table) is threaded onto the seed ADDITIVELY so
    it rides ``_overlay`` into ``VoiceDirection.rhetorical_role`` with ZERO contract
    change. The key is ADDED ONLY when the role actually maps to a rhetorical role —
    an unmapped role's seed stays BYTE-IDENTICAL to today (AC6).
    """
    row = PEDAGOGICAL_ROLE_TO_VOICE.get(str(role) if role is not None else "")
    if row is None:
        return None
    seed = dict(row)
    rhetorical = rhetorical_role_for_pedagogical_role(role)
    if rhetorical is not None:
        seed["rhetorical_role"] = rhetorical
    return seed


# ---------------------------------------------------------------------------
# The PINNED segment → component join (Winston A4)
# ---------------------------------------------------------------------------

# A component locator whose LAST breadcrumb is exactly ``Slide N`` (1-based). The
# enrichment card's narration components for deck slides carry locators like
# ``"Slide 1"`` (or ``"... > Slide 2"``); document-structure components carry
# breadcrumbs like ``"Course 1 > Module 1 > Part 1 > Page 3"`` which DO NOT match
# (they get no seed — the fail-open default). Matching only the trailing ``Slide N``
# token keeps the join deterministic + reported, never discovered live.
_SLIDE_LOCATOR_RE = re.compile(r"slide\s+(\d+)\s*$", re.IGNORECASE)


def slide_ordinal_from_locator(locator: Any) -> int | None:
    """Extract the 1-based slide ordinal from a component locator's trailing ``Slide N``.

    Only the LAST breadcrumb segment is considered (``"A > B > Slide 3"`` → 3;
    ``"Course 1 > ... > Page 3"`` → ``None``). Returns ``None`` when the locator
    does not terminate in a ``Slide N`` token.
    """
    if not isinstance(locator, str):
        return None
    last = locator.split(">")[-1].strip()
    match = _SLIDE_LOCATOR_RE.match(last)
    return int(match.group(1)) if match else None


def source_slide_ordinals(card_payload: dict[str, Any] | None) -> list[int]:
    """The DISTINCT source-deck slide ordinals the card enumerates (sorted).

    Every component whose locator terminates in ``Slide N`` contributes ordinal N.

    LEGACY (Story enhanced-vo.1, Slice 0): this was the source side of the EDGE-1
    divergence guard — the narration specialist compared this set against the FINAL
    deck's slide ordinals and FAILED OPEN whenever they differed (i.e. on EVERY
    clustered / sub-split / dropped / renumbered deck). That guard is retired: the
    specialist now resolves each final segment to its TRUE source slide via the
    deterministic lineage and joins by ``slide_key`` identity, so this universe is
    NO LONGER threaded to the specialist. The function is retained (pure + offline +
    deterministic) for diagnostics / back-compat callers.
    """
    if not isinstance(card_payload, dict):
        return []
    components = card_payload.get("typed_components")
    if not isinstance(components, list):
        return []
    ordinals: set[int] = set()
    for comp in components:
        if not isinstance(comp, dict):
            continue
        ordinal = slide_ordinal_from_locator(comp.get("locator"))
        if ordinal is not None:
            ordinals.add(ordinal)
    return sorted(ordinals)


def project_role_derived_voice_by_slide(
    card_payload: dict[str, Any] | None,
) -> dict[str, dict[str, str]]:
    """Project the frozen card → ``{slide_ordinal(str): voice_direction_seed}``.

    The COMPONENT MATCHER (A3, orchestrator-side). For each NARRATION component
    whose locator terminates in ``Slide N``, that is ``teachable`` (EDGE-3 — never
    seed delivery from ungrounded/failed content), AND carries a ``pedagogical_role``
    in the frozen map, the slide ordinal ``N`` is seeded with that role's voice
    direction. The narration component is the pedagogically correct signal for
    VOICE delivery (it is literally about how the slide is narrated).

    FAIL-SAFE (IR-A2, no-silent-anything): a slide whose ``Slide N`` ordinal has
    NO eligible narration component, or MORE THAN ONE (ambiguous-multi-match), gets
    NO seed — that slide's segments take the conservative built-in default. Keyed
    by the SOURCE-deck slide ordinal as a STRING — this IS the specialist's
    ``slide_key``: the narration specialist resolves each FINAL segment to its TRUE
    source slide via the deterministic lineage (slide_briefs.source_ref +
    lesson_plan plan_units) and joins ``by_slide[slide_key]`` by IDENTITY.
    A ``None``/empty card returns ``{}`` (caller no-ops → byte-identical).

    NOTE (Story enhanced-vo.1, Slice 0 — DETERMINISTIC IDENTITY JOIN): this maps the
    card's SOURCE slide ordinal to its role-derived voice seed. The legacy 1:1
    source==final ordinal coincidence requirement (and its fail-open EDGE-1 guard,
    which fired on EVERY clustered deck) is RETIRED: N sub-slides of one clustered
    source slide now share that source slide's ``slide_key`` and all inherit this
    seed. Discharges ``p5-s2-role-seed-robust-source-to-final-slide-linkage``.

    Pure + offline + deterministic (READ-ONLY over the frozen verdict).
    """
    # Shared candidate block (FORK C — one extracted helper, no duplication).
    candidates_by_ordinal = _candidate_narration_seeds_by_ordinal(card_payload)

    # Exactly-one-eligible-narration-per-slide wins; 0 or >1 ⇒ fail-safe no seed.
    seeds: dict[str, dict[str, str]] = {}
    for ordinal, seed_list in candidates_by_ordinal.items():
        if len(seed_list) == 1:
            seeds[str(ordinal)] = seed_list[0]
    return seeds


def _candidate_narration_seeds_by_ordinal(
    card_payload: dict[str, Any] | None,
) -> dict[int, list[dict[str, str]]]:
    """Collect eligible (teachable, role-bearing, Slide-N, narration) seeds per ordinal.

    The SHARED candidate-collection block behind BOTH
    :func:`project_role_derived_voice_by_slide` (which keeps the EXACTLY-one-eligible
    ordinals) AND :func:`project_ambiguous_narration_ordinals` (which surfaces the
    >1-eligible collisions the role-seed matcher silently drops). Extracted so the two
    consumers cannot drift (Winston — no duplication). Pure / offline / READ-ONLY.
    """
    if not isinstance(card_payload, dict):
        return {}
    components = card_payload.get("typed_components")
    annotations = card_payload.get("pedagogy_annotations")
    if not isinstance(components, list) or not isinstance(annotations, list):
        return {}

    annotation_by_component: dict[str, dict[str, Any]] = {
        str(a.get("component_id")): a
        for a in annotations
        if isinstance(a, dict) and a.get("component_id")
    }

    candidates_by_ordinal: dict[int, list[dict[str, str]]] = {}
    for comp in components:
        if not isinstance(comp, dict):
            continue
        if comp.get("source_type") != "narration":
            continue
        ordinal = slide_ordinal_from_locator(comp.get("locator"))
        if ordinal is None:
            continue
        ann = annotation_by_component.get(str(comp.get("component_id")))
        if ann is None:
            continue
        # EDGE-3: never seed delivery from a non-teachable (ungrounded/failed)
        # narration component — consistent with the workbook's teachable discipline.
        if ann.get("teachable") is not True:
            continue
        seed = role_to_voice_direction(ann.get("pedagogical_role"))
        if seed is None:
            continue
        candidates_by_ordinal.setdefault(ordinal, []).append(seed)
    return candidates_by_ordinal


def project_ambiguous_narration_ordinals(card_payload: dict[str, Any] | None) -> set[str]:
    """The Slide-N ordinals (as strings) the role-seed matcher DROPS as >1-ambiguous (FORK C).

    A slide with MORE THAN ONE eligible narration component is an ambiguous-multi-match:
    ``project_role_derived_voice_by_slide`` gives it NO seed (``enrichment_consumption``
    :336-340 fail-safe drop). This accessor surfaces those dropped ordinals so the
    coverage receipt logs the narration surface as ``missing``
    (``AnchorResolution.narration_ambiguous``) rather than trust an ambiguous join.

    The 0-eligible case (a Slide-N narration component that is not teachable / carries no
    mapped role) is NOT "ambiguous" — it simply yields no narration surface
    (``narration_present == False``), which the receipt already treats as uncovered.
    Keyed by the SOURCE-deck slide ordinal as a STRING (the role-seed ``slide_key``
    namespace). Pure / offline / READ-ONLY over the frozen card.
    """
    candidates_by_ordinal = _candidate_narration_seeds_by_ordinal(card_payload)
    return {str(ordinal) for ordinal, seeds in candidates_by_ordinal.items() if len(seeds) > 1}


# ---------------------------------------------------------------------------
# Consumer B — Gary deck directive hint (short structured token; GARY-A1)
# ---------------------------------------------------------------------------

# Caps so the hint stays a SHORT structured token, never a prose reflow (GARY-A1 /
# Murat): a bounded number of LO statements, each bounded in length.
_DECK_HINT_MAX_LOS = 12
_DECK_HINT_LO_STATEMENT_MAX_CHARS = 200
_WS_RUN_RE = re.compile(r"\s+")


def _sanitize_hint_statement(statement: str) -> str:
    """Make an LO statement safe to embed in the structured hint (EDGE-5).

    Collapses every whitespace run (incl. newlines) to a single space and
    neutralizes the literal ``" | "`` token separator so LO CONTENT can never
    break the hint's structure (a newline-bearing or pipe-bearing statement would
    otherwise spoof an extra card-split chunk or a fake token boundary). Then caps
    the length. Applied to EVERY LO statement before it enters the hint.
    """
    collapsed = _WS_RUN_RE.sub(" ", statement).strip()
    collapsed = collapsed.replace(" | ", " / ")
    return collapsed[:_DECK_HINT_LO_STATEMENT_MAX_CHARS]


def project_deck_enrichment_hint(card_payload: dict[str, Any] | None) -> str | None:
    """Project the frozen card → a SHORT structured enrichment hint string (or ``None``).

    The hint is a compact, deterministic, SENTINEL-bearing token (each surfaced
    provisional LO's id + verbatim statement, plus the set of pedagogical roles
    present) — NOT prose. It is routed ONLY into Gary's ``additional_instructions``
    so the directive SENT to Gamma is enrichment-shaped; it is structurally barred
    from the card body / Studio lock (GARY-A1). The LO statement is used VERBATIM
    (the anti-tautology sentinel): mutating an LO statement in the card mutates the
    hint byte-for-byte.

    Returns ``None`` when the card is absent/empty (caller leaves
    ``additional_instructions`` byte-identical). Pure + offline + deterministic.
    """
    if not isinstance(card_payload, dict):
        return None
    los = card_payload.get("provisional_los")
    annotations = card_payload.get("pedagogy_annotations")

    lo_tokens: list[str] = []
    if isinstance(los, list):
        for lo in los:
            if not isinstance(lo, dict):
                continue
            oid = str(lo.get("objective_id") or "").strip()
            if not oid:
                continue
            statement = _sanitize_hint_statement(str(lo.get("statement") or ""))
            lo_tokens.append(f"{oid}: {statement}" if statement else oid)
            if len(lo_tokens) >= _DECK_HINT_MAX_LOS:
                break

    roles: set[str] = set()
    if isinstance(annotations, list):
        for ann in annotations:
            if isinstance(ann, dict) and ann.get("pedagogical_role"):
                roles.add(str(ann["pedagogical_role"]))

    if not lo_tokens and not roles:
        return None

    parts = ["[g0-enrichment] Pedagogical context for slide design (do not restate verbatim)."]
    if lo_tokens:
        parts.append("Learning objectives: " + " | ".join(lo_tokens) + ".")
    if roles:
        parts.append("Pedagogical roles present: " + ", ".join(sorted(roles)) + ".")
    return " ".join(parts)


__all__ = [
    "ENRICHMENT_CARD_BASENAME",
    "MARCUS_DECK_ENRICHMENT_ACTIVE_ENV",
    "PEDAGOGICAL_ROLE_TO_VOICE",
    "ROLE_DERIVED_SOURCE",
    "deck_enrichment_active",
    "project_deck_enrichment_hint",
    "project_role_derived_voice_by_slide",
    "role_to_voice_direction",
    "slide_ordinal_from_locator",
    "source_slide_ordinals",
]

"""P2-4b conformance-finalize scoring harness (reading-path arc).

Scores EMITTED reading-path tuples against operator-confirmed GOLD tuples per the
A6 contract ratified in:

  - reading-path-patterns-catalog.md v1.1 §9.4 (A6 conformance-measurement contract)
  - reading-path-gap-resolution-G2-G3-2026-06-22.md (what's IN vs OUT of the primary key)
  - reading-path-holdout-gold-labels-2026-06-23.md (the 14 frozen gold tuples)

Contract (A6), implemented here:

  * PRIMARY KEY (the headline top-1, threshold >=0.85) = STRICT exact match on
    ``macro_layout x image_role`` ONLY. image_role is FOLDED to the live-scored
    set {1, 2, 4}: tier 2.5 -> 2; tier 3 is QUARANTINED (excluded -> treated as a
    distinct sentinel that can never match a scored tier, so a quarantined-tier
    slide is a guaranteed miss IF it appears -- but the held-out 14 carry none).
    No partial credit.

  * FULL-TUPLE exact match (threshold >=0.80) = exact match on
    ``macro_layout x image_role x text_substructure x narration_cadence``.
    callout_intent and quarantined tiers are NOT part of the full tuple.

  * PER-AXIS confirm vectors (reported, NEVER folded into top-1):
    text_substructure, narration_cadence, and (for transparency) macro_layout +
    image_role individually.

  * callout_intent reported as a SEPARATE PROBATIONARY vector, EXCLUDED from
    both the primary-key top-1 and the full-tuple match.

  * macro_layout CONFUSION MATRIX emitted as an artifact.

This module is PURE and deterministic. It does NOT touch the live classifier,
the perceiver, or any vision/perception substrate; it scores
(slide_id, emitted_tuple, gold_tuple) triples that callers supply. The P2-4b run
(once S2/S3 land) builds those triples by running the classifier over the 14
held-out perceptions and pairing each emitted tuple with its gold from
reading-path-holdout-gold-labels-2026-06-23.md.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

# A6 thresholds (catalog v1.1 §9.4).
PRIMARY_KEY_THRESHOLD = 0.85
FULL_TUPLE_THRESHOLD = 0.80
# callout_intent probation floor (D2 / catalog v1.1 §2 AXIS 5) -- reported, advisory.
CALLOUT_INTENT_AGREEMENT_FLOOR = 0.80

# Live-scored image-role tiers (G2 resolution). 2.5 folds -> 2; tier 3 quarantined.
SCORED_TIERS = {1, 2, 4}
# Sentinel a quarantined (tier-3) image_role folds to: it can never equal a scored
# tier, so a tier-3 slide is a guaranteed primary-key miss if one ever appears.
QUARANTINED_SENTINEL = "QUARANTINED_TIER_3"


def fold_image_role(role: object) -> object:
    """Fold a per-slide dominant image_role to the live-scored representation.

    - ``None`` / ``"none"`` -> ``None`` (no scored image element on the slide).
    - 2.5 -> 2 (tier-2.5 evidentiary FOLDS to illustrative per G2).
    - 3 -> QUARANTINED_SENTINEL (tier-3 instructional is excluded from scoring).
    - 1, 2, 4 -> themselves.
    - anything else -> returned unchanged (caller error surfaces as a mismatch).
    """
    if role is None or role == "none":
        return None
    if role in (2.5, "2.5"):
        return 2
    if role in (3, "3"):
        return QUARANTINED_SENTINEL
    # normalize numeric-ish strings for the scored set
    if isinstance(role, str) and role.isdigit():
        ival = int(role)
        return ival if ival in SCORED_TIERS else role
    return role


@dataclass(frozen=True)
class ReadingPathTuple:
    """A reading-path compositional tuple (emitted or gold).

    image_role is the SLIDE-LEVEL DOMINANT tier (pre-fold). callout_intent is the
    orthogonal speech-act axis (probationary; out of every scored top-1).
    """

    macro_layout: str
    image_role: object  # int|float|str|None; folded at scoring time
    text_substructure: str | None = None
    narration_cadence: str | None = None
    callout_intent: str | None = None
    derived_primary: str | None = None

    def primary_key(self) -> tuple:
        """The scored primary key: macro_layout x folded image_role."""
        return (self.macro_layout, fold_image_role(self.image_role))

    def full_tuple_key(self) -> tuple:
        """macro x folded-image_role x text_substructure x narration_cadence.

        Excludes callout_intent (D2) and never includes a quarantined tier as a
        scorable value (it remains the sentinel -> guaranteed miss).
        """
        return (
            self.macro_layout,
            fold_image_role(self.image_role),
            self.text_substructure,
            self.narration_cadence,
        )


@dataclass
class ScoreReport:
    """Result of scoring an emitted-vs-gold set."""

    n: int
    primary_key_hits: int
    full_tuple_hits: int
    per_axis_hits: dict  # axis_name -> hit count
    callout_intent_hits: int
    callout_intent_scorable: int  # rows where gold callout_intent is non-null/inform
    macro_confusion: dict  # (gold_macro, emitted_macro) -> count
    quarantined_rows: list  # slide_ids whose gold image_role was tier-3 quarantined
    per_slide: list  # list of dicts, one per scored slide

    # --- derived rates ---------------------------------------------------
    @property
    def primary_key_top1(self) -> float:
        return self.primary_key_hits / self.n if self.n else 0.0

    @property
    def full_tuple_rate(self) -> float:
        return self.full_tuple_hits / self.n if self.n else 0.0

    @property
    def callout_intent_agreement(self) -> float:
        if not self.callout_intent_scorable:
            return 0.0
        return self.callout_intent_hits / self.callout_intent_scorable

    def per_axis_rate(self, axis: str) -> float:
        return self.per_axis_hits.get(axis, 0) / self.n if self.n else 0.0

    @property
    def passes_primary_key(self) -> bool:
        return self.primary_key_top1 >= PRIMARY_KEY_THRESHOLD

    @property
    def passes_full_tuple(self) -> bool:
        return self.full_tuple_rate >= FULL_TUPLE_THRESHOLD

    # --- presentation ----------------------------------------------------
    def summary_lines(self) -> list:
        lines = [
            f"N scored slides:            {self.n}",
            f"PRIMARY-KEY top-1:          {self.primary_key_hits}/{self.n} = "
            f"{self.primary_key_top1:.3f}  "
            f"({'PASS' if self.passes_primary_key else 'FAIL'} vs >={PRIMARY_KEY_THRESHOLD})",
            f"FULL-TUPLE exact match:     {self.full_tuple_hits}/{self.n} = "
            f"{self.full_tuple_rate:.3f}  "
            f"({'PASS' if self.passes_full_tuple else 'FAIL'} vs >={FULL_TUPLE_THRESHOLD})",
            "per-axis vectors (reported, NOT folded into top-1):",
        ]
        for axis, label in (
            ("macro_layout", "macro_layout"),
            ("image_role", "image_role (folded)"),
            ("text_substructure", "text_substructure"),
            ("narration_cadence", "narration_cadence"),
        ):
            hits = self.per_axis_hits.get(axis, 0)
            lines.append(
                f"    {label:<22} {hits}/{self.n} = {self.per_axis_rate(axis):.3f}"
            )
        lines += [
            f"callout_intent (PROBATION, excluded from top-1): "
            f"{self.callout_intent_hits}/{self.callout_intent_scorable} = "
            f"{self.callout_intent_agreement:.3f} "
            f"(floor advisory >={CALLOUT_INTENT_AGREEMENT_FLOOR})",
        ]
        if self.quarantined_rows:
            lines.append(
                f"tier-3 QUARANTINED rows (excluded from scored match): "
                f"{', '.join(self.quarantined_rows)}"
            )
        return lines

    def confusion_lines(self) -> list:
        if not self.macro_confusion:
            return ["macro_layout confusion: (no rows)"]
        lines = ["macro_layout confusion (gold -> emitted : count) [only off-diagonal shown]:"]
        for (gold, emitted), count in sorted(self.macro_confusion.items()):
            if gold != emitted:
                lines.append(f"    {gold} -> {emitted} : {count}   <-- MISS")
        if len(lines) == 1:
            lines.append("    (all macro_layout values matched -- no off-diagonal entries)")
        return lines


def _is_inform(value: str | None) -> bool:
    """callout_intent 'inform'/null/None is the no-op default (D2)."""
    return value is None or value == "inform" or value == "none"


def score(rows: list) -> ScoreReport:
    """Score a list of (slide_id, emitted_tuple, gold_tuple) triples.

    Each row is a 3-tuple ``(slide_id: str, emitted: ReadingPathTuple,
    gold: ReadingPathTuple)``. Returns a ``ScoreReport``.
    """
    n = len(rows)
    primary_hits = 0
    full_hits = 0
    # Seed all axes at 0 so a fully-missed axis still appears in the report.
    per_axis: Counter = Counter(
        {
            "macro_layout": 0,
            "image_role": 0,
            "text_substructure": 0,
            "narration_cadence": 0,
        }
    )
    callout_hits = 0
    callout_scorable = 0
    confusion: Counter = Counter()
    quarantined_rows: list = []
    per_slide: list = []

    axes = ("macro_layout", "image_role", "text_substructure", "narration_cadence")

    for slide_id, emitted, gold in rows:
        # primary key (strict)
        pk_match = emitted.primary_key() == gold.primary_key()
        if pk_match:
            primary_hits += 1

        # full tuple (strict, callout_intent excluded)
        ft_match = emitted.full_tuple_key() == gold.full_tuple_key()
        if ft_match:
            full_hits += 1

        # per-axis (image_role compared on the FOLDED representation)
        axis_results = {}
        for axis in axes:
            if axis == "image_role":
                g = fold_image_role(gold.image_role)
                e = fold_image_role(emitted.image_role)
            else:
                g = getattr(gold, axis)
                e = getattr(emitted, axis)
            ok = g == e
            axis_results[axis] = ok
            if ok:
                per_axis[axis] += 1

        # macro confusion matrix
        confusion[(gold.macro_layout, emitted.macro_layout)] += 1

        # quarantine bookkeeping (tier-3 gold)
        if fold_image_role(gold.image_role) == QUARANTINED_SENTINEL:
            quarantined_rows.append(slide_id)

        # callout_intent (probationary; scored only where gold carries a real act)
        if not _is_inform(gold.callout_intent):
            callout_scorable += 1
            if gold.callout_intent == emitted.callout_intent:
                callout_hits += 1
        callout_match = gold.callout_intent == emitted.callout_intent

        per_slide.append(
            {
                "slide_id": slide_id,
                "primary_key_match": pk_match,
                "full_tuple_match": ft_match,
                "axis_matches": axis_results,
                "callout_intent_match": callout_match,
                "gold_primary_key": gold.primary_key(),
                "emitted_primary_key": emitted.primary_key(),
            }
        )

    return ScoreReport(
        n=n,
        primary_key_hits=primary_hits,
        full_tuple_hits=full_hits,
        per_axis_hits=dict(per_axis),
        callout_intent_hits=callout_hits,
        callout_intent_scorable=callout_scorable,
        macro_confusion=dict(confusion),
        quarantined_rows=quarantined_rows,
        per_slide=per_slide,
    )


# --------------------------------------------------------------------------- #
# Demo fixtures: a SYNTHETIC emitted/gold set mirroring the held-out round.    #
# 14 gold tuples = reading-path-holdout-gold-labels-2026-06-23.md.             #
# Synthetic "emitted" reproduces the held-out outcome: 13/14 primary-key       #
# (the 17_ macro flip is the single primary-key miss) -> 0.93.                 #
# --------------------------------------------------------------------------- #

_GOLD_14 = [
    ("1_Diagnosis-Innovation",
     ReadingPathTuple("split_image_text", 1, "hero_message", "moderate", "inform")),
    ("3_Achieving-the-Ideal-State",
     ReadingPathTuple("single_text_block", 4, "enumerated_process", "dense", "inform")),
    ("5_Check-Your-Understanding",
     ReadingPathTuple("single_text_block", 1, "peer_boxes", "moderate", "challenge_quiz")),
    ("6_All-of-them-belong-to-BOTH",
     ReadingPathTuple("split_image_text", 1, "hero_message", "sparse_slow", "inform")),
    ("8_Decision-Making-Foundations",
     ReadingPathTuple("split_image_text", 1, "comparison_pair", "moderate", "inform")),
    ("9_Comparing-Expected-Value-and-Expected-Utility",
     ReadingPathTuple("two_pane", None, "comparison_pair", "dense", "inform")),
    ("11_Value-Creation-in-Innovation",
     ReadingPathTuple("multi_column", None, "enumerated_process", "dense", "inform")),
    ("13_Effective-Problem-Solving-Approach",
     ReadingPathTuple("multi_column", 1, "enumerated_process", "dense", "inform")),
    ("15_Types-of-Motivation",
     ReadingPathTuple("split_image_text", 2, "comparison_pair", "moderate", "inform")),
    # 17_ : operator DENY -> D1 (multi_column, peer_boxes)
    ("17_Examples-of-Effective-Leadership-in-Public-Health",
     ReadingPathTuple("multi_column", 2, "peer_boxes", "dense", "inform")),
    ("18_The-Future-of-Public-Health-Leadership",
     ReadingPathTuple("single_text_block", None, "dense_exposition", "dense", "invite_response")),
    ("20_Resources-for-Entrepreneurship-and-Innovation",
     ReadingPathTuple("card_grid", None, "peer_boxes", "dense", "inform")),
    # 21_ : operator DENY -> D3 (peer_boxes, takeaway_imperative); primary key unchanged
    ("21_Key-Takeaways",
     ReadingPathTuple("split_image_text", 1, "peer_boxes", "moderate", "takeaway_imperative")),
    ("22_Next-Steps-Your-Path-Forward",
     ReadingPathTuple("card_grid", 4, "peer_boxes", "dense", "directive_cta")),
]


def build_demo_rows() -> list:
    """Build a SYNTHETIC (slide_id, emitted, gold) row set mirroring the held-out
    round: Claude's v1 "emitted" labels differ from gold on the 2 denied slides.

    - 17_ emitted as ``two_pane`` (kit proposal) -> primary-key MISS vs gold
      ``multi_column``.
    - 21_ emitted ``enumerated_process`` substructure (kit proposal) but the
      primary KEY (macro x image_role) is unchanged -> primary-key HIT; the
      text_substructure per-axis is the miss.

    Net: 13/14 primary-key = 0.929; macro 13/14; text_substructure 13/14.
    """
    emitted_overrides = {
        # 17_: kit proposed two_pane (oppositional MACRO read) -- the single macro
        # miss. text_substructure stays peer_boxes (matches gold) so the held-out
        # report's "macro 13/14, text_substructure 13/14 as INDEPENDENT single
        # misses" is faithfully reproduced.
        "17_Examples-of-Effective-Leadership-in-Public-Health": ReadingPathTuple(
            "two_pane", 2, "peer_boxes", "dense", "inform"
        ),
        # 21_: kit proposed enumerated_process + no callout_intent; macro/image unchanged.
        "21_Key-Takeaways": ReadingPathTuple(
            "split_image_text", 1, "enumerated_process", "moderate", "inform"
        ),
    }
    rows = []
    for slide_id, gold in _GOLD_14:
        emitted = emitted_overrides.get(slide_id, gold)
        rows.append((slide_id, emitted, gold))
    return rows


def main() -> None:
    rows = build_demo_rows()
    report = score(rows)
    print("=" * 72)
    print("P2-4b conformance score -- SYNTHETIC demo (mirrors held-out round)")
    print("=" * 72)
    for line in report.summary_lines():
        print(line)
    print("-" * 72)
    for line in report.confusion_lines():
        print(line)
    print("=" * 72)


if __name__ == "__main__":
    main()

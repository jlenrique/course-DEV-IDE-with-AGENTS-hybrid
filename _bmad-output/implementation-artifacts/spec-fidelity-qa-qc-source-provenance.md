# Spec — Source-fidelity QA/QC (Gamma numeric-preserve + downstream provenance audit)

**Status:** ready-for-dev
**Class:** S (substrate) · **Authority:** operator directive 2026-06-24 (implement at Gamma + downstream now); fidelity findings from trial `c2c6dcbf` narration-vs-source comparison.

## Problem (witnessed, trial c2c6dcbf)

Comparing the delivered narration to Tejal's source corpus (notes-only slides):
- **Faithful:** 73-day doubling, 66%/two-thirds AI, burnout-as-design, navigate-the-enterprise, the burnout knowledge-check — core claims preserved.
- **Number drift / invention:** narration said **$4.5T** (source: **$5.2T**), invented **"60%→35%"** independent practice (source: "fell drastically", no numbers), **"$760B–$1T"** waste (source narration: "25%"; figure traces to the *cited* Shrank study, not the narration).
- **Added frameworks:** Speaker 7's AI-oversight taxonomy, Speaker 11's five leadership dimensions — substantive structure with no source hook.

**Root cause of the number drift:** the figure-citation gate guarantees narration numbers ⊆ the **rendered Gamma slide** — NOT ⊆ the **source**. Gamma re-mints figures during rendering (the run passed with 0 figure-contradictions, so $4.5T *was* on the slide — Gamma drew it). There is currently **no gate that keeps the slide/narration faithful to the source corpus.**

## Principle

> **Compose freely; assert only what's sourced.** The pipeline may phrase, sequence, bridge, and frame (cluster-arc work — *required* with notes-only source). But every *checkable assertion* — numbers, named studies, named examples, specific magnitudes — must trace to the source, OR be a **declared, sanctioned supplement** (see provenance model).

The gate targets **facts, not form.** It must NOT fight legitimate notes→coherent-prose composition.

## Provenance model (the core abstraction — operator-directed)

Every checkable assertion (esp. numerics + named entities) is classified into one provenance bucket:

| Provenance | Meaning | Fidelity treatment |
|---|---|---|
| `source-derived` | Traces to a number/claim in the source corpus (within tolerance) | Expected. Scored as faithful. |
| `research-supplement` | A **sanctioned** addition a lesson plan / operator decision / research input called for; NOT in source but deliberately added with its own citation | **Does NOT count against fidelity.** **Reported as its own category** with provenance/citation. |
| `unsourced-elaboration` | Neither in source nor declared as a supplement | **Flagged** — this is the only class the gate penalizes. |

**Research seam (leave open per operator):** the model carries a `research-supplement` channel from day one, but it is *populated later*. A future research input (Tracy / research pipeline) declares its supplements + sources; those assertions carry `provenance=research-supplement` + a citation and are surfaced-and-attributed, never penalized. Until then, the channel is empty and everything is `source-derived` or `unsourced-elaboration`.

## Implementation — two levels (both now)

### L1 — Gamma upstream: numeric-preserve in the brief (the cure)
Treat source numbers as **load-bearing** in the brief Gamma renders from. Instruct Gamma (and/or the brief assembler) to render source figures **verbatim** and not re-mint or "round" them — the same lever as variant B's `text_mode=preserve` for figure-bearing content.
- **AC:** for a figure-bearing source slide, the rendered Gamma slide's numbers == the source numbers (within exact-match for currency/percent tokens). Witness: re-render slide-1; assert "$5.2 trillion" (not $4.5T) appears.
- **Fence:** does not touch the G5 figure detector or the chosen-variant figure-citation gate.

### L2 — downstream: source-coverage provenance audit (the safety net)
After Pass-2, classify every narration assertion's provenance against the **source corpus**:
- **Numeric leg (gate-able, deterministic):** reuse the existing `app/specialists/_shared/figure_tokens.py` extractor. Extract narration numeric tokens; classify each vs source-corpus numbers → `source-derived` | `research-supplement` (if declared) | `unsourced`. **Ship as warn/AUDIT first** (log the drift rate + the offending tokens), not a hard block — measure before gating (Murat's doctrine; the $4.5T case is one witness, not a rate).
- **Semantic leg (audit/measure, not hard-gate):** a coarse source-coverage signal per run — rough % of substantive claims that trace to source vs net-new — with a **tripwire** (escalate if net-new trends up run-over-run). This is the instrumented "watch" for free-style/volume-padding, NOT a blocking semantic gate (would strangle notes→prose value).
- **Output:** a per-run **fidelity report** with the three provenance buckets + the numeric drift list + the semantic coverage signal. `research-supplement` items listed in their own section (not penalized).

## Phasing
1. **Now:** L1 numeric-preserve brief directive + L2 numeric audit (warn) + the provenance report skeleton (with the empty research-supplement channel). All reuse existing substrate (figure_tokens, the brief assembler).
2. **Now:** L2 semantic coverage signal + tripwire (measurement only).
3. **Later (research lands):** populate the `research-supplement` channel; only then consider promoting the numeric audit from warn → gate, once a measured drift rate justifies it.

## Honesty / governance
- Measurement-first: the numeric audit ships as **warn/report**, not a hard block, until a measured drift rate justifies gating. No "0 ghost-vs-source" claim off n=1.
- Reuse `figure_tokens` (shared deterministic neck — touching it is governance, not refactor; see `figure-tokens-frozen-neck-discipline`).
- **G5 figure detector + the chosen-variant figure-citation gate UNTOUCHED** (this is a NEW, source-facing layer, orthogonal to the slide-facing gate).
- NEW CYCLE per substrate story; party green-light the scope (it's a new QA layer + a Gamma-brief change).

## Party-mode GREEN-LIGHT (2026-06-24) — 4/4 GREEN-WITH-AMENDMENTS, no impasse
John / Winston / Murat / Mary all GREEN-with-amendments. Binding amendments folded:
- **F1 (John+Murat):** committed scope = **L1 (Gamma numeric-preserve) + L2-numeric audit (WARN) + empty provenance-channel stub.** L2-semantic = **measurement-only, explicitly NON-GATING, labeled experimental**; NO tripwire thresholds tuned until **≥3 runs** exist; the threshold + run-baseline are **written down now** or "trends up" is unfalsifiable. "Warn" must not creep to "gate" without a measured drift rate.
- **F2 (Murat):** the fidelity report MUST be a real witness — (1) **non-zero numeric-token denominators** from narration AND source (else **FAIL, not PASS**), (2) per-token classification with the **offending value pairs** ($4.5T vs $5.2T), (3) computed **drift rate**, (4) the **three buckets explicitly counted** incl. an **empty-but-present** research-supplement section.
- **F3 (Mary) — KEY:** split `unsourced-elaboration` into **`unsourced-numeric/named-entity`** (the credibility risk) vs **`unsourced-framing/structure`** (sanctioned composition) **from day one** — else the empty research channel makes the audit read coherent prose (Speaker-7 taxonomy, Speaker-11 dimensions) as drift beside real errors ($4.5T), and the rate is uninterpretable.
- **F4 (Winston):** the L2 numeric leg is a **pure read-only caller of `figure_tokens._figures`/`_normalize_figure`** — **no signature change, no new state, ZERO edits to `figure_tokens.py`** (frozen neck, now 3 readers). Source-corpus-extraction extras go in the **new L2 module**, never by mutating the neck.
- **F5 (Winston):** source-facing layer, **orthogonal to** the slide-facing G5 / chosen-variant figure-citation gate (different referent: source corpus vs rendered slide; different lifecycle: warn-first). **G5 + the figure-citation gate UNTOUCHED.**

**Status: ready-for-dev (own NEW CYCLE).** Research-supplement channel = stub now; plug-in mechanism (lesson-plan directive field vs Tracy artifact) deferred until research lands.

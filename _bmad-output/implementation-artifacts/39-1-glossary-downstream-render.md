---
anchor_provenance: post-37-2b working tree  # (A-1 fold) code anchors (e.g. _act.py L880/L957) verified against the POST-37-2b WORKING TREE, not baseline 5938bb7d; 37-2b is IN FLIGHT — re-verify all "37-2b-contract-bound" seams at dev-open against landed code
---

# Story 39.1: Glossary downstream of the deep-dive — term-keyed encyclopedia render

Status: ready-for-dev  <!-- green-lit 2026-07-15: 4/4 GREEN-WITH-AMENDMENTS; split ratified — Package B lifted to 39-1b-exercise-merge-composition.md -->

## Story

As the learner,
I want key terms bolded where they appear in the Deep Dive and defined in a dedicated encyclopedia section — with real headwords, honest tiers, and honest "uncovered" handling,
so that I get vocabulary-for-status without back-matter I never reach.

## Scope-budget verdict — SPLIT RATIFIED at green-light (2026-07-15, 4/4 unanimous)

This story originally carried TWO ratified work packages: **(A) glossary downstream render** (Epic-39.1 ACs + rider J-F3 quality mandate) and **(B) the D2 MERGE exercise composition** (wave record §D2). The green-light party APPROVED the author's split recommendation unanimously: **A stays as 39-1 (this story); B lifted verbatim into `39-1b-exercise-merge-composition.md`**, strict-serialized after 39-1 on the shared files (`_act.py`, `workbook_producer.py`). Both stories MUST land before governed **run A** (the batch boundary is "after 37-2b + 39-1 + 39-1b"); 39-1b is purely deterministic (no LLM surface, no live probe of its own) so it boards run A on suite-green alone, with its own per-story verdict line. The ~5 intentional pin flips in existing workbook-producer tests land in 39-1b's diff, never this one's.

## Dependency Position

`… 38-1 ✅ → 37-2b (IN FLIGHT) → **39-1 (this)** → 39-1b (split; strict-serialized) → 38-2 → 39-2 → 40-1`

Hard dep: **37-2b** (the enriched deep-dive's canonical bolded-term set + `deep_dive_enrichment` contract). 37-2b is currently `in-progress` under another dev agent — every seam below marked **37-2b-contract-bound** cites the 37-2b SPEC (`_bmad-output/implementation-artifacts/37-2b-deep-dive-enrichment-cited.md`, incl. its 13 folded green-light amendments) as the authority and MUST be re-verified at dev-open against landed code. 39-1 does not open dev until 37-2b closes. Batched governed **run A** (after 37-2b + 39-1 + 39-1b) is this story's full-pipeline witness per the Paid-Run Economy Protocol.

## T1 Readiness (BINDING readings before any code)

1. **Epics doc** — `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md`: Story 39.1 ACs (L185–192), FR11 coverage row (L41), green-light amendments A5 (re-point 39.1 → Ask-A digest, L228), A9 golden semantics/gate taxonomy (L232), SHOULD amendment "pull the term-highlight MD→DOCX decision into 39.1 T1 with a plain-bold fallback" (Winston SF-3, L236).
2. **Wave party record (BINDING)** — `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md`: §D3 Paid-Run Economy Protocol (§D2 MERGE design items 1–7 now belong to `39-1b-exercise-merge-composition.md` per the ratified split) (zero-witness probe→freeze→replay→spend; probe honesty contract; live-shape fixtures only; same-diff deliverable bar with negative pins; batch attribution; `done-awaiting-live-witness` vocabulary).
3. **Quality mandate** — `party-closure-record-38-1-38-3a-2026-07-15.md` rider J-F3 + `epic-38-retro-2026-07-15.md` §Challenges 3: keyword-mangled headwords, tangential 0.10–0.25-reliability citations, cross-sectional study carrying `tier=T1_systematic`. Coupled deferred entry `research-quality-resolvable-doi-yield` (retro: "bundle with 39.1 / next research-quality batch") — the TIER-LABEL ACCURACY fix is upstream research-quality work; this story's obligation is RENDER HONESTY (AC-A4), and the story author has filed the coupling verdict in Scope Fences.
4. **37-2b SPEC contracts (37-2b-contract-bound)** — `37-2b-deep-dive-enrichment-cited.md`: AC4 bold-term continuity (skeleton set preserved exactly; additions only when pool-traced), AC1 `deep_dive_enrichment.py` contract, AC6 render + `## Deep Dive` section + `_assert_completed_workbook_deliverable` extension + `tests/live_witness_replay/` registry founding, amendments J1 (row d′ honest-decline degraded), A2 (real `AskAKnowledgeEntryV1`, field `evidence_hierarchy_tier`). **Verify each at dev-open against landed code.**
5. **Pipeline-lockstep regime doc** — `docs/dev-guide/pipeline-manifest-regime.md`. Checked against `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (L60–110) for EVERY file scoped below: **NO trigger path is touched** (see Lockstep declaration). If mid-dev scope drifts into `workbook_wiring.py`, `research_packet.py`, `production_runner.py`, or the manifest — STOP, re-open T1, party-gate.
6. **M-R2 BINDING rider (Epic-38 retro §Challenges 4)** — **checked: DOES NOT APPLY.** No path under `app/specialists/irene_pass1/` is in scope. Any mid-dev drift into it is a STOP: re-open T1 with the M-R2 reading.
7. **Live shapes** — `runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4/ask-a-research-call.v1.json` (the REAL 1-row pool: `ask-a-cite-001`, tier `T4_peer_other`, `supports_bold_terms` = ["AI"] — **THIN is the launch case, first-class**) and `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627/exports/workbooks/u01@1.md` L148–218 (the actual mangled headwords, e.g. L150 `### institutional approach support conduct use health`; L190 the `tier=T1_systematic` cross-sectional row `cite-003`).

## Package A — Glossary downstream render (terms = the 37-2b bolded set)

### Acceptance Criteria

1. **Term-keyed generation — exactly the bolded set, from the Ask-A pool, no re-research**
   - **Given** the enriched deep-dive's canonical bolded-term set (**37-2b-contract-bound**: 37-2b AC4 — skeleton `bold_terms` preserved exactly, pool-traced additions only; skeleton contract `deep_dive_projection.py` `BoldTermMarker` L146 / `bold_terms` L217) **When** the glossary is projected **Then** `app/marcus/lesson_plan/glossary_projection.py` gains a term-keyed projection (`project_glossary_entries_for_terms(bold_terms, packet)`): exactly ONE entry per bolded term, headword = the bolded term **byte-exact**; entries compose ONLY from Ask-A pool rows whose `supports_bold_terms` contains the term (`ask_a_enrichment.py:240`; association language is "association-covered" per 37-2b amendment J3 — token-match, never claimed semantic). Pool intake is `resolve_for_enrichment_pool(run_dir)` (`research_packet.py:332`, **read-only import — no research_packet.py edit**), packet digest witnessed identically (A5 re-point: 39.1 → Ask-A digest). The legacy generic-packet path (`resolve_for_glossary_writer` → `_term_from_title` title-mangling, `glossary_projection.py:81–94`) is REMOVED from the learner deliverable; `glossary_inputs_from_run` (L225) re-implements term-keyed or is replaced at its `_act.py:957` call site. **No new research dispatch of any kind** — the "optional targeted top-up" for uncovered terms is explicitly DEFERRED (see Scope Fences + deferred-inventory filing).
2. **Headword quality — the J-F3 mangle fix, pinned**
   - **Given** the real regression shape (u01@1.md L150/L164/L178: `institutional approach support conduct use health` etc.) **When** entries render **Then** no headword is ever derived from a paper title; the paper title appears INSIDE the entry as cited support ("the indexed work …"), never as the headword. A regression pin feeds the real 8b275e5b packet rows through the new projection and asserts the mangled strings can no longer appear as headwords (fixture derived from the real run — live-shape rule).
3. **Uncovered-term honesty — first-class (the 1-row launch case) + STATUS-DEPENDENT bold-term authority (W1/A-2 MUST) + lean uncovered render (J-1 MUST)**
   - **(W1/A-2) Bold-term authority is STATUS-DEPENDENT** — the projection reads the 07W.3 contribution status and picks its authority accordingly: **enriched** ⇒ authority is `result.bold_terms`; **degraded-with-skeleton** ⇒ authority is `result.request.skeleton.bold_terms`, and ALL entries render uncovered-honest (row-e style) with the degradation reason surfaced; **no contribution / no skeleton** ⇒ the section renders explicitly-empty with reason `bold-term authority absent`. (Matrix rows d and d′ pin the last two branches deterministically.)
   - **(J-1) Uncovered-entry render is LEAN:** each uncovered term gets its per-term `### <term>` heading + exactly ONE short line — "Key term from the Deep Dive. No research row in this run's pool covers it; no definition is invented." — with NO citation block, NO tier line, NO capability note per entry. The section lead carries ONE coverage line: "Research coverage this run: N of M terms". The typed loss `glossary_term_uncovered:<term>` stays per-term in the structured artifact (losses are artifact-side; the learner surface stays lean).
   - **Given** the real pool (1 row; only "AI" association-covered) **When** a bolded term has NO supporting pool row **Then** its entry renders per the J-1 shape above; NO citation, NO invented definition, NO capability-note implication of research backing. Pool packet degraded/empty ⇒ ALL terms render uncovered-honest with the packet reason surfaced. Consistent with empty-honesty doctrine (Epic-38 retro) and 37-2b row-d/d′ semantics.
4. **Tier + provenance honesty — render what the row carries (J-F3 tiering pin)**
   - **Given** a covered term **When** its entry renders **Then** it preserves verbatim: `GLOSSARY_CAPABILITY_NOTE` (`glossary_projection.py:30`), `evidence_hierarchy_tier` EXACTLY as the row carries it (never re-derived, never upgraded, never suppressed), citation_id, source_ref/DOI, peer_reviewed, provenance, triangulation, reliability when present. The capability note gains one sentence declaring tier labels are upstream machine labels, not this renderer's verification. **J-F3 mislabel pin:** a fixture from the real `cite-003` row (cross-sectional study carrying `T1_systematic`, u01@1.md L190) pins that the renderer carries the label verbatim AND that the honesty sentence renders — the LABEL-accuracy fix itself is upstream (`research-quality-resolvable-doi-yield`, fenced below). **(M2 MUST) The `cite-003` fixture DECLARES its derivation transform** in the fixture file itself: which fields are verbatim from the real 8b275e5b W1 row and which are synthesized `ask-a-knowledge-entry.v1` association fields; the fixture is digest-bound to `schema_version` with the bump tripwire. Multi-row coverage: all supporting rows render, ordered by `citation_id` (deterministic).
5. **Inline marker ↔ encyclopedia section association — DECIDED: explicit headword-identity convention, plain-bold inline (MD + DOCX), tested on both surfaces**
   - **Decision (ratifies Winston SF-3's fallback as the v1 mechanism):** the association is an **explicit convention — headword identity**: each term is `**bold**` inline in the `## Deep Dive` prose (37-2b render), and the encyclopedia section (existing `## Research Glossary` H2, `workbook_producer.py:748–757`; retitled copy may say "Encyclopedia" but the block position/idiom stays) carries exactly one `### <term>` heading per bolded term, byte-equal to the bolded text. No MD anchor links and no DOCX bookmarks/`w:hyperlink` OOXML in v1 (python-docx has no first-class internal-link API; raw-XML plumbing is deferred as a filed follow-on, not smuggled in).
   - **MD test:** parse the composed markdown — the set of `**bold**` terms in the `## Deep Dive` block ↔ the set of `###` headwords in the glossary block are EQUAL (missing entry = FAIL; orphan entry with no inline bold = FAIL).
   - **DOCX test:** open the rendered `.docx` via python-docx and assert the same invariant from the document itself: every bold run text in the deep-dive region has a matching Heading-3 paragraph in the glossary region (`_render_docx_body` maps `###`→Heading 3 and `**…**`→bold runs, `workbook_producer.py:942–966` — both channels already survive the projection; the test proves it stays true). Inline `[ask-a-cite-###]` markers are excluded from the association set (they associate to References, 37-2b AC6).
6. **Render reversal — markers in prose, entries in their own section, provenance preserved**
   - **Given** FR11 + §6.2 **When** the workbook composes **Then** the trailing-block-only render is reversed: the deep-dive prose carries the inline bold markers (37-2b), the encyclopedia section carries the full entries (AC-A1–A4 shape), and every covered entry's `citation_id` resolves into the existing cited-references block (`#### Live-research cited entries (DOI)` idiom, u01@1.md L248–253) — resolvability floor only; References assemble/dedupe ownership stays with 37.5. The composed-MD/DOCX single-source-of-truth invariant (`workbook_producer.py:478–496`) is untouched.
7. **Deliverable bar extended in THE SAME DIFF (protocol plank 5) + negative pins**
   - Extend `_assert_completed_workbook_deliverable` (`scripts/utilities/marcus_spoc_live_test_runner.py:1318`, call site L1398 at baseline `5938bb7d`; 37-2b lands the deep-dive clause first — **37-2b-contract-bound**) with the glossary conformance clause, asserted off structured artifacts first, then MD: authored deep-dive with bolded terms ⇒ glossary section present, term↔entry association exact, uncovered terms carry the honest note; no authored deep-dive ⇒ explicitly-empty reason present. **Negative-witness pins in the same diff** (fed mutated copies of frozen live shapes; each must REJECT): (i) mangled title-derived headword present; (ii) bolded term with no entry; (iii) orphan entry; (iv) uncovered term carrying a citation; (v) entry whose tier differs from its pool row's.
8. **Deterministic verification — live-shape fixtures ONLY**
   - Every pool/render fixture derives from the two real runs (a940c5eb pool; 8b275e5b rendered workbook + packet rows) — no hand-invented shapes; digest-bound to `schema_version` with a bump tripwire. Mutation tests cover the full I/O matrix below. Focused suite + dependency regressions (37-2b suite incl. bold-parity gates, 37.2a 58-test suite, 38.1 Ask-A suites, `test_workbook_answer_leak_hygiene.py` 47 pins, run-dir threading floor), strict warnings, Ruff, import-linter (M3: `lesson_plan` never imports `marcus.orchestrator`), lockstep checker — all green; inherited failures compared by exact node/signature, never by count.
9. **(W2/M1 MUST — the probe claim depends on this seam) Additive references-emission seam**
   - **Given** covered glossary entries carrying `citation_id`s **When** the workbook composes **Then** glossary-covered rows are APPENDED into the existing `#### … cited entries (DOI)` block in `workbook_producer.py`, deduped by `citation_id` against the enrichment-emitted lines (a citation cited by both the deep dive and a glossary entry appears ONCE). This seam is explicitly scoped as the **resolvability floor** — additive emission only, NOT the 37.5 References assemble/dedupe redesign (that ownership fence stands). The probe's "resolving citation" claim (matrix row j) depends on this seam existing; without it, row j cannot be honestly green on a glossary-only citation.
10. **(W3) Post-writer headword invariant**
   - **Given** ANY glossary writer implementation behind the injectable `GlossaryWriter` seam (deterministic default today; possible SME-prose writer later) **When** a writer returns entry content **Then** the projection VALIDATES/OVERRIDES the headword AFTER the writer returns: headword == bolded term **byte-exact regardless of writer output** — the invariant is enforced at the projection layer, not trusted to the writer. Pinned with a mutant writer that returns a mangled headword; the rendered headword must still be the bolded term.

### I/O matrix (Package A — every row a pinned deterministic test)

| # | Input condition | Verdict / rendered outcome |
|---|---|---|
| a | term association-covered by ≥1 pool row | entry: term headword + capability note + verbatim tier/citation/provenance |
| b | term covered by MULTIPLE rows | all rows render, ordered by citation_id (byte-deterministic) |
| c | term with NO supporting row (launch case) | honest-uncovered entry per J-1 lean shape (`### <term>` + ONE short line; no citation/tier/capability note) + typed loss `glossary_term_uncovered:<term>` in the artifact; zero citations; section-lead coverage line "Research coverage this run: N of M terms" |
| d | no contribution AND no skeleton (bold-term authority absent) (W1/A-2) | section explicitly-empty, reason `bold-term authority absent` |
| d′ | degraded-with-skeleton contribution (W1/A-2) | authority = `result.request.skeleton.bold_terms`; ALL entries uncovered-honest (row-e style) with the degradation reason surfaced; deterministic pin (offline-only until a degraded live run exists — see Batch-run AC witness-gap declarations, M3) |
| e | pool packet empty/degraded | all terms uncovered-honest; packet reason surfaced |
| f | headword integrity | headword == bolded term byte-exact; title-derived headword impossible (J-F3 regression pin) |
| g | tier verbatim (J-F3 `cite-003` pin) | row's `T1_systematic` rendered verbatim + upstream-label honesty sentence; renderer never re-tiers |
| h | MD association | bold-set == headword-set (missing/orphan ⇒ FAIL) |
| i | DOCX association | same invariant proven from the rendered .docx |
| j | citation resolvability | every covered citation_id resolves into the cited-references block |
| k | row missing source_ref/provenance | skipped into known_losses (existing idiom, `glossary_projection.py:206–213`), term degrades to uncovered-honest |

## Package B — MOVED to 39-1b (split ratified at green-light 2026-07-15, 4/4 unanimous)

**Package B (the D2 MERGE exercise composition — 7 ACs + 5-floor I/O matrix) lifted verbatim into [`39-1b-exercise-merge-composition.md`](39-1b-exercise-merge-composition.md).** 39-1b is strict-serialized after this story (shared files `_act.py` + `workbook_producer.py`; 39-1 MUST land first), boards run A on suite-green with no probe of its own (fully deterministic), and carries a separate per-story verdict line on run A. The ~5 intentional pin flips in existing workbook-producer tests land in 39-1b's diff, never this one's.

## Probe registration (BEFORE it runs — probe honesty contract, D3)

- **Probe id:** `probe-39-1-glossary-render-001`.
- **Exact claim licensed:** "the term-keyed glossary render, fed the frozen REAL Ask-A pool (a940c5eb, 1 row) and the landed 37-2b bolded-term set for that lesson, produces a workbook whose encyclopedia section carries exactly the bolded terms as headwords — 'AI' association-covered with verbatim T4 tier + resolving citation, every other term honest-uncovered — with the MD and DOCX association invariants green." It licenses NOTHING else (not "the pipeline works", not exercises, not run A).
- **Vehicle:** deterministic replay-render probe (no LLM surface in this story — the glossary writer stays the deterministic default; the injectable `GlossaryWriter` seam is preserved for a future SME-prose writer). One-shot script mirroring the `run_deep_dive_38_3a_live_evidence.py` immutable-attempt-dir discipline.
- **Deterministic machine judge:** the Package-A I/O-matrix gates + the deliverable-bar glossary clause — no human vibes.
- **Evidence pack:** immutable attempt dir under `_bmad-output/implementation-artifacts/evidence/` with input digests (pool packet digest, bolded-term-set digest, renderer config identity), rendered MD+DOCX, machine verdict JSON.
- **First-run-stands.** A failed probe is preserved immutably and remediated under governance. On PASS the output **freezes as this path's witness fixture** and enrolls in `tests/live_witness_replay/witnesses.yaml` (registry founded by 37-2b — **37-2b-contract-bound**; if the registry has not landed, this story STOPS and reconciles rather than founding a parallel one).
- The probe's "resolving citation" clause presupposes the AC-A9 additive references-emission seam (W2/M1) — the probe is not registered as green unless that seam is landed in the same diff.
- 39-1b (Package B, split) needs no separate probe (fully deterministic); its M-D2-2 replay pin + suite-green satisfy the boarding rule for run A.

## Batch-run AC — governed run A (full-pipeline claim)

When deterministic suite + probe + `bmad-code-review` are green, this story flips to `done-awaiting-live-witness  # deterministic+review green; component probe probe-39-1-glossary-render-001 green; full-run witness owed by batch run A (after 37-2b + 39-1 + 39-1b)`. Run A pre-flight replays ALL enrolled witnesses in STRICT mode (`WITNESS_REPLAY_STRICT=1`; skip ⇒ fail) and records "replay GREEN, N witnesses, 0 skipped". Run A's evidence pack carries this story's per-verdict line keyed to the terminal `07W` render + the glossary deliverable-bar clause: REACHED+PASS ⇒ flip to `done` citing the run id; NOT-REACHED ⇒ claim stays OPEN (never pass, never fail). This story never crosses two batch boundaries unwitnessed. Split ratified: 39-1b seats on run A with its own separate verdict line.

**Witness-gap declarations (M3 MUST — honesty about what run A can and cannot witness):**

- **Matrix row b (multi-row coverage) is OFFLINE-ONLY this wave.** The launch pool is 1 row (a940c5eb), so run A CANNOT exercise multi-row coverage — a green run A must NOT be read as implying row b live-witnessed. Row b's claim rests solely on its deterministic pin until a multi-row live pool exists.
- **Matrix row d′ (degraded-with-skeleton) is deterministic-only until a degraded live run exists.** No live degraded-contribution run is on disk; the d′ pin is the only witness this wave, declared as such — never claimed live-proven.

## Scope Fences (hard NO)

- NO new research dispatch: the "optional targeted top-up" for uncovered bolded terms is DEFERRED — file `glossary-uncovered-term-targeted-topup` in deferred-inventory §Named-But-Not-Filed at story close (direction-may-flip caveat). Uncovered terms render honest-uncovered, full stop.
- NO tier-label accuracy fix (the J-F3 mislabel ROOT CAUSE): upstream research-quality work — rides `research-quality-resolvable-doi-yield` (retro coupling verdict recorded there). This story renders labels honestly; it does not re-audit them.
- NO trends/Door-Ajar changes (the mangled-headword defect ALSO lives in `trends_projection.py` — that fix is 39.2's; note it in 39.2 grooming, do not drive-by).
- NO Ask-B / `07W.4` (38.2); NO References assemble/dedupe redesign (37.5); NO mode-parity (37.6); NO cover (40.1).
- NO `app/specialists/irene_pass1/` changes (M-R2 fence).
- NO edits to `workbook_wiring.py`, `research_packet.py`, `production_runner.py`, `state/config/pipeline-manifest.yaml`, or any node/manifest/pack-version/learning-event surface (= undeclared lockstep expansion → STOP, party-gate). Pool access is read-only via the existing `resolve_for_enrichment_pool`.
- NO machine semantic dedup of exercises (ratified reject); NO DOCX bookmark/hyperlink OOXML plumbing (filed follow-on `workbook-docx-internal-links`); NO LLM glossary writer (seam stays injectable, deterministic default).
- NO weakening of: the terminal `07W` model-free pin, G2 citation gate, VO↔on-screen protected invariants, the 47 answer-leak pins.

## Lockstep declaration

Checked every scoped file against `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (L60–110):

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/lesson_plan/glossary_projection.py` | not listed | yes (Package A core) |
| `app/marcus/lesson_plan/workbook_producer.py` | not listed | yes (glossary section render + references-emission seam AC-A9, bar-adjacent) |
| `app/specialists/workbook_producer/_act.py` | not listed | yes (glossary intake; the attach-seam MERGE moved to 39-1b) |
| `app/marcus/lesson_plan/workbook_enrichment.py` | not listed | **NO — moved to 39-1b** (origin stamp) |
| `app/marcus/lesson_plan/collateral_spec.py` | not listed | **NO — moved to 39-1b** (origin field) |
| `scripts/utilities/marcus_spoc_live_test_runner.py` | not listed | yes (deliverable bar) |
| `app/marcus/lesson_plan/research_packet.py` | **L110 — trigger** | **NO** (read-only import) |
| `app/marcus/orchestrator/workbook_wiring.py` | **L109 — trigger** | **NO** |
| `app/marcus/orchestrator/production_runner.py` | **L106 — trigger** | **NO** |
| `state/config/pipeline-manifest.yaml` | **L61 — trigger** | **NO** |

**Verdict: zero trigger paths touched — lockstep regime not triggered.** Regime doc still read at T1 (item 5); any drift into a trigger row is a STOP.

## Gate taxonomy (A9)

| Gate | Disposition | Witness | Owner |
|---|---|---|---|
| Term↔entry association, MD + DOCX (A-matrix h,i) | FAIL | automated | 39.1 |
| Headword integrity / J-F3 mangle regression (f) | FAIL | automated pin | 39.1 |
| Uncovered-term honesty / empty-honesty (c,d,e) | DEGRADE (typed) | automated | 39.1 |
| Tier verbatim + upstream-label honesty sentence (g) | FAIL | automated (`cite-003` pin) | 39.1 |
| Citation resolvability into references block (j) | FAIL | automated | 39.1 |
| Tier-label ACCURACY (semantic) | NOT OWNED | upstream (`research-quality-resolvable-doi-yield`) | fenced |
| Headword-CLASS quality (J-2: figure-emphasis bolds, e.g. `### 25%`, rendering as headwords) | SPOT-CHECK (declared) | operator spot-check at run A; follow-on `deep-dive-bold-term-class-curation` filed at story close | 39.1 (declared) / follow-on |
| Citation resolvability seam (AC-A9, W2/M1) | FAIL | automated (dedupe-by-citation_id pin) | 39.1 |
| Post-writer headword invariant (W3) | FAIL | automated (mutant-writer pin) | 39.1 |
| Deliverable bar: glossary clause + 5 negative pins | FAIL | automated (harness side) | 39.1 |
| Exercise floors + composition (B-matrix) | FAIL | automated | **39-1b** (split) |
| Residual exercise duplication (D2.6) | WARN | operator spot-check at run A (declared) | **39-1b** (split) |
| Answer-leak (`Correct Answer:` in prompt) | FAIL | automated (47-pin floor re-run) | inherited c0811817 |
| Trends headword quality / Door-Ajar | NOT OWNED | downstream | 39.2 |

## Dev Notes

- **Code map:** UPDATE `glossary_projection.py` (term-keyed projection + J-1 lean honest-uncovered entry + capability-note sentence + W3 post-writer headword override; retire `_term_from_title` from the deliverable path); UPDATE `_act.py` (glossary intake — see intake-ordering note below; the `:859–882` attach-seam MERGE moved to 39-1b); UPDATE `workbook_producer.py:748–757` (glossary section render) + the `#### … cited entries (DOI)` block (AC-A9 additive references-emission seam; the labeled-exercise-groups/`exercise_overlay_loss` work moved to 39-1b); UPDATE `marcus_spoc_live_test_runner.py` (glossary bar clause + negative pins, same diff — anchor re-verified against the post-37-2b tree per the A-1 provenance header); NEW probe script; tests under `tests/unit/marcus/lesson_plan/` + `tests/specialists/workbook_producer/`; fixtures under `tests/fixtures/glossary_39_1/` derived from the two real runs.
- **(A-3) Intake ordering — hoist the 07W.3 contribution load ABOVE the glossary intake in `_act.py`:** the contribution load (~L1005 post-37-2b) and the glossary intake (~L957) live in the SAME function; move the contribution load above the glossary intake so the status-dependent authority read (AC-A3, W1/A-2) is served from ONE disk read — do not read the artifact twice.
- **(A-3) Intentional pin flips enumerated for THIS story's diff:** `test_glossary_w2.py` + `test_workbook_w4_empty_honesty.py` (expectation updates driven by the term-keyed projection + J-1 lean uncovered render + row-d/d′ authority semantics). Enumerated per-test in the diff description, never drive-by. The ~5 workbook-producer exercise pin flips are 39-1b's, never this diff's.
- **(A-3) Pool join:** prefer the digest-verified EMBEDDED `result.request.pool_rows` join (already carried in the 07W.3 artifact) over re-resolving the packet via `resolve_for_enrichment_pool` — one authority, no re-resolution drift; the packet digest is still witnessed identically (A5 re-point).
- **(J-2) Follow-on to file at story close:** `deep-dive-bold-term-class-curation` in deferred-inventory §Named-But-Not-Filed (direction-may-flip caveat) — headword-CLASS curation (figure-emphasis bolds like `25%` should arguably not become encyclopedia headwords) is a curation question upstream of this renderer; this story renders the authority set faithfully and declares the class-quality gate as an operator spot-check at run A. Do NOT widen scope to solve it here.
- **Bold-term set source (37-2b-contract-bound):** read the ENRICHED result's term set from the persisted 07W.3 artifact per 37-2b AC1/AC4, status-dependent per AC-A3 (W1/A-2) — join by digests, never by prose scraping. Exact artifact path/model name verified at dev-open.
- **DOCX region identification for the AC-A5 test:** delimit the deep-dive and glossary regions by their H2 headings in the composed model (the same `doc.blocks` source both surfaces render from) — do not regex the raw .docx XML.
- **Guardrails:** product work only (SPOC — nothing lands "so the probe passes"); M3 wall (`lesson_plan` never imports `marcus.orchestrator`); terminal `07W` stays deterministic-consume; first-run-stands on every live leg; carrier robustness — additive-safe, fail-loud, no silent drops.

### References

- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` — Story 39.1 (L185–192), FR11 (L41), A5/A9/SF-3 (L228/232/236), graph-shape record (L243–268)
- `_bmad-output/planning-artifacts/wave-3940-kickoff-party-record-2026-07-15.md` — §D2 (items 1–7), §D3 planks + amendments, wave run plan
- `_bmad-output/implementation-artifacts/37-2b-deep-dive-enrichment-cited.md` — bolded-term + enrichment contracts (incl. 13 folded amendments) — **the 37-2b authority for every contract-bound seam**
- `party-closure-record-38-1-38-3a-2026-07-15.md` (rider J-F3) · `epic-38-retro-2026-07-15.md` (§Challenges 3, doctrine)
- `runs/a940c5eb-1043-42c1-a2a4-8a6301b6bcf4/ask-a-research-call.v1.json` · `runs/8b275e5b-ed8a-4720-8217-8ddaca4c6627/exports/workbooks/u01@1.md` — live shapes
- `docs/dev-guide/pipeline-manifest-regime.md` · commit `c0811817` (answer-leak strip + 47-pin precedent)

## Green-Light Round Record (2026-07-15)

- **Verdict: 4/4 GREEN-WITH-AMENDMENTS** — Winston (architecture), John (PM), Amelia (dev), Murat (test architecture); two combined-lens reviews.
- **Split: unanimous.** Package A stays as this story (`39-1-glossary-downstream-render.md`); Package B lifted verbatim into [`39-1b-exercise-merge-composition.md`](39-1b-exercise-merge-composition.md), strict-serialized after 39-1 on the shared files (`_act.py`, `workbook_producer.py`). Both seat on governed run A with separate per-story verdict lines; 39-1b boards on suite-green (no probe — fully deterministic).
- **Amendments folded into 39-1 per finding id:** W1/A-2 (status-dependent bold-term authority — AC-A3 + matrix rows d/d′), W2/M1 (additive references-emission seam — AC-A9, before probe registration; probe claim depends on it), J-1 (lean uncovered-entry render + section-lead coverage line — AC-A3 + matrix row c), W3 (post-writer headword invariant — AC-A10 + gate row), M2 (`cite-003` fixture derivation-transform declaration, digest-bound — AC-A4), M3 (witness-gap declarations: row b offline-only this wave, row d′ deterministic-only — Batch-run AC), J-2 (headword-CLASS gate-taxonomy row = declared operator spot-check at run A + `deep-dive-bold-term-class-curation` follow-on filed at story close — Gate taxonomy + Dev Notes), A-1 (provenance header corrected: anchors verified against the post-37-2b working tree, not baseline `5938bb7d`), A-3 (Dev Notes: 07W.3 contribution-load hoist above glossary intake — one disk read; `test_glossary_w2.py` + `test_workbook_w4_empty_honesty.py` added to the enumerated intentional pin flips; prefer the digest-verified embedded `result.request.pool_rows` join over re-resolving the packet).
- **Amendments folded into 39-1b per finding id (recorded there):** Murat deliverable-bar exercise clause + negative pins (D3 plank 5), J-3 (round-robin cross-unit collateral trim rule, pinned against the real 18→12 shape), split riders, pin-flip ownership (~5 flips in 39-1b's diff only).
- **Orchestrator concurred — party-consensus-=-approval** (solo-operator rule, CLAUDE.md): status flipped to **ready-for-dev** without a redundant human hold (dev-open still gated on 37-2b closing).

## Change Log

- 2026-07-15 (later): Party green-light round complete — 4/4 GREEN-WITH-AMENDMENTS; split ratified unanimously (Package B → `39-1b-exercise-merge-composition.md`); amendments W1/A-2, W2/M1, J-1, W3, M2, M3, J-2, A-1, A-3 folded per finding id (see Green-Light Round Record). Status flipped **draft → ready-for-dev**.
- 2026-07-15: Story authored downstream of 37-2b (in flight; all 37-2b seams contract-bound, verify at dev-open). Encodes: term-keyed glossary from the Ask-A pool (A5 re-point), J-F3 headword/tier honesty pins, first-class uncovered-term honesty (1-row launch pool), decided MD↔DOCX association (headword-identity convention, plain-bold, dual-surface tested), ratified D2 MERGE composition (5 floors + origin + cap + loss + collision guard), probe `probe-39-1-glossary-render-001` pre-registered, run-A batch seat, zero-lockstep declaration, M-R2 not-applicable. **Split recommendation on record: lift Package B to 39-1b at green-light.** Status: **draft** pending party green-light round.

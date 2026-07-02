# Story: Leg-E — `gamma_docs` live-doc audit (Texas RetrievalAdapter + audit driver + first real learned-store writes)

**Status:** ready-for-dev
**Arc:** Gamma Styleguide Library, Phase-1 final leg (operator feature #1: styleguide AUDIT). **Branch:** `dev/gamma-styleguide-leg-e-2026-07-02`.
**Gate mode:** dual-gate (Murat structural + Dan/Texas content).
**Authority:** GREEN-LIGHT party record `_bmad-output/planning-artifacts/leg-e-gamma-docs-audit-greenlight-party-record-2026-07-02.md` — RATIFIED 6/6; ALL amendments + synthesis rules S-1..S-4 are BINDING on this spec. Read that record in full at T1 before any code.

## Story

Build a Texas `gamma_docs` RetrievalAdapter (Shape-3 retrieval, `kind="direct_ref"`) that fetches Gamma's live documentation as raw markdown, plus an audit driver that compares the DOCUMENTED tier (live doc content) against code-authoritative frozen enums and doc-fact expectations, classifies every audit item into exactly one of three terminal states, and files the learned-store observations ledger's FIRST REAL WRITES (candidate-only, digest-idempotent) — so documented-vs-real drift (like the 401≠429 burst-throttle case) is caught by tooling before it bites a paid run.

## Grounded feasibility (Amelia live probe, 2026-07-02)

`developers.gamma.app` serves raw markdown: append `.md` to page URLs; `llms.txt` (5.9KB index) + `llms-full.txt` (221KB) both HTTP 200 to plain httpx, no JS, no auth, Cloudflare unchallenged. `skills/gamma-api-mastery/references/doc-sources.yaml` already catalogs 16 key `.md` pages. Probe already surfaced REAL image-model drift: `IMAGE_MODEL_VALUES` (`app/specialists/gary/_act.py:55`) contains `imagen-4-fast`, `qwen-image`, `qwen-image-fast` absent from the live docs page; live docs list ~10 models absent from the enum (flux-1-*, gpt-image-2*, imagen-3-pro, …).

## Acceptance Criteria

**Offline (hermetic, RED-first — every AC's tests written failing before the code):**

- **AC#1 Adapter.** `skills/bmad-agent-texas/scripts/retrieval/gamma_docs_provider.py`: `GammaDocsProvider(RetrievalAdapter)`, `PROVIDER_INFO(id="gamma_docs", shape="retrieval", auth_env_vars=[], notes=...)`. Notes declare BOTH the doc-audit purpose ("doc-audit tooling — not a course-content retrieval source") AND the three intentional degeneracies (pass-through `formulate_query`; `refine()`→None; cross-validate N/A) per anti-pattern #3. Pure leaf: ZERO `app.*` imports, zero writes, no clock, no LLM, no retry. `identity_key` = canonical doc URL (fragment/query stripped). `params: {pages: [...]}` only. TexasRow: `source_id`=canonical URL, `body`=fetched markdown (decoded UTF-8 explicitly, unicode-normalized), `source_origin="operator-named"`, honest `completeness_ratio`/`structural_fidelity` (None + `known_losses` sentinels when partial), `provider_metadata.gamma_docs` = {doc_url, fetched_at, http_status, content_sha256 (over NORMALIZED extracted text, optionally raw_sha256), extraction_pattern, etag/last_modified when present, known_losses, page_title, content_length_chars}.
- **AC#2 Registration + conformance.** Eager import added to `retrieval/__init__.py` (scite precedent); parametrized entry appended to `ADAPTER_FACTORIES` in `tests/contracts/test_retrieval_adapter_base.py` (NO bespoke harness); the autoregister test observes `gamma_docs` NON-vacuously; NEW import-purity test: importing the `retrieval` package loads no `app.*` module (assert via sys.modules).
- **AC#3 Audit manifest (data, not code).** `skills/gamma-api-mastery/references/gamma-doc-audit-manifest.yaml`, URL set derived from + citing `doc-sources.yaml`. Item shape: `{item_id, kind: enum-parity|doc-fact|probe, code_ref (dotted importable name — NEVER value literals) | expected_documented (doc-fact only), doc_url, comparator: enum-membership|literal-presence|numeric, extraction: {…}, notes}`. Must include: enum-parity items covering EVERY frozen enum the validator's `_ENUM_CHECKS` reuses from `_act.py` (a test PINS this coverage); doc-fact items for rate-limit claims (429-on-burst, `x-ratelimit-remaining-burst` header, 5s polling), the list_themes limit-50 cap; the two `imageOptions` field-surface questions (discrete tags field? stylePreset⊕style composition documented?) as FINDINGS-ONLY items; a `changelog/readme.md` literal-presence canary; exactly ONE labeled `kind: probe` item pointing at a known-absent anchor (the live TEETH witness).
- **AC#4 Audit driver.** `scripts/utilities/audit_gamma_docs.py` (sys.path bootstrap precedent: `validate_gamma_style_guides.py:28-48`). Resolves the adapter THROUGH `provider_directory` dispatch with a `RetrievalIntent(kind="direct_ref", provider_hints=[{provider:"gamma_docs", params:{pages:[…]}}], iteration_budget=1)` — NEVER direct class instantiation (D-2 reachability pin test `tests/contracts/test_gamma_docs_audit_reachability.py`). Deterministic comparators only. Terminal-state TOTALITY (exactly-one-of-three; no exception escape; no partial-ledger crash). Classification per synthesis S-2: transport failure→indeterminate; anchor present + comparison fails→drift-detected; anchor/section ABSENT→drift-detected `kind: doc-restructure` (LOUD, non-zero exit, run-report only — NO ledger write); ambiguous multi-match or known_losses implicating the fact→indeterminate (can never mint confirmed). Enum-membership asymmetry: enum-value-absent-from-docs→drift-detected; documented-value-absent-from-enum→drift-detected `kind: coverage-gap` (distinct kinds). Exit tiers per S-3: 0 all-confirmed / 10 drift (NOT a failure semantic) / 20 VOID (pre-flight probe failed, all-indeterminate, or integrity failure). Pre-flight `llms.txt` probe → VOID-before-start if down; ZERO mid-run retries. Driver stamps `observed_at` + `doc-sources.yaml::last_refreshed`.
- **AC#5 Ledger writes per synthesis S-1.** drift-detected → always writes; confirmed → writes ONLY when resolving a STANDING candidate (cites its observation_id); indeterminate/doc-restructure → never. Each observation: Dan's wording-triple as a FILING GATE (DOCUMENTED claim + doc URL/date; OBSERVED reality + location; OPERATIONAL consequence — driver rejects-and-reports failures), `observation_id` = `obs-gamma-<claim>-<date>`, `birthing_run_ref` = real repo-relative evidence-dir path, real `observed_at`, `source_component` = the audit component path, `output_digest` = sha256 over (item_id, doc content_sha256, terminal_state, sorted diff) — so unchanged-docs re-run is a ledger NO-OP. Driver is the SOLE writer of `GAMMA_LEARNED_OBSERVATIONS_PATH`.
- **AC#6 Ledger/SSOT protection.** All ledger tests tmp_path-only; NEW static guard test: no `append_observation(GAMMA_LEARNED_OBSERVATIONS_PATH, …)` anywhere under tests/; pin `gamma-learned-rules.lock` byte-identical + all Leg-E writes `status: candidate` + invisible to `apply_learned_rules`.
- **AC#7 Fixtures.** Recorded real-page fixtures under `tests/fixtures/retrieval/gamma_docs/` with provenance stamps (source_url, fetched_at UTC, content_sha256, selector) + README table — unstamped fixtures do not merge. All 3 terminal states reachable from fixtures. Per-test RequestsMock discipline + a no-stateful-mocks self-guard (mirror the scite test module exactly, including its location).
- **AC#8 Schema doc.** `provider_metadata.gamma_docs` subsection added to the extraction-report schema doc §Provider Metadata Sub-objects, same change-set; NO SCHEMA_VERSION bump (additive escape hatch by design).

**Live (indispensable; first-run-stands; no mocks; deterministic judge):**

- **AC#9 LIVE full-manifest audit** against real developers.gamma.app: every item reaches exactly one terminal state; per-item receipts (final URL, status, normalized-anchor sha256, fetched_at); terminal-state table; ledger before/after line counts + whole-file sha256; evidence dir `_bmad-output/implementation-artifacts/evidence/leg-e-gamma-docs-audit-<UTC>/`. Expected organic writes (probe-grounded): the image-model drift items; possibly the 401≠429 standing-candidate resolution. Zero-genuine-writes ⇒ escalate to the close party per John's liveness rider (never manufacture).
- **AC#10 LIVE TEETH:** the labeled probe item lands per S-2 with ZERO confirmed writes; run exits at the correct tier.
- **AC#11 Idempotent re-run:** immediate second run → 0 new ledger lines, byte-identical ledger digest; any state CHANGE between runs is recorded as a finding, not a do-over.
- **AC#12 Status honesty:** `PROVIDER_INFO.status` = `ready` ONLY in the change-set carrying this live proof (stub before).

## Out of scope (binding fences — John J-3 + Dan)

(1) No LLM/NLP/summarization anywhere. (2) No auto-updating frozen enums — drift FILES, humans change code. (3) No promotion machinery / CD ceremony (lock stays byte-identical). (4) No MCP server, no pipeline node, no production_runner/manifest touch. (5) No crawler — manifest-enumerated pages only. (6) No re-authoring `skills/bmad-agent-gamma/references/` or the gamma-api-mastery reference library (beyond the new manifest + last_refreshed stamp). (7) No keywords→imageOptions.style wiring — findings only. Plus: `--check-existence` hardening stays out (if reused, disclose its Studio-template + pagination gaps); `gamma-scripted-general-dead-config-detector` stays out.

## Conveyance no-touch pin (Dan D-7 — governance RED if violated)

Files-touched ALLOWLIST: `retrieval/gamma_docs_provider.py` (new) · `retrieval/__init__.py` (eager import) · `scripts/utilities/audit_gamma_docs.py` (new) · `skills/gamma-api-mastery/references/gamma-doc-audit-manifest.yaml` (new) · `doc-sources.yaml` (last_refreshed only) · extraction-report schema doc (additive subsection) · `app/specialists/gary/learned_dependencies.py` (DOCSTRING-ONLY: surgical D-9 disclaimer update — write path exercised live citing the evidence dir; ceremony/promotion REMAINS validated-by-fixture) · test files named in ACs + `tests/fixtures/retrieval/gamma_docs/` · `state/config/gamma-learned-observations.jsonl` (LIVE RUN ONLY, never tests) · the evidence dir. **Excluded absolutely:** `app/specialists/gary/_act.py`, all Irene modules, `state/config/gamma-style-guides.yaml` + thumbnails, production_runner, pipeline-manifest. Existing conveyance/instruction/keyword tests pass UNMODIFIED.

## Dev Notes

- Mirror `scite_provider.py` structure + its test module's location/discipline exactly. `AdapterFactory.get()` calls `cls()` no-args → default ctor with optional injected-client kwarg.
- httpx with polite UA (`bmad-gamma-docs-audit/0.1`), ≤1 req/s, one fetch per page per run. Decode `response.content` as UTF-8 explicitly; unicode-normalize before digest/match (GitBook `{% hint %}` tags present; console mojibake was a rendering artifact, payload is clean).
- Digest NORMALIZED selector-scoped text, never raw HTML/whole-page (CDN/build-hash churn = false drift).
- 401-during-audit = throttle signal (known Gamma gotcha) → transport-failure class → indeterminate, no retry.
- The three grandfathered seed observations keep their memory-citation birthing_run_refs; NEW writes use evidence dirs.
- Live proof may be executed by a fresh independent subagent under the strict validity protocol (deterministic judge, first-run-stands, no retry-to-green) per standing operator authorization.

## Tasks

T1 read party record + this spec + scite_provider + learned_dependencies → T2 RED battery (all ACs' tests failing) → T3 adapter → T4 manifest + driver → T5 GREEN battery + ruff → T6 3-lane `bmad-code-review` + RED-first remediation → T7 LIVE proof (AC#9–12, evidence dir) → T8 dual-gate CLOSE (Murat + Dan/Texas) → T9 deferred-inventory updates (promotion-path trigger noted FIRED; doc-restructure/coverage-gap follow-ons if found; J-6 expertise-ingestion adjacent story re-filed).

## Review Findings

**T6 3-lane `bmad-code-review` (Blind Hunter / Edge Case Hunter / Acceptance Auditor), 2026-07-02 — remediated RED-first on the uncommitted build.**

### Lane summary

Triage yield: **2 MUST-FIX + 9 SHOULD-FIX + NITs** (cheap NITs folded in as N1–N9; two findings DISMISSED, below). All three lanes independently **converged on the write-phase gap**: the exit tier (and the probe-integrity verdict) was computed AFTER the ledger-write loop, so a VOID run — the run the spec says certifies nothing — still wrote candidate observations and stamped `doc-sources.yaml::last_refreshed`.

### Remediation (every P-item RED-first: failing test recorded, then fixed)

- **P1 (MUST) Integrity/VOID write-gate.** Exit tier + `integrity_failure` computed BEFORE the write loop; a VOID run (any cause: integrity failure, all/partial-uncertified, zero real items) skips ALL ledger writes AND `stamp_doc_sources`. Report still records would-have-written rows (`ledger.would_write`). RED: `test_void_run_never_writes_ledger_or_stamps` (broken-probe-confirms + real-drift manifest wrote 2 rows + stamped at exit 20).
- **P2 (MUST) Manifest loader blank-expectation rejection.** `expected_documented` of None/empty/whitespace-only → fail-loud `ManifestError` at load. RED: `test_manifest_loader_rejects_blank_expected_documented[null|empty|whitespace]` (all three loaded clean; an empty literal is vacuously "present").
- **P3 Stamp gate** (subsumed by P1): `stamp_doc_sources` only when `not dry_run and exit_tier != EXIT_VOID`. RED: extended `test_exit_void_when_all_indeterminate` (503 path previously stamped).
- **P4 Write-phase totality.** New `_ledger_precheck_error` right after preflight (readable + every line parses as JSON; failure → report + exit 20, no traceback); write loop wrapped so an unexpected exception lands `ledger.write_phase_error` + report + 20. RED: `test_corrupt_ledger_precheck_voids_with_report` (bare `json.decoder.JSONDecodeError` traceback), `test_write_phase_exception_lands_report_and_void` (bare `RuntimeError` propagation).
- **P5 Standing-candidate verification.** Citations verified against `read_observations(ledger_path)` (pre-run state) before filing a standing-candidate-resolution or drift-with-`standing_candidate_ref`; miss → existing reject-and-report channel. RED: `test_standing_candidate_missing_from_ledger_is_rejected_not_filed` (empty ledger + `obs-DOES-NOT-EXIST` wrote a dangling citation). Tests that expect the standing write now seed the cited observation (`_seed_standing`), mirroring the real SSOT's grandfathered seed.
- **P6 Exit-tier aggregation — RATIFIED SPEC AMENDMENT to AC#4/S-3.** `probe` and `findings_only` items excluded from `compute_exit_tier`; the probe participates ONLY via the integrity check; findings-only items are report-only. Real items alone drive tiers (all real confirmed → 0; any real drift → 10; real uncertified without drift → 20; zero real items → 20; VOID causes unchanged). RED: `test_exit_zero_when_probe_and_findings_drift_but_real_confirmed` (healthy manifest exited 10), `test_exit_void_on_partial_outage_even_with_probe_drift` (probe drift masked an all-real-indeterminate outage as 10), `test_compute_exit_tier_excludes_probe_and_findings_only`.
- **P7 not-enumerated positive witness.** Empty token collection no longer mints confirmed — requires the scoped section non-empty beyond the anchor AND, when `witness_pattern` is declared, a match; else indeterminate (T-7). Manifest style-preset item: narrowing `line_pattern` dropped (collect over the whole scoped section with field-name/cross-ref `exclude_tokens`) + free-text witness sentence added. RED: `test_real_manifest_style_item_catches_enumeration_any_phrasing` ("Choose from `vivid` or `natural`" confirmed under the old `line_pattern`), `test_not_enumerated_empty_collection_needs_positive_witness` (gutted witness still confirmed).
- **P8 Content-shape honesty.** (a) Provider files a `content_type_not_markdown` known-loss when a 200's Content-Type is outside {text/markdown, text/plain, missing} — T-7 floor then forces indeterminate (live probe 2026-07-02: developers.gamma.app serves `text/markdown; charset=utf-8`, so honest pages pass). (b) Changelog canary strengthened to the line-anchored heading literal `"\n# "` (driver convention: a literal starting `"\n"` matches at start-of-line, including byte 0). RED: `test_changelog_canary_html_page_cannot_confirm` (200-HTML page confirmed), `test_gamma_docs_non_markdown_content_type_is_a_known_loss`, `test_changelog_canary_requires_line_anchored_heading`.
- **P9 Decode honesty.** Strict UTF-8 decode first; `UnicodeDecodeError` → `errors="replace"` + `decode_replacement` known-loss (floor → indeterminate); `normalize_doc_text` strips a leading BOM. RED: `test_gamma_docs_strict_utf8_decode_fallback_is_flagged`, BOM case in `test_gamma_docs_normalize_doc_text_helper`.
- **P10 Digest re-key — RATIFIED SPEC AMENDMENT to AC#5.** `output_digest` = sha256 over (item_id, per-item normalized ANCHOR-scope sha256 [`anchor_sha256`], terminal_state, sorted diff) — churn elsewhere on a shared page no longer re-files every item. `normalize_doc_text` also strips trailing whitespace per line. `observation_id` gains an 8-hex digest suffix (`obs-gamma-<slug>-<date>-<digest8>`) so same-day doc changes cannot mint duplicate ids. Pinned digest-recipe test updated citing this amendment. RED: `test_shared_page_churn_outside_anchor_is_ledger_noop` (footer churn re-filed the item), `test_output_digest_recipe_is_pinned`, `test_observation_field_discipline`.
- **P11 Standing-candidate wording.** Docs-still-drifted direction now reads "the standing candidate … **STANDS** — re-confirmed against the live docs…"; never "resolved/retired". Docs-changed direction stays drift with `standing_candidate_ref`. RED: wording assertions in `test_confirmed_resolving_standing_candidate_writes_citing_it`.
- **N1–N9 folded in:** N1 preflight requires non-empty llms.txt body; N2 `response.url` → receipt `final_url` + `redirected` known-loss; N3 covered by P9 BOM; N4 contracts guard — any tests/ call of `run_audit(` must pass `ledger_path=` (guard-of-absence, born green, disclosed); N5 `|` escaped in run-report md cells; N6 `stamp_doc_sources` preserves the file's CRLF/LF convention; N7 `canonical_doc_url` lowercases scheme+host, strips trailing slash, raises on empty/relative; N8 `main()` catches `ManifestError` → stderr + exit 20, manifest parsed once; N9 `_relative_evidence_ref` fails loud on out-of-repo evidence dirs.

### Ratified spec amendments

1. **P6 — exit-tier aggregation semantics** (AC#4/S-3): probe + findings-only excluded from tier aggregation; real items alone drive 0/10/20; probe contributes only through the integrity check.
2. **P10 — output_digest re-key + observation_id digest suffix** (AC#5): digest keyed to the item's own anchor-scoped text (not whole-page `content_sha256`); ids carry `-<digest8>`.

### Dismissals (with rationale)

1. **Wording-triple second-leg vacuity** — the helper's OBSERVED-leg check is satisfiable by the composed template alone; harmless because the driver composes all three legs itself and the consequence gate is enforced separately. No behavior at risk; DISMISSED.
2. **Test-count phrasing** — cosmetic wording in a test docstring/comment; no assertion or semantics affected. DISMISSED.

### Acceptance Auditor — deviation rulings

**7 deviations APPROVED; 2 approved WITH CONDITIONS**, both conditions now discharged:

- Condition 1 → discharged by **P11** (standing-candidate "STANDS" wording; no auto-resolve/retire vocabulary in filed behavior text).
- Condition 2 → discharged by a **T9 deferred-inventory entry** for the **text-language full-list follow-on** (the `enum-parity-text-language` item audits DEFAULT-language parity only by deliberate policy; the full accepted-language-list comparison against `reference/output-language-accepted-values.md` is filed at T9 in `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons, per deferred-inventory governance).

### Post-remediation validation

- Leg-E battery (driver + provider + reachability contracts): **98 passed** (31 RED-first failures recorded pre-fix, all green post-fix).
- Full `tests/contracts`: 293 passed, 1 skipped, **20 failed — the exact 20 KNOWN pre-existing failures proven at HEAD** (fit_report/modality_registry/marcus-routing et al.; untouched by this leg).
- Conveyance sweep untouched: `tests/specialists/gary` 155 passed + styleguide validator/picker/scripted 74 passed, zero modifications to those files.
- `ruff check` clean on all five touched Python files.
- Schema doc (`extraction-report-schema.md §provider_metadata.gamma_docs`) updated additively for the new `final_url`/`content_type` keys + known-losses vocabulary (P8/P9/N2); still no SCHEMA_VERSION bump.

## Completion Notes

*(populated at close)*

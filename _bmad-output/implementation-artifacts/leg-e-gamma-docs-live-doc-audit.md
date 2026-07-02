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

*(populated at T6)*

## Completion Notes

*(populated at close)*

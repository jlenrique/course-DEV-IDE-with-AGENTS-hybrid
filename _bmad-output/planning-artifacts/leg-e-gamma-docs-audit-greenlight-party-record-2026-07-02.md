# Leg-E — Live-Doc Audit (`gamma_docs`) — GREEN-LIGHT Party Record (2026-07-02)

**Arc:** Gamma Styleguide Library (Phase-1 machinery, final leg). **Branch:** `dev/gamma-styleguide-leg-e-2026-07-02`.
**Party:** fully-spawned, 6 seats — Winston (architecture), John (PM), Murat (test architecture), Amelia (dev), Texas (retrieval-contract owner), Dan (CD). Orchestrated per bmad-party-mode; Quinn-synthesis/John-tiebreak chain on standby (not needed — see Synthesis).
**Inputs:** Leg-E design dossier (compiled from `gamma-styleguide-library-briefing-2026-06-30.md`, `deferred-inventory.md` §Leg-B2/§instructions-channel/§Leg-C, the Texas retrieval package, `app/specialists/gary/learned_dependencies.py`, the observations ledger). Codex shadow-monitor standing guidance consulted (session-03 ledger, Polls 22–24: W-2 reactivation, honest-claims discipline, source-detail conveyance + 16:9 boundaries stable; no live monitor lane is running for this session — recorded honestly).

## Proposed scope (as tabled)

A new Texas `gamma_docs` RetrievalAdapter (Shape-3 retrieval provider, mirrors SciteProvider; deterministic, no LLM, no retry) fetching Gamma's live documentation (developers.gamma.app) + an audit driver comparing the DOCUMENTED tier (frozen enums in `app/specialists/gary/_act.py` reused by the styleguide validator; rate-limit claims; model strings) against live doc content + the LEARNED tier (`state/config/gamma-learned-observations.jsonl` via `append_observation`, digest-idempotent, candidate-only). Produces the observations ledger's FIRST REAL WRITES. 3 terminal states per audit item (confirmed / drift-detected / indeterminate). Promotion machinery, CD envelope ceremony, non-contradiction validator, keywords→imageOptions.style all remain deferred (reactivate post-Leg-E).

## Seat verdicts (round 1)

| Seat | Verdict | Amendments |
|---|---|---|
| John (PM) | RATIFY-WITH-AMENDMENTS | 7 |
| Murat (TEA) | RATIFY-WITH-AMENDMENTS | 11 |
| Amelia (dev) | RATIFY-WITH-AMENDMENTS | 8 |
| Texas | RATIFY-WITH-AMENDMENTS | 9 (A1–A9) |
| Dan (CD) | RATIFY-WITH-AMENDMENTS | 9 |
| Winston (arch) | (rendering — appended below) | — |

### John (PM) — key rulings
- **J-1 DONE-bar rewritten to the anti-vacuous form:** the audit RAN LIVE over the FULL documented-tier manifest; EVERY item reaches exactly one of 3 terminal states; writes only where genuinely warranted. Write-path liveness rider: zero-genuine-writes ⇒ escalate to the close party (never manufacture a finding); expected organic write = the 401≠429 standing candidate resolving in one direction or the other.
- **J-2 Probe labeling:** a synthetic failure-state witness item is labeled `probe` in the manifest (Leg-D precedent).
- **J-3 Scope fence (7 named exclusions, verbatim in the story spec):** no LLM/NLP/summarization; no auto-updating frozen enums (drift FILES, humans change code); no promotion; no MCP server / pipeline node / production-runner touch; no crawler (manifest-enumerated pages only); no re-authoring the Gamma reference library; no keywords→imageOptions.style wiring (Leg-E answers its field-surface questions as FINDINGS only).
- **J-4 `gamma-scripted-general-dead-config-detector` stays OUT** (surface-doubling; mechanically orthogonal — static reachability vs doc-vs-code drift).
- **J-5 Independence pin:** no dependency on/from `gary-export-matcher-*` / `leg-c-floored-deck-07g-live-walk` (scheduling adjacency only).
- **J-6 Expertise-ingestion PARTIAL fold:** green-light ratifies the two-tier FRAMING + per-item provenance-of-assertion; deferred-inventory:67 dispositions (1)–(4) re-file as a dedicated adjacent story, reactivation = Leg-E close.
- **J-7** Audit manifest includes the two `imageOptions` field-surface questions (discrete tags field? stylePreset⊕style composition?) as findings-only items.

### Murat (TEA) — key rulings (11 amendments, binding on the spec)
- **M-1** Conformance via extending `ADAPTER_FACTORIES` in `tests/contracts/test_retrieval_adapter_base.py` — no bespoke harness.
- **M-2** Adapter exported from `retrieval/__init__.py`; the autoregister test must observe `gamma_docs` NON-vacuously (RED first).
- **M-3** D-2 reachability pin (`tests/contracts/test_gamma_docs_audit_reachability.py`): the driver resolves the adapter THROUGH `provider_directory` dispatch, never direct instantiation; the driver is the ONLY module that may write `GAMMA_LEARNED_OBSERVATIONS_PATH`.
- **M-4** Static SSOT guard test: no `append_observation(GAMMA_LEARNED_OBSERVATIONS_PATH, …)` anywhere under tests/.
- **M-5** Terminal-state classifier TOTALITY test (exactly-one-of-three; no exception escape; no partial-ledger crash state).
- **M-6** Deterministic judge digests NORMALIZED selector-scoped text, never raw HTML (kills CDN/build-hash false drift).
- **M-7** Live TEETH: planted absent-anchor item witnessed LIVE in the proof run; zero confirmed writes for it. (Missing-digest ValueError accepted as hermetic witness.)
- **M-8** Fixture provenance stamps (source_url, fetched_at UTC, content_sha256, selector) on every recorded fixture + README table; unstamped fixtures do not merge.
- **M-9** Audit-item manifest is committed DATA; a test pins every scope-claimed frozen enum has audit coverage.
- **M-10** Post-run live-checked invariant: `gamma-learned-rules.lock` stays EMPTY; all new rows `status: candidate` (observation≠rule holds).
- **M-11** Unavailability protocol: pre-flight probe → VOID-before-start if site down; mid-run fetch failure → `indeterminate`; ZERO retries. Live-proof receipts: per-item HTTP evidence + terminal-state table + ledger before/after digests + idempotent re-run transcript (0 new lines); first-run-stands (run-2 exists only to witness idempotency; a state change between runs is itself a finding).

### Amelia (dev) — key findings + rulings (8 amendments)
- **FEASIBILITY GROUNDED BY LIVE PROBE:** developers.gamma.app serves RAW MARKDOWN (append `.md`; `llms.txt` 5.9KB index + `llms-full.txt` 221KB full corpus, both HTTP 200 to plain httpx, no JS, Cloudflare did not challenge). `skills/gamma-api-mastery/references/doc-sources.yaml` already catalogs 16 key `.md` pages — the manifest derives from it (A-7).
- **LIVE DRIFT ALREADY FOUND during the probe:** `IMAGE_MODEL_VALUES` (`_act.py:55`) vs the live image-models page — 3 enum values absent from live docs (`imagen-4-fast`, `qwen-image`, `qwen-image-fast`) + ~10 documented models absent from the enum (flux-1-*, gpt-image-2*, imagen-3-pro…). The leg pays for itself.
- **A-1** No third enum copy: manifest `expected_ref` = dotted import into `_act.py` frozensets, resolved at runtime.
- **A-2** Asymmetric drift semantics: enum-value-absent-from-docs → `drift-detected`; documented-model-absent-from-enum → `drift-detected` with `kind: coverage-gap` (distinct observation kinds); driver exit 0 on drift (observation, not CI failure).
- **A-3** Degenerates codified in spec (refine→None; provider_scored passthrough; identity_key=canonical URL).
- **A-4** One-way dependency: adapter is a pure leaf, zero `learned_dependencies` imports; only `scripts/utilities/audit_gamma_docs.py` writes the ledger.
- **A-5** `output_digest` = sha256(fact_id, doc_digest, terminal_state, sorted diff) → unchanged-docs re-run is a ledger NO-OP.
- **A-6** Registration hygiene: eager import in `retrieval/__init__.py` + provider-directory tests updated same diff.
- **A-7** Manifest URL set derived from `doc-sources.yaml` (cited as provenance) + `changelog/readme.md` as canary item.
- **A-8** UTF-8 discipline: decode response.content explicitly + unicode-normalize before digest/match.
- Layout: `retrieval/gamma_docs_provider.py` (~280 LOC) + `scripts/utilities/audit_gamma_docs.py` (~350) + `state/config/gamma-docs-audit-manifest.yaml` + 2 test modules + stamped fixtures. 2–3h dev inside a 4–5h leg = realistic.

### Texas (contract owner) — key rulings (A1–A9)
- **T-1 Shape ruled: retrieval, `kind="direct_ref"`,** with 3 degeneracies DECLARED in docstring + PROVIDER_INFO.notes (pass-through formulate_query; refine→None; cross-validate N/A) per anti-pattern #3 — so no future dev "fixes" them into ceremony.
- **T-2 Params purity:** `params: {pages: [...]}` ONLY; audit-fact vocabulary is driver knowledge, recorded in `semantic_deferred` as a string.
- **T-3 Identity vs snapshot:** `identity_key` = canonical URL (fragment/query stripped); `content_sha256` (over NORMALIZED extracted text) lives in `provider_metadata.gamma_docs` — URL+digest identity rejected (breaks the drift comparison).
- **T-4 Status discipline:** `ratified` placeholder if spec-before-code; landed-unproven = `stub`; **`ready` flips ONLY in the change-set carrying the live fetch proof.**
- **T-5 Auth seam:** `auth_env_vars=[]`; the adapter NEVER holds `GAMMA_API_KEY` (API existence probes are driver-side or a future separate provider).
- **T-6 Authority precedence (codified in driver):** docs beat stale frozen-tier notes (→ drift-detected); LIVE-OBSERVED behavior beats docs (→ drift-detected with dual citation; live entry preserved). Docs never silently overwrite live observations. `authority_tier="vendor-authoritative"` = tier-1 for documented-behavior claims, NOT for actual-behavior claims (the 401≠429 case in-house).
- **T-7 Indeterminate floor:** a row whose `known_losses` implicates the audited fact's location can never mint `confirmed`.
- **T-8** Parametrized `gamma_docs` entry in the base-contract test (= Murat M-1).
- **T-9 Schema:** NO version bump (provider_metadata is the additive escape hatch by design); add the `provider_metadata.gamma_docs` subsection to `extraction-report-schema.md` in the same change-set. TexasRow conventions: source_origin="operator-named"; completeness_ratio honest (None + known_losses sentinels when partial); structural_fidelity assigned deterministically from the extraction pattern.

### Dan (CD) — key rulings (9 amendments)
- **D-1 Terminal-state write mapping:** only DIVERGENCE files a ledger observation; CONFIRMED and INDETERMINATE leave residue solely in the evidence-dir audit report. The ledger is a high-signal divergence record, not an audit log. *(Reconciled with John's liveness rider at Synthesis — see below.)*
- **D-2 Wording standard as a FILING GATE:** each observation's `behavior` carries the mandatory triple — DOCUMENTED claim (+doc URL/date), OBSERVED reality (+location), OPERATIONAL consequence; the driver rejects (reports, does not file) candidates failing it. The 401≠429 seed is the exemplar.
- **D-3 Field discipline:** `birthing_run_ref` = REAL repo-relative evidence-dir path (memory-citation refs end with the grandfathered seeds); `observed_at` = real timestamp (T00:00:00Z placeholders end); `source_component` = the audit component; `output_digest` recipe defined in the spec.
- **D-4 Lock immunity:** `gamma-learned-rules.lock` byte-untouched through Leg-E; candidate-only writes; pin that nothing Leg-E writes is visible to `apply_learned_rules`.
- **D-5 Styleguide-SSOT immunity pin (AC):** zero diff to `gamma-style-guides.yaml` + thumbnails; enum-drift findings route observation → deferred-inventory follow-on, never in-leg edits.
- **D-6 `--check-existence` honesty:** if the driver reuses it, disclose the Studio-template + 50-theme-pagination gaps; no in-leg hardening (that slot belongs to `styleguide-validator-live-existence-hardening`).
- **D-7 Conveyance no-touch pin (three clauses, as ACs):** files-touched allowlist excluding `_act.py` + Irene composition modules (out-of-allowlist diff = governance RED); conveyance tests pass UNMODIFIED; `additionalInstructions`/`imageOptions.style` findings feed the sequenced keywords-routing story as evidence only. Protects [[source-detail → Gamma conveyance]].
- **D-8 Two-tier ratified in MINIMAL form:** expertise SSOT = `skills/bmad-agent-gamma/references/`; API-surface authority = code enums (a third authority — live Gamma docs — is external ground truth owned by neither store; the audit TRIANGULATES doc vs code vs learned, never resolves in-leg); learned tier = B2 ledger+lock; audit = observations-only ("refreshed by this audit" = informed-by-observations, never audit-writes-refs). Full ingestion architecture stays deferred-inventory:67's own scope.
- **D-9 Disclaimer retirement is surgical:** B2 docstring updates to "write path exercised live" (citing the Leg-E evidence dir); ceremony/promotion path REMAINS validated-by-fixture; the promotion-path reactivation trigger is noted as FIRED at close, not acted on.

### Winston (architecture) — key rulings (6 amendments)
- **W-1 Boundary (evidence-based):** import-linter governs only `app` (`pyproject.toml:108`); the retrieval package is TODAY a pure leaf with zero `app.*` imports, and `retrieval/__init__.py` eager-imports every provider while production Texas shells out to run_wrangler (`app/specialists/texas/retrieval_dispatch.py:15`) — so an `app.*` import inside the adapter would execute inside EVERY production Texas retrieval dispatch. Ruling: adapter = pure fetch/normalize leaf, ZERO app imports, zero writes, no clock; ALL comparison + observation writes in a new driver `scripts/utilities/audit_gamma_docs.py` (exact precedent: `validate_gamma_style_guides.py:28-48`). Hermetic battery adds an IMPORT-PURITY test (importing `retrieval` loads no `app.*` module) since import-linter cannot police skills.
- **W-2 Registry fence:** `gamma_docs` lands on the production `list_providers()` surface (CLAUDE.md: authoritative for "what Texas can fetch") — additive and inert, but `PROVIDER_INFO.notes` MUST declare "doc-audit tooling — not a course-content retrieval source."
- **W-3 Manifest geometry:** audit manifest at `skills/gamma-api-mastery/references/gamma-doc-audit-manifest.yaml` (sibling of `doc-sources.yaml`, which already catalogs the key pages + a refresh_protocol block). POINTER TABLE only: `code_ref` = importable dotted name (e.g. `app.specialists.gary._act:IMAGE_MODEL_VALUES`), resolved by the DRIVER at audit time — the manifest never holds enum literals (no second SSOT). Exception class typed explicitly: `kind: doc-fact` items with no code constant (list_themes limit-50, rate-limit numbers) may carry a literal `expected_documented` (an audit expectation, not duplicated authority). Driver stamps `doc-sources.yaml::last_refreshed`.
- **W-4 Blast radius verified:** no lockstep trigger paths hit; `learned_dependencies` is production-inert (offline validator + tests only); SPOC-guardrail compliant (dev/operator tooling; only `app/` surface touched is the already-landed B2 writer, unchanged).
- **W-5 Terminal-state boundary rules:** the dispatcher provides NO soft-fail wrapper (`dispatcher.py:190-193` calls execute() bare) — the DRIVER catches transport failures per-item → `indeterminate`. Anti-vacuous floor: an ALL-indeterminate run exits non-zero ("network down" must never read as "no drift"). Ledger hygiene: indeterminate never writes (no real output to digest).
- **W-6 Determinism:** no clock/LLM/retry in the adapter; extraction rules declared in the manifest; the driver stamps `observed_at`.

## Synthesis (orchestrator; 6/6 RATIFY-WITH-AMENDMENTS — no impasse, Quinn not invoked; four cross-seat tensions reconciled)

**S-1 Ledger-write mapping (Dan D-1 × Winston W-5 × John J-1).** Reconciled rule, binding:
- `drift-detected` → ALWAYS writes a ledger observation (wording-triple gate applies).
- `confirmed` → writes ONLY when it materially resolves/updates a STANDING candidate observation (the new observation cites the candidate's observation_id it confirms — e.g. Gamma docs corrected to 401 would confirm `obs-gamma-burst-throttle-401-not-429-2026-06-25`). Plain "docs agree with code, no standing candidate" → evidence-dir report only.
- `indeterminate` → NEVER writes.
This preserves Dan's high-signal ledger, Winston's real-output-to-digest requirement, and John's write-path liveness rider (the 401≠429 item resolves as a genuine write in EITHER direction).

**S-2 Extraction-miss classification (Winston W-5 × Amelia A-2/risk-2 × Texas T-7).** Sub-rules, binding:
- Transport failure (DNS/timeout/5xx/throttle) → `indeterminate` (driver-caught; no write).
- Page fetched, anchor present, value comparison fails → `drift-detected` (writes).
- Page fetched, anchor/section ABSENT → `drift-detected, kind: doc-restructure` — LOUD in the run report + non-zero exit (Winston: restructure is signal, never silent) but does NOT file a ledger observation (Dan: the ledger records Gamma-behavior divergence, not audit-tooling housekeeping); the residue is a manifest-fix follow-on filed at close.
- Extraction ambiguous (multi-match) or `known_losses` implicating the fact's location → `indeterminate`; can never mint `confirmed` (Texas T-7 floor).

**S-3 Exit-code tiers (Winston W-5 × Amelia A-2).** Driver exit codes: `0` = ran, all confirmed; `10` = ran, drift detected (loud + scriptable, NOT a failure semantic — drift is the audit WORKING; candidate observations never enforce); `20` = VOID (pre-flight probe failed / all-indeterminate / partial-run integrity failure). Mirrors the repo's exit-10 discard-tier precedent.

**S-4 Manifest location (Winston W-3 × Amelia A-Q2).** Winston's geometry stands: `skills/gamma-api-mastery/references/gamma-doc-audit-manifest.yaml`, derived from + citing `doc-sources.yaml` (Amelia A-7 composes). Also honors Dan D-3 (no new artifact class under `state/config/`).

All other amendments are orthogonal and STACK — John 1–7, Murat 1–11, Amelia 1–8 (as modified by S-2/S-3/S-4), Texas A1–A9, Dan 1–9 (as modified by S-1), Winston 1–6 are ratified in full.

## Ratified DONE-bar (anti-vacuous form)

1. **Hermetic battery (RED-first):** conformance via `ADAPTER_FACTORIES` extension; non-vacuous autoregister; import-purity test; recorded provenance-stamped fixtures (all 3 terminal states reachable); classifier TOTALITY test; ledger tests tmp_path-only + static SSOT write-guard; D-2 reachability pin (driver resolves adapter through provider_directory; driver = sole ledger writer).
2. **LIVE proof (indispensable; first-run-stands; no mocks):** full-manifest audit run against real developers.gamma.app; EVERY item reaches exactly one of 3 terminal states; per-item receipts (URL, status, normalized-anchor sha256, fetched_at) + terminal-state table + ledger before/after digests; planted absent-anchor PROBE item (labeled) lands per S-2 with zero confirmed writes; idempotent re-run transcript (0 new lines, byte-identical ledger); `gamma-learned-rules.lock` byte-identical; all new rows `status: candidate`.
3. **Writes per S-1** with Dan's wording-triple filing gate + real evidence-dir `birthing_run_ref` + real timestamps + spec-defined `output_digest` recipe.
4. **Fences held:** John's 7 exclusions; Dan's conveyance no-touch pin + styleguide-SSOT immunity AC; Texas auth/params/identity rules; Winston's registry note fence. `ready` status flips only in the change-set carrying the live proof.
5. **Dual-gate CLOSE:** Murat (structural) + Dan/Texas (content), independently re-verifying.

**VERDICT: GREEN-LIGHT RATIFIED 6/6 (all RATIFY-WITH-AMENDMENTS; amendments + synthesis binding on the story spec). Dev may open.**

---

## CLOSE ADDENDUM (2026-07-02) — Leg-E DUAL-GATE CLOSED

**Spine executed:** green-light 6/6 → story spec (`34fb2b84`) → spawned dev RED-first offline build (initial RED 6 failed/3 errors; 95-test battery) → 3-lane `bmad-code-review` (Blind Hunter + Edge Case Hunter converged on the post-classification write-phase gap: 2 MUST-FIX + 9 SHOULD-FIX + NITs; Acceptance Auditor APPROVE-FOR-LIVE-PROOF, 7 deviations ruled) → RED-first remediation P1–P11 + N-series (31 RED → 98 green; 2 ratified spec amendments: P6 tier aggregation excludes probe/findings-only; P10 digest re-key to anchor text + digest8 id suffix) → offline commit `06c39623` → **LIVE PROOF** `5730997f` (15/15 terminal states vs real developers.gamma.app; 3 organic candidate writes incl. the 429 standing-candidate STANDS resolution; probe teeth live; idempotent re-run byte-identical; status→ready + D-9 surgical disclaimer rode the change-set) → **dual-gate:** Murat structural HAND-BACK (F-1 stale duplicate status pin — caught by the pin's own teeth) → remediated `ea0c3294` → **Murat CLOSE no-conditions** + **Dan CD CLOSE** + **Texas contract CLOSE**.

**DONE-bar audit:** all 5 ratified DONE-bar items PASS (hermetic battery; live proof with receipts + probe + idempotency; S-1 writes with wording-triple gate; fences held incl. conveyance no-touch + styleguide-SSOT immunity; dual-gate close). John's liveness rider satisfied ORGANICALLY (image-model drift both kinds + the 429 resolution — nothing manufactured).

**Retro harvest (Murat):** duplicate status pins across test modules need a single-sweep grep at any lifecycle flip — the F-1 miss pattern was "re-ran the battery I remembered, not the battery that references the flipped symbol."

**NITs filed:** ledger rows 4/5 share behavior prose (differentiation carried structurally by kind+diff); run_wrangler `--list-providers` table renders no notes column (W-2 fence verified present in PROVIDER_INFO.notes itself).

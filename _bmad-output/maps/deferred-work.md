# Deferred Work

- ~~2026-04-02: Build function to save downloaded literal visuals from Gamma into the existing Git site destination. Status: implemented on `dev/storyboarding-feature` with preintegration publish helper, mode-aware fail-closed behavior, URL substitution wiring, and regression/live integration test coverage.~~ **Closed 2026-04-02.**

## Deferred from: code review of migration-2a-4-texas-scaffold-migration (2026-04-25)

Independent G6 layered code-review (`bmad-code-review` skill, three subagents in parallel: Blind Hunter, Edge Case Hunter, Acceptance Auditor) on the Codex-landed Texas implementation. Triaged per aggressive single-gate rubric in [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md): **8 PATCH applied + 9 DEFER + ~20 DISMISS**.

**PATCH applied at G6 close (in-tree):** §12.5 section-level framing sentence (Paige P2); §12.6 sub-section framing sentence in spec-required form (Paige P4); §12.7 worked example matched to real post-G6 code shape; §12.10 Murat M4 latency baseline + retro pointer + Slab 2b kickoff gate; AC-B 7-case parametrize with two-sided `bundle.parsed.*` trail-tag assertion (Murat M1 + M5); AC-B subprocess kwargs pin extended to `text` / `capture_output` / `cwd` (Amelia A1); fail-loud guards on malformed cache_state JSON + non-dict cache_state + missing `bundle_dir` in dispatch receipt + dispatch-exit-30 hard error (Blind HIGH); fixture-bundle BOM strip + `ingestion-evidence.md` PowerShell-escape rewrite; vacuous `fake_dispatch` test fixed to pin envelope thread-through; `__all__` cleaned (private helpers dropped); `slab-2a-retrospective.md` authored.

### Deferred (real, non-blocking, file under existing or new follow-ons)

- **Dispatch wrapper `tests/fixtures/...` runtime-path coupling** [`app/specialists/texas/retrieval_dispatch.py:12-14`] — `DEFAULT_FIXTURE_BUNDLE` references the test fixture tree from production runtime path. Same envelope-carrier-hack class as Kira `kling_dispatch.py`; Slab-3 retirement bundles with the cache_prefix payload-carrier replacement. Until then, the new `_decode_envelope_payload` fail-loud guards (PATCH applied) prevent silent fixture fallback in production.
- **`_check_provider_key` accepts non-empty string except 3 magic placeholders** [`scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py:_check_provider_key`] — operator-helper polish; AC-B-OP is DEFERRED-PENDING-SLAB-3 anyway, so the helper is uninvokable-on-hybrid-today. Slab-3 reactivation gate per Murat hard caveat is BINDING (live-wire 7-case + two-sided + sha256 re-validate + M4 latency baseline). Fix the gate at reactivation, not now.
- **AC-B-OP helper returns exit 0 even on non-zero wrangler** [`scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py`] — same Slab-3 reactivation scope as above.
- **Sanctum lock baseline regeneration script** — 17-file sha256 baseline is hardcoded as `TEXAS_SANCTUM_LOCK_BASELINE` module-level constant (per Amelia A3); operator can regenerate via `find _bmad/memory/bmad-agent-texas -type f -exec sha256sum {} +` per Story §G. A regen script (~30 LOC) would automate this for any future Slab-2 specialist with a populated-and-locked sanctum. Operator-path; not blocking for 2a.4 close.
- **`SanctumLockViolation` cross-specialist refactor** — 2a.4 introduced `SanctumLockViolation(RuntimeError)` for Texas with named-exception lock-and-verify protocol. Irene/Kira can be retrofitted to share the same protocol via a Slab-2-cross-cutting follow-on. Filed; non-urgent.
- **Fixture `manifest.json` fake sha256 `"abc"`** [`tests/fixtures/specialists/texas/fixture_bundle/manifest.json`] — minimal valid shape for shape-pin tests; nothing validates artifact-integrity from the manifest yet. If a future test does, this fixture will need a real sha256.
- **Fixture `extracted.md` declares `expected_min_words: 200` but body is 3 lines** [`tests/fixtures/specialists/texas/fixture_directive.yaml:8` vs `fixture_bundle/extracted.md`] — internal inconsistency; no runner validates min_words today. If runner ever does, fixture needs an extension.
- **`_gate_decision` post-interrupt code is dead-on-first-pass** [`app/specialists/texas/graph.py:_gate_decision`] — precedent-inherited from Irene/Kira; Slab-3 conditional-edge fix is the architectural remedy applied uniformly across all three specialists (already filed under "Gate-decision conditional-edge fix" carry).
- **Edge-case sanctum hashing on lone-CR-only or tab-in-filename paths** [`app/specialists/texas/graph.py:_read_sanctum_digest`] — Edge Case Hunter findings on improbable edge cases; current normalization handles `\r\n` → `\n` (the Windows case that actually matters); lone `\r` on macOS-classic and tabs-in-paths are not in the operator's environment. Defer until a real cross-platform regression appears.
- **Local environment optional-dep hygiene** — `tests/contracts/test_33_*.py` and several `tests/test_*.py` modules error at collection with `ModuleNotFoundError: responses` and pydantic-v2 schema-validation errors during 2a.4 regression. Pre-existing (unrelated to Texas migration). File at Slab 2b open as a one-shot env-restore PR so the migration-suite regression baseline can be quoted with full coverage again.

### Newly named follow-ons

- **Dispatch-wrapper extraction candidate** — `kira/kling_dispatch.py` (LLM+tool category) + `texas/retrieval_dispatch.py` (pure-tool category) are two independent occurrences of the same dispatch-wrapper shape. If 2b.1 (Gary) or 2b.2 surfaces a third occurrence, extract to `_bmad/scaffolds/dispatch_wrapper_template.py`.
- **`§12 size review** when subsection count exceeds 12** — readability check on `langgraph-migration-guide.md §12`. Currently 10 subsections post-2a.4; flag at 2b mid-slab.
- **`implementation-artifacts/` directory README/index** — file at Slab 2b open if directory clutter starts to hinder newcomer triage.

## Carries to 2a.4 T1 Readiness (party-mode ratified 2026-04-25)

Three items batched at 2a.3 close to land at 2a.4 T1 (NOT 2a.3-blocking):

1. **[Murat soft-blocker — Slab-2-mandatory]** Promote `_extract_kling_response` parse-branch coverage from DEFER. Add 4 parametrized tests: fenced-JSON, prose-only, double-fence, list-of-blocks. Single highest vacuous-pass risk on the board.
2. **[Hygiene PR — one-liner]** `.gitattributes`: `* text=auto eol=lf` for `_bmad/memory/**`; `* binary` for `tests/fixtures/**/*.mp4`. Storage-side hygiene complementing P6 runtime-side normalization (defense-in-depth per Murat 2a.2 MF3 binding).
3. **[Paige doc polish]** Migration-guide §12.6 framing sentence above divergences-from-Irene table ("When you migrate the next specialist, expect divergences in these eight categories...") + §12.7/§12.8 renumber back-reference grep across migration guide + Slab 2a specs (verify no internal refs point at pre-renumber slots).

**Winston spec-vs-implementation drift reconciliation:** `_gate_decision` "routes around" spec language vs implementation-routes-through reality is identical across Irene 2a.2 + Kira 2a.3. The Slab-3 conditional-edge entry below MUST explicitly carry the spec-reconciliation language when Slab-3 stories author.

## Deferred from: code review of migration-2a-3-kira-motion-scaffold-migration (2026-04-25)

- **`cache_state.cache_prefix` overloaded as input + output blob** [`app/specialists/kira/graph.py:174-218`] — pre-existing inherited from 2a.2 envelope-carrier-hack. Slab-3 retirement already tracked in `_bmad-output/planning-artifacts/deferred-inventory.md` "Replace cache_prefix payload-carrier hack with first-class RunState envelope field". 2a.3 surface reinforces urgency.
- **`_gate_decision` unconditional `interrupt()` on canonical edge chain** [`app/specialists/kira/graph.py:236-240`] — both Irene (2a.2) and Kira (2a.3) ship identical pattern; AC-E "routes-around" was structurally unfulfilled at 2a.2 already. Conditional-edge fix touches Irene + Kira + future specialists; Slab-3 cross-cutting. File a Slab-3 follow-on at next retrospective. **SPEC-RECONCILIATION REQUIRED** (Winston flag, party-mode 2026-04-25): when Slab-3 conditional-edge fix lands, the Slab-2 epic spec language ("routes around `gate_decision` on clean verify") must be reconciled — either spec amends to match implementation OR implementation moves to match spec. Do not ship Slab-3 with the ambiguity unresolved.
- **`dispatch_to_kling` swallows runner exceptions mid-call; silent-empty `motion_asset_path` when receipt missing both keys** [`app/specialists/kira/kling_dispatch.py:61-77`] — operator-path hardening; AC-B-OP scope only. Wrap `module.run_motion_generation_for_slide(...)` in try/except returning structured-error receipt; surface `status="degraded"` when receipt missing `motion_asset_path` AND `output_path`.
- **`_load_target_module` no caching, no `sys.modules` registration, no `exec_module` try/except** [`app/specialists/kira/kling_dispatch.py:22-28`] — operator-path hardening. Cache via `_TARGET_MODULE: ModuleType | None` module-level; `sys.modules[name] = module` before `exec_module`; wrap in try/except → `RuntimeError`.
- **`_act` LLM response `content` shape — list-of-blocks (multimodal AIMessage) handling missing** [`app/specialists/kira/graph.py:185-186`] — LangChain message-shape hardening. Detect `isinstance(content, list)` and join `block.get("text", "")`; current behavior raises clear `RuntimeError` (loud failure OK as default).
- **`_act` silently coerces non-dict-but-decodable cache_prefix (list, scalar, null) to empty payload — no log, no warning** [`app/specialists/kira/graph.py:174-177`] — paired with envelope-carrier-hack retirement; Slab-3 scope.
- **`KiraEnvelope._pin_specialist_id` size-cap dump permits NaN/Inf floats** [`app/specialists/kira/state.py:26`] — Slab-2 cross-cutting validator hardening. Add `allow_nan=False` to `json.dumps`; Irene `IreneEnvelope` has identical pattern and should land in lockstep.
- **`mock_motion.mp4` is 29-byte ASCII text — could lose CRLF stability across Windows checkouts** [`tests/fixtures/specialists/kira/mock_motion.mp4`] — file is acceptable per Auditor §6 verification (no test parses real MP4 bytes); Slab-2-cross-cutting hygiene follow-on: add `* binary` `.gitattributes` entry for `tests/fixtures/specialists/**/*.mp4`.
- **`_extract_kling_response` parse-branch test coverage — fenced-JSON variants, prose-only, double-fence, list-of-blocks** [`tests/specialists/kira/`] — test-pack expansion; defer as defensive over-engineering for 2a.3 close.


## 33-1 generator discovery deferred findings (2026-04-19)

- Generator creation is required before Story 33-2 can execute its current "rewire existing generator to pipeline-manifest.yaml" scope. Route: propose Story `33-1a` or re-scope `33-2` in party-mode.
- If generator creation is folded into 33-2, update story points and gate mode because scope is no longer "rewire only"; it becomes net-new generator architecture work.
- Preserve a multi-version extension hook (`--pack-version` style) while designing the generator so v4.1/v4.2 parity does not require a second refactor story.

## 33-2 pipeline-manifest-ssot deferred findings (2026-04-19)

- AC-B.15 generator rewire DEFERRED per 33-1 kill-switch Case C; routed to Story 33-1a (generator build-from-scratch). Pack hand-edit remains forbidden; regeneration gates on 33-1a completion.

## Stashed for Story 27-5 (Notion provider) — 2026-04-17

Cursor loads TWO Notion MCP servers in parallel (non-conflicting keys):

**User-scope** `C:\Users\juanl\.cursor\mcp.json` → `"Notion"` → hosted HTTP MCP at `https://mcp.notion.com/mcp`
- Tools: `notion-*` curated surface (~12-14 tools: `notion-search`, `notion-fetch`, `notion-create-pages`, etc.)
- Auth: Notion's hosted flow (typically OAuth / session)
- Designed for agent-UX (Tracy, IDE sessions)

**Project-scope** `.cursor/mcp.json` + `.mcp.json` → `"notion"` → local stdio via `scripts/run_mcp_from_env.cjs notion` → `npx -y @notionhq/notion-mcp-server`
- Tools: `API-*` wrappers (~22 tools: `API-post-search`, `API-retrieve-a-page`, etc.)
- Auth: integration token (`NOTION_API_KEY` in `.env`, mapped to `NOTION_TOKEN`)
- Designed for API-key automation (headless Python, CI)

**For Story 27-5 (Texas Notion adapter, locator-shape)**: use **project-scope stdio version**. Rationale:
1. Token-auth matches `run_mcp_from_env.cjs` pattern already established for canvas-lms, gamma, and this notion entry.
2. Texas runs headless in CI — OAuth-style user-session auth doesn't fit.
3. Granular `API-*` tools map cleanly onto locator-shape dispatch (operator provides Notion page-id → Texas fetches via `API-retrieve-a-page` / `API-get-block-children`).
4. Deterministic for testing — stdio subprocess can be mocked; hosted HTTP requires live auth flow.

**For Tracy's IDE-agent exploratory research (Epic 28)**: user-scope hosted version is better. Curated `notion-*` tools are designed for agent reasoning; OAuth session matches Cursor's session auth; fewer tools = less prompt bloat.

**Recommendation**: keep both — they serve different consumers. When 27-5 reshapes post-27-0, spec notes that Texas's Notion adapter uses project-scope stdio; Tracy may use either in IDE sessions at her discretion.

## Deferred from: code review of story-27-1 (2026-04-17)

- Sibling Office-ZIP suffixes `.docm` / `.dotx` / `.dotm` still fall through to `read_text_file()` in Texas's `local_file` dispatch, re-introducing the binary-garbage defect 27-1 fixes for slightly rarer suffixes. Real-world-shape robustness was explicitly deferred to a follow-on Epic 27 story per Murat's implementation-review note (candidate name: "Texas intake robustness" — password-protected, macros, Google Docs / Pages exports, corrupted-ZIP-valid).
- DOCX body-order iteration silently drops `<w:sdt>` (content controls / structured document tags) and `<w:altChunk>` (embedded sub-document) elements. Form-control DOCX files produce empty extraction with no `known_loss` sentinel. Same follow-on story as the sibling-suffix gap.
- `extract_docx_text` docstring only documents `PackageNotFoundError`, but python-docx can raise `BadZipFile`, `KeyError` (missing style reference), or `AttributeError` under unusual inputs. Either expand the classifier's case table or broaden the docstring's Raises clause. Low-priority doc accuracy.
- Integration test `provenance[0]["ref"] == str(docx_path)` could theoretically flake on Windows short-path resolution (`JUANLE~1` format). Not observed in practice; switch to `Path(...).samefile(...)` comparison if observed.
- Negative-control fixture for Tejal cross-validator — a DOCX/PDF pair from unrelated source docs that should cross-validate as DIFFERENT. Without it, the 100% key-term coverage result cannot be distinguished from "heuristic is loose." Murat implementation-review follow-on.
- Collapse `_EXTRACTOR_LABELS` + `_EXTRACTOR_LABELS_BY_KIND` to a single kind-keyed source of truth with provider-derived default kind. Winston implementation-review architectural polish pass (~20 min).

## Deferred from: implementation review of story-27-2 (2026-04-18)

- **Winston nit — authority-tier lookup promotion.** `SCITE_AUTHORITY_TIERS` in `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py` is provider-local today (correctly so — data, not inference, AC-C.7). Promote to `skills/bmad-agent-texas/scripts/retrieval/authority_tiers.py` as a shared module when a second retrieval-shape provider (Consensus 27-2.5, YouTube 27-4) needs tier-lookup semantics. Do not let the second consumer copy-paste. Trigger: first cross-provider demand. Effort: ~30 min (extract + one-adapter migration + test).
- **Amelia nit — adapter-factory registration drift guard.** `tests/contracts/test_retrieval_adapter_base.py::ADAPTER_FACTORIES` currently requires human memory — a new adapter that ships without being appended to the list silently skips the parametrized contract tests. Add a meta-test that enumerates `RetrievalAdapter.__subclasses__()` and asserts every subclass with a live `PROVIDER_INFO.status == "ready"` appears in `ADAPTER_FACTORIES`. Catches 27-3 / 27-4 / 27-2.5 onboarding misses. Effort: ~15 min.
- **Amelia nit — spec-gap tells for future provider authors.** Two 27-2 implementation debug-log entries worth surfacing in `docs/dev-guide/how-to-add-a-retrieval-provider.md` §11 Anti-patterns so 27-3/27-4 authors don't re-discover them: (a) **self-reference trap in literal-token guards** — a test that greps its own source for forbidden literals will match its own docstring; runtime string concatenation (`"Magic" + "Mock"`) is the mitigation; (b) **regex-ordering pitfalls in log-scrubbers** — `(ms|s|seconds)` matches `s` of "seconds" greedily; put longer alternations first (`(seconds|ms|s)\b`) with explicit word boundary. Both are one-paragraph additions to the §11 anti-pattern list. Effort: ~10 min.
- **Paige nit (applied in 27-2)** — see `retrieval-contract.md` §"Authoring retrieval-shape directives directly (advanced)" for the added operator "when would I reach for this" framing sentence. Kept here as the acknowledgement trail.

## Deferred from: code review of story-27-2-scite-ai-provider (2026-04-18)

19 findings from the three-layer adversarial code-review pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Real but non-blocking; reduce surface area of future stories' dev-time surprises.

- `SCITE_MCP_URL` captured at module import (`scite_provider.py:38` — `os.environ.get` at import time). Monkeypatched env post-import has no effect. Future: move URL resolution into `_client()` for full lazy-resolution parity with auth env vars.
- `_truncate_citation_contexts` silently drops unknown classifications (e.g., future scite category beyond supporting/contradicting/mentioning) — no `known_losses` sentinel. Add `unknown_classification` sentinel to surface schema drift from scite MCP.
- Year-only vs ISO-date lexicographic comparison in `_row_date` / date_range filter — `pub_date[:10]` slice on non-ISO input (e.g., bare "2023") produces a 4-char string that lexicographically sorts below any YYYY-MM-DD range and silently passes the filter. Tighten to isoparse + explicit comparison.
- Eager `from .scite_provider import SciteProvider` in `retrieval/__init__.py:72` creates hard import coupling — a scite import failure cascades to all retrieval imports including FakeProvider tests. Winston SF-1 shipped this intentionally for directory-registration determinism; revisit if a retrieval path must remain available with scite disabled (e.g., optional-provider build).
- Legacy-DOCX structural-parity test uses `yaml.safe_load` + dict-compare instead of "plain string equality" required by AC-T.6. This is an authorized deviation per AC-C.6 ("one-line deviation permitted IFF intentional"); document the deviation rationale explicitly in a future 27-* story's Review Record template so it stays authorized.
- `_load_runner` creates multiple module-copies of `run_wrangler.py` under distinct `sys.modules` names in each test file — cross-module `isinstance(o, SourceOutcome)` checks would silently fail if future tests passed dataclass instances across the boundary. Consolidate to a single `conftest.py`-scoped fixture.
- `exclude_ids` / `license_allow` identity surface inconsistent — `source_id` fallback uses `result.get("id")` but `exclude_ids` only checks `doi` + `scite_paper_id`. Add `id` to the exclude-check tuple.
- `int(result.get("supporting_count", 0) or 0)` coercion crashes on non-numeric provider payloads (`int("abc")` → ValueError). Wrap in try/except returning a sentinel or swap to `int(x) if isinstance(x, (int, float, str)) and str(x).lstrip('-').isdigit() else 0`.
- Empty/whitespace DOI slips through `intent.intent.strip()` (`scite_provider.py:283`) → MCP called with empty DOI string. Validate post-strip before query construction.
- `max_results` has no upper bound (scite API may reject `max_results=10_000_000`). Cap at a sane ceiling (e.g., 200) with a log entry when operator hint exceeds it.
- Unicode venue lookup doesn't match substring fallback for non-ASCII strings ("Nature Médicine"). Returns None (→ authority_tier=None), acceptable today but future-proof via NFKC normalization if non-English venues become common.
- `year` type inconsistency — `date = str(year) if year else None` accepts int/str; `_row_date`'s `isinstance(year, int)` guard rejects string "2023". Normalize to int at normalize-time or isoparse at compare-time.
- MCPRateLimitError (429) specific-semantic test not present — AC-T.10 module-prefix test covers the taxonomy generically. Add a 429→MCPRateLimitError assertion for symmetry with 401→MCPAuthError.
- Dispatcher `DispatchError` on constructor `TypeError` unexercised for scite (SciteProvider's `__init__` accepts optional kwargs so the path is reachable via `AdapterFactory.get()` if a future subclass tightens the constructor). Add a negative test if future adapters start requiring constructor args.
- `_acceptance_met` raises `DispatchError` mid-loop AFTER `formulate_query` + `execute` already ran — wasted network call if `min_results` is malformed. Pre-flight the dispatcher's acceptance-criteria validation before first execute.
- `execute` paper-mode `args = {"doi": query["doi"]}` KeyError if caller constructs query without `doi`. Caller-guaranteed today by `formulate_query`, but defensive `.get()` with None-check is low-cost.
- Fixture realism gaps (5 items): null venue, non-ISO `publication_date`, mixed-form authors in one paper, 0/5/2 citation-context distribution across classifications, missing `papers` key schema drift. Add one shared "edge-fixture" per release cycle as live-cassette data informs.
- Paywall graceful degradation with empty abstract → body="" and no `abstract_empty` sentinel alongside `full_text_paywalled`. Add the sentinel so Vera's `completeness_ratio` logic can distinguish "paywalled but abstract available" from "fully opaque."
- Test coverage gaps in `apply_provider_scored`: non-int `supporting_citations_min` / `cited_by_count_min` silently skip filtering (no refinement_log entry). Tighten to raise `DispatchError` or log `criterion_key=<key> reason="invalid_type"`.
- `_mode_from_intent` silently falls through to "search" default when `params["mode"]` is an invalid string — no warning. Add a `_log_unknown_criteria`-style warning path.

## 31-1 G5+G6 deferred findings

Dated 2026-04-18; updated 2026-04-19 after party-mode consensus follow-on remediation pass.

**Closed by 2026-04-19 party-mode consensus pass** (5-persona round: John PM / Murat TEA / Winston Architect / Amelia Dev / Paige Tech Writer):

- ✅ [Edge][#5] ScopeDecision(state=proposed, ratified_by=maya) — closed by `_guard_locked_without_maya` extension in `marcus/lesson_plan/schema.py`; new test `test_scope_decision_proposed_with_ratified_by_rejected` in `tests/test_scope_decision_transitions.py`.
- ✅ [Edge][#6] locked_at set on non-locked state — closed by same validator extension; new tests `test_scope_decision_proposed_locked_at_rejected` + `test_scope_decision_ratified_locked_at_rejected`.
- ✅ [Edge][#7] from_state validator dead code — `_from_state_not_locked` field_validator deleted from `marcus/lesson_plan/events.py` (Literal["proposed", "ratified"] already enforces).
- ✅ [Auditor][#4] ScopeDecisionTransition JSON Schema parity — explicit Non-goals declaration added to 31-1 spec Out-of-scope section explaining intentional exclusion + Pydantic-as-source-of-truth.
- ✅ [Auditor][Coverage] `model_dump(by_alias=True, exclude={...})` literal path — pinned by `test_scope_decision_model_dump_by_alias_does_not_leak_internal` + `test_scope_decision_model_dump_by_alias_with_empty_exclude_does_not_leak`.
- ✅ NIT (duplicate regex constants) — `_OPEN_ID_REGEX` consolidated to single source of truth in `marcus/lesson_plan/event_type_registry.py` (`OPEN_ID_REGEX_PATTERN`). `schema.py` and `events.py` now import.
- ✅ Cross-story G6-D2 slip from 30-1 closed — named constants `EVENT_PRE_PACKET_SNAPSHOT`, `EVENT_PLAN_UNIT_CREATED`, `EVENT_SCOPE_DECISION_SET`, `EVENT_SCOPE_DECISION_TRANSITION`, `EVENT_PLAN_LOCKED`, `EVENT_FANOUT_ENVELOPE_EMITTED`, `EVENT_FIT_REPORT_EMITTED` exported from `event_type_registry.py`. 30-2b dispatch can now import the constant; eliminates the literal-string-hard-code class of drift.
- ✅ Spec status header drift — flipped `**Status:** in-progress` → `**Status:** done` on the 31-1 spec.

**Confirmed-defer (party-mode consensus 4–1 or stronger):**

- [SHOULD-FIX][Blind][#4] _json_default pragma coverage — pragma acceptable; add negative test later if Decimal/UUID fields enter
- [SHOULD-FIX][Blind][#5] structure: dict untyped — spec calls "opaque-to-platform free-shape"; document intent in future schema PR if sprawl observed
- [SHOULD-FIX][Blind][#11] to_internal_actor error path untested — pragma acceptable; add negative test when caller surface grows in 31-2
- [SHOULD-FIX][Edge][#10] proposed → proposed same-scope no-op — minor contract violation; promote if log-noise observed; natural home 30-3a state-lock interface
- [SHOULD-FIX][Edge][#11] _strip_none list None theoretical — not reachable in 31-1; promote when a nested Optional field lands
- [SHOULD-FIX][Auditor][#3] AC-T.3 error-message specificity — tests pass; future-proofing if error string drifts
- [NIT-grouped][22 of original 23] cosmetic NITs — naming, DRY, imports; dismissed per consensus (duplicate-regex NIT promoted + closed above)

## 31-2 G5+G6 deferred findings

Dated 2026-04-18; updated 2026-04-19 after party-mode consensus follow-on remediation pass.

**Closed by 2026-04-19 party-mode consensus pass** (4-persona round: Murat TEA / Winston Architect / Amelia Dev / John PM):

- ✅ [Blind][#15] WRITER_EVENT_MATRIX outer dict mutable — wrapped via `types.MappingProxyType` in `marcus/lesson_plan/log.py`. Single-writer rule (R1 amendment 13) is tamper-resistant at runtime.
- ✅ [Auditor][#5] AC-T.3 REJECT post-condition loose — tightened to strict `path.stat().st_size == 0` byte-level assertion in `tests/test_lesson_plan_log_single_writer.py`.
- ✅ [Auditor][#2] AC-T.4 Cell 2 digest substring — tightened to exact `envelope='def'` + `log='abc'` substring assertions in `tests/test_lesson_plan_log_staleness.py` (substring-only matching could pass on a swapped-axis regression).
- ✅ [Edge][#7] read_events iterator-across-append undefined — explicit snapshot-semantics contract added to `LessonPlanLog.read_events` docstring.
- ✅ [Blind][#8] read_events iterator leak — explicit iterator-drain contract added to `LessonPlanLog.read_events` docstring (CPython refcount-GC behavior + PyPy/freethreading caveat + `contextlib.closing` recipe).
- ✅ Cross-store consolidation: `PRE_PACKET_SNAPSHOT_EVENT_TYPE` in `log.py` now binds to `EVENT_PRE_PACKET_SNAPSHOT` from `event_type_registry.py` (single source of truth; closes the second copy from the 30-1 G6-D2 cross-story slip).
- ✅ Spec status header drift — flipped `**Status:** review` → `**Status:** done`.

**Confirmed-defer (party-mode consensus 3–1 or stronger):**

- [SHOULD-FIX][Blind][#5][Edge][#5] mkdir on every append — minor perf; move to LessonPlanLog.__init__ or accept as idempotent-cheap. No user-impact until scale matters.
- [SHOULD-FIX][Blind][#15-NIT] canonical_json duplicated in log.py + digest.py — DRY violation, no behavioral drift observed yet. **Watch flag**: extract shared helper at first sign of digest-determinism flake or before any consumer outside marcus/lesson_plan/ computes digests over log payloads.
- [NIT-grouped][Blind+Edge+Auditor] ~20 cosmetic NITs — DISMISSED per aggressive-DISMISS rubric.
- [SHOULD-FIX][Blind][#14-NIT] PIPE_BUF docstring citation technical error — DISMISSED (Winston) / batch into next docstring hygiene pass.

**Consolidated into a separate cross-cutting story (party-mode 4-1 consensus):**

- 🔁 [Edge][#13] text-mode "\n" vs Windows CRLF translation — folded into the 0.5-pt CRLF hygiene story alongside 30-2b EC13 + 30-1 golden-trace per the 2026-04-19 audit's cross-story finding #4. Natural home: pre-work ahead of 32-3 trial-run smoke harness (cross-platform CI). Murat dissented ("patch in-place AND consolidate"), but the 3-vote majority on cross-story atomicity prevails.

## 31-3 G5+G6 deferred findings

Dated 2026-04-18; updated 2026-04-19 after party-mode consensus follow-on remediation pass.

**Closed by 2026-04-19 party-mode consensus** (3-persona round: Winston / Murat / Amelia, unanimous):

- ✅ [SHOULD-FIX][Edge][#6] ProducedAsset.source_plan_unit_id regex pin — added `pattern=OPEN_ID_REGEX_PATTERN` import from `event_type_registry.py` (single source of truth post-31-1 follow-on). 7 new parametrized rejection tests + 1 acceptance test in `tests/test_produced_asset_fulfills.py`. Closes the trust-the-caller hole where a non-PlanUnit producer could synthesize a malformed identifier passing only `min_length=1`.

**Confirmed-dismiss (4 NITs):**
- [NIT][Blind][#4] `_fulfills_regex` isinstance-guard is dead code — Pydantic v2's string-field type validation rejects int/None/list before the field_validator runs. The guard is belt-and-suspenders documentation; harmless. Keep or remove at future-refactor discretion.
- [NIT][Blind][#6] `# noqa: S101` in component_type_registry.py import-time assertion references Bandit's S rule family which is NOT in the active ruff select list. Harmless forward-compat; no-op today.
- [NIT][Blind][#1,#2] `_MODALITY_REGISTRY_UNDERLYING` + `_COMPONENT_TYPE_REGISTRY_UNDERLYING` — leading-underscore discourages but doesn't enforce; determined code could import and mutate. `MappingProxyType` is the public contract. Acceptable at MVP.
- [NIT][Auditor] A few tests use inline `from X import Y` within function bodies where module-top would be fine — style-only, no behavior impact.
- [NIT][Auditor] `test_valid_subclass_is_instantiable` could be parametrized over (valid_status, valid_modality) pairs for more coverage; landed single-case + G5 rider strengthened class+instance ClassVar readback.

## 29-1 code-review deferred findings

Dated 2026-04-18; updated 2026-04-19 after party-mode consensus follow-on remediation pass.

**Closed:**

- ✅ [Review][Defer][#3-dedup] Duplicate `unit_id` entries in `report.diagnoses` — closed by 29-2 (gagne-diagnostician) line 309 duplicate-target rejection at construction time per audit verification 2026-04-19.
- ✅ [Review][Defer][#4-leak] `UnknownUnitIdError` message embeds full plan unit_id list — closed by party-mode 2026-04-19 follow-on. `marcus/lesson_plan/fit_report.py` now emits only `{sorted(unknown_ids)} ({N} unit_ids in plan)` — count-only, no per-id leak. Test `test_unknown_unit_id_error_does_not_leak_full_plan_id_list` in `tests/test_fit_report_validator.py` pins the new contract.
- ✅ Bonus consolidation: `FIT_REPORT_EMITTED_EVENT_TYPE` in `marcus/lesson_plan/fit_report.py` now binds to `EVENT_FIT_REPORT_EMITTED` from `event_type_registry.py` (single source of truth, mirrors the `PRE_PACKET_SNAPSHOT_EVENT_TYPE` chain).

## 30-1 G6 deferred findings (CENTRALIZED 2026-04-19 from spec inline)

Dated 2026-04-18; centralized into `deferred-work.md` on 2026-04-19 per party-mode consensus (audit cross-story finding #1: 30-1 originally logged DEFERs inline in the story spec rather than this central register, breaking discoverability for future stories that grep here).

**Closed before centralization:**

- ✅ [G6-D7] AC-T.10 zero-test-edit pin self-heals at commit — pin became active post-`d1a788c` commit per audit verification.
- ✅ [G6-D2] `_PRE_PACKET_SNAPSHOT_EVENT_TYPE` literal consolidation — closed by 31-1 follow-on (party-mode 2026-04-19): `EVENT_PRE_PACKET_SNAPSHOT` exported from `marcus/lesson_plan/event_type_registry.py`; `marcus/lesson_plan/log.py:PRE_PACKET_SNAPSHOT_EVENT_TYPE` binds to it; `marcus/orchestrator/write_api.py:69:_PRE_PACKET_SNAPSHOT_EVENT_TYPE` already chained through log → registry. Single source of truth restored.
- ✅ [G6-D6] `NEGOTIATOR_SEAM` string-collision risk — closed by 30-3a structural-marker upgrade. `marcus/orchestrator/__init__.py` now exports a typed `NegotiatorSeam` singleton, with backward-compatible `str(NEGOTIATOR_SEAM) == "marcus-negotiator"` preserved. Contract coverage exists in `tests/test_marcus_negotiator_seam_structural.py` and `tests/test_marcus_negotiator_seam_named.py`.
- ✅ [G6-D1] `get_facade` thread-safety — closed by lock-guarded double-check singleton initialization in `marcus/facade.py` (`_facade_lock` + guarded construction). Contract pin added: `tests/test_marcus_facade_roundtrip.py::test_get_facade_thread_safe_singleton`.
- ✅ [G6-D4] mutable class-attribute leak trap on `Facade.marcus_identity` — closed by converting to a read-only property in `marcus/facade.py`. Contract pin added: `tests/test_marcus_facade_roundtrip.py::test_marcus_identity_read_only_property`.

**Still-open (centralized; assigned future targets):**

- [G6-D3] Test count 33 vs 1.5×K=19 ceiling. Dev Agent Record justifies in aggregate per [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md). **Target: Epic 30 retrospective if pattern recurs.**
- [G6-D5] `UnauthorizedFacadeCallerError` pickle round-trip loses `offending_writer`. Dormant in single-process MVP; activates only if multiprocessing propagation ever lands. **Target: future multiproc hardening story.**
- [G6-D8] `patch("marcus.orchestrator.write_api.EventEnvelope.model_validate")` patches the class globally. Assertion still holds because no path calls `model_validate` in this case. Minor test-design imprecision. **Target: Epic 30 retrospective.**

## 30-2b code-review deferred findings

Dated 2026-04-19; updated 2026-04-19 (party-mode follow-on consensus pass).

**Confirmed-defer (party-mode 2026-04-19, 3-persona unanimous):**

- [Review][Defer][30-2b-EC13] Cross-platform digest stability — **CONSOLIDATED INTO Windows-newline hygiene story** (see "## Cross-cutting CRLF hygiene story" section). Same-class concern as 31-2 Edge#13 + 30-1 golden-trace `\r\n→\n` normalization. Single 0.5-pt focused story slot ahead of 32-3 trial-run harness rather than three per-story patches.
- [Review][Defer][30-2b-EC14] Race window on bundle metadata read. **CONFIRMED-DEFER, blocked by 30-2a byte-identical LOCK.** Mitigation requires reopening the 30-2a `prepare_irene_packet` body to return raw bytes alongside the packet result, which would invalidate the 30-2a LOCK. Single-process single-writer MVP makes the race window theoretical; no test exercises this code path's race window.

## 32-2 follow-on identified by 2026-04-19 audit

**32-2 itself remains BMAD-CLOSED-CLEAN.** The Python inventory in `marcus/lesson_plan/coverage_manifest.py` IS up-to-date (the step_05 entry correctly reflects 30-2b's actual landing — emitter at `marcus/intake/pre_packet.py` + `marcus/orchestrator/dispatch.py`; the step_05 surface is now legitimately owned by 30-4 for the consumer-side `assert_plan_fresh` boundary).

**Closed by `32-2a-inventory-hardening`** (1pt, BMAD-closed 2026-04-19, spec at [`_bmad-output/implementation-artifacts/32-2a-inventory-hardening.md`](../implementation-artifacts/32-2a-inventory-hardening.md)).

**Reconciliation note** — the 2026-04-19 audit follow-on initially proposed a new key `32-2h` for this work; that proposal is RETRACTED. `32-2a-inventory-hardening` already exists, was authored 2026-04-19 against the same audit finding, and supersedes the proposal. Scope alignment:

- ✅ Sample-factory backfill — `32-2a` covers steps **05/06/07/11/12/13** (broader than the proposal's 11/12/13 only — also covers 30-4-owned envelopes that the audit missed).
- ✅ Stale on-disk JSON regeneration — `32-2a` Done-when criterion #5.
- ✅ Step 12 module_path correction — `32-2a` Done-when criterion #2 (phantom `quinn_r_branch_payload.py` → real `quinn_r_gate.py` per 31-5 consolidation).
- ✅ Steps 08/09/10 ownership uncertainty — `32-2a` Done-when criterion #4 marks them `deferred=True` with notes (30-4 closed having shipped only 05/06/07).
- ✅ Honest-audit rule — `32-2a` explicitly forbids synthesizing `plan_ref` onto payloads that don't carry one in production code (`ProducedAsset` revision lives in `fulfills` string; `QuinnRUnitVerdict` carries no `plan_ref`).

The audit-proposed scope estimate (2pt) was generous; the story is correctly scoped at **1pt single-gate** because it ships zero new schema shapes.

## 32-2a code-review deferred findings

- **32-2a-EC7 — concurrent-session sprint-status snapshot hardening.** `tests/test_coverage_manifest_regenerates_on_current_state.py::test_honest_summary_invariants_on_current_repo` reads live `sprint-status.yaml` at test time. If a concurrent session mutates the file mid-test, the test could observe transient state. Risk is low in CI but real in this repo's concurrent-session workflow. Hardening patch would monkeypatch `_load_story_statuses` to a fixed snapshot or fixture-captured dict. Not blocking: the concurrent-session failure mode is session-local rather than observed test-flake. Natural home: 32-3 trial-run smoke harness, which has stronger isolation needs.

## MVP-deferred: rendered UX layer (cross-epic, no owner story)

**Surfaced 2026-04-19 during Story 32-4 close.** The Lesson Planner MVP (Epics 28–32, 22 stories) does not contain a story that owns rendered user interface. Every landed story terminates at schema / log / harness / backend-specialist code. Maya cannot currently "paste source" into a text field, "see a weather ribbon", "click a gray card", or "watch the card turn gold" — those are UI-rendering semantics, not schema mutations, and no MVP story builds the rendering layer.

**What the MVP does deliver for UX**: a set of UX invariants pinned at schema + validator + grep-test level. A future UI layer must honor these:

- `PlanUnit.weather_band: Literal["gold", "green", "amber", "gray"]` (31-1) — no-red triple-layer rejection; band-set closed.
- Voice Register discipline on Facade surfaces (30-1) — first-person present-tense no-hedges ends-with-question.
- `_FORBIDDEN_PATTERN = r"\b(intake|orchestrator)\b"` grep contract (30-1 + 32-4) — pinned in 5+ test files; UI strings must pass.
- Rationale verbatim preservation on `PlanUnit.rationale` (30-3a + 32-4 stage-6) — free text, no parsing, no coercion, no enum. UI must echo stored string byte-for-byte.
- Marcus posture sentence templates (30-5) — one sentence per Tracy posture; UI renders as-is.
- Prior-declined rationale carry-forward (29-2 + 30-3a) — UI must surface these when re-opening a run.

**Pantomime ACs that encode UI expectations without building the UI**:

- Sally YELLOW R1-4 pantomime AC on 32-4 ("card turns gold"). Currently pinned as "scope_decision.state == ratified" + rationale verbatim; no visual gold-repaint is built.
- Sally §6-C Tuesday-morning experiential AC ("operator completes 4A loop in under 12 minutes"). Currently runnable only by a human reading CLI / JSON output and mentally rendering the ribbon.
- "Operator click-through" affordances implied by 30-3a stub-dials ("I'll learn to tune these next sprint"). Currently a `StubDialsAffordance` frozen Pydantic model with a Literal-typed sentence — no clickable dial.

**Natural home**: a new `epic-33-ux-rendering-layer` (or equivalent) post-MVP epic. Out-of-scope for the Lesson Planner MVP itself; belongs in the next planning cycle. Suggested scope placeholder:

- Frame / shell that hosts the ribbon + card grid.
- Card component keyed on `plan_unit.unit_id`; color driven by `weather_band`; state transitions driven by `scope_decision.state` (gray → gold rendering).
- Rationale text box binding to `PlanUnit.rationale` as a controlled input; echo on ratification; one-sentence-per-Declined readback surface.
- Posture-sentence display component consuming `render_retrieval_narration()` output verbatim.
- Voice-register regression CI: every user-visible string in the rendered layer routed through the same `_FORBIDDEN_PATTERN` gate.

**Pre-MVP-ratification flag**: see [`lesson-planner-mvp-ratification-preflight-flags.md`](lesson-planner-mvp-ratification-preflight-flags.md) for the items to surface at F4 (bmad-party-mode green-light) before MVP-complete is stamped.

## 32-4 code-review deferred findings

- ✅ **32-4-BH5 — default `output_path` fixture-pollution hardening** is now closed. `marcus.orchestrator.maya_walkthrough.run_maya_walkthrough()` defaults to a runtime-safe path under `state/runtime/maya-walkthrough/<run_id>/irene-packet.md` rooted at the repository, rather than writing into committed fixture directories.

## Cross-cutting CRLF hygiene story (NEW — 2026-04-19 party-mode consensus)

**Source:** consensus across 31-2 Edge#13 + 30-2b EC13 + 30-1 golden-trace `\r\n→\n` normalization. Three per-story deferrals on the same class of concern argue for one focused 0.5-pt hygiene story rather than three independent patches.

**Working name:** `32-3p-windows-newline-hygiene` (`p` = originally proposed pre-work for 32-3; now retained as a follow-on identifier).

**Scope:**

- Audit every `Path.write_text(...)` call site in `marcus/` and pin `newline="\n"` (or convert to `.write_bytes()`) where determinism matters (digest computation paths in particular).
- Add a single cross-platform contract test that writes a JSONL log, reads its `.read_bytes()`, and asserts byte-equality with the same payload computed via canonical-JSON serialization (closes 31-2 Edge#13).
- Audit text-mode `open()` call sites in `marcus/lesson_plan/log.py` — specifically `LessonPlanLog._path.open("a", encoding="utf-8")` at line 510 and `open("r", encoding="utf-8")` at lines 538 + 574; pin `newline="\n"` on writes and `newline=""` on reads as appropriate.
- Verify 30-1 golden-trace bundle path: the `\r\n → \n` in-test normalization is currently defense-in-depth; the production write path should make it unnecessary.

**Acceptance criteria (one-liner each):**

- AC-1: every `Path.write_text(...)` call site in `marcus/` either passes `newline="\n"` or has a comment explaining why platform-default is intentional.
- AC-2: `LessonPlanLog` log writes produce identical bytes on Windows + Linux (parametrized cross-platform contract test).
- AC-3: 30-1 golden-trace fixture round-trips byte-identical on Windows without test-side `\r\n→\n` normalization.
- AC-4: contract test in `tests/contracts/test_marcus_path_write_text_newline_discipline.py` greps `marcus/` for `write_text(` and fails on any unannotated platform-default-newline call.

**Estimated points:** 0.5

**Natural home:** Post-MVP cross-platform hardening batch (32-3 is already BMAD-closed). Do not reopen 30-3a / 30-3b / 30-4 for this; scope it as a narrow hygiene follow-on.

## G6-Opus independent code-review sweep across 30-3a / 30-3b / 32-1 / 32-2a (2026-04-19)

Per CLAUDE.md "different-LLM-than-implementer" governance, an independent G6 layered code-review by Claude Opus 4.7 ran across the four Lesson Planner stories that were closed with self-conducted code review (Codex 5.3 implementer + same-LLM G6) rather than the cross-LLM gate. Surfaces reviewed: `marcus/orchestrator/loop.py` (653 LOC), `marcus/orchestrator/stub_dials.py` (63 LOC), `marcus/orchestrator/workflow_runner.py` (83 LOC), `marcus/lesson_plan/coverage_manifest.py` sample-factory inventory.

**1 MUST-FIX patch landed:**

- ✅ **G6-Opus 30-3b-B1 — event-type semantic conflation in `tune_unit_dials`.** `marcus/orchestrator/loop.py:tune_unit_dials` was emitting `EVENT_SCOPE_DECISION_SET` for dial-tuning operations. The payload included a `dials` field, but downstream readers (32-3 smoke harness, future audit consumers, 31-2 log readers) interpreting `scope_decision.set` events would mistake a dial change for a scope change. Fixed by introducing a dedicated `EVENT_DIALS_TUNED = "dials.tuned"` constant in `marcus/lesson_plan/event_type_registry.py`, registering it in `RESERVED_LOG_EVENT_TYPES`, adding it to `WRITER_EVENT_MATRIX` as marcus-orchestrator-only in `marcus/lesson_plan/log.py`, switching `tune_unit_dials` to emit it, and updating the two affected tests in `tests/test_marcus_4a_reassessment.py`.

**Per-story DEFER findings (NIT-level, real but corner-case):**

- [Defer][30-3a-B4] `marcus/orchestrator/loop.py:633-637` raises `RuntimeError` if `pending_units==[]` but `locked==False` — defensive but never triggers under current `trigger_plan_lock_if_ready` semantics. Document as invariant rather than runtime guard in next docstring pass.
- [Defer][30-3a-EC3] `intake_scope_decision` does NOT validate `decision.state == "ratified"` (only requires unit_id to exist). Could append a `state="proposed"` ScopeDecision if caller misuses; loop would re-prompt. Consider tightening if observed in trial runs.
- [Defer][30-3b-B2] `sync_reassess_with_irene` line 396 — late `from marcus.lesson_plan.digest import compute_digest` inside function body (same pattern as 30-4 B5). Move to module top in next refactor pass.
- [Defer][30-3b-EC1] `sync_reassess_with_irene` line 416-417: `if diagnosis.unit_id in normalized_prior: recommended = "out-of-scope"` — overrides Irene's recommendation when unit was previously declined. Behavior is correct per R1 amendment 15 (Maya already decided) but not documented inline.
- [Defer][32-1-B3] `route_step_04_gate_to_step_05` doesn't enforce step-04 prerequisite — caller could invoke without step 04 having run. Function name is suggestive but no enforcement. Consider renaming or adding a prereq check; low risk because pipeline runner controls callsite ordering.
- [Defer][32-1-EC2] `Iterable[str]` typed but no runtime check on `insert_4a_between_step_04_and_05` step values. NIT — Pydantic would catch in production.

**Reconciliation update (2026-04-19):**

- ✅ Prior note about `tests/contracts/test_32_4_maya_walkthrough_voice_register.py::test_no_intake_or_orchestrator_tokens_in_operator_surface` failing is now stale. Current branch verification passes (`py -3.13 -m pytest -q tests/contracts/test_32_4_maya_walkthrough_voice_register.py` -> `1 passed`), so this is no longer an active deferred finding.

## 30-4 code-review deferred findings

Dated 2026-04-19. Findings from independent G6 layered code-review by Claude Opus 4.7 on Story 30-4 plan-lock-fanout (run as the second-pass review per CLAUDE.md "different-LLM-than-implementer" governance; first pass was by Codex 5.3 the implementer). 6 DEFER + 1 DISMISS; 3 MUST-FIX patches landed in the story.

- [Defer][30-4-B3] `marcus/orchestrator/fanout.py` posture-name normalization: bridge-result matching keys on `posture == "gap-fill"` (Tracy hyphen form) but `IdentifiedGap.suggested_posture` Literal is `"gap_fill"` (Marcus underscore form). The seam is intentional (mirrors 30-5's normalized `gap-fill`/`gap_fill` seam) but isn't single-sourced — drift hazard if Tracy posture vocabulary widens. Natural home: 30-5 retrieval-narration-grammar follow-up or a focused posture-vocabulary-consolidation pass.
- [Defer][30-4-B5] `marcus/orchestrator/fanout.py:127` late `from marcus.lesson_plan.digest import compute_digest` inside `emit_plan_lock_fanout` body — no actual circular reason (digest.py imports schema.py; fanout.py imports schema.py). Move to module top in next refactor pass.
- [Defer][30-4-B6] `marcus/orchestrator/fanout.py` reassigns `locked_plan` via `model_copy` when `digest == ""`. Caller's reference is untouched (Pydantic model_copy returns new) but the function name suggests pure emission, not silent digest backfill. Add docstring sentence "if digest is empty, computes and uses fresh digest" in next docstring pass.
- [Defer][30-4-EC1] Zero `plan_units` test coverage gap. Behavior is correct (emits step 05/06 only; in_scope_units empty; bridge skipped; result has 2 envelopes + 0 bridge_results) but no dedicated test pins it. Natural home: 32-3 trial-run smoke harness.
- [Defer][30-4-EC4] `_gap_envelopes_for_unit` builds `results_by_gap_type` ONCE outside the per-unit loop, so a single bridge result of `[{posture: "embellish", status: "ok"}]` propagates to EVERY in-scope unit's embellish gaps. This is the right per-posture interpretation of bridge contract, but isn't documented. Add docstring clarification in next pass.
- [Defer][30-4-EC7] Duplicate posture in bridge_results → last-write-wins on `results_by_gap_type[posture] = result` (line 89-93). Silent override. Real but corner case — promote if observed in trial runs.
- [Dismiss] AC-Auditor.D loose `bridge: Any | None` typing on `emit_plan_lock_fanout`. Protocol class would clarify the contract but adds complexity for marginal benefit at MVP. Revisit when 32-3 wires a real bridge if drift materializes.

## 30-3a code-review deferred findings

Dated 2026-04-19 (via REMEDIATION pass after concurrent-session false closure). DEFER findings from the dual-gate G6 layered code-review (self-conducted Blind Hunter + Edge Case Hunter + Acceptance Auditor) on Story 30-3a 4A-skeleton-and-lock.

- [Review][Defer][30-3a-EC1] Empty-packet (zero plan units) test gap. `FourALoop.run_4a` with a `LessonPlan` whose `plan_units == []` transitions directly to plan-lock (zero `plan_unit.created` + zero `scope_decision.set` + one `plan.locked`). Behavior covered by AC-B.3 but not pinned by a dedicated test. Natural home: 30-3b or 32-3.
- [Review][Defer][30-3a-EC2] Prior-decline rationale naming an unknown `unit_id` is silent-skipped at `FourALoop.run_4a` step 2. Behavior is correct but not explicitly tested. Natural home: 30-3b or 32-3.

Dated 2026-07-19 (Q1.1 code-review triage; DEFER). From the `bmad-code-review` of Story Q1.1 (scorecard schema v2 + generalized reader).

- [Review][Defer][Q1.1-CR1] `scripts/utilities/quality_scorecard.py --check` staleness ratchet keys on the block-level `as_of`, not per-dimension `as_verified`. This belongs to Q1.3, which owns the honesty-pin ratchet framework and demotes `--check` to a secondary nag (per Q1.1 AC4 note + GL-6). No action in Q1.1: the `as_of`/`as_verified` split lands structurally here; consuming `as_verified` in the staleness check is Q1.3's job. Natural home: Q1.3.

## Q1.4a R2 fence_state witness obligation (GL-10)

Dated 2026-07-19. Filed by Story Q1.4a (per-run `fence_state` + honest `silent_bypass_events` detector). Q1.4a landed the run-summary emission + hermetic (direct-emit) coverage; the live E2E witness is deferred to R2 per GL-10.

- [Defer][Q1.4a-R2] **R2 operator-steered trial witnesses `fence_state`.** During the R2 operator-steered live trial, capture the emitted `run_summary.yaml` `fence_state` block to a NAMED evidence artifact, then ASSERT equality between the witnessed `fences_enabled` / `hil_allowlist_empty` / `cost_posture` / `silent_bypass_events` and the INDEPENDENTLY-computed env truth for that run (a checkable comparison, not a mere observation): read `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE` / `MARCUS_COVERAGE_GATE_ACTIVE` / `MARCUS_UDAC_ACTIVE`, `hil_tabular_projector.KNOWN_UNRENDERED_ALLOWLIST`, and the run's `cost-report.json` `cost_posture` at trial time and confirm the run_summary matches. No live trial is run inside Q1.4a. Reactivation trigger: the next R2 operator-steered trial.

- [Defer][Q1.4a-DETECTOR] **Wire a REAL silent-bypass detector.** Today `fence_state.silent_bypass_events` is `"undetected"` on 100% of real runs (no caller supplies the detector signal). GL-8's honest sentinel is shipped (Q1.4a); a real cross-walk detector — a run-scoped ledger counting the uncounted bypass classes (e.g. the Path-Z §05/§05B skip) so a completed run can emit a genuine `0`/`N` instead of `"undetected"` — is future work (rides/after R2). Distinct from the Q1.4a-R2 witness obligation above (that witnesses the sentinel; this replaces it with a real count).

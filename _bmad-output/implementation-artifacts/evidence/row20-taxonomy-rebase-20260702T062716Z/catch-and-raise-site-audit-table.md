# Row-20 taxonomy re-base — enumerated catch-site + raise-site audit (gate artifact)

Task-3 party pick (carried-findings-remediation-greenlight-party-record-2026-07-02.md, Task-3 sequencing round, 3/3).
Change under audit: `VoiceProviderTextError` (`app/specialists/_shared/voice_provider_text.py`) and
`StyleguideError` (`app/specialists/gary/styleguide_library.py`) re-based `Exception` -> `SpecialistDispatchError`
(RuntimeError-derived; identical `(message, *, tag)` ctor now inherited). Template: 37f8323.

## Catch-site table

| # | file:line | clause | pre-change behavior | post-change behavior | verdict | intentional? |
|---|-----------|--------|---------------------|----------------------|---------|--------------|
| 1 | app/specialists/enrique/_act.py:549 | `except VoiceProviderTextError as exc` (wraps compile_provider_text + build_text_channels) | caught by name -> re-raised as `EnriqueActError(tag=exc.tag)` (dispatch-family) | identical — by-name subclass identity preserved; first matching clause | unchanged | yes (live narration path; conversion already routes to error-pause at the runner) |
| 2 | app/specialists/irene/authoring/warm_callback.py:133 | `except VoiceProviderTextError as exc` (wraps assert_rhetorical_source_containment) | caught by name -> `kept=False` block-by-omission | identical | unchanged | yes |
| 3 | skills/bmad-agent-marcus/scripts/generate-storyboard.py:545 | `except VoiceProviderTextError as exc` (v3 preview compile) | caught by name -> `{"status": "fail"}` panel | identical — by-name clause precedes the `except Exception` at :547, MRO/first-match preserved | unchanged | yes |
| 4 | skills/bmad-agent-marcus/scripts/generate-storyboard.py:520 | `except Exception` (around the leaf IMPORT, not raise sites) | import failure -> `return None` | identical (leaf's new import `app.specialists.dispatch_errors` is a zero-import stdlib module; import cannot newly fail) | unchanged | yes |
| 5 | app/specialists/gary/_act.py:471 | `except StyleguideError as exc` (wraps resolve_styleguide) | caught by name -> re-raised as `GaryActError(str(exc), tag=exc.tag)` | identical | unchanged | yes (live Gamma path) |
| 6 | scripts/utilities/validate_gamma_style_guides.py:180 | `except StyleguideError as exc` (expand_record) | caught by name -> appended to errors list | identical | unchanged | yes (offline write-gate) |
| 7 | scripts/utilities/validate_gamma_style_guides.py:327 | `except StyleguideError` (expand_record, learned-rules leg) | caught by name -> `resolved = {}` | identical | unchanged | yes |
| 8 | app/marcus/orchestrator/production_runner.py:1637, 2300, 2366, 2476, 2529, 2587, 3034, 3096, 3202, 3252, 3311 | `except SpecialistDispatchError` (both walkers' shared dispatch sites -> `_pause_at_error`) | an ESCAPED VoiceProviderTextError/StyleguideError was NOT caught -> uncaught crash, walk dead | now-also-caught -> recoverable error-pause | now-also-caught-by-SpecialistDispatchError | yes — this routing change IS the fix (crash -> error-pause per PIN-AUD-3T). On today's live paths both errors are already converted at rows 1/5 before reaching these clauses, so observed runner behavior is byte-identical; the new routing covers only a future uncovered escape. |
| 9 | app/marcus/cli/gate_shims/g{1,2b,2c,3,4,4a}_shim.py:41 | `except RuntimeError` | would NOT catch (both were Exception-based) | WOULD catch if ever reached | widened-but-unreachable | n/a — shims wrap resume_api gate calls; neither module is invoked beneath them (verified: no import/call path from gate shims into voice_provider_text or styleguide_library) |
| 10 | broad `except Exception` sites on adjacent paths (irene/graph.py:1132,1179; gary/gamma_dispatch.py:75; enrique/elevenlabs_dispatch.py:104; storyboard_publisher.py:324,352; fanout.py:173; styleguide_picker.py:557,680; coverage_runner.py:592,656; marcus_interlocutor.py:490; generate-storyboard.py:547 et al.) | `except Exception` | caught (Exception base) | caught (RuntimeError ⊂ Exception) | unchanged | yes |
| 11 | app/marcus/lesson_plan/coverage_receipt.py:622,692 | no except — calls `audit_rhetorical_source_containment` (REPORTING variant; documented "never raises") | no exception path | identical | unchanged | yes |
| 12 | tests: tests/specialists/_shared/test_voice_provider_text.py (7x pytest.raises), tests/utilities/test_validate_gamma_style_guides.py (3x), tests/specialists/gary/test_scripted_min_cluster_floor.py (2x), test_styleguide_resolution_seam.py (1x), tests/marcus/orchestrator/test_irene_pass1_floor_threading.py:236 | `pytest.raises(...)` / `except StyleguideError` | pass | pass (subclass identity preserved) — all re-run GREEN post-change | unchanged | yes |

Dangerous-inverse summary: the ONLY behavioral delta is row 8 — an error escaping uncaught past the by-name
conversion sites now routes to `_pause_at_error` instead of killing the walk. That is precisely the ratchet's
stated purpose ("kills the cycle-5 walk-dead-instead-of-error-pause crash class"). No catch site narrowed;
no by-name handler bypassed; no MRO reordering at any multi-clause try (row 3 verified explicitly).

## Raise-site table

All raise sites live inside the two defining modules; every raise already uses the `tag=` kwarg, which matches
the inherited `SpecialistDispatchError.__init__(self, message, *, tag)` signature EXACTLY (the subclasses' former
own `__init__` was byte-equivalent and was removed per the 37f8323 pattern; the taxonomy pin now proves the
INHERITED ctor carries the tag).

VoiceProviderTextError (app/specialists/_shared/voice_provider_text.py):
- :~153 `assert_no_tag_leak` — tag `elevenlabs.v3.captions.tag-leak`
- :~171 `compile_provider_text` — tag `elevenlabs.v3.role.unpopulated`
- :~183 `compile_provider_text` — tag `elevenlabs.v3.canonical.contains-tag`
- :~197 `compile_provider_text` — tag `elevenlabs.v3.firewall.breach`
- :~346 `assert_rhetorical_source_containment` — tag `elevenlabs.v3.vera-r7.source-containment`

StyleguideError (app/specialists/gary/styleguide_library.py):
- :132/:140/:145/:150 `load_style_guides` — tag `gamma.styleguide.load-error`
- :202 `_expand_api` — tag `gamma.styleguide.incomplete`
- :244/:253 studio surface checks — tag `gamma.styleguide.surface-violation`
- :305/:317 scripted enum checks — tags `gamma.scripted.unknown-class` / `gamma.scripted.bad-value`
- :341 `resolve_styleguide` — tag `gamma.styleguide.unknown`

Constructors of downstream wrappers (`EnriqueActError`, `GaryActError`) are already dispatch-family (37f8323)
and unchanged.

## Import-contract verdict (bar-4 caution)

- Contract M3 forbids `app.specialists` -> `app.marcus.{facade,intake,orchestrator}` only. The new import
  `app.specialists.dispatch_errors` is INSIDE `app.specialists` and imports nothing (pure stdlib leaf) — no
  cycle, no fence breach. voice_provider_text's leaf purity ("no app.marcus, nothing from irene at runtime")
  holds; docstring updated to record this.
- lint-imports: 14 kept / 1 broken BOTH at HEAD and post-change (stash-verified). The broken contract
  (`app.specialists.workbook_producer.graph -> app.gates.resume_api`, C3) is PRE-EXISTING ambient on this
  branch, untouched by this change.

## Witnesses (this dir)

- red-witness-taxonomy.txt — PRE-edit: 1 failed (the ratchet, exactly the two row-20 classes) / 2 passed
- green-witness-taxonomy.txt — POST-edit: 3 passed
- battery-touched-modules-and-error-pause.txt — 184 passed (voice_provider_text + styleguide + warm_callback + enrique v3 + crash-taxonomy guard + coverage-gate wiring + production_runner error-pause/gate-pause + storyboard v3 parity/display)
- battery-gary-enrique-shared-full.txt — 311 passed, 1 skipped (full tests/specialists/{gary,enrique,_shared})
- battery-full-contracts.txt — 311 passed, 1 skipped, 2 failed = EXACTLY the pre-declared row-18 (test_30_1_zero_test_edits, E) + row-14 (test_transform_registry_lockstep, L-pending) — row 20 now GREEN
- battery-tw7c4-audit.txt — 4 passed, 1 failed (`test_live_dispatch_python_scope_is_bounded`) — fire is on 10 pre-existing untracked `scratchpad/*.py` drivers from prior sessions, stash-verified IDENTICAL at HEAD; app-scope predicate PASSES with the new roster entries

Non-vacuity (bar 2): the ratchet walks every module under `app.specialists` (+ EXTRA_MODULES) and asserts
`issubclass(obj, SpecialistDispatchError)` for every Exception type whose ctor takes `tag` — behavioral
subclass membership by discovery, not name-presence. NON-VACUOUS as-is; additionally the two classes were
added to the `test_known_rebased_classes` by-name pin with ctor-semantics assertions per the template.
EXCLUSIONS untouched (the pair was never excluded — born non-compliant; shrink-only ratchet intact).

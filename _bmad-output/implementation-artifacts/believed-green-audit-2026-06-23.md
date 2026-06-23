# Believed-Green Tracker Audit — 2026-06-23

**Scope:** READ-ONLY two-strata sweep of all specialists under `app/specialists/` (+ underlying `skills/` provider modules) for anti-pattern **G1** (`docs/dev-guide/dev-agent-anti-patterns.md` §G1: "Fixture-backed contract mistaken for live capability") and the believed-green **config-drift** sibling. Charge per deferred-inventory entry `believed-green-tracker-audit`.

**Method:** grepped the G1 signature set (`fixture-v`, `_stub`, `PROVIDER_ENDPOINT`, `API_KEY`, `recorded`, `golden`, `snapshot`, `published_catalog`, `cascade`); traced each dispatch seam through to the underlying `skills/` operation module and its API client; ran the two believed-green guard tests (`test_no_fictitious_model_ids.py`, `test_cascade_ids_in_openai_published_catalog.py`) to capture ground-truth green/red.

**IN-FLIGHT exclusion (no firm verdict):** `app/specialists/vision/*`, `scripts/utilities/reading_path_*` + `scripts/analysis/reading_path_*`, `app/models/perception/*` are being edited concurrently by the S2 build (live `gpt-5.5` multimodal perceiver, replacing the retired `vision-fixture-v1` contract). Observations there are noted as transient, NOT flagged as defects.

---

## Stratum (a) — Liveness per specialist

Shared LLM seam: every LLM-driven specialist resolves its model via `selector.resolve(...)` (live cascade) → `make_chat_model()` (`app/models/adapter.py:70`), which returns a real `langchain_openai.ChatOpenAI` and `.invoke()`s the live OpenAI API. When `OPENAI_API_KEY` is unset, a deliberately-invalid sentinel `sk-substrate-no-real-key-do-not-invoke` is injected (`adapter.py:34,97`) that **fails loud server-side at invoke** — it does NOT return canned text. No fixture in the LLM production path.

| Specialist | Live? | Endpoint / SDK | Signature hits (file:line) | Risk | Recommended verification |
|---|---|---|---|---|---|
| **enrique** | GENUINE LIVE | ElevenLabs HTTP `api.elevenlabs.io/v1` via `skills/elevenlabs-audio/.../elevenlabs_operations.py` → `ElevenLabsClient` | `elevenlabs_dispatch.py:32-44` (`_ensure_module_stub` = benign importlib shim, **not** a fixture); `elevenlabs_operations.py:33,1079` | LOW | key-gated `pytest -m live` TTS smoke; assert non-empty audio bytes + alignment |
| **gary** | GENUINE LIVE (INDIRECT) | Gamma API via `skills/gamma-api-mastery/...`; `_require_gamma_api_key()` **raises** if `GAMMA_API_KEY` unset | `gamma_dispatch.py:30,41` (`allow_fixture` opt-in, prod never sets) | LOW | live deck-export smoke, key-gated |
| **kira** | GENUINE LIVE | Kling/Kuaishou client via `skills/kling-video/.../run_motion_generation.py` | `kling_dispatch.py:46,59` (`allow_fixture` mock-MP4 opt-in, prod never sets) | LOW | live motion-gen smoke, key-gated; assert real MP4 not mock |
| **wanda** | GENUINE LIVE (EP/DP/AS); local-synth (CM/AH) | Wondercraft HTTP `/podcast`, `/podcast/scripted` via `scripts/api_clients/wondercraft_client.py` | `wondercraft_dispatch.py:166-171` (MB unimplemented **raises** unless `allow_fixture`) | LOW | live podcast smoke; confirm CM/AH local synthesis is intentional (legit, not fixture) |
| **texas** | GENUINE LIVE via subprocess (provider-dependent) | venv-python → `skills/bmad-agent-texas/scripts/run_wrangler.py` retrieval providers | `retrieval_dispatch.py:16-18,69,78` — `DEFAULT_FIXTURE_BUNDLE` reachable only via `allow_fixture=False` default + explicit RAISE (S0 fail-loud, SCP 2026-06-11) | LOW (seam) / MED (Scite provider) | seam is GOOD pattern; Scite provider has a separate known gap — see `5a-2-scite-mcp-oauth-integration` in deferred-inventory |
| **quinn_r** | NO-EXTERNAL (deterministic validators) + LLM review via `make_chat_model` | local file validators via `skills/quality-control/scripts/*`; `_ensure_module_stub` benign shim | `quality_control_dispatch.py:71,153` (fail-loud starvation raise) | LOW | n/a (deterministic); LLM-review leg covered by shared seam |
| **vera** | modality-dependent; LLM via shared seam | `skills/sensory-bridges/scripts/bridge_utils.py::perceive`; `image` modality → vision perceiver (**IN-FLIGHT S2**) | `vera/sensory_bridges_dispatch.py:63-69` (`allow_fixture` low-confidence short-circuit, prod never sets) | LOW (seam) | image-modality verdict deferred to S2 close |
| **tracy** | NO-EXTERNAL (bounded by design) + LLM via shared seam | `posture_dispatch.py` → vocab YAML → trail-tag string | `posture_dispatch.py:28-33` (returns a tag string; intentional no-op) | LOW | n/a — confirm intent at next review |
| **compositor** | NO-EXTERNAL (deterministic assembly) | file copy/hash bundle | `compositor/_act.py:34-60` | LOW | n/a |
| **irene / irene_pass1 / cd / dan / desmond / kim / vyx / aria / mira / tamara** | GENUINE LIVE | OpenAI via shared `make_chat_model` → `ChatOpenAI.invoke` | `irene/graph.py:769,806`; `adapter.py:97` | LOW | key-gated live `.invoke` smoke per specialist (construction-only tests do not exercise the live call — see Note 1) |
| **vision / perception** | IN-FLIGHT (S2) — live `gpt-5.5` perceiver replacing retired `vision-fixture-v1` | `vision/provider.py:3-22`, `vision/model_config.yaml:7` | EXCLUDED | verdict deferred to S2 close; was the original confirmed G1 instance |

### Notes on stratum (a)
1. **`make_chat_model` placeholder-key path is fail-loud, not fixture-backed.** Construction succeeds without a key (sentinel injected), so a believed-green *construction-only* test could pass while `.invoke` is never exercised. This is the documented Slab-1 boundary, not a hidden fixture — but it means per-specialist live `.invoke` smokes are the actual liveness proof, and several specialists may lack one. Lowest-effort hardening: a single parametrized key-gated `.invoke` smoke across all LLM specialists.
2. **`_ensure_module_stub` (enrique, quinn_r, vera dispatch) is a benign importlib namespace shim**, NOT a G1 fixture-contract. It creates empty parent packages so `spec_from_file_location` resolves. Do not flag.
3. **Uniform S0 fail-loud remediation** (SCP 2026-06-11 "segment-data-plane") is in place across every billing/asset dispatch: fixtures reachable ONLY via an `allow_fixture=` kwarg that production dispatch never sets; missing inputs RAISE rather than silently emitting placeholder artifacts. This is the systemic fix for the prior "fixture slides into attempt-4 envelope" class. **No fixture-in-production-path found in any non-in-flight specialist.**

---

## Stratum (b) — Believed-green config / catalog-snapshot drift

### 🔴 HIGH — Stale denylist guard contradicts the refreshed catalog allowlist (LIVE RED on HEAD)

**`tests/test_no_fictitious_model_ids.py` is RED on clean HEAD (15 occurrences).** Confirmed by running the test.

Root cause: `gpt-5.4` (priced + registered since 2026-06-11) and `gpt-5.5` (vision-capable, released 2026-04-24; party-mode-ratified Tier-2 add) are now **real, registry-blessed models**. The allowlist guard was correctly refreshed — `tests/fixtures/openai_catalog_snapshot.json` (snapshot_date 2026-06-21) lists both, and `test_cascade_ids_in_openai_published_catalog.py` **PASSES**. But the denylist guard `test_no_fictitious_model_ids.py` was NOT updated: its `FORBIDDEN_IDS` tuple still contains `"gpt-5"+".4"` and `"gpt-5"+".5"` (lines 38-39) and its docstring still claims "Real OpenAI catalog (April 2026)" (line 16). The two guards now **disagree**: allowlist says these IDs are real → green; denylist says they are fictitious → red.

Hits flagged by the red test (the load-bearing, non-in-flight subset):
- `app/models/registry.yaml` — `gpt-5.4`, `gpt-5.5` (the registry entries that BLESS these models; `registry.yaml:48,60`)
- `runtime/config/model_cascade.yaml` — `gpt-5.5` (`:29`)
- `runtime/config/openai_pricing.yaml` — `gpt-5.4`, `gpt-5.5`
- `app/specialists/dan/model_config.yaml`, `irene_pass1/model_config.yaml`, `tracy/model_config.yaml` — `gpt-5.4` defaults

In-flight subset (do NOT remediate here; will move under S2): `app/models/perception/perception_artifact.py`, `app/specialists/vision/{payload_contract,provider,_act,model_config}.py`, `scripts/analysis/reading_path_corpus_scan.py`, `scripts/analysis/reading_path_holdout_perceive.py`.

This is a textbook believed-green/believed-RED-on-HEAD instance — the exact second root example named in the audit charge ("a model id added to runtime config but not the [guard] was RED on clean HEAD"). It is also a NEW finding: the deferred inventory tracks the *allowlist* staleness (`postmigration-catalog-snapshot-staleness-warn`) but NOT the denylist-vs-allowlist contradiction.

**Fix (out of scope for this read-only sweep):** remove `gpt-5.4`/`gpt-5.5` from `FORBIDDEN_IDS`, refresh the docstring's "Real OpenAI catalog (April 2026)" line + the `(gpt-5, ...)` help text to the current catalog, and keep only the genuinely-fictitious IDs (`gpt-5.4-nano`, `gpt-5-haiku`, `gpt-5-codex`). Single source of truth should be the catalog snapshot; the denylist should derive its allowed set from it (or at minimum be refreshed in lockstep — same gap the inventory's `postmigration-cascade-config-collapse` and `catalog-snapshot-staleness-warn` entries circle).

### 🟡 MED — Two divergent sources of truth for per-specialist model assignment (known, tracked)

`runtime/config/model_cascade.yaml` and 17 per-specialist `app/specialists/<name>/model_config.yaml` files both encode model IDs and can drift semantically (lint guards catch fictitious tokens, not a specialist pinned to a stale-but-real successor). Already filed: `postmigration-cascade-config-collapse` (deferred-inventory line 132). No new action; surface at the catalog-snapshot remediation alongside the HIGH item.

### 🟢 LOW — Catalog snapshot itself is current but lacks a freshness CI guard (known, tracked)

`openai_catalog_snapshot.json` is fresh (2026-06-21, `next_refresh_due_by` 2026-09-21) but no CI guard fails when the date lapses. Already filed: `postmigration-catalog-snapshot-staleness-warn` (line 133). No new action.

---

## Riskiest-first ranking

1. **🔴 HIGH — stale denylist `test_no_fictitious_model_ids.py` (RED on HEAD).** Live failing test; blocks any clean full-suite run; will keep firing on every legitimate `gpt-5.4`/`gpt-5.5` reference. NEW finding.
2. **🟡 MED — Scite retrieval provider** structurally wrong against the real MCP (auth + tool-count + params + response shape). Already tracked (`5a-2-scite-mcp-oauth-integration`); Texas dispatch seam itself is GOOD, but a live Scite retrieval through normal dispatch would fail/misbehave.
3. **🟡 MED — cascade-vs-per-specialist-config divergence** (semantic drift; tracked).
4. **🟢 LOW — per-specialist live `.invoke` smoke coverage gap** for LLM specialists (construction-only tests can be believed-green; the seam itself is genuinely live and fail-loud).

---

## Verify-before-next-trial list (prioritized)

1. **Remediate the stale denylist guard** (`test_no_fictitious_model_ids.py`) so the suite is green on HEAD and the denylist derives from / stays in lockstep with the catalog snapshot. Until fixed, full-suite green is unattainable and masks any *real* fictitious-ID regression. (Governance: substrate-touching → route through bmad-quick-dev + party + dev per project policy; this report is read-only and does not edit it.)
2. **Add one key-gated parametrized live `.invoke` smoke** across all LLM specialists (irene, irene_pass1, cd, dan, desmond, kim, vyx, aria, mira, tamara, quinn_r-review, vera-review, tracy) to convert "construction-only believed-green" into proof-of-live. `pytest.skip` when `OPENAI_API_KEY` absent.
3. **Key-gated live media smokes** for enrique (TTS), gary (Gamma export), kira (motion), wanda (podcast) — confirm each returns a real artifact (assert byte size / format), not the `allow_fixture` path.
4. **Re-confirm at S2 close** that vision/perception ships genuinely live (`gpt-5.5` multimodal) with a key-gated live-perceive smoke and that `vision-fixture-v1` is fully retired from the production path — closes the original G1 instance.
5. **No action needed** on the S0 fail-loud dispatch remediation — it is correctly in place repo-wide; record as the positive control.

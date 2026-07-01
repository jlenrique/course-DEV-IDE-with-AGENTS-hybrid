# Leg-3 — Per-Sub-Slide 07G VO↔on-screen Invariant on Clustered Slide c-u03

**UTC:** 2026-07-01T02:10:37Z
**Repo / branch:** course-DEV-IDE-with-AGENTS-hybrid @ `dev/concierge-production-substrate-2026-06-29`
**Driver (pre-validated, offline):** `scratchpad/leg3_perception_persubslide_driver.py`
**Bundle:** `scratchpad/leg3-c-u03-persubslide-bundle/`
**Agent:** independent live-validation agent. Protocol: FIRST-RUN-STANDS, NO MOCKS, real APIs, sequential, deterministic + independent judging.

Cluster c-u03 = head slide-05 ("66%") + interstitials slide-06/07. Rendered per sub-slide to 3 distinct PNGs; each PNG perceived independently (gpt-5.5); Irene Pass-2 authored over the 3-slide roster; negative-control trip-wire proves the figure-citation gate has teeth.

## Per-step live outcome

| Step | Command | Result | Evidence |
|---|---|---|---|
| 1 build | `--build` | PASS | 3 slides (S05 head / S06,S07 interstitial), 16x9 Classic, themeId njim9kuhfnljvaa, keys loaded (OPENAI len=164 sk-proj / GAMMA len=52 sk-gamma) |
| 2 render (LIVE Gamma) | `--render --live` | PASS | generation_id `C5RyVdVJXWkj5zPikx3lk`, 44.3s, 1 generation → 3 cards → 3 distinct PNGs (965 KB / 1.38 MB / 556 KB) |
| 3 perceive (LIVE gpt-5.5) | `--perceive --live` | PASS | 3 artifacts, 3 distinct slide_id, 3 distinct source_png_path, all reading_path_source=llm_primary |
| 4 author (LIVE Pass-2) | `--author --live` | PASS | 3 narration segments, gate_b join PASS, gate_c figure-citation PASS; 28,719 tokens |
| 5 tripwire (LIVE neg-control) | `--tripwire --live` | PASS (raised) | real production gate raised `Pass2GroundingError(tag=irene.pass2.figure-contradiction)` on head-only 66% injected into interstitial card-02 |

No infra failures. No infra re-run needed. No quality do-over. First run stands.

## Independent verification (artifacts read directly, not exit codes)

### (a) PERCEPTION per sub-slide — PASS
3 perception artifacts in `perception-artifacts.json`, each with a distinct slide_id → its OWN PNG; no two share a PNG; every `reading_path_source == "llm_primary"`.

| slide_id | source_png_path | perceived content (sample) |
|---|---|---|
| c-u03-persubslide-probe-card-01 (HEAD) | ...\gamma-export\c-u03-persubslide-probe_slide_01.png | "Medical Knowledge Is Accelerating…"; **66% of physicians** in paragraph_left; exponential-growth infographic (RESEARCH/INNOVATION/DIAGNOSTICS/…); split_image_text |
| c-u03-persubslide-probe-card-02 (INTERSTITIAL) | ...\gamma-export\c-u03-persubslide-probe_slide_02.png | "Adoption Is Racing. Oversight Is Not."; two_up_comparison; adoption/oversight/bottom-risk callouts; **no percent figure** (uses "Two-thirds" textually) |
| c-u03-persubslide-probe-card-03 (INTERSTITIAL) | ...\gamma-export\c-u03-persubslide-probe_slide_03.png | "When Used Thoughtfully…"; RemoteMed dashboard (SpO2 **92%**, alert **91%**, HR 74, BP 128/82); VR simulation; multi_column |

### (b) TRACEABLE references — PASS
`pass2-output.json` — every segment's `visual_references[*].perception_source` keys to its OWN slide_id; zero cross-sub-slide orphans:

- seg-c-u03-01 (slide_id card-01) → 3 refs, all perception_source = card-01
- seg-c-u03-02 (slide_id card-02) → 3 refs, all perception_source = card-02
- seg-c-u03-03 (slide_id card-03) → 3 refs, all perception_source = card-03

Driver's 4 post-parse gates passed: extracted_source_ok, roster join (gate_b_join=PASS), cross_artifact_path_match=true, gate_c_figure_citation=PASS.

### (c) FIGURE-CITATION 0-contradiction per sub-slide — PASS
No `irene.pass2.figure-contradiction` on the clean author run. The load-bearing observation: the head-only **66%** figure did NOT bleed into the interstitials. Interstitial card-02's authored narration says **"about two-thirds of physicians"** — its own slide's language — NOT "66%". Every numeral each segment speaks is present on that segment's own perceived slide. This is the per-sub-slide invariant holding.

### (d) TRIP-WIRE (negative control) — PASS
The `--tripwire --live` run drove the REAL production gate `app.specialists.irene.graph._assert_figure_citations_within_perceived` over the LIVE roster. It selected interstitial card-02 (head figure `percent:66` absent from card-02's perceived figures), injected `66%` into card-02's real narration text, and the gate raised. Confirmed via a standalone let-it-propagate reproduction (see `tripwire-raise.stderr.txt`):

```
app.specialists.irene.graph.Pass2GroundingError: scope=narration;
  slide c-u03-persubslide-probe-card-02 narration figures not present
  in perceived authority: ['percent:66']
  (graph.py:693)
```

Driver also confirmed field-sensitivity: clean text = no raise; injection into a NON-read field (visual_description) = no raise; only injecting into the gate-read field (narration text) raises. Trip-wire was CONSTRUCTIBLE (head had usable numeral 66) — no BLOCKED fallback invoked.

## OVERALL VERDICT: **PASS**

The 07G VO↔on-screen invariant holds PER SUB-SLIDE on clustered slide c-u03: each sub-slide is perceived from its own PNG, Pass-2 references are traceable to the correct sub-slide, no figure bleeds across sub-slides, and the gate authentically raises when a head-only figure is forced into an interstitial's narration.

## Live spend
- **Gamma:** 1 generation (id C5RyVdVJXWkj5zPikx3lk) → 3 Classic 16x9 cards. Exact credit debit not exposed in the artifact; a 3-card Classic generation (low tens of credits, Classic tier — not Studio).
- **OpenAI perception (gpt-5.5 vision):** 3 calls (1 per PNG).
- **OpenAI author (gpt-5.5 reasoning tier, Pass-2):** 1 call = 28,719 total tokens (22,838 in / 5,881 out incl 3,648 reasoning).
- Trip-wire reused the authored output + cached perception → no additional Gamma/LLM spend. Two standalone raise reproductions also reused cached artifacts → no extra spend.
- **Totals:** 1 Gamma generation (3 cards); 4 OpenAI calls (3 perception + 1 author).

## Guardrails honored
No commit, no push, no source-code edit. Evidence written only under this bundle dir. Live keys from `.env`. Real APIs only; no mocks.

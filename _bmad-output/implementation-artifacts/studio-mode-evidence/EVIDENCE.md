# Studio-B via create-from-template — live evidence (2026-06-25)

Real artifacts from the live de-risking of the `production_mode: studio` B-variant feature.
These pin the spec/dev facts (request field, card-type markers, costs) and serve as the guard's
test fixtures (real Studio = PASS; real Classic = the genuine adversary = RAISE).

## Finding (reverses the earlier "Studio is UI-only / Playwright required" note)

Gamma's **create-from-template API produces genuine Studio image-cards** when driven with a
**lock-and-replace** prompt. Plain `/generations` is still Classic-only. **No Playwright needed.**

## Template

- Name `Tejal-C1M1-template-B-STUDIO`, id `g_nv5q4da69qiiu8q`.
- A **1-card image-card** template (`read_gamma`: card-type=`image`, single AI image with title+data baked into the prompt).
- Carries **A's theme** `njim9kuhfnljvaa` ("2026 HIL APC (Nejal)") + `artStylePreset: "custom"`.
- Operator decision: Studio-B uses **A's theme**; the A-vs-Studio-B differentiator is **treatment** (Classic typography vs Studio image-card), not theme.

## Runs

| # | generationId | docId | prompt style | Result | Cost (cr) | Artifact |
|---|---|---|---|---|---|---|
| 1 | `ZDykty77nYbOOj7GLmCM1` | `termumfhly9rdz0` | prose-dump + "make one card" | **CLASSIC (silent fallback)** | 3 | `CLASSIC-fallback-failure.png` |
| 2 | `ieMnpwul2lV1EZkZuI8ps` | `zb6sstgk6k8eloq` | lock-and-replace | **STUDIO** ✓ | 23 | `STUDIO-success-1-innovators-mindset.png` |
| 3 | `KJWe0gAxJltzLoi4Q6dgv` | `4i7rfndv4ywv4vd` | lock-and-replace (diff. slide) | **STUDIO** ✓ | 23 | `STUDIO-success-2-escalating-stakes.png` |

Run 1 is the **demonstrated silent-Classic-fallback failure mode** — HTTP success, no error, wrong card type. This is why the guard is non-negotiable.

## Pinned facts for the spec

- **Request field carrying the lock text:** the `prompt` param of `generate_from_template` (→ API `inputText`/prompt). NOT `additionalInstructions`.
- **Card-type markers in the SYNCHRONOUS generation response** (`get_generation_status` → `generationDetails.content…`), so the guard needs no separate read-back:
  - **STUDIO:** a single `cardImageItem` with `attrs.image.source: "image.ai-generated"` (and `loadImageParams.provider: "aiGenerated"`).
  - **CLASSIC:** `cardLayoutItem` / `smartLayout` / `gridLayout` / `smartDiagram` blocks; **no** `cardImageItem`.
- **Cost:** ~23 cr per Studio card vs ~3 per Classic (~8×). gpt-image-2.
- **Export:** `exportAs:"png"` → single signed PNG URL per 1-card gen (named by docId for Studio); **signed URLs expire ~1 week** (that's why the PNGs are copied here).

## Working lock-and-replace prompt (n=2 verified — freeze as the pinned constant)

> LOCK THE DESIGN. Keep exactly ONE single full-bleed image card with the title and key data embedded in the illustration. DO NOT convert the full-bleed image card into Classic typography. DO NOT add, remove, or reorder cards, and DO NOT change the card type or layout.
>
> ONLY swap the image subject to this new topic, matching the template's existing visual style:
> `<slide title + visual description>`

## Re-pulling the full response JSON

The full generation JSON (for fixtures) can be re-pulled by `generationId` via `get_generation_status`
while retained; capture both a STUDIO and the CLASSIC (run 1) response into the test tree at dev T-red-1.

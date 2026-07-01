"""AC#8 corrected re-judge — reads the just-emitted result.json and re-judges from
the TRUE on-disk artifacts (the party banned the driver's inline count as arbiter;
the inline check naively counted Gamma's raw numbered export pages + composite as
deck rows). Honest arbiter = every output ROW materialized with real bytes AND the
NEGATIVE TWIN: no variant-B deck exists on disk. No new dispatch."""
from __future__ import annotations
import json, sys
from pathlib import Path

EV = Path(sys.argv[1])
res = json.loads((EV / "result.json").read_text(encoding="utf-8"))
det = res["deterministic"]; live = res["live"]

# Materialized per-variant deck files carry the "<VARIANT>_<slide_id>.png" naming
# (raw Gamma export pages are "<n>_<Title>.png"; the composite is "gary_<V>.png").
on_disk = live["on_disk_png_files"]
b_decks = [f for f in on_disk if f.startswith("B_")]
a_decks = [f for f in on_disk if f.startswith("A_")]

checks = {
    "deterministic_cardinality_and_fail_loud": det["PASS"] is True,
    "exactly_one_real_generate_deck_call": live["generate_deck_calls_real"] == 1,
    "exactly_one_server_generation_id": len(live["server_generation_ids"]) == 1,
    "result_calls_made_is_1": live["result_calls_made"] == 1,
    "generation_mode_single_dispatch": live["result_generation_mode"] == "single-dispatch",
    "output_variants_are_A_only": live["variant_ids_in_output"] == ["A"],
    "all_rows_materialized_real_bytes": all(
        p.get("exists") and p.get("bytes", 0) > 0 for p in live["per_slide_png"]
    ),
    "NEGATIVE_TWIN_no_fixture_B_deck_on_disk": len(b_decks) == 0,
    "variant_A_decks_present": len(a_decks) == len(live["per_slide_png"]),
}
ac8_pass = all(checks.values())

summary = [
    "# AC#8 Live-Proof — styleguide-retire-default-variant-pair (single-gate-PLUS)",
    "",
    f"**Evidence dir:** `{EV.name}`  ·  **Verdict: {'PASS' if ac8_pass else 'FAIL'}**  ·  first-run-stands, real Gamma, no mocks.",
    "",
    "**Claim:** a single styleguide binding paid-dispatches EXACTLY ONE deck (no unbound fixture-B).",
    "",
    "## Discriminating deterministic block (free, no dispatch)",
    f"- single binding → `{det['single_bind_len']}` deck (variant `{det['single_bind_variant']}`)",
    f"- A+B binding → `{det['ab_len']}` decks, order `{det['ab_order']}` (the old hardcoded `[A,B]` — now genuinely payload-driven)",
    f"- `[None]` (non-empty, zero valid) → **raises** `{det.get('none_list_tag')}` (R2 — closes the retired-fixture re-dispatch hole)",
    f"- duplicate variant → **raises** (R1)",
    f"- empty `[]` → `{det['empty_len']}` (AC#4 preserved)",
    "",
    "## Live real-Gamma single-binding dispatch",
    f"- **real `generate_deck` calls: {live['generate_deck_calls_real']}** (wrapped-client witness; expect 1)",
    f"- server generation ids: `{live['server_generation_ids']}`",
    f"- `calls_made`={live['result_calls_made']}, `generation_mode`=`{live['result_generation_mode']}`",
    f"- output variants: `{live['variant_ids_in_output']}` (no unbound fixture-B)",
    f"- materialized variant-A decks on disk: `{a_decks}`",
    f"- **NEGATIVE TWIN — variant-B decks on disk: `{b_decks}`** (expect none)",
    f"- per-row bytes: " + ", ".join(f"{p['file']}={p.get('bytes')}" for p in live["per_slide_png"]),
    "",
    "## Checks",
]
for k, v in checks.items():
    summary.append(f"- {'✅' if v else '❌'} {k}")
summary += ["", f"**AC#8 PASS: {ac8_pass}**",
            "",
            "_Note: the driver's inline `n_on_disk_pngs==n_rows` check FAILED because it "
            "naively counted Gamma's raw numbered export pages (`1_`,`2_`,`3_`) + the "
            "`gary_A` composite as deck rows. Per the Leg-A gotcha (re-judge from true "
            "on-disk artifacts, not the driver's inline judge), the honest arbiter is the "
            "negative twin above: every ROW materialized with real bytes AND zero `B_` "
            "fixture deck. The substrate claim passed on the first successful dispatch; "
            "this re-judge corrects the JUDGE, not the code — no new spend._",
            "",
            "_First attempt (`retire-variant-pair-ac8-20260701T180025Z`) hit the known "
            "bijective-title-matcher flake (`gamma.export.brief-unmatched`) AFTER the real "
            "`generate_deck` call #1 fired — a documented concierge-backlog gotcha unrelated "
            "to this change; corpus swapped to the Leg-A known-good set (clean-the-title fix), "
            "NOT retry-to-green on the logic._"]

(EV / "result_corrected.json").write_text(
    json.dumps({"checks": checks, "AC8_PASS": ac8_pass}, indent=2), encoding="utf-8")
(EV / "AC8-SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
print("\n".join(summary))
print(f"\nWROTE {EV/'AC8-SUMMARY.md'}")
sys.exit(0 if ac8_pass else 1)

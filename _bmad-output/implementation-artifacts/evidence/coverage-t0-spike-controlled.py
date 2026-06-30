"""Controlled T0 segmentation spike — bounded + observable. Real gpt-5, hard per-request timeout.

Measures: assertions/block, seed-determinism (2 runs), latency, parse. NO build.
"""
from __future__ import annotations
import functools, json, os, re, sys, time
from pathlib import Path
from dotenv import load_dotenv

print = functools.partial(print, flush=True)
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
SLIDES = REPO / "course-content/courses/tejal-apc-c1-m1-p2-trends/slides"

os.environ.pop("OPENAI_API_KEY", None)
load_dotenv(REPO / ".env", override=True)
from openai import OpenAI
client = OpenAI(timeout=60.0, max_retries=0)
MODEL = "gpt-5"
SEED = 7

NOTES_RE = re.compile(r"\*\*Narration \(Speaker Notes\):\*\*\s*[\"“]?(.+?)[\"”]?\s*$", re.MULTILINE)

PROMPT = (
    "You are segmenting a slide's speaker notes into ATOMIC TEACHING ASSERTIONS for a coverage ledger. "
    "An assertion = ONE claim, instruction, caution, statistic, or framing the instructor intends a learner to take away. "
    "Split compound sentences; keep each assertion atomic and faithful (no fabrication, no merging unrelated claims). "
    "Return STRICT JSON: {\"assertions\":[{\"text\":\"<paraphrase of the single assertion>\",\"verbatim_span\":\"<exact substring from the notes>\"}, ...]}. "
    "Use ONLY content present in the notes.\n\nSPEAKER NOTES:\n"
)

def notes_for(p: Path) -> str | None:
    m = NOTES_RE.search(p.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None

def segment(notes: str) -> tuple[float, int, list, str]:
    t = time.time()
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT + notes}],
        max_completion_tokens=4000,
        reasoning_effort="low",
        response_format={"type": "json_object"},
        seed=SEED,
    )
    dt = time.time() - t
    raw = r.choices[0].message.content or ""
    try:
        items = json.loads(raw).get("assertions", [])
    except Exception as e:
        return dt, -1, [], f"PARSE_FAIL: {e}: {raw[:120]}"
    return dt, len(items), items, "ok"

def main() -> int:
    files = sorted(SLIDES.glob("slide-*.md"))[:3]
    print(f"[spike] {len(files)} blocks, model={MODEL}, per-req timeout=60s, seed={SEED}\n")
    summary = []
    for p in files:
        notes = notes_for(p)
        if not notes:
            print(f"[spike] {p.name}: NO notes block"); continue
        print(f"=== {p.name} ({len(notes)} chars) ===")
        dt1, n1, items1, s1 = segment(notes)
        print(f"  run1: {n1} assertions, {dt1:.1f}s, {s1}")
        dt2, n2, items2, s2 = segment(notes)
        print(f"  run2: {n2} assertions, {dt2:.1f}s, {s2}")
        det = (n1 == n2 and [i.get("text") for i in items1] == [i.get("text") for i in items2])
        print(f"  deterministic(count+text)={det}")
        if items1:
            print("  sample assertions (run1):")
            for it in items1[:6]:
                print(f"    - {str(it.get('text',''))[:100]}")
        summary.append({"slide": p.name, "n1": n1, "n2": n2, "det": det, "lat1": round(dt1,1), "lat2": round(dt2,1)})
        print()
    print("=== SUMMARY ===")
    for s in summary:
        print(f"  {s['slide']}: n={s['n1']}/{s['n2']} det={s['det']} lat={s['lat1']}/{s['lat2']}s")
    counts = [s["n1"] for s in summary] + [s["n2"] for s in summary]
    lats = [s["lat1"] for s in summary] + [s["lat2"] for s in summary]
    all_det = all(s["det"] for s in summary)
    bounded = counts and max(counts) <= 15 and min(counts) >= 1
    fast = lats and max(lats) <= 90
    print(f"\nVERDICT INPUTS: max_count={max(counts) if counts else 'NA'} (<=15), determinism_all={all_det}, max_latency={max(lats) if lats else 'NA'}s (<=90)")
    print(f"GATE: {'GO' if (bounded and all_det and fast) else 'REVIEW/ESCALATE'}")
    (REPO / "_bmad-output/implementation-artifacts/evidence").mkdir(parents=True, exist_ok=True)
    out = REPO / "_bmad-output/implementation-artifacts/evidence/coverage-t0-spike-controlled.json"
    out.write_text(json.dumps({"model": MODEL, "seed": SEED, "blocks": summary,
        "bounded": bounded, "deterministic": all_det, "fast": fast}, indent=2), encoding="utf-8")
    print(f"evidence -> {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

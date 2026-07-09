"""S2 AC-L live witness driver — REAL interactive ceremony through start_trial.

Real gh-pages publish (publish_picker default), real LLM composition, scripted
operator feeder, deterministic assertions, evidence pack. FIRST-RUN-STANDS.
"""
from __future__ import annotations

import faulthandler
import hashlib
import json
import os
import shutil
import sys
import threading
import traceback
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = REPO / "_bmad-output/implementation-artifacts/evidence/s2-acl-liveproof-20260706T211912Z"
CORPUS = REPO / "course-content/courses/tejal-apc-c1-m1-p2-trends"
GUIDE = "hil-2026-apc-crossroads-classic"
OPERATOR = "operator_juan"
HARD_TIMEOUT_S = 900

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log.txt", "a", encoding="utf-8")
TRANSCRIPT = open(EVIDENCE / "ceremony-transcript.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def transcript(kind: str, text: str) -> None:
    TRANSCRIPT.write(f"--- {kind} ---\n{text}\n")
    TRANSCRIPT.flush()


# ---------------------------------------------------------------- env (override gotcha)
def load_env_override() -> None:
    for raw in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        k, _, v = raw.partition("=")
        k, v = k.strip(), v.strip()
        if v:
            os.environ[k] = v  # OVERRIDE (dotenv gotcha: shell sentinel must lose)
    os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)  # first pause must be G1


load_env_override()
ok_key = os.environ.get("OPENAI_API_KEY", "")
assert ok_key.startswith("sk-") and "subst" not in ok_key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GITHUB_PAGES_TOKEN"), "GITHUB_PAGES_TOKEN absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")
log(f"env loaded: OPENAI_API_KEY={ok_key[:8]}...{ok_key[-4:]} (len {len(ok_key)}); "
    f"GITHUB_PAGES_TOKEN present; LANGSMITH present")

# watchdog: hard 15-min budget, dump stacks on trip
faulthandler.enable(LOG)


def _watchdog() -> None:
    log(f"WATCHDOG TRIPPED at {HARD_TIMEOUT_S}s — dumping stacks and exiting 3")
    faulthandler.dump_traceback(LOG)
    LOG.flush()
    os._exit(3)


timer = threading.Timer(HARD_TIMEOUT_S, _watchdog)
timer.daemon = True
timer.start()

from app.marcus.cli.trial import _course_key, start_trial  # noqa: E402
from app.marcus.cli.marcus_spoc import run_picker_preflight  # noqa: E402
from app.marcus.orchestrator.picker_html_emitter import build_selection_code  # noqa: E402
from app.marcus.orchestrator.styleguide_picker import (  # noqa: E402
    GAMMA_STYLEGUIDE_PICKS_PATH,
    load_picker_roster,
)
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
RUN_TAG = TRIAL_ID.hex
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(RUN_TAG, {"A": GUIDE})
COURSE_KEY = _course_key(CORPUS)
log(f"trial_id={TRIAL_ID} run_tag={RUN_TAG}")
log(f"selection code (pre-minted, versions=1): {CODE}")
log(f"canonical course key: {COURSE_KEY}")

state: dict = {
    "trial_id": str(TRIAL_ID),
    "run_tag": RUN_TAG,
    "selection_code": CODE,
    "course_key": COURSE_KEY,
    "path_taken": "happy-publish",  # flips to degrade-inline-list if publish fails
    "preflight_called": 0,
    "prompts": [],
}


def feeder(prompt: str) -> str:
    """Scripted operator: prompt-aware, fail-loud on anything unexpected."""
    transcript("PROMPT", prompt)
    if "Paste your selection code" in prompt:
        reply = CODE
    elif "Reply 'confirm'" in prompt:
        reply = "confirm"
    elif "Choose 1 (retry publish)" in prompt:
        state["path_taken"] = "degrade-inline-list"
        reply = "2"
    elif "Style A number" in prompt:
        roster = load_picker_roster(include_probes=False)
        idx = next(i for i, e in enumerate(roster, 1) if e["name"] == GUIDE)
        reply = str(idx)
    elif "Style B number" in prompt:
        reply = ""
    else:
        raise AssertionError(f"UNEXPECTED ceremony prompt: {prompt!r}")
    state["prompts"].append({"prompt": prompt, "reply": reply})
    transcript("REPLY", reply)
    log(f"feeder: {prompt.splitlines()[-1][:60]!r} -> {reply[:60]!r}")
    return reply


def capture_print(text: str) -> None:
    transcript("MARCUS", str(text))
    log(f"narration: {str(text).splitlines()[0][:100]}")


def preflight_wrapper(**kwargs):
    state["preflight_called"] += 1
    log(f"picker_preflight_fn invoked with keys={sorted(kwargs)}")
    state["preflight_kwargs"] = {
        k: str(v) for k, v in kwargs.items() if k in {"run_tag", "directive_path", "out_dir", "picked_by", "run_id", "course"}
    }
    record = run_picker_preflight(
        input_fn=feeder,
        print_fn=capture_print,
        **kwargs,
    )  # REAL publish_fn default = publish_picker (real gh-pages)
    state["pick_record"] = json.loads(json.dumps(record, default=str)) if record else None
    log(f"preflight returned: {state['pick_record']}")
    return record


def confirm_fn(*, directive_path, auto_confirm_directive):
    transcript("G0-CONFIRM-GATE", f"directive={directive_path} auto={auto_confirm_directive} -> scripted 'c' (confirmed)")
    log("G0 confirm gate: scripted confirm ('c')")
    return "confirmed"


log("=== invoking start_trial (REAL: gh-pages publish + LLM compose + walk to G1) ===")
t0 = datetime.now(tz=UTC)
try:
    result = start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        picker_preflight_fn=preflight_wrapper,
        confirm_fn=confirm_fn,
        max_specialist_calls=8,
    )
except BaseException:
    log("start_trial RAISED:\n" + traceback.format_exc())
    state["start_trial_exception"] = traceback.format_exc()
    result = None
elapsed = (datetime.now(tz=UTC) - t0).total_seconds()
log(f"start_trial returned after {elapsed:.0f}s: {json.dumps(result, default=str) if result else 'EXCEPTION'}")
state["start_trial_result"] = result
state["elapsed_s"] = elapsed

# ---------------------------------------------------------------- assertions
assertions: list[dict] = []


def check(name: str, ok: bool, value) -> None:
    assertions.append({"assertion": name, "pass": bool(ok), "value": value})
    log(f"ASSERT {name}: {'PASS' if ok else 'FAIL'} — {value}")


import yaml  # noqa: E402
import httpx  # noqa: E402

directive_path = RUN_DIR / "directive.yaml"
receipt_path = RUN_DIR / f"picker-publish-{RUN_TAG}.json"

# (a) real publish URL + verify-after-push 200 + independent GET 200
publish_url = None
if state["path_taken"] == "happy-publish":
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else None
    state["publish_receipt"] = receipt
    publish_url = (receipt or {}).get("publish_url")
    check(
        "a1-publish-url-real-ghpages",
        bool(publish_url) and str(publish_url).startswith("https://jlenrique.github.io/"),
        publish_url,
    )
    check(
        "a2-publisher-verify-after-push-200",
        bool(receipt) and receipt.get("verified_live") is True and receipt.get("http_status") == 200,
        {k: (receipt or {}).get(k) for k in ("verified_live", "http_status")},
    )
    try:
        r = httpx.get(str(publish_url), timeout=30, follow_redirects=True)
        check("a3-independent-httpx-get-200", r.status_code == 200, {"status": r.status_code, "bytes": len(r.content)})
    except Exception as exc:
        check("a3-independent-httpx-get-200", False, repr(exc))
else:
    check("a-degrade-path-ran-inline-list", True, "publish failed; inline-list arm exercised (valid AC-L outcome)")

# (b) directive carries the pick + provenance with the real URL
if directive_path.exists():
    doc = yaml.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    gs = doc.get("gamma_settings") or []
    row_a = next((r for r in gs if isinstance(r, dict) and str(r.get("variant_id", "")).upper() == "A"), None)
    check("b1-directive-gamma-settings-pick", bool(row_a) and row_a.get("styleguide") == GUIDE, row_a)
    prov = doc.get("styleguide_picker_provenance")
    expected_url = publish_url if state["path_taken"] == "happy-publish" else "degraded:inline-text-list (no picker page published)"
    check(
        "b2-provenance-block-publish-url",
        isinstance(prov, dict) and prov.get("publish_url") == expected_url and prov.get("run_tag") == RUN_TAG
        and prov.get("selection_code") == (CODE if state["path_taken"] == "happy-publish" else prov.get("selection_code")),
        {k: prov.get(k) for k in ("publish_url", "run_tag", "selection_code", "picked_by", "version_count")} if isinstance(prov, dict) else prov,
    )
    shutil.copyfile(directive_path, EVIDENCE / "directive.yaml")
else:
    check("b1-directive-gamma-settings-pick", False, f"directive missing: {directive_path}")
    check("b2-provenance-block-publish-url", False, "directive missing")

# (c) sidecar pick event carries F-502 course (canonical key)
events = []
if GAMMA_STYLEGUIDE_PICKS_PATH.exists():
    for line in GAMMA_STYLEGUIDE_PICKS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                ev = json.loads(line)
                if ev.get("run_id") == str(TRIAL_ID):
                    events.append(ev)
            except json.JSONDecodeError:
                pass
check(
    "c-sidecar-event-course-field",
    len(events) >= 1 and all(e.get("course") == COURSE_KEY for e in events)
    and any(e.get("variant_id") == "A" and e.get("guide_name") == GUIDE for e in events),
    events,
)
(EVIDENCE / "sidecar-event.jsonl").write_text(
    "\n".join(json.dumps(e, sort_keys=True) for e in events) + "\n", encoding="utf-8"
)

# (d) walk proceeded and PAUSED AT G1
run_json_path = RUN_DIR / "run.json"
if run_json_path.exists():
    rj = json.loads(run_json_path.read_text(encoding="utf-8"))
    check(
        "d-paused-at-G1",
        rj.get("status") == "paused-at-gate" and rj.get("paused_gate") == "G1",
        {"status": rj.get("status"), "paused_gate": rj.get("paused_gate"),
         "paused_error_tag": rj.get("paused_error_tag"),
         "evidence": rj.get("production_clone_launch_evidence")},
    )
    (EVIDENCE / "run-json-excerpt.json").write_text(
        json.dumps({k: rj.get(k) for k in (
            "trial_id", "status", "paused_gate", "paused_error_tag", "corpus_path",
            "started_at", "production_clone_launch_evidence",
            "production_clone_launch_evidence_reason")}, indent=2) + "\n",
        encoding="utf-8",
    )
else:
    check("d-paused-at-G1", False, f"run.json missing: {run_json_path}")

# (e) trial-start.json directive_digest == sha256(final directive bytes)
ts_path = RUN_DIR / "trial-start.json"
if ts_path.exists() and directive_path.exists():
    ts = json.loads(ts_path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    check(
        "e-directive-digest-matches-final-bytes",
        ts.get("directive_digest") == actual,
        {"trial_start_digest": ts.get("directive_digest"), "sha256_of_final_bytes": actual},
    )
else:
    check("e-directive-digest-matches-final-bytes", False,
          {"trial_start_exists": ts_path.exists(), "directive_exists": directive_path.exists()})

# publish receipt copy
if receipt_path.exists():
    shutil.copyfile(receipt_path, EVIDENCE / f"picker-publish-{RUN_TAG}.json")

# cost report (spend evidence)
cost_path = RUN_DIR / "cost-report.json"
if cost_path.exists():
    shutil.copyfile(cost_path, EVIDENCE / "cost-report.json")

state["assertions"] = assertions
state["all_pass"] = all(a["pass"] for a in assertions)
(EVIDENCE / "result.json").write_text(json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8")
log(f"=== WITNESS {'PASS' if state['all_pass'] else 'FAIL'} — path={state['path_taken']} — evidence at {EVIDENCE} ===")
timer.cancel()
sys.exit(0 if state["all_pass"] else 1)

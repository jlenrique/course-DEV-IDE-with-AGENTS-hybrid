"""ElevenLabs API exploration sweep (P5 directed-voice arc, §10 item 5).

Exercises EVERY locally-available ElevenLabs TTS request parameter with at
least one REAL live call, or records precisely why it is unavailable. This is
the BROADER API-exploration sweep, deliberately distinct from the production
heartbeat (the v1 product contract). No mocks. First-run-stands honesty.

Run FOREGROUND:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/diagnostics/elevenlabs_api_sweep.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
# --- Live-key recipe (MANDATORY) ---
os.environ.pop("ELEVENLABS_API_KEY", None)
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY not loaded"

sys.path.insert(0, str(REPO))
from scripts.api_clients.base_client import APIError, AuthenticationError  # noqa: E402
from scripts.api_clients.elevenlabs_client import ElevenLabsClient  # noqa: E402

UTCSTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
EVID = REPO / "_bmad-output/implementation-artifacts/evidence"
AUDIO_DIR = EVID / "elevenlabs-sweep-audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = EVID / f"p5-directed-voice-elevenlabs-api-sweep-{UTCSTAMP}.calls.json"

TEXT = "Hello from the sweep."  # ~21 chars, keeps cost tiny

calls: list[dict] = []


def record(**kw) -> None:
    calls.append(kw)
    LOG_PATH.write_text(json.dumps(calls, indent=2, default=str), encoding="utf-8")
    print(f"  -> {kw.get('outcome')}: {kw.get('note','')[:120]}", flush=True)


def err_detail(exc: Exception) -> tuple[int | None, str]:
    status = getattr(exc, "status_code", None)
    body = getattr(exc, "response_body", None)
    if body is None:
        body = str(exc)
    return status, json.dumps(body, default=str)[:600]


def tts(label: str, *, voice_id: str, **params):
    """One live TTS call via the request-id-bearing seam. Returns TtsResult or None."""
    print(f"[{label}] params={ {k:v for k,v in params.items() if k!='text'} }", flush=True)
    t0 = time.time()
    try:
        res = client.text_to_speech_with_request_id(TEXT, voice_id, **params)
        dt = round(time.time() - t0, 1)
        md5 = hashlib.md5(res.audio).hexdigest()
        record(
            label=label, params={k: v for k, v in params.items()},
            outcome="ACCEPTED", status=200, request_id=res.request_id,
            bytes=len(res.audio), md5=md5, seconds=dt,
            note=f"{len(res.audio)} bytes, request_id={res.request_id}",
        )
        return res
    except (APIError, AuthenticationError) as exc:
        dt = round(time.time() - t0, 1)
        status, detail = err_detail(exc)
        outcome = "UNAVAILABLE" if status in (401, 403) else "REJECTED"
        record(
            label=label, params={k: v for k, v in params.items()},
            outcome=outcome, status=status, request_id=None,
            bytes=0, seconds=dt, note=f"HTTP {status}: {detail}",
        )
        return None


# ============================================================
# Phase 1 — cheap probes
# ============================================================
client = ElevenLabsClient()
print("=== Phase 1: cheap probes ===", flush=True)

tier = char_used = char_limit = None
user = None
try:
    user = client.get_user()
    sub = user.get("subscription", {}) if isinstance(user, dict) else {}
    tier = sub.get("tier")
    char_used = sub.get("character_count")
    char_limit = sub.get("character_limit")
    print(f"user tier={tier} chars={char_used}/{char_limit}", flush=True)
    (EVID / f"p5-directed-voice-elevenlabs-get-user-{UTCSTAMP}.json").write_text(
        json.dumps(user, indent=2, default=str), encoding="utf-8")
    get_user_note = f"tier={tier} chars={char_used}/{char_limit}"
    get_user_outcome, get_user_status = "ACCEPTED", 200
except (APIError, AuthenticationError) as exc:
    st, dt = err_detail(exc)
    get_user_outcome = "UNAVAILABLE"
    get_user_status = st
    get_user_note = f"HTTP {st}: {dt}"
    print(f"get_user UNAVAILABLE: {get_user_note}", flush=True)

models = client.list_models()
model_ids = [m.get("model_id") for m in models]
usable = [m.get("model_id") for m in models if m.get("can_do_text_to_speech")]
print(f"models can-do-tts: {usable}", flush=True)

voices = client.list_voices()
# Prefer a known premade voice for comparability; else first voice.
voice = None
for v in voices:
    if v.get("name") in ("Rachel", "Adam", "Bella", "Antoni"):
        voice = v
        break
voice = voice or (voices[0] if voices else None)
assert voice, "no voices available"
VOICE_ID = voice["voice_id"]
print(f"using voice {voice.get('name')} ({VOICE_ID})", flush=True)

# voice detail probe
voice_detail = client.get_voice(VOICE_ID)
record(label="get_user", params={}, outcome=get_user_outcome,
       status=get_user_status, request_id=None, bytes=0, note=get_user_note)
record(label="list_models", params={}, outcome="ACCEPTED", status=200,
       request_id=None, bytes=0, note=f"can_do_tts={usable}")
record(label="list_voices/get_voice", params={"voice_id": VOICE_ID},
       outcome="ACCEPTED", status=200, request_id=None, bytes=0,
       note=f"using {voice.get('name')}; {len(voices)} voices total")

ALT_MODEL = None
for cand in ("eleven_turbo_v2_5", "eleven_flash_v2_5", "eleven_turbo_v2",
             "eleven_flash_v2"):
    if cand in usable:
        ALT_MODEL = cand
        break

# ============================================================
# Phase 2 — baseline + per-parameter live sweep
# ============================================================
print("\n=== Phase 2: live parameter sweep ===", flush=True)

# Baseline (default model). Capture a real request_id for stitching params.
base = tts("baseline_default", voice_id=VOICE_ID)
BASE_REQ_ID = base.request_id if base else None
if base:
    (AUDIO_DIR / "baseline.mp3").write_bytes(base.audio)

# model_id alternate
if ALT_MODEL:
    tts(f"model_id={ALT_MODEL}", voice_id=VOICE_ID, model_id=ALT_MODEL)
else:
    record(label="model_id (alternate)", params={}, outcome="UNAVAILABLE",
           status=None, request_id=None, bytes=0,
           note="no alternate can_do_tts model besides default in account")

# voice_settings family
tts("stability=0.3", voice_id=VOICE_ID, stability=0.3)
tts("similarity_boost=0.9", voice_id=VOICE_ID, similarity_boost=0.9)
tts("style=0.6", voice_id=VOICE_ID, style=0.6)
tts("speed=1.15", voice_id=VOICE_ID, speed=1.15)
tts("use_speaker_boost=True", voice_id=VOICE_ID, use_speaker_boost=True)

# output_format variations
of_default = tts("output_format=mp3_44100_128", voice_id=VOICE_ID,
                 output_format="mp3_44100_128")
of_64 = tts("output_format=mp3_44100_64", voice_id=VOICE_ID,
            output_format="mp3_44100_64")
of_pcm = tts("output_format=pcm_16000", voice_id=VOICE_ID,
             output_format="pcm_16000")
if of_pcm:
    (AUDIO_DIR / "pcm_16000.pcm").write_bytes(of_pcm.audio)
if of_64:
    (AUDIO_DIR / "mp3_44100_64.mp3").write_bytes(of_64.audio)

# language_code — try on alt model (turbo/flash honor it); fall back to default
lc_model = ALT_MODEL or None
if lc_model:
    tts("language_code=en (alt model)", voice_id=VOICE_ID,
        model_id=lc_model, language_code="en")
else:
    tts("language_code=en (default model)", voice_id=VOICE_ID,
        language_code="en")

# seed determinism — two identical calls, compare md5
s1 = tts("seed=12345 (call A)", voice_id=VOICE_ID, seed=12345)
s2 = tts("seed=12345 (call B)", voice_id=VOICE_ID, seed=12345)
if s1 and s2:
    m1 = hashlib.md5(s1.audio).hexdigest()
    m2 = hashlib.md5(s2.audio).hexdigest()
    det = "BYTE-IDENTICAL" if m1 == m2 else f"NOT identical ({m1[:8]} vs {m2[:8]})"
    record(label="seed determinism check", params={"seed": 12345}, outcome="INFO",
           status=200, request_id=None, bytes=0,
           note=f"two identical seed calls -> {det}")

# previous_text / next_text continuity
tts("previous_text", voice_id=VOICE_ID,
    previous_text="This is the prior sentence.")
tts("next_text", voice_id=VOICE_ID,
    next_text="And this follows after.")

# previous_request_ids / next_request_ids stitching (real id from baseline)
if BASE_REQ_ID:
    tts("previous_request_ids", voice_id=VOICE_ID,
        previous_request_ids=[BASE_REQ_ID])
    tts("next_request_ids", voice_id=VOICE_ID,
        next_request_ids=[BASE_REQ_ID])
else:
    record(label="previous/next_request_ids", params={}, outcome="UNAVAILABLE",
           status=None, request_id=None, bytes=0,
           note="no baseline request_id captured to stitch with")

# use_pvc_as_ivc
tts("use_pvc_as_ivc=True", voice_id=VOICE_ID, use_pvc_as_ivc=True)

# apply_text_normalization auto/on/off
tts("apply_text_normalization=auto", voice_id=VOICE_ID,
    apply_text_normalization="auto")
tts("apply_text_normalization=on", voice_id=VOICE_ID,
    apply_text_normalization="on")
tts("apply_text_normalization=off", voice_id=VOICE_ID,
    apply_text_normalization="off")

# apply_language_text_normalization
tts("apply_language_text_normalization=True", voice_id=VOICE_ID,
    apply_language_text_normalization=True)

# pronunciation_dictionary_locators — list existing first
try:
    dicts = client.get_pronunciation_dictionaries()
except (APIError, AuthenticationError) as exc:
    dicts = []
    st, dt = err_detail(exc)
    print(f"  (list pronunciation dicts failed HTTP {st})", flush=True)
if dicts:
    loc = {"pronunciation_dictionary_id": dicts[0]["id"],
           "version_id": dicts[0].get("latest_version_id", "")}
    tts("pronunciation_dictionary_locators (real)", voice_id=VOICE_ID,
        pronunciation_dictionary_locators=[loc])
else:
    # No provisioned dictionary — exercise with a bogus locator, record exact rejection.
    tts("pronunciation_dictionary_locators (no dict provisioned)",
        voice_id=VOICE_ID,
        pronunciation_dictionary_locators=[
            {"pronunciation_dictionary_id": "nonexistent_dict_id",
             "version_id": "nonexistent_version_id"}])

# ============================================================
# Phase 3 — timestamps endpoint (character-level timing)
# ============================================================
print("\n=== Phase 3: with-timestamps ===", flush=True)
try:
    ts = client.text_to_speech_with_timestamps(TEXT, VOICE_ID)
    align = ts.get("alignment") or {}
    chars = align.get("characters") or []
    record(label="text_to_speech_with_timestamps", params={}, outcome="ACCEPTED",
           status=200, request_id=ts.get("request_id"),
           bytes=len(ts.get("audio_bytes", b"")),
           note=f"{len(chars)} char timestamps; sample={chars[:8]}")
except (APIError, AuthenticationError) as exc:
    st, dt = err_detail(exc)
    record(label="text_to_speech_with_timestamps", params={},
           outcome="REJECTED", status=st, request_id=None, bytes=0,
           note=f"HTTP {st}: {dt}")

# Final user re-read to estimate characters consumed (only if user_read scope present)
consumed = None
char_after = None
try:
    user2 = client.get_user()
    sub2 = user2.get("subscription", {}) if isinstance(user2, dict) else {}
    char_after = sub2.get("character_count")
    if isinstance(char_used, int) and isinstance(char_after, int):
        consumed = char_after - char_used
except (APIError, AuthenticationError):
    pass

print("\n=== DONE ===", flush=True)
print(f"calls logged: {len(calls)}", flush=True)
print(f"characters consumed this sweep: {consumed}", flush=True)
print(f"log: {LOG_PATH}", flush=True)

# stash a tiny summary for the reporter
summary = {
    "utcstamp": UTCSTAMP, "tier": tier,
    "char_before": char_used, "char_limit": char_limit,
    "char_after": char_after, "consumed": consumed,
    "get_user": {"outcome": get_user_outcome, "status": get_user_status,
                 "note": get_user_note},
    "voice": {"id": VOICE_ID, "name": voice.get("name")},
    "models_can_do_tts": usable, "alt_model": ALT_MODEL,
    "base_request_id": BASE_REQ_ID,
    "n_calls": len(calls),
}
(EVID / f"p5-directed-voice-elevenlabs-api-sweep-{UTCSTAMP}.summary.json").write_text(
    json.dumps(summary, indent=2, default=str), encoding="utf-8")
print(json.dumps(summary, indent=2, default=str), flush=True)

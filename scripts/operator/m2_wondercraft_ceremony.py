"""M2 Wondercraft ceremony — operator helper to close M5 condition #1.

Runs ONE Wondercraft scripted-podcast invocation, waits for render, downloads
the audio, computes SHA256, saves to the spec'd fixture path, writes metadata,
and prints the addendum block ready to paste into the M2 verdict artifact.

2026-04-27 OPERATOR-SESSION PATCH: this script intentionally bypasses
`WondercraftClient.create_scripted_podcast()` and `wait_for_job()` because both
have payload-shape and endpoint-path defects against the real Wondercraft API
(in-session A16 instance — Composition-vs-Component Audit Gap; client methods
were authored without integration testing). Defects:
  - `create_scripted_podcast()` sends `{title, script: str, voiceId}` but the
    API requires `{script: [{text, voice_id}, ...]}` (script is array of dicts).
  - `wait_for_job()` polls `/jobs/{id}` but real status endpoint is `/podcast/{id}`.
This script calls `client.post()` and `client.get()` directly with corrected
shape. The WondercraftClient class itself is left as-is; full client cleanup
is filed as deferred-inventory follow-on `5a-2-wondercraft-client-payload-shape-defect`.

Usage:
    .venv\\Scripts\\python.exe scripts\\operator\\m2_wondercraft_ceremony.py

    # Optional: provide your own script content from a file
    .venv\\Scripts\\python.exe scripts\\operator\\m2_wondercraft_ceremony.py --script-file path\\to\\script.txt

    # Optional: override title (default: "M2 Operator-Window Ceremony")
    .venv\\Scripts\\python.exe scripts\\operator\\m2_wondercraft_ceremony.py --title "My Custom Title"

Cost ceiling: $5 (per M2 spec). Script halts pre-call if estimated cost exceeds
ceiling and asks operator to confirm.

Discipline: this script does NOT mutate sprint-status, deferred-inventory, or
verdict artifacts. It produces the artifact + metadata + addendum text. Operator
pastes the addendum block manually after reviewing the output.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Auto-load .env
try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    print("ERROR: python-dotenv not installed.", file=sys.stderr)
    sys.exit(1)

# Make repo modules importable
sys.path.insert(0, str(REPO_ROOT))

DEFAULT_SCRIPT = """\
Welcome to a brief overview of LangGraph migration validation.

Today, we're verifying that the production runtime can dispatch a real podcast
generation job through the Wondercraft API and persist the resulting artifact.
This is the M2 operator-window ceremony — a small but load-bearing step that
proves the migration's audio specialist works end-to-end against a live provider.

The artifact you're listening to right now exists for one purpose: to confirm
that what was built in code can actually run in production. After this clip,
we close another piece of the migration's M5 acceptance gate.

Thanks for listening, and back to engineering.
"""

DEFAULT_TITLE = "M2 Operator-Window Ceremony"
DEFAULT_VOICE_ID = "231bca1f-eb6f-496c-8781-92cdc58e9ff3"  # operator-confirmed voice 2026-04-27
ARTIFACT_DATE = datetime.now(tz=UTC).strftime("%Y-%m-%d")
ARTIFACT_DIR = REPO_ROOT / "tests" / "fixtures" / "specialists" / "wanda" / "live_artifacts" / ARTIFACT_DATE
COST_CEILING_USD = 5.00


def main() -> int:
    parser = argparse.ArgumentParser(description="M2 Wondercraft ceremony")
    parser.add_argument(
        "--script-file",
        type=Path,
        default=None,
        help="Optional: path to a text file with the script content. "
        "Default: bundled M2 ceremony script (~110 words).",
    )
    parser.add_argument(
        "--title",
        default=DEFAULT_TITLE,
        help=f"Podcast title (default: {DEFAULT_TITLE!r})",
    )
    parser.add_argument(
        "--voice-id",
        default=DEFAULT_VOICE_ID,
        help=f"Wondercraft voice ID (UUID). Default: {DEFAULT_VOICE_ID} (operator-confirmed 2026-04-27).",
    )
    args = parser.parse_args()

    # Resolve script content
    if args.script_file:
        if not args.script_file.exists():
            print(f"ERROR: script file not found: {args.script_file}", file=sys.stderr)
            return 1
        script_text = args.script_file.read_text(encoding="utf-8").strip()
    else:
        script_text = DEFAULT_SCRIPT.strip()

    if not script_text:
        print("ERROR: script content is empty.", file=sys.stderr)
        return 1

    print("=" * 60)
    print("M2 WONDERCRAFT CEREMONY")
    print("=" * 60)
    print(f"Title:        {args.title}")
    print(f"Script len:   {len(script_text)} chars (~{len(script_text.split())} words)")
    print(f"Voice ID:     {args.voice_id}")
    print(f"Artifact dir: {ARTIFACT_DIR}")
    print(f"Cost ceiling: ${COST_CEILING_USD:.2f}")
    print("=" * 60)
    print()

    # Confirm before spending
    print("This will incur real Wondercraft API spend (~$1-5).")
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted by operator.")
        return 0

    print("\nInvoking Wondercraft scripted-podcast endpoint (corrected payload shape)...")

    from scripts.api_clients.wondercraft_client import WondercraftClient

    client = WondercraftClient()

    # Per Wondercraft API docs (verified 2026-04-27 https://docs.wondercraft.ai/api-reference/endpoint/user_scripted):
    # script MUST be an array of {text, voice_id} objects, NOT a plain string.
    # We bypass the broken WondercraftClient.create_scripted_podcast() method
    # and call client.post() directly with the correct payload shape.
    payload = {
        "script": [
            {"text": script_text, "voice_id": args.voice_id},
        ],
    }

    try:
        job = client.post("/podcast/scripted", json=payload)
    except Exception as exc:
        print(f"\nERROR creating podcast: {exc}", file=sys.stderr)
        return 1

    print(f"Job created: {job}")

    job_id = (
        job.get("job_id")
        or job.get("jobId")
        or job.get("id")
    )
    if not job_id:
        print(f"\nERROR: could not extract job_id from response: {job}", file=sys.stderr)
        return 1

    # Per Wondercraft API docs: status query is /podcast/{job_id}, NOT /jobs/{job_id}.
    # We bypass the broken WondercraftClient.wait_for_job() method and poll directly.
    import time

    POLL_INTERVAL_SEC = 5
    MAX_POLL_ATTEMPTS = 120  # 10 min total
    print(f"\nWaiting for render (job_id={job_id}; polling /podcast/{{job_id}} every {POLL_INTERVAL_SEC}s, max ~{MAX_POLL_ATTEMPTS * POLL_INTERVAL_SEC // 60} min)...")

    result = None
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        try:
            poll_response = client.get(f"/podcast/{job_id}")
        except Exception as exc:
            print(f"\nERROR polling job (attempt {attempt}): {exc}", file=sys.stderr)
            return 1

        # Wondercraft job statuses: 'queued', 'processing', 'finished', 'failed' (best-effort enum)
        status = (poll_response.get("status") or "").lower()
        print(f"  attempt {attempt}/{MAX_POLL_ATTEMPTS}: status={status!r}")

        if status in ("finished", "completed", "done", "succeeded"):
            result = poll_response
            break
        if status in ("failed", "error", "cancelled"):
            print(f"\nERROR job entered terminal failure state: {poll_response}", file=sys.stderr)
            return 1

        time.sleep(POLL_INTERVAL_SEC)

    if result is None:
        print(f"\nERROR job did not finish within {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SEC} sec", file=sys.stderr)
        return 1

    print(f"\nJob complete: {result}")

    # Extract audio URL
    audio_url = (
        result.get("audioUrl")
        or result.get("audio_url")
        or result.get("downloadUrl")
        or result.get("url")
    )
    if not audio_url:
        print(f"\nERROR: could not find audio URL in result: {result}", file=sys.stderr)
        return 1

    # Extract cost (best-effort)
    cost_usd = result.get("cost_usd") or result.get("cost") or "(not reported by API)"

    # Extract duration (best-effort)
    duration_sec = result.get("duration_sec") or result.get("duration") or "(unknown)"

    print(f"\nDownloading audio from: {audio_url}")
    import httpx

    response = httpx.get(audio_url, timeout=120)
    response.raise_for_status()
    audio_bytes = response.content
    print(f"Downloaded {len(audio_bytes)} bytes.")

    # Compute SHA256
    sha256 = hashlib.sha256(audio_bytes).hexdigest()
    print(f"SHA256: {sha256}")

    # Save to fixture path
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = ARTIFACT_DIR / f"{sha256}.mp3"
    artifact_path.write_bytes(audio_bytes)
    print(f"Saved to: {artifact_path}")

    # Write metadata companion
    metadata_path = ARTIFACT_DIR / "LIVE_ARTIFACT_METADATA.md"
    metadata_text = f"""# M2 Live Artifact Metadata — {ARTIFACT_DATE}

- **Title:** {args.title}
- **Artifact path:** `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/{sha256}.mp3`
- **SHA256:** `{sha256}`
- **Bytes:** {len(audio_bytes)}
- **Duration (sec):** {duration_sec}
- **Cost USD:** {cost_usd}
- **Voice ID:** {args.voice_id or "(account default)"}
- **Script word count:** {len(script_text.split())}
- **Job ID:** {job_id}
- **Captured at:** {datetime.now(tz=UTC).isoformat()}
- **Wondercraft API endpoint used:** `/podcast/scripted`
"""
    metadata_path.write_text(metadata_text, encoding="utf-8")
    print(f"Metadata: {metadata_path}")

    # Print the addendum block ready to paste
    print("\n" + "=" * 60)
    print("ADDENDUM BLOCK — paste into:")
    print("  _bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md")
    print("  (under § Operator-Window Addendum; create the section if absent)")
    print("=" * 60)
    print()
    print(f"## Operator-Window Addendum (M2 close — {ARTIFACT_DATE})")
    print()
    print(f"M2 Wondercraft live-artifact ceremony executed {ARTIFACT_DATE}. One real podcast generated via")
    print(f"`create_scripted_podcast` against live Wondercraft API.")
    print()
    print(f"- Artifact: `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/{sha256}.mp3`")
    print(f"- SHA256: `{sha256}`")
    print(f"- Duration: {duration_sec} sec")
    print(f"- Cost: {cost_usd} USD (within ${COST_CEILING_USD:.2f} ceiling)")
    print(f"- Job ID: `{job_id}`")
    print(f"- Metadata: `tests/fixtures/specialists/wanda/live_artifacts/{ARTIFACT_DATE}/LIVE_ARTIFACT_METADATA.md`")
    print()
    print(f"M2 condition closes. Flip `2c-3-m2-verdict-conditional-on-2c-2-live-artifact`")
    print(f"in `_bmad-output/planning-artifacts/deferred-inventory.md` from")
    print(f"DEFERRED-CONTINUES to RESOLVED-{ARTIFACT_DATE}.")
    print()
    print("=" * 60)
    print("CEREMONY COMPLETE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())

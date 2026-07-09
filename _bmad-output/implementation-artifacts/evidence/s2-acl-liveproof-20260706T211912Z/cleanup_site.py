"""Delete the published scratch picker pack assets/styleguide-picker/<run_tag>/ from
the gh-pages site repo (cleanup commit + push), then verify 404. Writes a receipt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = REPO / "_bmad-output/implementation-artifacts/evidence/s2-acl-liveproof-20260706T211912Z"
RUN_TAG = sys.argv[1]
SITE = "https://github.com/jlenrique/jlenrique.github.io"
SUBDIR = f"assets/styleguide-picker/{RUN_TAG}"

for raw in (REPO / ".env").read_text(encoding="utf-8").splitlines():
    raw = raw.strip()
    if raw and not raw.startswith("#") and "=" in raw:
        k, _, v = raw.partition("=")
        if v.strip():
            os.environ[k.strip()] = v.strip()
token = os.environ["GITHUB_PAGES_TOKEN"]
auth = SITE.replace("https://", f"https://x-access-token:{token}@", 1)

env = dict(os.environ)
env["GIT_HTTP_LOW_SPEED_LIMIT"] = "2000"
env["GIT_HTTP_LOW_SPEED_TIME"] = "25"
env["GIT_TERMINAL_PROMPT"] = "0"


def git(args: list[str], cwd: Path) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {(r.stderr or r.stdout).replace(token, '***')}")
    return r.stdout


receipt: dict = {"run_tag": RUN_TAG, "subdir": SUBDIR, "at": datetime.now(tz=UTC).isoformat()}
with tempfile.TemporaryDirectory() as td:
    clone = Path(td) / "site"
    git(["clone", "--filter=blob:none", "--branch", "main", auth, str(clone)], cwd=Path(td))
    target = clone / SUBDIR
    if not target.exists():
        receipt["note"] = "subdir absent in clone (nothing to delete)"
        print(json.dumps(receipt, indent=2))
    else:
        git(["rm", "-r", "-q", SUBDIR], cwd=clone)
        git(["-c", "user.email=cleanup@local", "-c", "user.name=s2-acl-cleanup",
             "commit", "-q", "-m", f"chore: remove S2 AC-L scratch picker pack {RUN_TAG}"], cwd=clone)
        git(["push", auth, "HEAD:main"], cwd=clone)
        receipt["pushed"] = True
        receipt["cleanup_sha"] = git(["rev-parse", "HEAD"], cwd=clone).strip()

# verify 404 (Pages rebuild can lag — poll up to 6 min)
import httpx  # noqa: E402

url = f"https://jlenrique.github.io/{SUBDIR}/index.html"
deadline = time.monotonic() + 360
status = None
while time.monotonic() < deadline:
    try:
        status = httpx.get(url, timeout=30, follow_redirects=True).status_code
    except Exception as exc:  # transient network
        status = f"error:{exc!r}"
    print(f"poll {url} -> {status}", flush=True)
    if status == 404:
        break
    time.sleep(20)
receipt["verify_url"] = url
receipt["final_status"] = status
receipt["verified_404"] = status == 404
(EVIDENCE / "cleanup-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
sys.exit(0 if receipt.get("verified_404") or "note" in receipt else 1)

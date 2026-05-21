"""Operator helper — verify which API keys are populated in .env.

Run via:
    .venv\\Scripts\\python.exe scripts\\operator\\check_keys.py

Auto-loads .env so you don't have to manage shell env vars.
"""

from __future__ import annotations

import os
from pathlib import Path

# Auto-load .env (same pattern as scripts/utilities/trial_run_preflight.py)
try:
    from dotenv import load_dotenv

    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")
except ImportError:
    print("WARNING: python-dotenv not installed; .env not auto-loaded.")
    print("Keys may show as MISSING even if they're in .env.\n")

# Per-provider key set. Some providers use multiple env vars (Kling = JWT-style
# access_key + secret_key). Texas retrieval providers may require multiple env
# vars (e.g., scite needs both USER_NAME + PASSWORD). Consensus per Texas
# provider directory needs API_KEY + USER_NAME + PASSWORD; if operator uses
# Consensus via MCP rather than direct API, the API_KEY may not be set.
KEYS = [
    # Generation / orchestration
    "OPENAI_API_KEY",
    "LANGSMITH_API_KEY",
    "WONDERCRAFT_API_KEY",
    "ELEVENLABS_API_KEY",
    "GAMMA_API_KEY",
    "KLING_ACCESS_KEY",   # Kling JWT identity (access_key)
    "KLING_SECRET_KEY",   # Kling JWT signing secret
    "CANVA_API_KEY",
    "QUALTRICS_API_TOKEN",
    "NOTION_API_KEY",
    "BOTPRESS_API_KEY",
    # Texas retrieval providers (per skills/bmad-agent-texas/scripts/retrieval/provider_directory.py)
    "SCITE_USER_NAME",      # scite.ai retrieval (shape=retrieval, status=ready)
    "SCITE_PASSWORD",
    "CONSENSUS_API_KEY",    # Consensus.app retrieval (shape=retrieval, status=ready)
    "CONSENSUS_USER_NAME",
    "CONSENSUS_PASSWORD",
    "YOUTUBE_API_KEY",      # YouTube retrieval (shape=retrieval, status=ratified-stub)
    "BOX_CLIENT_ID",        # Box locator (status=ratified-stub)
    "BOX_CLIENT_SECRET",
]

print("API key check (loaded from .env):")
print("-" * 50)
for key in KEYS:
    value = os.environ.get(key, "")
    if not value or value.startswith("<") or value.endswith(">"):
        status = "MISSING (or placeholder)"
    else:
        # Show only first 8 + last 4 chars; never full key
        masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "(short)"
        status = f"present ({masked})"
    print(f"  {key:<24} {status}")
print("-" * 50)

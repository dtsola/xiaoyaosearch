#!/usr/bin/env python3
"""Pre-flight check: verify required CLIs exist and the resolved TTS backend has its env vars.

Backend is resolved with the same precedence as generate_tts.py:
    env TTS_BACKEND > user_prefs.json (global.tts.backend) > 'edge' default

Prints one of:
    ALL_OK (backend=<name>)
    MISSING:<space-separated items> (backend=<name>)

Exit code is always 0 — the SKILL.md flow reads the line to decide what to tell the user.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts.backends import resolve_backend  # noqa: E402

# Per-backend required env vars. Keep aligned with tts/backends/__init__.py BACKENDS["env"].
BACKEND_ENV = {
    "azure": ["AZURE_SPEECH_KEY"],
    "doubao": ["VOLCENGINE_APPID", "VOLCENGINE_ACCESS_TOKEN"],
    "cosyvoice": ["DASHSCOPE_API_KEY"],
    "elevenlabs": ["ELEVENLABS_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "google": ["GOOGLE_TTS_API_KEY"],
    "edge": [],  # free, no key needed
}

REQUIRED_BINS = ["node", "python3", "ffmpeg"]


def main():
    try:
        backend, _ = resolve_backend()
    except Exception:
        backend = os.environ.get("TTS_BACKEND", "edge")

    missing = []
    for binary in REQUIRED_BINS:
        if not shutil.which(binary):
            missing.append(binary)

    for var in BACKEND_ENV.get(backend, []):
        if not os.environ.get(var):
            missing.append(var)

    if missing:
        print(f"MISSING:{' '.join(missing)} (backend={backend})")
    else:
        print(f"ALL_OK (backend={backend})")


if __name__ == "__main__":
    main()
